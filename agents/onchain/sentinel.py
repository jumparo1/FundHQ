#!/usr/bin/env python3
"""
On-Chain Sentinel Agent
========================
Multi-venue on-chain intelligence agent. Wraps venue-specific agents
(starting with Hyperliquid) and provides a unified interface for
whale tracking, copy signals, and pattern detection.

Usage:
  python sentinel.py                    # Run full sentinel (all venues)
  python sentinel.py regime             # Check market regime
  python sentinel.py scan               # Scan saved wallets (all venues)
  python sentinel.py discover           # Discover whales
  python sentinel.py profile <address>  # Profile a wallet
  python sentinel.py signals            # Generate copy-trade signals
  python sentinel.py --help             # Show help

Supported venues: hyperliquid (more coming)
"""

import asyncio
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from typing import Optional

import aiohttp
import requests

# Add parent dirs to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config import (
    FIREBASE_DB_URL, FIREBASE_ALERTS_PATH, WATCH_COINS,
    GRADE_RANK, grade_passes,
)
from shared.models import Signal, Alert, Entity
from onchain.regime_monitor import MarketRegimeMonitor

# ===== VENUE: HYPERLIQUID =====
# Import the existing HL agent's core functions by adding its path
HL_AGENT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hyperliquid")
sys.path.insert(0, HL_AGENT_DIR)

from config import (
    HL_API_URL, HL_WS_URL, HL_LEADERBOARD_URL,
    FIREBASE_HL_PATH,
    SCAN_INTERVAL_SECONDS, REGIME_INTERVAL_SECONDS,
    WHALE_MIN_POSITION_USD, WHALE_MIN_ACCOUNT_USD,
    PROFITABILITY_MIN_TRADES,
    ALERT_NEW_POSITION_USD, ALERT_POSITION_CLOSE_USD, ALERT_PNL_CHANGE_PCT,
    ALERT_MIN_WHALE_GRADE,
    COPY_MIN_GRADE, COPY_MIN_POSITION_USD, COPY_MAX_LEVERAGE,
    ACCUMULATION_MIN_WHALES, ACCUMULATION_LOOKBACK_SCANS,
    STALKER_MIN_SIZE_INCREASE_PCT,
)


# ===== FIREBASE (shared utility) =====

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


def push_alert(title: str, content: str, severity: str = "info",
               tags: list = None, source: str = "onchain-sentinel"):
    """Push an alert to Fund HQ's alerts page."""
    alert = Alert(
        title=title,
        content=content,
        source=source,
        severity=severity,
        tags=tags or [],
    )
    firebase_write(f"{FIREBASE_ALERTS_PATH}/{alert.id}", alert.to_dict())
    print(f"  [ALERT] {severity.upper()}: {title}")
    return alert.id


# ===== VENUE INTERFACE =====

class VenueAdapter:
    """Base class for venue-specific adapters."""
    name: str = "unknown"

    async def discover_whales(self, coins: list) -> list:
        raise NotImplementedError

    async def scan_wallets(self, wallets: list) -> list:
        raise NotImplementedError

    async def get_wallet_profile(self, address: str) -> dict:
        raise NotImplementedError


class HyperliquidAdapter(VenueAdapter):
    """Adapter wrapping the existing Hyperliquid agent functionality."""
    name = "hyperliquid"

    def __init__(self):
        # Lazy import from HL agent to avoid circular deps
        self._agent_imported = False

    def _ensure_imports(self):
        if not self._agent_imported:
            # Import functions from the existing HL agent
            import agent as hl_agent
            self._hl = hl_agent
            self._agent_imported = True

    async def discover_whales(self, coins: list = None) -> list:
        self._ensure_imports()
        return await self._hl.discover_whales(coins)

    async def get_wallet_profile(self, address: str) -> dict:
        self._ensure_imports()
        return await self._hl.cmd_profile(address)

    async def scan_wallets(self, wallets: list = None) -> None:
        self._ensure_imports()
        await self._hl.cmd_scan()


# ===== ON-CHAIN SENTINEL =====

