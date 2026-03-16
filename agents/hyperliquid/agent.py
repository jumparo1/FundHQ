#!/usr/bin/env python3
"""
Hyperliquid Smart Whale Agent v2
=================================
Intelligent whale tracker with pattern detection, market regime awareness,
copy-trade signals, and smart alert filtering.

Informed by Senpi's 22-agent experiment: fewer trades + higher conviction = alpha.

Usage:
  python agent.py                    # Run full agent (monitor + scan + regime)
  python agent.py scan               # One-shot: scan saved wallets
  python agent.py discover           # One-shot: discover whales on watch coins
  python agent.py profile <address>  # One-shot: profile a single wallet
  python agent.py regime             # One-shot: check market regime
  python agent.py signals            # One-shot: generate copy-trade signals
"""

import asyncio
import json
import sys
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from typing import Optional

import aiohttp
import requests

from config import (
    HL_API_URL, HL_WS_URL, HL_LEADERBOARD_URL,
    FIREBASE_DB_URL, FIREBASE_ALERTS_PATH, FIREBASE_HL_PATH,
    SCAN_INTERVAL_SECONDS, REGIME_INTERVAL_SECONDS,
    WHALE_MIN_POSITION_USD, WHALE_MIN_ACCOUNT_USD,
    PROFITABILITY_MIN_TRADES, WATCH_COINS,
    ALERT_NEW_POSITION_USD, ALERT_POSITION_CLOSE_USD, ALERT_PNL_CHANGE_PCT,
    ALERT_MIN_WHALE_GRADE, GRADE_RANK,
    COPY_MIN_GRADE, COPY_MIN_POSITION_USD, COPY_MAX_LEVERAGE,
    FUNDING_BULLISH_THRESHOLD, FUNDING_BEARISH_THRESHOLD,
    OI_EXPANDING_PCT, OI_CONTRACTING_PCT,
    SQUEEZE_FUNDING_EXTREME, SQUEEZE_FUNDING_NEGATIVE,
    ACCUMULATION_MIN_WHALES, ACCUMULATION_LOOKBACK_SCANS,
    STALKER_MIN_SIZE_INCREASE_PCT,
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


def firebase_push_alert(title: str, content: str, severity: str = "info", tags: list = None):
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
    if tags:
        data["tags"] = tags
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


async def get_wallet_fills(session: aiohttp.ClientSession, address: str) -> list:
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
    Senpi insight: profit factor and avg_win/avg_loss ratio matter more than win rate.
    A 43% win rate prints money when avg winner is 10x avg loser.
    """
    if not fills:
        return {"grade": "?", "total_trades": 0}

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
    # Senpi key metric: avg_win / avg_loss ratio (power law indicator)
    win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else float('inf')

    mg = state.get("marginSummary", {})
    account_value = float(mg.get("accountValue", 0))

    # Parse positions for leverage
    positions = []
    for ap in state.get("assetPositions", []):
        p = ap.get("position", ap)
        sz = float(p.get("szi", 0))
        if sz != 0:
            lev = float(p.get("leverage", {}).get("value", 1)) if isinstance(p.get("leverage"), dict) else 1
            positions.append({"leverage": lev})

    avg_leverage = sum(p["leverage"] for p in positions) / len(positions) if positions else 1
    leverage_penalty = max(0, (avg_leverage - 5) * 2)

    # Enhanced grading — rewards power-law traders (Senpi insight)
    score = 0
    # Win rate (less important than people think)
    if win_rate >= 60: score += 20
    elif win_rate >= 45: score += 15
    elif win_rate >= 35: score += 10

    # Profit factor (most important single metric)
    if profit_factor >= 3.0: score += 35
    elif profit_factor >= 2.0: score += 30
    elif profit_factor >= 1.5: score += 20
    elif profit_factor >= 1.0: score += 10

    # Win/loss ratio — power law indicator
    if win_loss_ratio >= 5.0: score += 15
    elif win_loss_ratio >= 3.0: score += 10
    elif win_loss_ratio >= 2.0: score += 5

    # Profitable overall
    if total_pnl > 0: score += 15

    # Selectivity bonus (Senpi: fewer trades = better)
    if 20 <= total_trades <= 120: score += 10
    elif total_trades <= 200: score += 5
    # Penalty for overtrading
    if total_trades > 400: score -= 10

    # Diversification
    if len(coins_traded) >= 3: score += 5

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
        "win_loss_ratio": round(win_loss_ratio, 2) if win_loss_ratio != float('inf') else 999,
        "account_value": round(account_value, 2),
        "avg_leverage": round(avg_leverage, 1),
        "coins_traded": len(coins_traded),
    }


def grade_passes(grade: str, min_grade: str) -> bool:
    """Check if a grade meets the minimum threshold."""
    return GRADE_RANK.get(grade, 0) >= GRADE_RANK.get(min_grade, 0)


# ===== MARKET REGIME DETECTION =====

class MarketRegime:
    """
    Detects macro market regime from funding rates, OI, and volume.
    Senpi insight: mean reversion fails when BTC regime is bearish.
    """

    def __init__(self):
        self.prev_snapshot = {}  # coin -> {oi, funding, volume}
        self.current_regime = "unknown"
        self.coin_regimes = {}   # coin -> regime details
        self.squeeze_alerts = set()  # avoid duplicate squeeze alerts

    async def update(self, session: aiohttp.ClientSession) -> dict:
        """Fetch fresh market data and compute regime."""
        meta = await get_meta(session)
        universe = meta[0]["universe"]
        ctxs = meta[1]

        snapshot = {}
        for i, coin_meta in enumerate(universe):
            coin = coin_meta["name"]
            ctx = ctxs[i]
            snapshot[coin] = {
                "mark_px": float(ctx.get("markPx") or 0),
                "funding": float(ctx.get("funding") or 0),
                "oi": float(ctx.get("openInterest") or 0),
                "volume": float(ctx.get("dayNtlVlm") or 0),
                "premium": float(ctx.get("premium") or 0),
            }

        # Compute BTC regime (anchor for everything)
        btc = snapshot.get("BTC", {})
        btc_funding = btc.get("funding", 0)
        btc_oi = btc.get("oi", 0)
        btc_prev_oi = self.prev_snapshot.get("BTC", {}).get("oi", btc_oi)
        btc_oi_change = ((btc_oi - btc_prev_oi) / btc_prev_oi * 100) if btc_prev_oi else 0

        # Determine overall regime
        if btc_funding > FUNDING_BULLISH_THRESHOLD and btc_oi_change > OI_EXPANDING_PCT:
            self.current_regime = "risk-on"
        elif btc_funding < FUNDING_BEARISH_THRESHOLD or btc_oi_change < OI_CONTRACTING_PCT:
            self.current_regime = "risk-off"
        else:
            self.current_regime = "neutral"

        # Per-coin analysis for squeeze detection and opportunities
        self.coin_regimes = {}
        squeeze_coins = []
        for coin in WATCH_COINS:
            if coin not in snapshot:
                continue
            s = snapshot[coin]
            prev = self.prev_snapshot.get(coin, {})
            prev_oi = prev.get("oi", s["oi"])
            oi_change = ((s["oi"] - prev_oi) / prev_oi * 100) if prev_oi else 0

            coin_regime = {
                "funding": s["funding"],
                "funding_annual": s["funding"] * 24 * 365 * 100,
                "oi": s["oi"],
                "oi_usd": s["oi"] * s["mark_px"],
                "oi_change_pct": round(oi_change, 2),
                "volume": s["volume"],
                "premium": s["premium"],
                "mark_px": s["mark_px"],
            }

            # Squeeze detection
            if s["funding"] > SQUEEZE_FUNDING_EXTREME:
                coin_regime["squeeze"] = "short_squeeze"
                squeeze_coins.append((coin, "SHORT SQUEEZE", s["funding"]))
            elif s["funding"] < SQUEEZE_FUNDING_NEGATIVE:
                coin_regime["squeeze"] = "long_squeeze"
                squeeze_coins.append((coin, "LONG SQUEEZE", s["funding"]))
            else:
                coin_regime["squeeze"] = None

            self.coin_regimes[coin] = coin_regime

        # Fire squeeze alerts (deduplicated)
        for coin, squeeze_type, funding in squeeze_coins:
            key = f"{coin}_{squeeze_type}"
            if key not in self.squeeze_alerts:
                self.squeeze_alerts.add(key)
                ann_rate = funding * 24 * 365 * 100
                firebase_push_alert(
                    f"{squeeze_type} setup: {coin}",
                    f"Extreme funding {funding*100:.4f}% ({ann_rate:.0f}% ann). "
                    f"OI: {snapshot[coin]['oi']:,.0f}. Regime: {self.current_regime}. "
                    f"Consider fading the crowd.",
                    severity="opportunity",
                    tags=["squeeze", "regime", coin.lower()],
                )

        # Clear old squeeze alerts when funding normalizes
        for key in list(self.squeeze_alerts):
            coin = key.split("_")[0]
            if coin in snapshot:
                f = snapshot[coin]["funding"]
                if abs(f) < SQUEEZE_FUNDING_EXTREME * 0.5:
                    self.squeeze_alerts.discard(key)

        self.prev_snapshot = snapshot

        return {
            "regime": self.current_regime,
            "btc_funding": btc_funding,
            "btc_oi_change": round(btc_oi_change, 2),
            "squeeze_coins": [c[0] for c in squeeze_coins],
            "coin_count": len(self.coin_regimes),
        }

    def get_signal_conviction(self, coin: str, side: str) -> str:
        """
        Grade signal conviction based on regime alignment.
        Senpi: best agents gate signals on regime — won't enter if regime opposes.
        """
        cr = self.coin_regimes.get(coin, {})
        regime = self.current_regime

        # Perfect alignment: whale + regime agree
        if regime == "risk-on" and side == "LONG":
            return "high"
        if regime == "risk-off" and side == "SHORT":
            return "high"

        # Squeeze fade: contrarian with extreme funding
        squeeze = cr.get("squeeze")
        if squeeze == "short_squeeze" and side == "SHORT":
            return "high"  # Fading the crowd at extremes
        if squeeze == "long_squeeze" and side == "LONG":
            return "high"

        # Neutral regime: moderate conviction
        if regime == "neutral":
            return "medium"

        # Against regime: low conviction
        return "low"


# ===== TRADING PATTERN DETECTION =====

class PatternDetector:
    """
    Detects whale trading patterns across scans.
    Senpi insight: Stalker mode (quiet accumulation) produces the biggest winners.
    """

    def __init__(self):
        # coin -> [{scan_time, wallets: {addr: {side, size}}}]
        self.scan_history = defaultdict(list)
        self.alerted_patterns = set()

    def record_scan(self, coin: str, wallet_positions: list):
        """Record whale positions for a coin at this scan."""
        wallets = {}
        for wp in wallet_positions:
            wallets[wp["address"]] = {
                "side": wp["side"],
                "size": wp["size_usd"],
                "grade": wp.get("grade", "?"),
            }
        self.scan_history[coin].append({
            "time": time.time(),
            "wallets": wallets,
        })
        # Keep only last N scans
        self.scan_history[coin] = self.scan_history[coin][-ACCUMULATION_LOOKBACK_SCANS:]

    def detect_accumulation(self, coin: str) -> Optional[dict]:
        """
        Detect accumulation pattern: multiple whales building same-direction positions.
        This is Senpi's "Stalker mode" — quiet building before the crowd arrives.
        """
        history = self.scan_history.get(coin, [])
        if len(history) < 2:
            return None

        latest = history[-1]["wallets"]
        if not latest:
            return None

        # Count wallets per side in latest scan
        long_wallets = [a for a, w in latest.items() if w["side"] == "LONG"]
        short_wallets = [a for a, w in latest.items() if w["side"] == "SHORT"]

        # Check for accumulation (same direction convergence)
        for side, wallets in [("LONG", long_wallets), ("SHORT", short_wallets)]:
            if len(wallets) < ACCUMULATION_MIN_WHALES:
                continue

            # Check if wallets are growing their positions (stalker mode)
            growing = 0
            for addr in wallets:
                sizes = []
                for scan in history:
                    if addr in scan["wallets"] and scan["wallets"][addr]["side"] == side:
                        sizes.append(scan["wallets"][addr]["size"])
                if len(sizes) >= 2 and sizes[-1] > sizes[0] * (1 + STALKER_MIN_SIZE_INCREASE_PCT / 100):
                    growing += 1

            total_size = sum(latest[a]["size"] for a in wallets)
            grades = [latest[a].get("grade", "?") for a in wallets]
            a_or_b = sum(1 for g in grades if g in ("A", "B"))

            pattern_key = f"{coin}_{side}_{len(wallets)}"
            if pattern_key in self.alerted_patterns:
                return None

            pattern = {
                "coin": coin,
                "side": side,
                "whale_count": len(wallets),
                "total_size": total_size,
                "growing_count": growing,
                "high_grade_count": a_or_b,
                "type": "stalker" if growing >= 2 else "accumulation",
            }

            self.alerted_patterns.add(pattern_key)
            return pattern

        return None

    def detect_distribution(self, coin: str) -> Optional[dict]:
        """Detect distribution: whales closing positions (exiting before crash)."""
        history = self.scan_history.get(coin, [])
        if len(history) < 2:
            return None

        prev = history[-2]["wallets"]
        latest = history[-1]["wallets"]

        # Count wallets that disappeared (closed positions)
        closed = []
        for addr, wp in prev.items():
            if addr not in latest:
                closed.append({"address": addr, "side": wp["side"], "size": wp["size"]})

        if len(closed) >= 2:
            total_exited = sum(c["size"] for c in closed)
            sides = [c["side"] for c in closed]
            dominant_side = max(set(sides), key=sides.count)

            pattern_key = f"{coin}_exit_{len(closed)}"
            if pattern_key in self.alerted_patterns:
                return None
            self.alerted_patterns.add(pattern_key)

            return {
                "coin": coin,
                "type": "distribution",
                "exited_count": len(closed),
                "total_exited_usd": total_exited,
                "dominant_side": dominant_side,
            }
        return None


# ===== WHALE DISCOVERY =====

async def discover_whales(coins: list = None, min_position: float = None) -> list:
    """Scan recent trades on target coins to discover whale wallets."""
    coins = coins or WATCH_COINS
    min_pos = min_position or WHALE_MIN_POSITION_USD
    print(f"[DISCOVER] Scanning {len(coins)} coins for whales (min ${min_pos:,.0f})...")

    async with aiohttp.ClientSession() as session:
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
            await asyncio.sleep(0.1)

        print(f"  Found {len(addresses)} unique addresses, checking positions...")

        whales = []
        checked = 0
        for addr in list(addresses)[:50]:
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
                    # Score the wallet for quality filtering
                    fills = await get_wallet_fills(session, addr)
                    score = compute_wallet_score(fills, state)
                    whales.append({
                        "address": addr,
                        "account_value": round(acct_val, 2),
                        "positions": positions,
                        "total_notional": sum(p["size_usd"] for p in positions),
                        "grade": score.get("grade", "?"),
                        "score": score,
                    })

                checked += 1
                if checked % 10 == 0:
                    print(f"  Checked {checked}/{min(len(addresses), 50)} addresses...")

            except Exception:
                pass
            await asyncio.sleep(0.05)

        whales.sort(key=lambda w: w["total_notional"], reverse=True)
        print(f"  Found {len(whales)} whales with {sum(len(w['positions']) for w in whales)} positions")
        return whales


# ===== SMART WALLET MONITORING =====

class WalletMonitor:
    """
    Monitors saved wallets with smart alert filtering.
    Senpi insight: only high-grade wallets generate actionable signals.
    """

    def __init__(self, regime: MarketRegime, patterns: PatternDetector):
        self.snapshots: dict[str, dict] = {}
        self.wallet_grades: dict[str, str] = {}  # addr -> grade
        self.saved_wallets: list[dict] = []
        self.regime = regime
        self.patterns = patterns

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
        """Scan all saved wallets with smart filtering."""
        if not self.saved_wallets:
            self.load_saved_wallets()
            if not self.saved_wallets:
                print("[MONITOR] No saved wallets to monitor")
                return

        print(f"[MONITOR] Scanning {len(self.saved_wallets)} wallets (regime: {self.regime.current_regime})...")

        # Collect positions per coin for pattern detection
        coin_positions = defaultdict(list)

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

                    # Get or refresh wallet grade
                    if addr not in self.wallet_grades:
                        fills = await get_wallet_fills(session, addr)
                        score = compute_wallet_score(fills, state)
                        self.wallet_grades[addr] = score.get("grade", "?")

                    grade = self.wallet_grades[addr]

                    # Detect changes (only alert for quality wallets)
                    if old_positions:
                        self._detect_changes(addr, label, grade, old_positions, new_positions, state)

                    # Record for pattern detection
                    for coin, pos in new_positions.items():
                        coin_positions[coin].append({
                            "address": addr,
                            "side": pos["side"],
                            "size_usd": pos["size_usd"],
                            "grade": grade,
                        })

                    self.snapshots[addr] = new_positions
                except Exception as e:
                    print(f"  Warning: failed to scan {label}: {e}")

                await asyncio.sleep(0.05)

        # Run pattern detection on aggregated positions
        for coin, positions in coin_positions.items():
            self.patterns.record_scan(coin, positions)

            # Check for accumulation
            acc = self.patterns.detect_accumulation(coin)
            if acc:
                conviction = self.regime.get_signal_conviction(coin, acc["side"])
                emoji = "🟢" if acc["side"] == "LONG" else "🔴"
                mode = "STALKER" if acc["type"] == "stalker" else "ACCUMULATION"
                firebase_push_alert(
                    f"{emoji} {mode}: {acc['whale_count']} whales {acc['side']} {coin}",
                    f"${acc['total_size']:,.0f} total. "
                    f"{acc['growing_count']} growing positions. "
                    f"{acc['high_grade_count']} A/B-grade wallets. "
                    f"Regime: {self.regime.current_regime}. Conviction: {conviction}.",
                    severity="opportunity",
                    tags=["pattern", mode.lower(), coin.lower(), conviction],
                )

            # Check for distribution
            dist = self.patterns.detect_distribution(coin)
            if dist:
                firebase_push_alert(
                    f"DISTRIBUTION: {dist['exited_count']} whales exited {coin}",
                    f"${dist['total_exited_usd']:,.0f} in {dist['dominant_side']} positions closed. "
                    f"Smart money leaving — potential reversal ahead.",
                    severity="warning",
                    tags=["pattern", "distribution", coin.lower()],
                )

    def _parse_positions(self, state: dict) -> dict:
        """Parse positions from clearinghouse state."""
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

    def _detect_changes(self, addr: str, label: str, grade: str, old: dict, new: dict, state: dict):
        """Compare positions and generate smart alerts (filtered by grade + regime)."""
        mg = state.get("marginSummary", {})
        acct_val = float(mg.get("accountValue", 0))

        # Skip alerts for low-quality wallets
        if not grade_passes(grade, ALERT_MIN_WHALE_GRADE):
            return

        # New positions opened
        for coin, pos in new.items():
            if coin not in old and pos["size_usd"] >= ALERT_NEW_POSITION_USD:
                conviction = self.regime.get_signal_conviction(coin, pos["side"])
                regime_tag = self.regime.current_regime
                firebase_push_alert(
                    f"[{grade}] {label} opened {pos['side']} {coin}",
                    f"${pos['size_usd']:,.0f} at {pos['leverage']:.0f}x. Entry ${pos['entry_px']:,.2f}. "
                    f"Account: ${acct_val:,.0f}. Regime: {regime_tag}. Signal: {conviction}.",
                    severity="opportunity" if conviction in ("high", "medium") else "info",
                    tags=["whale-open", coin.lower(), conviction, f"grade-{grade.lower()}"],
                )

        # Positions closed
        for coin, pos in old.items():
            if coin not in new and pos["size_usd"] >= ALERT_POSITION_CLOSE_USD:
                firebase_push_alert(
                    f"[{grade}] {label} closed {pos['side']} {coin}",
                    f"Was ${pos['size_usd']:,.0f} at {pos['leverage']:.0f}x. Account: ${acct_val:,.0f}.",
                    severity="info",
                    tags=["whale-close", coin.lower(), f"grade-{grade.lower()}"],
                )

        # PnL swings
        for coin in set(old.keys()) & set(new.keys()):
            old_pnl = old[coin]["unrealized_pnl"]
            new_pnl = new[coin]["unrealized_pnl"]
            if old_pnl != 0:
                pnl_change = ((new_pnl - old_pnl) / abs(old_pnl)) * 100
                if abs(pnl_change) >= ALERT_PNL_CHANGE_PCT and abs(new_pnl - old_pnl) > 10_000:
                    direction = "up" if pnl_change > 0 else "down"
                    firebase_push_alert(
                        f"[{grade}] {label}: {coin} PnL {direction} {abs(pnl_change):.0f}%",
                        f"{new[coin]['side']} ${new[coin]['size_usd']:,.0f}: "
                        f"${old_pnl:,.0f} -> ${new_pnl:,.0f}",
                        severity="warning" if pnl_change < 0 else "info",
                        tags=["pnl-swing", coin.lower()],
                    )


# ===== COPY-TRADE SIGNAL GENERATOR =====

class CopyTradeSignals:
    """
    Generates copy-trade signals from A/B-grade wallets.
    Senpi: only follow wallets with proven profit factor. Gate on regime.
    """

    def __init__(self, regime: MarketRegime):
        self.regime = regime
        self.emitted_signals = set()  # avoid duplicates

    async def generate(self, session: aiohttp.ClientSession, saved_wallets: list, wallet_grades: dict):
        """Scan high-grade wallets for new positions worth copying."""
        signals = []
        for wallet in saved_wallets:
            addr = wallet.get("address", "")
            grade = wallet_grades.get(addr, "?")

            if not grade_passes(grade, COPY_MIN_GRADE):
                continue

            try:
                state = await get_wallet_state(session, addr)
                label = wallet.get("label", "") or addr[:10]

                for ap in state.get("assetPositions", []):
                    p = ap.get("position", ap)
                    sz = float(p.get("szi", 0))
                    if sz == 0:
                        continue

                    entry = float(p.get("entryPx", 0))
                    notional = abs(sz * entry)
                    lev = float(p.get("leverage", {}).get("value", 1)) if isinstance(p.get("leverage"), dict) else 1
                    coin = p.get("coin", "?")
                    side = "LONG" if sz > 0 else "SHORT"
                    upnl = float(p.get("unrealizedPnl", 0))

                    # Filter: size, leverage, and early in trade (small uPnL)
                    if notional < COPY_MIN_POSITION_USD:
                        continue
                    if lev > COPY_MAX_LEVERAGE:
                        continue

                    # Only signal if position is fresh (uPnL < 5% of notional)
                    if abs(upnl) > notional * 0.05:
                        continue

                    # Check regime alignment
                    conviction = self.regime.get_signal_conviction(coin, side)

                    sig_key = f"{addr}_{coin}_{side}"
                    if sig_key in self.emitted_signals:
                        continue

                    signals.append({
                        "wallet": label,
                        "grade": grade,
                        "coin": coin,
                        "side": side,
                        "size_usd": notional,
                        "entry_px": entry,
                        "leverage": lev,
                        "conviction": conviction,
                        "regime": self.regime.current_regime,
                    })
                    self.emitted_signals.add(sig_key)

            except Exception:
                pass
            await asyncio.sleep(0.05)

        # Fire alerts for high-conviction signals
        for sig in signals:
            if sig["conviction"] in ("high", "medium"):
                emoji = "🟢" if sig["side"] == "LONG" else "🔴"
                firebase_push_alert(
                    f"{emoji} COPY SIGNAL: {sig['side']} {sig['coin']} ({sig['grade']}-grade)",
                    f"Wallet: {sig['wallet']}. Size: ${sig['size_usd']:,.0f} at {sig['leverage']:.0f}x. "
                    f"Entry: ${sig['entry_px']:,.2f}. "
                    f"Regime: {sig['regime']}. Conviction: {sig['conviction']}.",
                    severity="opportunity",
                    tags=["copy-signal", sig["coin"].lower(), sig["conviction"]],
                )

        return signals


# ===== WEBSOCKET MONITOR (Enhanced) =====

async def ws_monitor_trades(coins: list = None, regime: MarketRegime = None):
    """
    Monitor real-time trades via WebSocket for whale-size fills.
    Enhanced with regime context in alerts.
    """
    import websockets

    coins = coins or WATCH_COINS
    print(f"[WS] Connecting to Hyperliquid WebSocket for {len(coins)} coins...")

    while True:
        try:
            async with websockets.connect(HL_WS_URL) as ws:
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
                                    regime_str = regime.current_regime if regime else "unknown"
                                    conviction = regime.get_signal_conviction(coin, side) if regime else "unknown"

                                    print(f"  [WHALE TRADE] {coin} ${notional:,.0f} | {side} | regime:{regime_str} | conviction:{conviction}")

                                    firebase_push_alert(
                                        f"Whale trade: ${notional:,.0f} {coin} ({side})",
                                        f"Size: {sz}, Price: ${px:,.2f}. "
                                        f"Regime: {regime_str}. Conviction: {conviction}.",
                                        severity="opportunity" if conviction in ("high", "medium") else "info",
                                        tags=["ws-trade", coin.lower(), conviction],
                                    )
                    except Exception:
                        pass

        except Exception as e:
            print(f"[WS] Connection lost: {e}. Reconnecting in 5s...")
            await asyncio.sleep(5)


# ===== MAIN AGENT LOOP =====

async def run_agent():
    """Main agent loop: regime monitoring + wallet scanning + WebSocket + copy signals."""
    regime = MarketRegime()
    patterns = PatternDetector()
    monitor = WalletMonitor(regime, patterns)
    copy_signals = CopyTradeSignals(regime)

    async def periodic_regime():
        """Update market regime every 10 min."""
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    result = await regime.update(session)
                    print(f"[REGIME] {result['regime'].upper()} | BTC funding: {result['btc_funding']*100:.4f}% | "
                          f"OI change: {result['btc_oi_change']}%"
                          + (f" | Squeezes: {', '.join(result['squeeze_coins'])}" if result['squeeze_coins'] else ""))

                    # Save regime to Firebase for UI
                    firebase_write(f"{FIREBASE_HL_PATH}/regime", {
                        "updated": datetime.now(timezone.utc).isoformat(),
                        **result,
                        "coin_regimes": regime.coin_regimes,
                    })
            except Exception as e:
                print(f"[REGIME ERROR] {e}")
            await asyncio.sleep(REGIME_INTERVAL_SECONDS)

    async def periodic_scan():
        """Scan wallets + generate copy signals every 5 min."""
        while True:
            try:
                monitor.load_saved_wallets()
                await monitor.scan_all()

                # Generate copy-trade signals after scan
                if monitor.saved_wallets:
                    async with aiohttp.ClientSession() as session:
                        sigs = await copy_signals.generate(
                            session, monitor.saved_wallets, monitor.wallet_grades
                        )
                        if sigs:
                            print(f"[SIGNALS] Generated {len(sigs)} copy-trade signals")
            except Exception as e:
                print(f"[ERROR] Scan failed: {e}")
            print(f"[MONITOR] Next scan in {SCAN_INTERVAL_SECONDS}s...")
            await asyncio.sleep(SCAN_INTERVAL_SECONDS)

    print("=" * 60)
    print("  HYPERLIQUID SMART WHALE AGENT v2")
    print(f"  Watching: {', '.join(WATCH_COINS)}")
    print(f"  Scan interval: {SCAN_INTERVAL_SECONDS}s | Regime: {REGIME_INTERVAL_SECONDS}s")
    print(f"  Min whale position: ${WHALE_MIN_POSITION_USD:,.0f}")
    print(f"  Alert filter: grade {ALERT_MIN_WHALE_GRADE}+ | Copy: grade {COPY_MIN_GRADE}+")
    print("  Features: regime detection, pattern recognition, copy signals")
    print("=" * 60)

    # Initial regime check before starting
    try:
        async with aiohttp.ClientSession() as session:
            result = await regime.update(session)
            print(f"[REGIME] Initial: {result['regime'].upper()}")
    except Exception as e:
        print(f"[REGIME] Initial check failed: {e}")

    await asyncio.gather(
        periodic_regime(),
        periodic_scan(),
        ws_monitor_trades(WATCH_COINS, regime),
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
        print(f"  W/L Ratio:      {score.get('win_loss_ratio', '?')}x")
        print(f"  Trades:         {score.get('total_trades', 0)} ({score.get('wins', 0)}W / {score.get('losses', 0)}L)")
        print(f"  Avg Leverage:   {score.get('avg_leverage', '?')}x")
        print(f"  Coins Traded:   {score.get('coins_traded', '?')}")
        print(f"{'='*50}")

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
        top_whales = whales[:20]
        firebase_write(f"{FIREBASE_HL_PATH}/discovered_whales", {
            "updated": datetime.now(timezone.utc).isoformat(),
            "count": len(whales),
            "whales": {w["address"][:12]: w for w in top_whales},
        })
        print(f"\nSaved {len(top_whales)} whales to Firebase")

        print(f"\n{'='*80}")
        print(f"  TOP WHALES ({len(whales)} found)")
        print(f"{'='*80}")
        for w in whales[:10]:
            addr = w["address"][:10] + "..."
            grade = w.get("grade", "?")
            print(f"  [{grade}] {addr}  ${w['account_value']:>12,.0f}  {len(w['positions'])} pos  ${w['total_notional']:>14,.0f} total")
            for p in w["positions"][:3]:
                print(f"       {p['coin']:>6} {p['side']:>5} ${p['size_usd']:>12,.0f}  PnL ${p['unrealized_pnl']:>10,.0f}  {p['leverage']:.0f}x")
    return whales


async def cmd_regime():
    """One-shot: check current market regime."""
    regime = MarketRegime()
    async with aiohttp.ClientSession() as session:
        result = await regime.update(session)

    print(f"\n{'='*60}")
    print(f"  MARKET REGIME: {result['regime'].upper()}")
    print(f"{'='*60}")
    print(f"  BTC Funding (8h):  {result['btc_funding']*100:.4f}%")
    print(f"  BTC OI Change:     {result['btc_oi_change']}%")
    if result['squeeze_coins']:
        print(f"  Squeeze Setups:    {', '.join(result['squeeze_coins'])}")
    print()

    for coin in WATCH_COINS:
        cr = regime.coin_regimes.get(coin, {})
        if not cr:
            continue
        funding = cr['funding'] * 100
        squeeze = cr.get('squeeze', '')
        oi_usd = cr.get('oi_usd', 0)
        squeeze_tag = f" *** {squeeze.upper()} ***" if squeeze else ""
        print(f"  {coin:>6}  funding: {funding:>8.4f}%  OI: ${oi_usd:>12,.0f}  OI chg: {cr['oi_change_pct']:>6.1f}%{squeeze_tag}")

    print()
    return result


async def cmd_signals():
    """One-shot: generate copy-trade signals from saved wallets."""
    regime = MarketRegime()
    async with aiohttp.ClientSession() as session:
        await regime.update(session)

    print(f"\n[REGIME] {regime.current_regime.upper()}")
    print("[SIGNALS] Scanning saved wallets for copy-trade signals...\n")

    # Load saved wallets
    data = firebase_read(f"{FIREBASE_HL_PATH}/saved_wallets")
    wallets = list(data.values()) if data and isinstance(data, dict) else []
    if not wallets:
        print("  No saved wallets found")
        return []

    # Grade each wallet and scan for signals
    copy = CopyTradeSignals(regime)
    wallet_grades = {}

    async with aiohttp.ClientSession() as session:
        for w in wallets:
            addr = w.get("address", "")
            if not addr:
                continue
            try:
                state = await get_wallet_state(session, addr)
                fills = await get_wallet_fills(session, addr)
                score = compute_wallet_score(fills, state)
                wallet_grades[addr] = score.get("grade", "?")
            except Exception:
                wallet_grades[addr] = "?"
            await asyncio.sleep(0.05)

        signals = await copy.generate(session, wallets, wallet_grades)

    if signals:
        print(f"  {'='*70}")
        print(f"  COPY-TRADE SIGNALS ({len(signals)})")
        print(f"  {'='*70}")
        for s in signals:
            emoji = "🟢" if s["side"] == "LONG" else "🔴"
            print(f"  {emoji} {s['coin']:>6} {s['side']:>5} | ${s['size_usd']:>10,.0f} | {s['leverage']:.0f}x | "
                  f"entry ${s['entry_px']:,.2f} | [{s['grade']}] {s['wallet']} | conviction: {s['conviction']}")
    else:
        print("  No signals found (filters: grade B+, fresh positions, regime-aligned)")

    return signals


async def cmd_scan():
    """One-shot scan of saved wallets."""
    regime = MarketRegime()
    patterns = PatternDetector()
    async with aiohttp.ClientSession() as session:
        await regime.update(session)
    monitor = WalletMonitor(regime, patterns)
    monitor.load_saved_wallets()
    await monitor.scan_all()
    print("[SCAN] Complete")


def main():
    if len(sys.argv) < 2:
        asyncio.run(run_agent())
    elif sys.argv[1] == "scan":
        asyncio.run(cmd_scan())
    elif sys.argv[1] == "discover":
        asyncio.run(cmd_discover())
    elif sys.argv[1] == "profile" and len(sys.argv) > 2:
        asyncio.run(cmd_profile(sys.argv[2]))
    elif sys.argv[1] == "regime":
        asyncio.run(cmd_regime())
    elif sys.argv[1] == "signals":
        asyncio.run(cmd_signals())
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
