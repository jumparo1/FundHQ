"""
Phase 4: Learning & Edge
=========================
Trade feedback loops, score calibration based on outcomes,
backtesting integration for strategy validation.
"""

import math
from datetime import datetime, timezone, timedelta
from typing import Optional
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.firebase import fb_write, fb_read, fb_patch, push_alert, now_iso


# ===== TRADE FEEDBACK LOOP =====

class TradeFeedback:
    """
    Tracks trade outcomes and builds a feedback loop:
    - Records predictions (signal score, conviction, direction)
    - Compares to actual outcomes
    - Identifies what's working and what's not
    - Adjusts scoring weights over time
    """

    def __init__(self):
        self.history = []

    def load_trades(self) -> list:
        """Load trade history from Firebase."""
        try:
            data = fb_read("/fundHQ/trades") or {}
            if isinstance(data, dict):
                self.history = list(data.values()) if data else []
            elif isinstance(data, list):
                self.history = [t for t in data if t]
            return self.history
        except:
            return []

    def analyze_performance(self) -> dict:
        """Analyze overall trading performance."""
        trades = self.load_trades()
        if not trades:
            return {"error": "no_trades", "message": "No trade history found"}

        closed = [t for t in trades if t.get("status") == "closed" and t.get("pnl") is not None]
        if not closed:
            return {"total_trades": len(trades), "closed": 0, "message": "No closed trades yet"}

        wins = [t for t in closed if (t.get("pnl", 0) or 0) > 0]
        losses = [t for t in closed if (t.get("pnl", 0) or 0) <= 0]

        total_pnl = sum(t.get("pnl", 0) or 0 for t in closed)
        avg_win = sum(t.get("pnl", 0) or 0 for t in wins) / len(wins) if wins else 0
        avg_loss = sum(abs(t.get("pnl", 0) or 0) for t in losses) / len(losses) if losses else 0
        profit_factor = (sum(t.get("pnl", 0) or 0 for t in wins) /
                        sum(abs(t.get("pnl", 0) or 0) for t in losses)) if losses else float('inf')

        # Win rate by conviction
        by_conviction = {}
        for t in closed:
            conv = t.get("conviction", "medium")
            if conv not in by_conviction:
                by_conviction[conv] = {"wins": 0, "losses": 0, "pnl": 0}
            if (t.get("pnl", 0) or 0) > 0:
                by_conviction[conv]["wins"] += 1
            else:
                by_conviction[conv]["losses"] += 1
            by_conviction[conv]["pnl"] += t.get("pnl", 0) or 0

        # Win rate by source/agent
        by_source = {}
        for t in closed:
            source = t.get("source", t.get("agent", "manual"))
            if source not in by_source:
                by_source[source] = {"wins": 0, "losses": 0, "pnl": 0}
            if (t.get("pnl", 0) or 0) > 0:
                by_source[source]["wins"] += 1
            else:
                by_source[source]["losses"] += 1
            by_source[source]["pnl"] += t.get("pnl", 0) or 0

        # R-multiple distribution
        r_multiples = []
        for t in closed:
            risk = t.get("risk_amount", 0) or t.get("stop_distance_pct", 0)
            if risk and risk > 0:
                r = (t.get("pnl", 0) or 0) / risk
                r_multiples.append(round(r, 2))

        # Streak analysis
        streak = 0
        max_win_streak = 0
        max_loss_streak = 0
        current_streak_type = None
        for t in sorted(closed, key=lambda x: x.get("closeDate", x.get("created", ""))):
            won = (t.get("pnl", 0) or 0) > 0
            if current_streak_type == won:
                streak += 1
            else:
                streak = 1
                current_streak_type = won
            if won:
                max_win_streak = max(max_win_streak, streak)
            else:
                max_loss_streak = max(max_loss_streak, streak)

        result = {
            "total_trades": len(trades),
            "closed_trades": len(closed),
            "open_trades": len(trades) - len(closed),
            "win_rate": round(len(wins) / len(closed) * 100, 1),
            "total_pnl": round(total_pnl, 2),
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2),
            "profit_factor": round(profit_factor, 2) if profit_factor != float('inf') else "N/A",
            "expectancy": round((len(wins)/len(closed) * avg_win) - (len(losses)/len(closed) * avg_loss), 2),
            "best_trade": round(max(t.get("pnl", 0) or 0 for t in closed), 2),
            "worst_trade": round(min(t.get("pnl", 0) or 0 for t in closed), 2),
            "max_win_streak": max_win_streak,
            "max_loss_streak": max_loss_streak,
            "by_conviction": by_conviction,
            "by_source": by_source,
            "r_multiples": r_multiples[:50],
            "avg_r": round(sum(r_multiples) / len(r_multiples), 2) if r_multiples else None,
            "updated": now_iso(),
        }

        # Push to Firebase
        try:
            fb_write("/fundHQ/performance", result)
        except:
            pass

        return result

    def analyze_by_setup(self) -> dict:
        """Analyze win rate by setup type (MR Long, Spike Reversal, etc.)."""
        trades = self.load_trades()
        closed = [t for t in trades if t.get("status") == "closed" and t.get("pnl") is not None]

        by_setup = {}
        for t in closed:
            setup = t.get("setup", t.get("playbook", "unknown"))
            if setup not in by_setup:
                by_setup[setup] = {"wins": 0, "losses": 0, "total_pnl": 0, "trades": 0}
            by_setup[setup]["trades"] += 1
            if (t.get("pnl", 0) or 0) > 0:
                by_setup[setup]["wins"] += 1
            else:
                by_setup[setup]["losses"] += 1
            by_setup[setup]["total_pnl"] += t.get("pnl", 0) or 0

        # Add win rate
        for setup in by_setup:
            total = by_setup[setup]["trades"]
            by_setup[setup]["win_rate"] = round(by_setup[setup]["wins"] / total * 100, 1) if total else 0
            by_setup[setup]["avg_pnl"] = round(by_setup[setup]["total_pnl"] / total, 2) if total else 0

        return by_setup


