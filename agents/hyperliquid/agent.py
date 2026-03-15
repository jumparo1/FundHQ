#!/usr/bin/env python3
"""
Hyperliquid Whale Tracker Agent
================================
Monitors whale wallets on Hyperliquid, computes profitability scores,
and pushes alerts to Fund HQ via Firebase REST API.

Usage:
  python agent.py                    # Run full agent (monitor + scan)
  python agent.py scan               # One-shot: scan saved wallets
  python agent.py discover           # One-shot: discover whales on watch coins
  python agent.py profile <address>  # One-shot: profile a single wallet
"""

import asyncio
import json
import sys
import time
import uuid
from datetime import datetime, timezone
from typing import Optional

import aiohttp
import requests

from config import (
    HL_API_URL, HL_WS_URL,
    FIREBASE_DB_URL, FIREBASE_ALERTS_PATH, FIREBASE_HL_PATH,
    SCAN_INTERVAL_SECONDS, WHALE_MIN_POSITION_USD, WHALE_MIN_ACCOUNT_USD,
    PROFITABILITY_MIN_TRADES, WATCH_COINS,
    ALERT_NEW_POSITION_USD, ALERT_POSITION_CLOSE_USD, ALERT_PNL_CHANGE_PCT,
)


# ===== FIREBASE =====

def firebase_write(path: str, data: dict):
    """Write data to Firebase Realtime Database via REST API."""
    url = f"{FIREBASE_DB_URL}{path}.json"
    r = requests.put(url, json=data, timeout=10)
    r.raise_for_status()
    return r.json()


def firebase_read(path: str) -> Optional[dict]:
    """Read data from Firebase Realtime Database via REST API."""
    url = f"{FIREBASE_DB_URL}{path}.json"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()


def firebase_push_alert(title: str, content: str, severity: str = "info"):
    """Push an alert to Fund HQ's alerts page."""
    alert_id = f"hl_{uuid.uuid4().hex[:12]}"
    data = {
        "id": alert_id,
        "type": "hyperliquid",
        "title": title,
        "content": content,
        "severity": severity,      # info, warning, opportunity
        "dismissed": False,
        "created": datetime.now(timezone.utc).isoformat(),
        "source": "hl-agent",
    }
    firebase_write(f"{FIREBASE_ALERTS_PATH}/{alert_id}", data)
    print(f"  [ALERT] {severity.upper()}: {title}")
    return alert_id


# ===== HYPERLIQUID API =====

async def hl_post(session: aiohttp.ClientSession, body: dict) -> dict:
    """POST to Hyperliquid /info endpoint."""
    async with session.post(HL_API_URL, json=body) as resp:
        if resp.status != 200:
            raise Exception(f"HL API error {resp.status}: {await resp.text()}")
        return await resp.json()


async def get_wallet_state(session: aiohttp.ClientSession, address: str) -> dict:
    """Get wallet's current positions and margin summary."""
    return await hl_post(session, {"type": "clearinghouseState", "user": address})


async def get_wallet_fills(session: aiohttp.ClientSession, address: str, limit: int = 2000) -> list:
    """Get wallet's trade history."""
    return await hl_post(session, {"type": "userFills", "user": address})


async def get_meta(session: aiohttp.ClientSession) -> dict:
    """Get all perp metadata + asset contexts (OI, funding, volume)."""
    return await hl_post(session, {"type": "metaAndAssetCtxs"})


async def get_recent_trades(session: aiohttp.ClientSession, coin: str) -> list:
    """Get recent trades for a coin (returns buyer/seller addresses)."""
    return await hl_post(session, {"type": "recentTrades", "coin": coin})


# ===== WALLET PROFITABILITY SCORING =====

