"""
Phase 2: Quantitative Models
==============================
DCF valuation, multi-factor scoring, auto-discovery engine.
Implements systematic crypto valuation and opportunity scoring.
"""

import asyncio
import aiohttp
import math
from datetime import datetime, timezone
from typing import Optional
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.firebase import fb_write, fb_read, push_alert, now_iso


# ===== DCF / VALUATION MODELS =====

class CryptoValuation:
    """
    Crypto protocol valuation using multiple methods:
    - Revenue multiple (P/S ratio vs peers)
    - TVL-based (MCap/TVL ratio)
    - DCF-lite (discounted cash flow on protocol revenue)
    - Comparative (vs sector median)
    """

    # Sector median multiples (approximate, updated periodically)
    SECTOR_MEDIANS = {
        "DEX": {"ps": 15, "mcap_tvl": 0.8, "pe": 30},
        "Lending": {"ps": 12, "mcap_tvl": 0.3, "pe": 25},
        "L1": {"ps": 50, "mcap_tvl": 5.0, "pe": 100},
        "L2": {"ps": 40, "mcap_tvl": 3.0, "pe": 80},
        "Derivatives": {"ps": 20, "mcap_tvl": 1.0, "pe": 35},
        "LST": {"ps": 25, "mcap_tvl": 0.15, "pe": 40},
        "Bridge": {"ps": 10, "mcap_tvl": 0.5, "pe": 20},
        "Other": {"ps": 20, "mcap_tvl": 1.0, "pe": 30},
    }

    def revenue_multiple_valuation(self, annual_revenue: float, sector: str = "Other",
                                    current_mcap: float = 0) -> dict:
        """Value protocol using revenue multiple (P/S ratio)."""
        medians = self.SECTOR_MEDIANS.get(sector, self.SECTOR_MEDIANS["Other"])
        fair_value_mcap = annual_revenue * medians["ps"]
        premium_discount = ((current_mcap / fair_value_mcap) - 1) * 100 if fair_value_mcap > 0 else 0

        return {
            "method": "revenue_multiple",
            "annual_revenue": annual_revenue,
            "sector": sector,
            "sector_median_ps": medians["ps"],
            "fair_value_mcap": fair_value_mcap,
            "current_mcap": current_mcap,
            "premium_discount_pct": round(premium_discount, 1),
            "verdict": "UNDERVALUED" if premium_discount < -20 else "OVERVALUED" if premium_discount > 50 else "FAIR",
        }

    def tvl_valuation(self, tvl: float, mcap: float, sector: str = "Other") -> dict:
        """Value protocol using MCap/TVL ratio."""
        ratio = mcap / tvl if tvl > 0 else float('inf')
        medians = self.SECTOR_MEDIANS.get(sector, self.SECTOR_MEDIANS["Other"])
        fair_ratio = medians["mcap_tvl"]
        fair_mcap = tvl * fair_ratio
        premium_discount = ((mcap / fair_mcap) - 1) * 100 if fair_mcap > 0 else 0

        return {
            "method": "tvl_valuation",
            "tvl": tvl,
            "mcap": mcap,
            "mcap_tvl_ratio": round(ratio, 3),
            "sector_median_ratio": fair_ratio,
            "fair_value_mcap": fair_mcap,
            "premium_discount_pct": round(premium_discount, 1),
            "verdict": "UNDERVALUED" if ratio < fair_ratio * 0.5 else "OVERVALUED" if ratio > fair_ratio * 2 else "FAIR",
        }

    def dcf_lite(self, current_revenue: float, growth_rate: float = 0.3,
                 discount_rate: float = 0.25, terminal_multiple: float = 15,
                 years: int = 5) -> dict:
        """
        Simplified DCF for crypto protocols.
        Projects revenue forward, discounts back at crypto-appropriate rate (25%+).
        """
        projected = []
        rev = current_revenue
        total_pv = 0

        for year in range(1, years + 1):
            rev *= (1 + growth_rate)
            # Growth decays by 20% each year (mean-reversion)
            growth_rate *= 0.8
            discount_factor = 1 / ((1 + discount_rate) ** year)
            pv = rev * discount_factor
            total_pv += pv
            projected.append({
                "year": year,
                "revenue": round(rev),
                "growth": round(growth_rate * 100 / 0.8, 1),
                "pv": round(pv),
            })

        # Terminal value
        terminal_value = rev * terminal_multiple
        terminal_pv = terminal_value / ((1 + discount_rate) ** years)
        total_value = total_pv + terminal_pv

        return {
            "method": "dcf_lite",
            "current_revenue": current_revenue,
            "initial_growth": round(growth_rate / 0.8 * 100 / 0.8, 1),
            "discount_rate": discount_rate,
            "terminal_multiple": terminal_multiple,
            "projected_years": projected,
            "terminal_value": round(terminal_pv),
            "fair_value_mcap": round(total_value),
            "breakdown": {
                "cash_flow_pv": round(total_pv),
                "terminal_pv": round(terminal_pv),
                "terminal_pct": round(terminal_pv / total_value * 100, 1) if total_value else 0,
            },
        }

    def full_valuation(self, data: dict) -> dict:
        """Run all valuation methods and produce composite verdict."""
        results = {}
        verdicts = []

        if data.get("revenue"):
            rev = self.revenue_multiple_valuation(
                data["revenue"], data.get("sector", "Other"), data.get("mcap", 0)
            )
            results["revenue_multiple"] = rev
            verdicts.append(rev["premium_discount_pct"])

        if data.get("tvl") and data.get("mcap"):
            tvl = self.tvl_valuation(data["tvl"], data["mcap"], data.get("sector", "Other"))
            results["tvl_valuation"] = tvl
            verdicts.append(tvl["premium_discount_pct"])

        if data.get("revenue"):
            dcf = self.dcf_lite(
                data["revenue"],
                growth_rate=data.get("growth_rate", 0.3),
            )
            results["dcf"] = dcf
            if data.get("mcap") and dcf["fair_value_mcap"]:
                dcf_discount = ((data["mcap"] / dcf["fair_value_mcap"]) - 1) * 100
                results["dcf"]["premium_discount_pct"] = round(dcf_discount, 1)
                verdicts.append(dcf_discount)

        # Composite
        avg_discount = sum(verdicts) / len(verdicts) if verdicts else 0
        results["composite"] = {
            "avg_premium_discount": round(avg_discount, 1),
            "methods_used": len(verdicts),
            "verdict": "STRONG BUY" if avg_discount < -40 else
                       "UNDERVALUED" if avg_discount < -15 else
                       "FAIR" if avg_discount < 30 else
                       "OVERVALUED" if avg_discount < 80 else "AVOID",
            "confidence": "high" if len(verdicts) >= 3 else "medium" if len(verdicts) >= 2 else "low",
        }

        return results