# ===== SCORE CALIBRATION =====

class ScoreCalibrator:
    """
    Calibrates multi-factor scores based on actual trade outcomes.
    Tracks which factors are predictive and adjusts weights.
    """

    DEFAULT_WEIGHTS = {
        "fundamental": 0.25,
        "technical": 0.20,
        "onchain": 0.20,
        "sentiment": 0.15,
        "valuation": 0.20,
    }

    def __init__(self):
        self.calibrated_weights = dict(self.DEFAULT_WEIGHTS)

    def load_calibration(self) -> dict:
        """Load calibration data from Firebase."""
        try:
            data = fb_read("/fundHQ/calibration")
            if data and "weights" in data:
                self.calibrated_weights = data["weights"]
            return data or {}
        except:
            return {}

    def calibrate(self, scored_trades: list) -> dict:
        """
        Calibrate weights based on which factors predicted winners.
        scored_trades: [{factors: {fundamental: 4, technical: 3, ...}, pnl: 500}, ...]
        """
        if len(scored_trades) < 10:
            return {"status": "insufficient_data", "min_required": 10, "current": len(scored_trades)}

        # Split into winners and losers
        winners = [t for t in scored_trades if t.get("pnl", 0) > 0]
        losers = [t for t in scored_trades if t.get("pnl", 0) <= 0]

        if not winners or not losers:
            return {"status": "need_both_winners_and_losers"}

        # Calculate average factor score for winners vs losers
        factor_effectiveness = {}
        for factor in self.DEFAULT_WEIGHTS:
            avg_winner = sum(t.get("factors", {}).get(factor, 3) for t in winners) / len(winners)
            avg_loser = sum(t.get("factors", {}).get(factor, 3) for t in losers) / len(losers)
            spread = avg_winner - avg_loser  # Positive = factor differentiates winners

            factor_effectiveness[factor] = {
                "avg_winner_score": round(avg_winner, 2),
                "avg_loser_score": round(avg_loser, 2),
                "spread": round(spread, 3),
                "predictive": spread > 0.3,
            }

        # Adjust weights based on effectiveness
        total_spread = sum(max(0.1, fe["spread"]) for fe in factor_effectiveness.values())
        new_weights = {}
        for factor, fe in factor_effectiveness.items():
            raw = max(0.1, fe["spread"]) / total_spread
            # Blend with default (80% data, 20% prior)
            new_weights[factor] = round(raw * 0.8 + self.DEFAULT_WEIGHTS[factor] * 0.2, 3)

        # Normalize to sum to 1.0
        total = sum(new_weights.values())
        new_weights = {k: round(v / total, 3) for k, v in new_weights.items()}

        self.calibrated_weights = new_weights

        result = {
            "status": "calibrated",
            "trades_analyzed": len(scored_trades),
            "winners": len(winners),
            "losers": len(losers),
            "factor_effectiveness": factor_effectiveness,
            "old_weights": self.DEFAULT_WEIGHTS,
            "new_weights": new_weights,
            "weight_changes": {k: round(new_weights[k] - self.DEFAULT_WEIGHTS[k], 3)
                              for k in self.DEFAULT_WEIGHTS},
            "calibrated_at": now_iso(),
        }

        # Save to Firebase
        try:
            fb_write("/fundHQ/calibration", result)
        except:
            pass

        return result


# ===== BACKTESTING BRIDGE =====

