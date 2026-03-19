"""
Phase 3: Risk Framework
========================
VaR calculations, correlation analysis, liquidity monitoring,
portfolio construction and position sizing.
"""

import math
import asyncio
import aiohttp
from datetime import datetime, timezone, timedelta
from typing import Optional
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.firebase import fb_write, fb_read, push_alert, now_iso

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


# ===== VALUE AT RISK =====

class VaRCalculator:
    """
    Portfolio Value at Risk using historical simulation.
    Uses CoinGecko historical prices for return distribution.
    """

    async def fetch_historical_prices(self, session: aiohttp.ClientSession,
                                       coin_id: str, days: int = 90) -> list:
        """Fetch daily prices from CoinGecko."""
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={days}&interval=daily"
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 429:
                    return []
                data = await resp.json()
                prices = [p[1] for p in data.get("prices", [])]
                return prices
        except:
            return []

    def calculate_returns(self, prices: list) -> list:
        """Calculate daily log returns from price series."""
        if len(prices) < 2:
            return []
        returns = []
        for i in range(1, len(prices)):
            if prices[i-1] > 0:
                r = math.log(prices[i] / prices[i-1])
                returns.append(r)
        return returns

    def historical_var(self, returns: list, confidence: float = 0.95,
                       position_value: float = 10000) -> dict:
        """Calculate VaR using historical simulation."""
        if not returns or not HAS_NUMPY:
            # Fallback: simple parametric
            if not returns:
                return {"var_1d": 0, "var_10d": 0, "method": "insufficient_data"}
            avg_return = sum(returns) / len(returns)
            variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
            std = math.sqrt(variance)
            z = 1.645 if confidence == 0.95 else 2.326
            var_1d = position_value * (avg_return - z * std)
            return {
                "var_1d": round(abs(var_1d), 2),
                "var_10d": round(abs(var_1d) * math.sqrt(10), 2),
                "method": "parametric_fallback",
                "std_daily": round(std * 100, 2),
                "confidence": confidence,
            }

        arr = np.array(returns)
        percentile = (1 - confidence) * 100
        var_pct = float(np.percentile(arr, percentile))
        var_1d = abs(var_pct * position_value)

        return {
            "var_1d": round(var_1d, 2),
            "var_10d": round(var_1d * math.sqrt(10), 2),
            "var_pct": round(var_pct * 100, 3),
            "method": "historical_simulation",
            "confidence": confidence,
            "std_daily": round(float(np.std(arr)) * 100, 2),
            "mean_daily": round(float(np.mean(arr)) * 100, 3),
            "worst_day": round(float(np.min(arr)) * 100, 2),
            "best_day": round(float(np.max(arr)) * 100, 2),
            "observations": len(returns),
        }

    async def portfolio_var(self, portfolio: list, confidence: float = 0.95) -> dict:
        """
        Calculate portfolio VaR.
        portfolio: [{"coin_id": "bitcoin", "symbol": "BTC", "value": 5000}, ...]
        """
        COIN_MAP = {
            "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana",
            "HYPE": "hyperliquid", "DOGE": "dogecoin", "SUI": "sui",
            "AVAX": "avalanche-2", "LINK": "chainlink", "PEPE": "pepe",
            "WIF": "dogwifcoin", "AAVE": "aave", "UNI": "uniswap",
            "ARB": "arbitrum", "OP": "optimism", "ONDO": "ondo-finance",
        }

        total_value = sum(p.get("value", 0) for p in portfolio)
        if total_value == 0:
            return {"var_1d": 0, "error": "empty_portfolio"}

        async with aiohttp.ClientSession() as session:
            all_returns = {}
            for pos in portfolio:
                symbol = pos.get("symbol", "")
                coin_id = pos.get("coin_id") or COIN_MAP.get(symbol, symbol.lower())
                prices = await self.fetch_historical_prices(session, coin_id)
                returns = self.calculate_returns(prices)
                if returns:
                    all_returns[symbol] = returns
                await asyncio.sleep(0.5)  # Rate limit

        # Per-position VaR
        position_vars = []
        for pos in portfolio:
            symbol = pos.get("symbol", "")
            value = pos.get("value", 0)
            returns = all_returns.get(symbol, [])
            var = self.historical_var(returns, confidence, value)
            position_vars.append({
                "symbol": symbol,
                "value": value,
                "weight": round(value / total_value * 100, 1),
                **var,
            })

        # Portfolio VaR (undiversified = sum of individual VaRs)
        undiversified_var = sum(p["var_1d"] for p in position_vars)

        # Diversified VaR (approximate with correlation discount)
        n = len(position_vars)
        diversified_var = undiversified_var * (0.7 if n >= 5 else 0.8 if n >= 3 else 0.9)

        return {
            "total_value": total_value,
            "var_1d_undiversified": round(undiversified_var, 2),
            "var_1d_diversified": round(diversified_var, 2),
            "var_10d_diversified": round(diversified_var * math.sqrt(10), 2),
            "var_pct_of_portfolio": round(diversified_var / total_value * 100, 2),
            "confidence": confidence,
            "positions": position_vars,
            "risk_level": "HIGH" if diversified_var / total_value > 0.08 else
                         "MEDIUM" if diversified_var / total_value > 0.04 else "LOW",
            "updated": now_iso(),
        }