def compute_wallet_score(fills: list, state: dict) -> dict:
    """
    Compute profitability metrics for a wallet.
    Returns a score card with:
      - total_pnl, win_rate, avg_win, avg_loss, profit_factor
      - risk_score (leverage-adjusted)
      - consistency (Sharpe-like metric)
      - grade (A-F)
    """
    if not fills:
        return {"grade": "?", "total_trades": 0}

    # Parse fills
    wins, losses = [], []
    total_pnl = 0
    coins_traded = set()

    for f in fills:
        pnl = float(f.get("closedPnl", 0))
        if pnl > 0:
            wins.append(pnl)
        elif pnl < 0:
            losses.append(pnl)
        total_pnl += pnl
        coins_traded.add(f.get("coin", "?"))

    total_trades = len(wins) + len(losses)
    if total_trades < PROFITABILITY_MIN_TRADES:
        return {"grade": "?", "total_trades": total_trades, "note": "too few trades"}

    win_rate = len(wins) / total_trades * 100 if total_trades else 0
    avg_win = sum(wins) / len(wins) if wins else 0
    avg_loss = abs(sum(losses) / len(losses)) if losses else 0
    profit_factor = (sum(wins) / abs(sum(losses))) if losses and sum(losses) != 0 else float('inf')

    # Account info
    mg = state.get("marginSummary", {})
    account_value = float(mg.get("accountValue", 0))

    # Risk score: penalize high leverage
    positions = []
    for ap in state.get("assetPositions", []):
        p = ap.get("position", ap)
        sz = float(p.get("szi", 0))
        if sz != 0:
            lev = float(p.get("leverage", {}).get("value", 1)) if isinstance(p.get("leverage"), dict) else 1
            positions.append({"leverage": lev})

    avg_leverage = sum(p["leverage"] for p in positions) / len(positions) if positions else 1
    leverage_penalty = max(0, (avg_leverage - 5) * 2)  # Penalize >5x

    # Grade calculation
    score = 0
    if win_rate >= 60: score += 30
    elif win_rate >= 50: score += 20
    elif win_rate >= 40: score += 10

    if profit_factor >= 2.0: score += 30
    elif profit_factor >= 1.5: score += 20
    elif profit_factor >= 1.0: score += 10

    if total_pnl > 0: score += 20
    if total_trades >= 100: score += 10
    if len(coins_traded) >= 3: score += 10

    score = max(0, score - leverage_penalty)

    if score >= 80: grade = "A"
    elif score >= 60: grade = "B"
    elif score >= 40: grade = "C"
    elif score >= 20: grade = "D"
    else: grade = "F"

    return {
        "grade": grade,
        "score": round(score),
        "total_pnl": round(total_pnl, 2),
        "win_rate": round(win_rate, 1),
        "total_trades": total_trades,
        "wins": len(wins),
        "losses": len(losses),
        "avg_win": round(avg_win, 2),
        "avg_loss": round(avg_loss, 2),
        "profit_factor": round(profit_factor, 2) if profit_factor != float('inf') else 999,
        "account_value": round(account_value, 2),
        "avg_leverage": round(avg_leverage, 1),
        "coins_traded": len(coins_traded),
    }


# ===== WHALE DISCOVERY =====

async def discover_whales(coins: list = None, min_position: float = None) -> list:
    """
    Scan recent trades on target coins to discover whale wallets.
    Returns list of {address, positions, account_value, score}.
    """
    coins = coins or WATCH_COINS
    min_pos = min_position or WHALE_MIN_POSITION_USD
    print(f"[DISCOVER] Scanning {len(coins)} coins for whales (min ${min_pos:,.0f})...")

    async with aiohttp.ClientSession() as session:
        # Step 1: Collect addresses from recent trades
        addresses = set()
        for coin in coins:
            try:
                trades = await get_recent_trades(session, coin)
                if isinstance(trades, list):
                    for t in trades:
                        for u in t.get("users", []):
                            if u and u.startswith("0x"):
                                addresses.add(u)
            except Exception as e:
                print(f"  Warning: failed to get trades for {coin}: {e}")
            await asyncio.sleep(0.1)  # Rate limit

        print(f"  Found {len(addresses)} unique addresses, checking positions...")

        # Step 2: Check each address for whale-size positions
        whales = []
        checked = 0
        for addr in list(addresses)[:50]:  # Cap at 50 to respect rate limits
            try:
                state = await get_wallet_state(session, addr)
                mg = state.get("marginSummary", {})
                acct_val = float(mg.get("accountValue", 0))

                if acct_val < WHALE_MIN_ACCOUNT_USD:
                    continue

                positions = []
                for ap in state.get("assetPositions", []):
                    p = ap.get("position", ap)
                    sz = float(p.get("szi", 0))
                    if sz == 0:
                        continue
                    entry = float(p.get("entryPx", 0))
                    notional = abs(sz * entry)
                    if notional >= min_pos:
                        positions.append({
                            "coin": p.get("coin"),
                            "side": "LONG" if sz > 0 else "SHORT",
                            "size_usd": round(notional, 2),
                            "entry_px": entry,
                            "unrealized_pnl": round(float(p.get("unrealizedPnl", 0)), 2),
                            "leverage": float(p.get("leverage", {}).get("value", 1)) if isinstance(p.get("leverage"), dict) else 1,
                        })

                if positions:
                    whales.append({
                        "address": addr,
                        "account_value": round(acct_val, 2),
                        "positions": positions,
                        "total_notional": sum(p["size_usd"] for p in positions),
                    })

                checked += 1
                if checked % 10 == 0:
                    print(f"  Checked {checked}/{min(len(addresses), 50)} addresses...")

            except Exception as e:
                pass  # Skip failed addresses
            await asyncio.sleep(0.05)  # Rate limit (weight 2)

        # Sort by total notional
        whales.sort(key=lambda w: w["total_notional"], reverse=True)
        print(f"  Found {len(whales)} whales with {sum(len(w['positions']) for w in whales)} positions")
        return whales


