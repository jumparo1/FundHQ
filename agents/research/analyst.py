#!/usr/bin/env python3
"""
Research Analyst Agent
======================
AI-powered research agent for crypto projects and market analysis.
Generates reports, tracks narratives, and surfaces alpha from research data.

Usage:
  python analyst.py --help              # Show help
  python analyst.py report BTC          # Generate research report for BTC
  python analyst.py narratives          # List active market narratives
  python analyst.py watchlist           # Show watchlist with research scores
  python analyst.py scan               # Scan for new research opportunities

Status: STUB — basic CLI structure ready, implementation pending.
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from typing import Optional

# Add parent dirs to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config import FIREBASE_DB_URL, WATCH_COINS, grade_passes
from shared.models import Signal, Alert


class ResearchAnalyst:
    """
    AI research analyst agent.
    Consumes data from multiple sources (CoinGecko, news, on-chain),
    generates structured reports, and surfaces research-based signals.
    """

    def __init__(self):
        self.watch_coins = WATCH_COINS
        self.reports = {}       # coin -> latest report
        self.narratives = []    # active market narratives

    async def generate_report(self, coin: str) -> dict:
        """Generate a research report for a coin."""
        # TODO: Implement with CoinGecko data + Claude analysis
        print(f"[ANALYST] Generating report for {coin}...")
        report = {
            "coin": coin,
            "generated": datetime.now(timezone.utc).isoformat(),
            "status": "stub",
            "sections": {
                "summary": f"Research report for {coin} — not yet implemented",
                "fundamentals": None,
                "on_chain": None,
                "sentiment": None,
                "technicals": None,
            },
            "grade": "?",
            "conviction": "none",
        }
        self.reports[coin] = report
        return report

    async def scan_narratives(self) -> list:
        """Scan for active market narratives."""
        # TODO: Implement narrative detection from news/social data
        print("[ANALYST] Scanning for market narratives...")
        self.narratives = [
            {"name": "AI tokens", "coins": ["FET", "RENDER", "TAO"], "strength": "strong", "status": "stub"},
            {"name": "L2 season", "coins": ["ARB", "OP", "BASE"], "strength": "medium", "status": "stub"},
            {"name": "RWA", "coins": ["ONDO", "MKR"], "strength": "emerging", "status": "stub"},
        ]
        return self.narratives

    async def get_watchlist(self) -> list:
        """Get watchlist with research scores."""
        # TODO: Pull from Firebase and score each entry
        print("[ANALYST] Loading watchlist...")
        return [{"coin": c, "score": "?", "last_report": None} for c in self.watch_coins]

    async def scan(self) -> list:
        """Scan for new research opportunities."""
        # TODO: Identify coins with unusual activity that need deeper research
        print("[ANALYST] Scanning for research opportunities...")
        return []

    def to_signal(self, coin: str, side: str, conviction: str) -> Signal:
        """Convert a research insight into a Signal."""
        return Signal(
            coin=coin,
            side=side,
            source="research:analyst",
            conviction=conviction,
            regime="unknown",
        )


# ===== CLI =====

def main():
    parser = argparse.ArgumentParser(
        description="Research Analyst Agent — AI-powered crypto research",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python analyst.py report BTC          # Generate research report
  python analyst.py narratives          # List active narratives
  python analyst.py watchlist           # Show watchlist
  python analyst.py scan               # Scan for opportunities
        """,
    )
    parser.add_argument("command", nargs="?", default="help",
                        choices=["report", "narratives", "watchlist", "scan", "help"],
                        help="Command to execute")
    parser.add_argument("coin", nargs="?", help="Coin symbol (for report command)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    analyst = ResearchAnalyst()

    if args.command == "report":
        if not args.coin:
            print("Error: report requires a coin symbol (e.g. python analyst.py report BTC)")
            sys.exit(1)
        result = asyncio.run(analyst.generate_report(args.coin.upper()))
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n{'='*50}")
            print(f"  RESEARCH REPORT: {result['coin']}")
            print(f"{'='*50}")
            print(f"  Status: {result['status']}")
            print(f"  Grade:  {result['grade']}")
            print(f"  {result['sections']['summary']}")
            print()

    elif args.command == "narratives":
        narratives = asyncio.run(analyst.scan_narratives())
        if args.json:
            print(json.dumps(narratives, indent=2))
        else:
            print(f"\n{'='*50}")
            print(f"  ACTIVE NARRATIVES ({len(narratives)})")
            print(f"{'='*50}")
            for n in narratives:
                coins = ", ".join(n["coins"])
                print(f"  {n['name']:.<25} {n['strength']:<10} [{coins}]")
            print(f"\n  (stub data — implementation pending)")
            print()

    elif args.command == "watchlist":
        wl = asyncio.run(analyst.get_watchlist())
        if args.json:
            print(json.dumps(wl, indent=2))
        else:
            print(f"\n{'='*50}")
            print(f"  WATCHLIST ({len(wl)} coins)")
            print(f"{'='*50}")
            for item in wl:
                print(f"  {item['coin']:>6}  score: {item['score']}")
            print()

    elif args.command == "scan":
        results = asyncio.run(analyst.scan())
        print(f"  Found {len(results)} opportunities (stub)")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