# ===== CORRELATION ANALYSIS =====

class CorrelationAnalyzer:
    """Cross-asset correlation matrix for portfolio risk."""

    async def build_correlation_matrix(self, symbols: list, days: int = 60) -> dict:
        """Build correlation matrix from historical prices."""
        COIN_MAP = {
            "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana",
            "AVAX": "avalanche-2", "LINK": "chainlink", "DOGE": "dogecoin",
            "AAVE": "aave", "UNI": "uniswap", "ARB": "arbitrum",
            "SUI": "sui", "HYPE": "hyperliquid", "OP": "optimism",
        }

        var_calc = VaRCalculator()
        all_returns = {}

        async with aiohttp.ClientSession() as session:
            for symbol in symbols:
                coin_id = COIN_MAP.get(symbol, symbol.lower())
                prices = await var_calc.fetch_historical_prices(session, coin_id, days)
                returns = var_calc.calculate_returns(prices)
                if returns:
                    all_returns[symbol] = returns
                await asyncio.sleep(0.5)

        if not HAS_NUMPY or len(all_returns) < 2:
            return {"error": "insufficient_data", "symbols": list(all_returns.keys())}

        # Align return series (use minimum common length)
        min_len = min(len(r) for r in all_returns.values())
        aligned = {s: r[-min_len:] for s, r in all_returns.items()}
        syms = list(aligned.keys())
        matrix_data = np.array([aligned[s] for s in syms])

        # Correlation matrix
        corr = np.corrcoef(matrix_data)

        # Build readable output
        matrix = {}
        for i, s1 in enumerate(syms):
            matrix[s1] = {}
            for j, s2 in enumerate(syms):
                matrix[s1][s2] = round(float(corr[i][j]), 3)

        # Find highest/lowest correlations
        pairs = []
        for i in range(len(syms)):
            for j in range(i+1, len(syms)):
                pairs.append({
                    "pair": f"{syms[i]}/{syms[j]}",
                    "correlation": round(float(corr[i][j]), 3),
                })
        pairs.sort(key=lambda x: abs(x["correlation"]), reverse=True)

        return {
            "symbols": syms,
            "matrix": matrix,
            "highest_correlations": pairs[:5],
            "lowest_correlations": sorted(pairs, key=lambda x: abs(x["correlation"]))[:5],
            "observations": min_len,
            "days": days,
            "updated": now_iso(),
        }


# ===== LIQUIDITY SCORING =====

class LiquidityScorer:
    """Score asset liquidity for position sizing decisions."""

    def score(self, data: dict) -> dict:
        """
        Score liquidity 1-5 based on volume, spread, and depth.
        data: {volume_24h, market_cap, avg_spread_pct}
        """
        score = 3.0
        details = []

        # Volume / MCap ratio
        vol = data.get("volume_24h", 0)
        mcap = data.get("market_cap", 0)
        if mcap > 0:
            ratio = vol / mcap
            if ratio > 0.5:
                score += 1.0
                details.append(f"Excellent volume ratio: {ratio:.2f}")
            elif ratio > 0.1:
                score += 0.5
                details.append(f"Good volume ratio: {ratio:.2f}")
            elif ratio < 0.01:
                score -= 1.5
                details.append(f"Very low volume: {ratio:.3f}")
            elif ratio < 0.03:
                score -= 0.5
                details.append(f"Low volume ratio: {ratio:.3f}")

        # Absolute volume
        if vol > 1_000_000_000:
            score += 0.5
            details.append("$1B+ daily volume")
        elif vol < 1_000_000:
            score -= 1.0
            details.append(f"Under $1M daily volume")

        # Spread
        spread = data.get("avg_spread_pct", 0)
        if spread > 0:
            if spread < 0.05:
                score += 0.5
                details.append(f"Tight spread: {spread:.2f}%")
            elif spread > 0.5:
                score -= 0.5
                details.append(f"Wide spread: {spread:.1f}%")

        return {
            "score": min(5, max(1, round(score, 1))),
            "details": details,
            "max_position_pct": self._max_position(score),
        }

    def _max_position(self, liquidity_score: float) -> float:
        """Max position size as % of portfolio based on liquidity."""
        if liquidity_score >= 4.5:
            return 25.0
        elif liquidity_score >= 3.5:
            return 15.0
        elif liquidity_score >= 2.5:
            return 8.0
        elif liquidity_score >= 1.5:
            return 3.0
        return 1.0