# ===== WALLET MONITORING =====

class WalletMonitor:
    """Monitors saved wallets for position changes and generates alerts."""

    def __init__(self):
        self.snapshots: dict[str, dict] = {}  # addr -> last known state
        self.saved_wallets: list[dict] = []

    def load_saved_wallets(self):
        """Load saved wallets from Firebase."""
        try:
            data = firebase_read(f"{FIREBASE_HL_PATH}/saved_wallets")
            if data and isinstance(data, dict):
                self.saved_wallets = list(data.values())
            elif data and isinstance(data, list):
                self.saved_wallets = data
            else:
                self.saved_wallets = []
            print(f"[MONITOR] Loaded {len(self.saved_wallets)} saved wallets from Firebase")
        except Exception as e:
            print(f"[MONITOR] Warning: could not load from Firebase: {e}")
            self.saved_wallets = []

    async def scan_all(self):
        """Scan all saved wallets for changes."""
        if not self.saved_wallets:
            self.load_saved_wallets()
            if not self.saved_wallets:
                print("[MONITOR] No saved wallets to monitor")
                return

        print(f"[MONITOR] Scanning {len(self.saved_wallets)} wallets...")

        async with aiohttp.ClientSession() as session:
            for wallet in self.saved_wallets:
                addr = wallet.get("address", "")
                if not addr:
                    continue
                label = wallet.get("label", "") or addr[:10]

                try:
                    state = await get_wallet_state(session, addr)
                    new_positions = self._parse_positions(state)
                    old_positions = self.snapshots.get(addr, {})

                    # Detect changes
                    if old_positions:
                        self._detect_changes(addr, label, old_positions, new_positions, state)

                    self.snapshots[addr] = new_positions
                except Exception as e:
                    print(f"  Warning: failed to scan {label}: {e}")

                await asyncio.sleep(0.05)

    def _parse_positions(self, state: dict) -> dict:
        """Parse positions from clearinghouse state into a comparable dict."""
        positions = {}
        for ap in state.get("assetPositions", []):
            p = ap.get("position", ap)
            sz = float(p.get("szi", 0))
            if sz == 0:
                continue
            coin = p.get("coin", "?")
            entry = float(p.get("entryPx", 0))
            positions[coin] = {
                "side": "LONG" if sz > 0 else "SHORT",
                "size_usd": abs(sz * entry),
                "entry_px": entry,
                "unrealized_pnl": float(p.get("unrealizedPnl", 0)),
                "leverage": float(p.get("leverage", {}).get("value", 1)) if isinstance(p.get("leverage"), dict) else 1,
                "szi": sz,
            }
        return positions

    def _detect_changes(self, addr: str, label: str, old: dict, new: dict, state: dict):
        """Compare old vs new positions and generate alerts."""
        mg = state.get("marginSummary", {})
        acct_val = float(mg.get("accountValue", 0))

        # New positions opened
        for coin, pos in new.items():
            if coin not in old and pos["size_usd"] >= ALERT_NEW_POSITION_USD:
                firebase_push_alert(
                    f"Whale {label} opened {pos['side']} on {coin}",
                    f"${pos['size_usd']:,.0f} at {pos['leverage']:.0f}x leverage, entry ${pos['entry_px']:,.2f}. Account: ${acct_val:,.0f}",
                    severity="opportunity"
                )

        # Positions closed
        for coin, pos in old.items():
            if coin not in new and pos["size_usd"] >= ALERT_POSITION_CLOSE_USD:
                firebase_push_alert(
                    f"Whale {label} closed {pos['side']} on {coin}",
                    f"Was ${pos['size_usd']:,.0f} at {pos['leverage']:.0f}x. Account now: ${acct_val:,.0f}",
                    severity="info"
                )

        # Major PnL swings on existing positions
        for coin in set(old.keys()) & set(new.keys()):
            old_pnl = old[coin]["unrealized_pnl"]
            new_pnl = new[coin]["unrealized_pnl"]
            if old_pnl != 0:
                pnl_change = ((new_pnl - old_pnl) / abs(old_pnl)) * 100
                if abs(pnl_change) >= ALERT_PNL_CHANGE_PCT and abs(new_pnl - old_pnl) > 10_000:
                    direction = "up" if pnl_change > 0 else "down"
                    firebase_push_alert(
                        f"Whale {label}: {coin} PnL {direction} {abs(pnl_change):.0f}%",
                        f"{new[coin]['side']} ${new[coin]['size_usd']:,.0f}: PnL moved from ${old_pnl:,.0f} to ${new_pnl:,.0f}",
                        severity="warning" if pnl_change < 0 else "info"
                    )


