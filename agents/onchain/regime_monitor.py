#!/usr/bin/env python3
"""
Market Regime Monitor
=====================
Detects macro market regime from funding rates, OI, and volume.
Extracted from the Hyperliquid agent — runs standalone or as a module.

Usage:
  python regime_monitor.py              # Check BTC regime (one-shot)
  python regime_monitor.py --watch      # Continuous monitoring (10 min interval)
  python regime_monitor.py --coin ETH   # Check specific coin details
  python regime_monitor.py --json       # Output as JSON (for piping)
"""

import asyncio
import json
import sys
import os

import aiohttp

# Add parent dirs to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config import (
    WATCH_COINS, REGIME_RISK_ON, REGIME_RISK_OFF, REGIME_NEUTRAL, REGIME_UNKNOWN,
    FIREBASE_DB_URL,
)

# ===== REGIME THRESHOLDS =====
# These are tuned for Hyperliquid perp data but the regime logic is venue-agnostic

# Funding rate thresholds (8h rate)
FUNDING_BULLISH_THRESHOLD = 0.0001     # > 0.01% = longs paying = bullish sentiment
FUNDING_BEARISH_THRESHOLD = -0.00005   # < -0.005% = shorts paying = bearish

# OI change thresholds (% change over scan interval)
OI_EXPANDING_PCT = 3.0                 # OI up 3%+ = expanding
OI_CONTRACTING_PCT = -3.0              # OI down 3%+ = contracting

# Squeeze detection
SQUEEZE_FUNDING_EXTREME = 0.0005       # Extreme positive funding
SQUEEZE_FUNDING_NEGATIVE = -0.0003     # Extreme negative funding

# Hyperliquid API (data source for regime)
HL_API_URL = "https://api.hyperliquid.xyz/info"


async def hl_post(session: aiohttp.ClientSession, body: dict) -> dict:
    """POST to Hyperliquid /info endpoint."""
    async with session.post(HL_API_URL, json=body) as resp:
        if resp.status != 200:
            raise Exception(f"HL API error {resp.status}: {await resp.text()}")
        return await resp.json()


async def get_meta(session: aiohttp.ClientSession) -> dict:
    """Get all perp metadata + asset contexts (OI, funding, volume)."""
    return await hl_post(session, {"type": "metaAndAssetCtxs"})


class MarketRegimeMonitor:
    """
    Detects macro market regime from funding rates, OI, and volume.
    Senpi insight: mean reversion fails when BTC regime is bearish.

    Can be used standalone or imported by other agents for regime-gating signals.
    """

    def __init__(self):
        self.prev_snapshot = {}      # coin -> {oi, funding, volume}
        self.current_regime = REGIME_UNKNOWN
        self.coin_regimes = {}       # coin -> regime details
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
            self.current_regime = REGIME_RISK_ON
        elif btc_funding < FUNDING_BEARISH_THRESHOLD or btc_oi_change < OI_CONTRACTING_PCT:
            self.current_regime = REGIME_RISK_OFF
        else:
            self.current_regime = REGIME_NEUTRAL

        # Per-coin analysis for squeeze detection
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
        Senpi: best agents gate signals on regime.
        """
        cr = self.coin_regimes.get(coin, {})
        regime = self.current_regime

        if regime == REGIME_RISK_ON and side == "LONG":
            return "high"
        if regime == REGIME_RISK_OFF and side == "SHORT":
            return "high"

        squeeze = cr.get("squeeze")
        if squeeze == "short_squeeze" and side == "SHORT":
            return "high"
        if squeeze == "long_squeeze" and side == "LONG":
            return "high"

        if regime == REGIME_NEUTRAL:
            return "medium"

        return "low"

    def format_report(self, result: dict, coins: list = None) -> str:
        """Format a human-readable regime report."""
        coins = coins or WATCH_COINS
        lines = []
        lines.append(f"{'='*60}")
        lines.append(f"  MARKET REGIME: {result['regime'].upper()}")
        lines.append(f"{'='*60}")
        lines.append(f"  BTC Funding (8h):  {result['btc_funding']*100:.4f}%")
        lines.append(f"  BTC OI Change:     {result['btc_oi_change']}%")
        if result['squeeze_coins']:
            lines.append(f"  Squeeze Setups:    {', '.join(result['squeeze_coins'])}")
        lines.append("")

        for coin in coins:
            cr = self.coin_regimes.get(coin, {})
            if not cr:
                continue
            funding = cr['funding'] * 100
            squeeze = cr.get('squeeze', '')
            oi_usd = cr.get('oi_usd', 0)
            squeeze_tag = f" *** {squeeze.upper()} ***" if squeeze else ""
            lines.append(
                f"  {coin:>6}  funding: {funding:>8.4f}%  "
                f"OI: ${oi_usd:>12,.0f}  "
                f"OI chg: {cr['oi_change_pct']:>6.1f}%{squeeze_tag}"
            )

        lines.append("")
        return "\n".join(lines)


# ===== CLI =====

async def main():
    import argparse

    parser = argparse.ArgumentParser(description="Market Regime Monitor")
    parser.add_argument("--watch", action="store_true", help="Continuous monitoring (10 min interval)")
    parser.add_argument("--coin", type=str, help="Show details for a specific coin")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--interval", type=int, default=600, help="Watch interval in seconds (default: 600)")
    args = parser.parse_args()

    monitor = MarketRegimeMonitor()

    if args.watch:
        print(f"[REGIME] Watching market regime every {args.interval}s. Ctrl+C to stop.\n")
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    result = await monitor.update(session)
                if args.json:
                    print(json.dumps({"result": result, "coins": monitor.coin_regimes}, indent=2))
                else:
                    print(monitor.format_report(result))
            except Exception as e:
                print(f"[ERROR] {e}")
            await asyncio.sleep(args.interval)
    else:
        async with aiohttp.ClientSession() as session:
            result = await monitor.update(session)

        if args.json:
            output = {"result": result, "coins": monitor.coin_regimes}
            if args.coin:
                coin_data = monitor.coin_regimes.get(args.coin.upper())
                output = {"result": result, "coin": args.coin.upper(), "data": coin_data}
            print(json.dumps(output, indent=2))
        else:
            coins = [args.coin.upper()] if args.coin else WATCH_COINS
            print(monitor.format_report(result, coins))


if __name__ == "__main__":
    asyncio.run(main())