# ===== PORTFOLIO CONSTRUCTION =====

class PortfolioOptimizer:
    """
    Portfolio construction based on risk budget, correlation,
    and conviction-weighted allocation.
    """

    def __init__(self):
        self.max_single_position = 0.25  # 25% max in one asset
        self.cash_reserve_min = 0.20     # Keep 20% cash minimum
        self.max_correlated_exposure = 0.50  # Max 50% in highly correlated group

    def construct_portfolio(self, candidates: list, total_capital: float,
                           risk_budget: float = 0.05) -> dict:
        """
        Build optimal portfolio from candidates.
        candidates: [{symbol, conviction, var_pct, liquidity_score, ...}]
        risk_budget: max acceptable daily VaR as % of capital
        """
        if not candidates:
            return {"allocations": [], "error": "no_candidates"}

        # Sort by conviction (higher = more allocation)
        sorted_candidates = sorted(candidates, key=lambda x: x.get("conviction", 0), reverse=True)

        allocatable = total_capital * (1 - self.cash_reserve_min)
        allocations = []
        remaining = allocatable

        for candidate in sorted_candidates:
            if remaining <= 0:
                break

            symbol = candidate.get("symbol", "?")
            conviction = candidate.get("conviction", 3)  # 1-5 scale
            var_pct = candidate.get("var_pct", 5)  # daily VaR %
            liquidity = candidate.get("liquidity_score", 3)

            # Base allocation: conviction-weighted
            # High conviction (5) = 15% base, Low (1) = 3% base
            base_pct = 0.03 + (conviction - 1) * 0.03
            base_allocation = allocatable * base_pct

            # Risk-adjusted: reduce if VaR is too high
            if var_pct > 8:
                base_allocation *= 0.5
            elif var_pct > 5:
                base_allocation *= 0.75

            # Liquidity-adjusted: cap based on liquidity score
            max_liq_pct = self._liquidity_cap(liquidity) / 100
            max_liq_alloc = allocatable * max_liq_pct
            allocation = min(base_allocation, max_liq_alloc)

            # Cap at max single position
            allocation = min(allocation, allocatable * self.max_single_position)
            allocation = min(allocation, remaining)

            if allocation > 0:
                allocations.append({
                    "symbol": symbol,
                    "allocation": round(allocation, 2),
                    "weight_pct": round(allocation / total_capital * 100, 1),
                    "conviction": conviction,
                    "var_contribution": round(allocation * var_pct / 100, 2),
                })
                remaining -= allocation

        # Portfolio metrics
        total_allocated = sum(a["allocation"] for a in allocations)
        total_var = sum(a["var_contribution"] for a in allocations)
        cash = total_capital - total_allocated

        return {
            "total_capital": total_capital,
            "allocated": round(total_allocated, 2),
            "cash_reserve": round(cash, 2),
            "cash_pct": round(cash / total_capital * 100, 1),
            "num_positions": len(allocations),
            "portfolio_var_1d": round(total_var, 2),
            "portfolio_var_pct": round(total_var / total_capital * 100, 2),
            "within_risk_budget": total_var / total_capital <= risk_budget,
            "allocations": allocations,
            "updated": now_iso(),
        }

    def _liquidity_cap(self, score: float) -> float:
        """Max allocation % based on liquidity score."""
        if score >= 4.5: return 25
        if score >= 3.5: return 15
        if score >= 2.5: return 8
        if score >= 1.5: return 3
        return 1

    def position_size(self, capital: float, risk_per_trade: float,
                      entry: float, stop_loss: float) -> dict:
        """Calculate position size based on risk parameters."""
        risk_amount = capital * risk_per_trade
        risk_distance = abs(entry - stop_loss)
        risk_pct = risk_distance / entry if entry > 0 else 0

        if risk_pct == 0:
            return {"error": "stop_loss_equals_entry"}

        position_size = risk_amount / risk_pct
        num_units = position_size / entry if entry > 0 else 0
        leverage = position_size / capital if capital > 0 else 0

        return {
            "capital": capital,
            "risk_per_trade": f"{risk_per_trade * 100:.1f}%",
            "risk_amount": round(risk_amount, 2),
            "entry": entry,
            "stop_loss": stop_loss,
            "risk_distance": round(risk_distance, 4),
            "risk_pct": f"{risk_pct * 100:.2f}%",
            "position_size_usd": round(position_size, 2),
            "num_units": round(num_units, 4),
            "implied_leverage": round(leverage, 2),
            "r_multiples": {
                "1R": round(risk_amount, 2),
                "2R": round(risk_amount * 2, 2),
                "3R": round(risk_amount * 3, 2),
                "5R": round(risk_amount * 5, 2),
            },
        }