# ===== WEBSOCKET MONITOR =====

async def ws_monitor_trades(coins: list = None):
    """
    Monitor real-time trades via WebSocket for whale-size fills.
    Runs indefinitely, alerting when large trades happen on watch coins.
    """
    import websockets

    coins = coins or WATCH_COINS
    print(f"[WS] Connecting to Hyperliquid WebSocket for {len(coins)} coins...")

    while True:
        try:
            async with websockets.connect(HL_WS_URL) as ws:
                # Subscribe to trades for each watched coin
                for coin in coins:
                    sub = {"method": "subscribe", "subscription": {"type": "trades", "coin": coin}}
                    await ws.send(json.dumps(sub))
                print(f"[WS] Subscribed to trades on: {', '.join(coins)}")

                async for msg in ws:
                    try:
                        data = json.loads(msg)
                        if data.get("channel") == "trades":
                            for trade in data.get("data", []):
                                sz = float(trade.get("sz", 0))
                                px = float(trade.get("px", 0))
                                notional = sz * px
                                coin = trade.get("coin", "?")

                                if notional >= ALERT_NEW_POSITION_USD:
                                    users = trade.get("users", [])
                                    side = trade.get("side", "?")
                                    buyer = users[0][:10] if users else "?"
                                    seller = users[1][:10] if len(users) > 1 else "?"
                                    print(f"  [WHALE TRADE] {coin} ${notional:,.0f} | {side} | buyer:{buyer} seller:{seller}")

                                    firebase_push_alert(
                                        f"Whale trade: ${notional:,.0f} {coin}",
                                        f"Side: {side}, Size: {sz}, Price: ${px:,.2f}. Buyer: {users[0] if users else '?'}, Seller: {users[1] if len(users)>1 else '?'}",
                                        severity="opportunity"
                                    )
                    except Exception as e:
                        pass  # Skip malformed messages

        except Exception as e:
            print(f"[WS] Connection lost: {e}. Reconnecting in 5s...")
            await asyncio.sleep(5)


# ===== MAIN AGENT LOOP =====

async def run_agent():
    """Main agent loop: periodic wallet scanning + WebSocket monitoring."""
    monitor = WalletMonitor()

    # Run both tasks concurrently
    async def periodic_scan():
        while True:
            try:
                monitor.load_saved_wallets()
                await monitor.scan_all()
            except Exception as e:
                print(f"[ERROR] Scan failed: {e}")
            print(f"[MONITOR] Next scan in {SCAN_INTERVAL_SECONDS}s...")
            await asyncio.sleep(SCAN_INTERVAL_SECONDS)

    print("=" * 60)
    print("  HYPERLIQUID WHALE TRACKER AGENT")
    print(f"  Watching: {', '.join(WATCH_COINS)}")
    print(f"  Scan interval: {SCAN_INTERVAL_SECONDS}s")
    print(f"  Min whale position: ${WHALE_MIN_POSITION_USD:,.0f}")
    print("=" * 60)

    await asyncio.gather(
        periodic_scan(),
        ws_monitor_trades(WATCH_COINS),
    )