# ===== MULTI-FACTOR SCORING =====

class MultiFactorScorer:
    """
    Scores assets across multiple dimensions:
    - Fundamental (revenue, TVL, growth)
    - Technical (RSI, trend, volume)
    - On-chain (whale activity, holder growth)
    - Sentiment (social, funding rates)
    - Valuation (P/S, MCap/TVL, DCF)
    """

    WEIGHTS = {
        "fundamental": 0.25,
        "technical": 0.20,
        "onchain": 0.20,
        "sentiment": 0.15,
        "valuation": 0.20,
    }

    def score_fundamental(self, data: dict) -> dict:
        """Score 1-5 based on protocol fundamentals."""
        score = 3.0  # Neutral baseline
        details = []

        # Revenue growth
        growth = data.get("revenue_growth_30d", 0)
        if growth > 20:
            score += 1.0
            details.append(f"Strong revenue growth: {growth:.0f}%")
        elif growth > 5:
            score += 0.5
            details.append(f"Positive revenue growth: {growth:.0f}%")
        elif growth < -10:
            score -= 1.0
            details.append(f"Revenue declining: {growth:.0f}%")

        # TVL trend
        tvl_change = data.get("tvl_change_7d", 0)
        if tvl_change > 10:
            score += 0.5
            details.append(f"TVL growing: +{tvl_change:.0f}%")
        elif tvl_change < -10:
            score -= 0.5
            details.append(f"TVL declining: {tvl_change:.0f}%")

        # Active development
        if data.get("active_development"):
            score += 0.3
            details.append("Active development")

        return {"score": min(5, max(1, round(score, 1))), "details": details}

    def score_technical(self, data: dict) -> dict:
        """Score 1-5 based on technical indicators."""
        score = 3.0
        details = []

        # Price vs moving averages
        change_7d = data.get("change_7d", 0)
        change_24h = data.get("change_24h", 0)

        if change_7d > 15:
            score += 0.8
            details.append(f"Strong 7d momentum: +{change_7d:.1f}%")
        elif change_7d > 5:
            score += 0.4
            details.append(f"Positive 7d: +{change_7d:.1f}%")
        elif change_7d < -15:
            score -= 0.8
            details.append(f"Weak 7d: {change_7d:.1f}%")

        # ATH distance (recovery potential)
        ath_change = data.get("ath_change", 0)
        if ath_change < -80:
            score += 0.5
            details.append(f"Deep discount from ATH: {ath_change:.0f}%")
        elif ath_change > -10:
            score -= 0.3
            details.append(f"Near ATH: {ath_change:.0f}%")

        # Volume
        vol = data.get("volume_24h", 0)
        mcap = data.get("market_cap", 0)
        if mcap > 0:
            vol_ratio = vol / mcap
            if vol_ratio > 0.3:
                score += 0.5
                details.append(f"High volume/mcap: {vol_ratio:.2f}")
            elif vol_ratio < 0.02:
                score -= 0.5
                details.append(f"Low volume/mcap: {vol_ratio:.3f}")

        return {"score": min(5, max(1, round(score, 1))), "details": details}

    def score_onchain(self, data: dict) -> dict:
        """Score 1-5 based on on-chain activity."""
        score = 3.0
        details = []

        # Whale activity
        whale_count = data.get("whale_positions", 0)
        if whale_count >= 5:
            score += 1.0
            details.append(f"High whale interest: {whale_count} positions")
        elif whale_count >= 2:
            score += 0.5
            details.append(f"Moderate whale interest: {whale_count} positions")

        # Funding rate
        funding = data.get("funding_rate", 0)
        if funding > 0.0005:
            score -= 0.5
            details.append(f"Elevated funding: {funding*100:.3f}%")
        elif funding < -0.0001:
            score += 0.3
            details.append(f"Negative funding (contrarian): {funding*100:.3f}%")

        # Open interest
        oi_change = data.get("oi_change_24h", 0)
        if oi_change > 10:
            score += 0.3
            details.append(f"OI expanding: +{oi_change:.0f}%")

        return {"score": min(5, max(1, round(score, 1))), "details": details}

    def score_sentiment(self, data: dict) -> dict:
        """Score 1-5 based on market sentiment."""
        score = 3.0
        details = []

        # Fear & Greed
        fng = data.get("fear_greed", 50)
        if fng < 25:
            score += 0.8  # Extreme fear = contrarian buy
            details.append(f"Extreme fear ({fng}) — contrarian bullish")
        elif fng > 75:
            score -= 0.5
            details.append(f"Extreme greed ({fng}) — caution")

        # Trending
        if data.get("is_trending"):
            score += 0.3
            details.append("Trending on CoinGecko")

        # Social mentions
        social = data.get("social_score", 0)
        if social > 80:
            score += 0.3
            details.append(f"High social activity: {social}")

        return {"score": min(5, max(1, round(score, 1))), "details": details}

    def score_valuation(self, data: dict) -> dict:
        """Score 1-5 based on valuation metrics."""
        score = 3.0
        details = []

        # MCap/TVL
        mcap_tvl = data.get("mcap_tvl", None)
        if mcap_tvl is not None:
            if mcap_tvl < 0.3:
                score += 1.0
                details.append(f"Very low MCap/TVL: {mcap_tvl:.2f}")
            elif mcap_tvl < 1.0:
                score += 0.5
                details.append(f"Reasonable MCap/TVL: {mcap_tvl:.2f}")
            elif mcap_tvl > 5.0:
                score -= 0.5
                details.append(f"High MCap/TVL: {mcap_tvl:.1f}")

        # FDV/MCap (dilution risk)
        fdv = data.get("fdv", 0)
        mcap = data.get("market_cap", 0)
        if fdv > 0 and mcap > 0:
            dilution = fdv / mcap
            if dilution > 5:
                score -= 1.0
                details.append(f"High dilution risk (FDV/MCap: {dilution:.1f}x)")
            elif dilution > 2:
                score -= 0.3
                details.append(f"Moderate dilution (FDV/MCap: {dilution:.1f}x)")
            elif dilution < 1.3:
                score += 0.3
                details.append(f"Low dilution (FDV/MCap: {dilution:.1f}x)")

        return {"score": min(5, max(1, round(score, 1))), "details": details}

    def score_asset(self, data: dict) -> dict:
        """Full multi-factor score for an asset."""
        factors = {
            "fundamental": self.score_fundamental(data),
            "technical": self.score_technical(data),
            "onchain": self.score_onchain(data),
            "sentiment": self.score_sentiment(data),
            "valuation": self.score_valuation(data),
        }

        # Weighted composite
        composite = sum(
            factors[k]["score"] * self.WEIGHTS[k]
            for k in self.WEIGHTS
        )

        # All details
        all_details = []
        for k, v in factors.items():
            for d in v["details"]:
                all_details.append(f"[{k.upper()}] {d}")

        return {
            "composite_score": round(composite, 2),
            "factors": {k: v["score"] for k, v in factors.items()},
            "details": all_details,
            "grade": "A" if composite >= 4.0 else "B" if composite >= 3.5 else "C" if composite >= 2.5 else "D",
            "signal": "STRONG BUY" if composite >= 4.2 else
                      "BUY" if composite >= 3.5 else
                      "HOLD" if composite >= 2.5 else
                      "AVOID",
            "updated": now_iso(),
        }