# ===== RISK DASHBOARD =====

class RiskDashboard:
    """Aggregates all risk metrics into a single dashboard view."""

    def __init__(self):
        self.var_calc = VaRCalculator()
        self.corr_analyzer = CorrelationAnalyzer()
        self.liquidity_scorer = LiquidityScorer()
        self.portfolio_optimizer = PortfolioOptimizer()

    async def full_risk_assessment(self, portfolio: list) -> dict:
        """Run complete risk assessment on portfolio."""
        if not portfolio:
            return {"error": "no_portfolio"}

        # Calculate VaR
        var_result = await self.var_calc.portfolio_var(portfolio)

        # Get symbols for correlation
        symbols = [p["symbol"] for p in portfolio if p.get("symbol")]
        corr_result = await self.corr_analyzer.build_correlation_matrix(symbols[:8])

        # Concentration risk
        total_value = sum(p.get("value", 0) for p in portfolio)
        concentration = []
        for p in portfolio:
            weight = p.get("value", 0) / total_value * 100 if total_value else 0
            concentration.append({
                "symbol": p.get("symbol"),
                "weight": round(weight, 1),
                "overweight": weight > 25,
            })
        concentration.sort(key=lambda x: x["weight"], reverse=True)

        # Risk score (1-10, lower = less risky)
        risk_score = 5
        var_pct = var_result.get("var_pct_of_portfolio", 0)
        if var_pct > 10: risk_score = 9
        elif var_pct > 7: risk_score = 8
        elif var_pct > 5: risk_score = 7
        elif var_pct > 3: risk_score = 5
        elif var_pct > 1: risk_score = 3
        else: risk_score = 2

        # Adjust for concentration
        top_weight = concentration[0]["weight"] if concentration else 0
        if top_weight > 40: risk_score = min(10, risk_score + 2)
        elif top_weight > 25: risk_score = min(10, risk_score + 1)

        result = {
            "risk_score": risk_score,
            "risk_label": "LOW" if risk_score <= 3 else "MEDIUM" if risk_score <= 6 else "HIGH",
            "var": var_result,
            "correlations": corr_result if "error" not in corr_result else None,
            "concentration": concentration,
            "recommendations": self._recommendations(var_result, concentration, risk_score),
            "updated": now_iso(),
        }

        # Push to Firebase
        try:
            fb_write("/fundHQ/riskDashboard", result)
        except:
            pass

        return result

    def _recommendations(self, var: dict, concentration: list, risk_score: int) -> list:
        """Generate risk recommendations."""
        recs = []
        if risk_score >= 8:
            recs.append("REDUCE EXPOSURE: Portfolio risk is very high. Consider taking profits or hedging.")
        if concentration and concentration[0]["weight"] > 30:
            recs.append(f"DIVERSIFY: {concentration[0]['symbol']} is {concentration[0]['weight']}% — consider rebalancing.")
        var_pct = var.get("var_pct_of_portfolio", 0)
        if var_pct > 5:
            recs.append(f"DAILY VAR: {var_pct:.1f}% of portfolio at risk daily. Consider tighter stops.")
        if len(concentration) < 3:
            recs.append("LOW DIVERSIFICATION: Only {0} positions. Consider adding uncorrelated assets.".format(len(concentration)))
        if not recs:
            recs.append("Portfolio risk is within acceptable bounds.")
        return recs