class BacktestBridge:
    """
    Connects to the Backtesting engine for strategy validation.
    The Backtesting repo runs separately — this bridge sends requests
    and collects results.
    """

    STRATEGIES = {
        "mr-long": {
            "name": "MR Long (Journal Edge)",
            "description": "EMA 21 pullback + RSI < 40 + hammer + green close + BB touch",
            "timeframe": "1d",
            "side": "LONG",
        },
        "spike-reversal": {
            "name": "Spike Exhaustion Reversal",
            "description": "Fade parabolic moves with scored confirmation",
            "timeframe": "1d",
            "side": "LONG",
        },
        "crt-cisd": {
            "name": "CRT + CISD",
            "description": "Candle range theory, liquidity sweep pattern",
            "timeframe": "1d",
            "side": "BOTH",
        },
        "momentum-short": {
            "name": "Momentum Short",
            "description": "Short overextended moves after exhaustion signals",
            "timeframe": "4h",
            "side": "SHORT",
        },
    }

    async def run_backtest(self, symbol: str, strategy: str, days: int = 365) -> dict:
        """
        Run a backtest via the Backtesting engine.
        Falls back to simple simulation if engine isn't running.
        """
        if strategy not in self.STRATEGIES:
            return {"error": f"Unknown strategy: {strategy}", "available": list(self.STRATEGIES.keys())}

        import aiohttp
        # Try local backtesting engine first
        try:
            async with aiohttp.ClientSession() as session:
                url = f"http://localhost:8877/api/backtest"
                payload = {"symbol": symbol, "strategy": strategy, "days": days}
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status == 200:
                        return await resp.json()
        except:
            pass

        # Fallback: simple historical simulation using CoinGecko data
        return await self._simple_backtest(symbol, strategy, days)

    async def _simple_backtest(self, symbol: str, strategy: str, days: int) -> dict:
        """Simple backtest using price data + basic strategy rules."""
        import aiohttp
        from services.risk_engine import VaRCalculator

        var_calc = VaRCalculator()
        COIN_MAP = {
            "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana",
            "AVAX": "avalanche-2", "LINK": "chainlink",
        }
        coin_id = COIN_MAP.get(symbol.upper(), symbol.lower())

        async with aiohttp.ClientSession() as session:
            prices = await var_calc.fetch_historical_prices(session, coin_id, days)

        if len(prices) < 30:
            return {"error": "insufficient_price_data", "prices": len(prices)}

        # Simple MR strategy simulation
        strat = self.STRATEGIES[strategy]
        trades = []
        position = None

        for i in range(21, len(prices)):
            price = prices[i]
            sma_21 = sum(prices[i-21:i]) / 21
            recent_high = max(prices[i-5:i])
            recent_low = min(prices[i-5:i])

            if strategy == "mr-long":
                # Buy when price touches lower band (below 95% of SMA)
                if not position and price < sma_21 * 0.95:
                    position = {"entry": price, "entry_idx": i}
                # Sell at SMA or +5%
                elif position and (price >= sma_21 or price >= position["entry"] * 1.05):
                    pnl_pct = (price / position["entry"] - 1) * 100
                    trades.append({"pnl_pct": round(pnl_pct, 2), "bars": i - position["entry_idx"]})
                    position = None
                # Stop loss at -3%
                elif position and price <= position["entry"] * 0.97:
                    pnl_pct = (price / position["entry"] - 1) * 100
                    trades.append({"pnl_pct": round(pnl_pct, 2), "bars": i - position["entry_idx"]})
                    position = None

            elif strategy == "spike-reversal":
                # Buy when price drops 10%+ from recent high
                if not position and price < recent_high * 0.90:
                    position = {"entry": price, "entry_idx": i}
                elif position and (price >= position["entry"] * 1.08 or price <= position["entry"] * 0.95):
                    pnl_pct = (price / position["entry"] - 1) * 100
                    trades.append({"pnl_pct": round(pnl_pct, 2), "bars": i - position["entry_idx"]})
                    position = None

            elif strategy == "momentum-short":
                # Short when price is 15%+ above SMA
                if not position and price > sma_21 * 1.15:
                    position = {"entry": price, "entry_idx": i, "side": "SHORT"}
                elif position and (price <= sma_21 or price >= position["entry"] * 1.05):
                    pnl_pct = (position["entry"] / price - 1) * 100
                    trades.append({"pnl_pct": round(pnl_pct, 2), "bars": i - position["entry_idx"]})
                    position = None

        if not trades:
            return {
                "strategy": strat["name"],
                "symbol": symbol,
                "days": days,
                "trades": 0,
                "message": "No signals generated in this period",
            }

        wins = [t for t in trades if t["pnl_pct"] > 0]
        losses = [t for t in trades if t["pnl_pct"] <= 0]

        return {
            "strategy": strat["name"],
            "symbol": symbol,
            "days": days,
            "total_trades": len(trades),
            "win_rate": round(len(wins) / len(trades) * 100, 1),
            "avg_win": round(sum(t["pnl_pct"] for t in wins) / len(wins), 2) if wins else 0,
            "avg_loss": round(sum(t["pnl_pct"] for t in losses) / len(losses), 2) if losses else 0,
            "total_return": round(sum(t["pnl_pct"] for t in trades), 2),
            "profit_factor": round(
                sum(t["pnl_pct"] for t in wins) / abs(sum(t["pnl_pct"] for t in losses)), 2
            ) if losses and sum(t["pnl_pct"] for t in losses) != 0 else "N/A",
            "avg_bars_held": round(sum(t["bars"] for t in trades) / len(trades), 1),
            "best_trade": round(max(t["pnl_pct"] for t in trades), 2),
            "worst_trade": round(min(t["pnl_pct"] for t in trades), 2),
            "method": "simple_simulation",
            "note": "Basic simulation — connect Backtesting engine for full results",
            "updated": now_iso(),
        }

    def get_strategies(self) -> dict:
        return self.STRATEGIES