class OnChainSentinel:
    """
    Multi-venue on-chain intelligence agent.
    Currently wraps Hyperliquid; designed to add more venues
    (GMX, dYdX, on-chain whale wallets, etc.).
    """

    def __init__(self):
        self.regime = MarketRegimeMonitor()
        self.venues = {
            "hyperliquid": HyperliquidAdapter(),
        }

    async def check_regime(self) -> dict:
        """Check current market regime."""
        async with aiohttp.ClientSession() as session:
            result = await self.regime.update(session)
        return result

    async def discover(self, venue: str = None, coins: list = None) -> list:
        """Discover whales across venues."""
        coins = coins or WATCH_COINS
        all_whales = []

        targets = [venue] if venue else list(self.venues.keys())
        for v_name in targets:
            adapter = self.venues.get(v_name)
            if not adapter:
                print(f"[SENTINEL] Unknown venue: {v_name}")
                continue
            print(f"[SENTINEL] Discovering on {v_name}...")
            whales = await adapter.discover_whales(coins)
            for w in whales:
                w["venue"] = v_name
            all_whales.extend(whales)

        all_whales.sort(key=lambda w: w.get("total_notional", 0), reverse=True)
        return all_whales

    async def profile(self, address: str, venue: str = "hyperliquid") -> dict:
        """Profile a wallet on a specific venue."""
        adapter = self.venues.get(venue)
        if not adapter:
            print(f"[SENTINEL] Unknown venue: {venue}")
            return {}
        return await adapter.get_wallet_profile(address)

    async def scan(self, venue: str = None) -> None:
        """Scan saved wallets across venues."""
        targets = [venue] if venue else list(self.venues.keys())
        for v_name in targets:
            adapter = self.venues.get(v_name)
            if not adapter:
                continue
            print(f"[SENTINEL] Scanning {v_name}...")
            await adapter.scan_wallets()

    async def run(self):
        """Main sentinel loop — regime monitoring + wallet scanning across all venues."""
        print("=" * 60)
        print("  ON-CHAIN SENTINEL")
        print(f"  Venues: {', '.join(self.venues.keys())}")
        print(f"  Watching: {', '.join(WATCH_COINS)}")
        print("=" * 60)

        # Initial regime check
        try:
            result = await self.check_regime()
            print(f"[REGIME] Initial: {result['regime'].upper()}")
        except Exception as e:
            print(f"[REGIME] Initial check failed: {e}")

        async def periodic_regime():
            while True:
                try:
                    async with aiohttp.ClientSession() as session:
                        result = await self.regime.update(session)
                        print(f"[REGIME] {result['regime'].upper()} | "
                              f"BTC funding: {result['btc_funding']*100:.4f}% | "
                              f"OI change: {result['btc_oi_change']}%")
                        firebase_write(f"{FIREBASE_HL_PATH}/regime", {
                            "updated": datetime.now(timezone.utc).isoformat(),
                            **result,
                            "coin_regimes": self.regime.coin_regimes,
                        })
                except Exception as e:
                    print(f"[REGIME ERROR] {e}")
                await asyncio.sleep(REGIME_INTERVAL_SECONDS)

        async def periodic_scan():
            while True:
                try:
                    await self.scan()
                except Exception as e:
                    print(f"[SCAN ERROR] {e}")
                print(f"[SENTINEL] Next scan in {SCAN_INTERVAL_SECONDS}s...")
                await asyncio.sleep(SCAN_INTERVAL_SECONDS)

        await asyncio.gather(periodic_regime(), periodic_scan())


# ===== CLI =====

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="On-Chain Sentinel — multi-venue whale intelligence",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python sentinel.py                    # Run full sentinel loop
  python sentinel.py regime             # Check market regime
  python sentinel.py scan               # Scan saved wallets
  python sentinel.py discover           # Discover whales
  python sentinel.py profile 0xabc...   # Profile a wallet
  python sentinel.py signals            # Generate copy-trade signals
        """,
    )
    parser.add_argument("command", nargs="?", default="run",
                        choices=["run", "regime", "scan", "discover", "profile", "signals"],
                        help="Command to execute (default: run)")
    parser.add_argument("address", nargs="?", help="Wallet address (for profile command)")
    parser.add_argument("--venue", type=str, default=None, help="Venue filter (default: all)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    sentinel = OnChainSentinel()

    if args.command == "regime":
        result = asyncio.run(sentinel.check_regime())
        if args.json:
            print(json.dumps({"result": result, "coins": sentinel.regime.coin_regimes}, indent=2))
        else:
            print(sentinel.regime.format_report(result))

    elif args.command == "discover":
        whales = asyncio.run(sentinel.discover(venue=args.venue))
        if args.json:
            print(json.dumps(whales[:20], indent=2, default=str))
        else:
            print(f"\nDiscovered {len(whales)} whales")
            for w in whales[:10]:
                addr = w["address"][:10] + "..."
                print(f"  [{w.get('grade','?')}] {addr}  ${w.get('total_notional',0):>12,.0f}  "
                      f"venue:{w.get('venue','?')}")

    elif args.command == "profile":
        if not args.address:
            print("Error: profile requires a wallet address")
            sys.exit(1)
        asyncio.run(sentinel.profile(args.address, venue=args.venue or "hyperliquid"))

    elif args.command == "scan":
        asyncio.run(sentinel.scan(venue=args.venue))

    elif args.command == "signals":
        # Delegate to HL agent's signal generation for now
        sys.path.insert(0, HL_AGENT_DIR)
        import agent as hl_agent
        asyncio.run(hl_agent.cmd_signals())

    else:
        asyncio.run(sentinel.run())


if __name__ == "__main__":
    main()