# ===== CLI =====

async def cmd_profile(address: str):
    """Profile a single wallet — positions + profitability score."""
    async with aiohttp.ClientSession() as session:
        print(f"\nProfiling {address}...")
        state = await get_wallet_state(session, address)
        fills = await get_wallet_fills(session, address)
        score = compute_wallet_score(fills, state)

        mg = state.get("marginSummary", {})
        print(f"\n{'='*50}")
        print(f"  Account Value:  ${float(mg.get('accountValue', 0)):,.2f}")
        print(f"  Grade:          {score['grade']} ({score.get('score', '?')}/100)")
        print(f"  Win Rate:       {score.get('win_rate', '?')}%")
        print(f"  Total PnL:      ${score.get('total_pnl', 0):,.2f}")
        print(f"  Profit Factor:  {score.get('profit_factor', '?')}")
        print(f"  Trades:         {score.get('total_trades', 0)} ({score.get('wins', 0)}W / {score.get('losses', 0)}L)")
        print(f"  Avg Leverage:   {score.get('avg_leverage', '?')}x")
        print(f"  Coins Traded:   {score.get('coins_traded', '?')}")
        print(f"{'='*50}")

        # Show open positions
        positions = []
        for ap in state.get("assetPositions", []):
            p = ap.get("position", ap)
            sz = float(p.get("szi", 0))
            if sz != 0:
                positions.append(p)

        if positions:
            print(f"\n  Open Positions ({len(positions)}):")
            for p in positions:
                sz = float(p.get("szi", 0))
                side = "LONG" if sz > 0 else "SHORT"
                entry = float(p.get("entryPx", 0))
                notional = abs(sz * entry)
                upnl = float(p.get("unrealizedPnl", 0))
                lev = float(p.get("leverage", {}).get("value", 1)) if isinstance(p.get("leverage"), dict) else 1
                pnl_sign = "+" if upnl >= 0 else ""
                print(f"    {p.get('coin', '?'):>6} {side:>5}  ${notional:>12,.0f}  entry ${entry:>10,.2f}  PnL {pnl_sign}${upnl:>10,.2f}  {lev:.0f}x")

        return score


async def cmd_discover():
    """Discover whales and save results to Firebase."""
    whales = await discover_whales()
    if whales:
        # Save top whales to Firebase for the UI
        top_whales = whales[:20]
        firebase_write(f"{FIREBASE_HL_PATH}/discovered_whales", {
            "updated": datetime.now(timezone.utc).isoformat(),
            "count": len(whales),
            "whales": {w["address"][:12]: w for w in top_whales},
        })
        print(f"\nSaved {len(top_whales)} whales to Firebase")

        # Print summary
        print(f"\n{'='*70}")
        print(f"  TOP WHALES ({len(whales)} found)")
        print(f"{'='*70}")
        for w in whales[:10]:
            addr = w["address"][:10] + "..."
            print(f"  {addr}  ${w['account_value']:>12,.0f}  {len(w['positions'])} positions  ${w['total_notional']:>14,.0f} total")
            for p in w["positions"][:3]:
                print(f"    -> {p['coin']:>6} {p['side']:>5} ${p['size_usd']:>12,.0f}  PnL ${p['unrealized_pnl']:>10,.0f}  {p['leverage']:.0f}x")
    return whales


async def cmd_scan():
    """One-shot scan of saved wallets."""
    monitor = WalletMonitor()
    monitor.load_saved_wallets()
    await monitor.scan_all()
    print("[SCAN] Complete")


def main():
    if len(sys.argv) < 2:
        # Default: run full agent
        asyncio.run(run_agent())
    elif sys.argv[1] == "scan":
        asyncio.run(cmd_scan())
    elif sys.argv[1] == "discover":
        asyncio.run(cmd_discover())
    elif sys.argv[1] == "profile" and len(sys.argv) > 2:
        asyncio.run(cmd_profile(sys.argv[2]))
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