# ===== AUTO-DISCOVERY ENGINE =====

class AutoDiscovery:
    """
    Scans the crypto market for opportunities matching the 5-lens filter.
    Looks for: undervalued protocols, momentum shifts, whale accumulation,
    narrative front-runs, and deep value recovery.
    """

    def __init__(self):
        self.scorer = MultiFactorScorer()
        self.valuation = CryptoValuation()

    async def scan_coingecko_opportunities(self, session: aiohttp.ClientSession,
                                            min_mcap: float = 10_000_000,
                                            max_mcap: float = 2_000_000_000) -> list:
        """Scan CoinGecko for coins in the sweet spot (low mcap, high potential)."""
        opportunities = []
        for page in range(1, 4):  # Top 750 coins
            url = (f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd"
                   f"&order=market_cap_desc&per_page=250&page={page}"
                   f"&sparkline=false&price_change_percentage=7d,30d")
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 429:
                        break
                    coins = await resp.json()
                    for coin in coins:
                        mcap = coin.get("market_cap", 0) or 0
                        if min_mcap <= mcap <= max_mcap:
                            ath_change = coin.get("ath_change_percentage", 0) or 0
                            change_7d = coin.get("price_change_percentage_7d_in_currency", 0) or 0
                            change_30d = coin.get("price_change_percentage_30d_in_currency", 0) or 0

                            # Filter: deep discount + momentum turning
                            if ath_change < -70 and change_7d > 0:
                                opportunities.append({
                                    "symbol": coin.get("symbol", "").upper(),
                                    "name": coin.get("name"),
                                    "price": coin.get("current_price"),
                                    "market_cap": mcap,
                                    "fdv": coin.get("fully_diluted_valuation"),
                                    "volume_24h": coin.get("total_volume"),
                                    "change_7d": round(change_7d, 1),
                                    "change_30d": round(change_30d, 1) if change_30d else None,
                                    "ath_change": round(ath_change, 1),
                                    "rank": coin.get("market_cap_rank"),
                                })
            except Exception as e:
                break
            await asyncio.sleep(1)  # Rate limit

        # Score each
        for opp in opportunities:
            data = {
                "change_7d": opp.get("change_7d", 0),
                "change_24h": 0,
                "ath_change": opp.get("ath_change", 0),
                "volume_24h": opp.get("volume_24h", 0),
                "market_cap": opp.get("market_cap", 0),
                "fdv": opp.get("fdv", 0),
                "fear_greed": 50,
            }
            score = self.scorer.score_asset(data)
            opp["composite_score"] = score["composite_score"]
            opp["grade"] = score["grade"]
            opp["signal"] = score["signal"]

        # Sort by score
        opportunities.sort(key=lambda x: x["composite_score"], reverse=True)
        return opportunities[:30]

    async def scan_defi_undervalued(self, session: aiohttp.ClientSession) -> list:
        """Find DeFi protocols with TVL growing faster than price."""
        url = "https://api.llama.fi/protocols"
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                protocols = await resp.json()
                opportunities = []
                for p in protocols:
                    tvl = p.get("tvl", 0) or 0
                    mcap = p.get("mcap", 0) or 0
                    change_7d = p.get("change_7d", 0) or 0

                    if tvl > 10_000_000 and mcap > 0:
                        mcap_tvl = mcap / tvl
                        # Look for low MCap/TVL with growing TVL
                        if mcap_tvl < 1.0 and change_7d > 0:
                            opportunities.append({
                                "name": p.get("name"),
                                "symbol": p.get("symbol", "").upper(),
                                "tvl": tvl,
                                "mcap": mcap,
                                "mcap_tvl": round(mcap_tvl, 3),
                                "tvl_change_7d": round(change_7d, 1),
                                "category": p.get("category"),
                                "chains": p.get("chains", [])[:3],
                                "signal": "UNDERVALUED" if mcap_tvl < 0.3 else "INTERESTING",
                            })

                opportunities.sort(key=lambda x: x["mcap_tvl"])
                return opportunities[:20]
        except Exception as e:
            return []

    async def run_full_scan(self) -> dict:
        """Run complete auto-discovery scan."""
        async with aiohttp.ClientSession() as session:
            cg_opps, defi_opps = await asyncio.gather(
                self.scan_coingecko_opportunities(session),
                self.scan_defi_undervalued(session),
                return_exceptions=True,
            )

            result = {
                "deep_value": cg_opps if isinstance(cg_opps, list) else [],
                "defi_undervalued": defi_opps if isinstance(defi_opps, list) else [],
                "scanned_at": now_iso(),
            }

            # Push top picks to Firebase
            try:
                fb_write("/fundHQ/autoDiscovery", result)
                # Alert on strong finds
                strong = [o for o in (cg_opps if isinstance(cg_opps, list) else [])
                          if o.get("grade") in ("A", "B")]
                if strong:
                    names = ", ".join(o["symbol"] for o in strong[:5])
                    push_alert(
                        f"Auto-Discovery: {len(strong)} opportunities found",
                        f"Top picks: {names}",
                        severity="opportunity",
                        source="auto-discovery",
                    )
            except Exception as e:
                print(f"[DISCOVERY] Firebase error: {e}")

            return result
