"""
Phase 5: Full Autonomy
=======================
Unprompted research execution, portfolio-aware alerts,
and external API platform.
"""

import asyncio
import aiohttp
from datetime import datetime, timezone, timedelta
from typing import Optional
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.firebase import fb_write, fb_read, fb_patch, push_alert, now_iso
from shared.config import WATCH_COINS


# ===== AUTONOMOUS RESEARCH ENGINE =====

class AutonomousResearch:
    """
    Triggers research automatically based on market conditions.
    No human prompt needed — monitors and acts on opportunities.
    """

    # Trigger thresholds
    TRIGGERS = {
        "price_spike": 15,       # % move in 24h triggers deep dive
        "volume_spike": 3.0,     # Volume/avg ratio triggers investigation
        "whale_accumulation": 3, # N whales accumulating same coin
        "correlation_break": 0.3,# Sudden decorrelation from BTC
        "regime_change": True,   # Market regime transitions
        "unlock_proximity": 3,   # Days before major unlock
        "tvl_surge": 20,         # % TVL increase in 7d
    }

    async def check_triggers(self, market_data: dict) -> list:
        """
        Scan market data for autonomous research triggers.
        Returns list of triggered conditions with context.
        """
        triggered = []

        prices = market_data.get("prices", {})
        for symbol, data in prices.items():
            if not isinstance(data, dict):
                continue

            # Price spike trigger
            change_24h = abs(data.get("change_24h", 0) or 0)
            if change_24h >= self.TRIGGERS["price_spike"]:
                triggered.append({
                    "trigger": "price_spike",
                    "symbol": symbol,
                    "value": change_24h,
                    "direction": "up" if (data.get("change_24h", 0) or 0) > 0 else "down",
                    "priority": "high",
                    "action": f"Deep dive: {symbol} moved {change_24h:.1f}% in 24h",
                })

            # Volume spike
            vol = data.get("volume_24h", 0) or 0
            mcap = data.get("market_cap", 0) or 0
            if mcap > 0:
                vol_ratio = vol / mcap
                if vol_ratio > self.TRIGGERS["volume_spike"]:
                    triggered.append({
                        "trigger": "volume_spike",
                        "symbol": symbol,
                        "value": round(vol_ratio, 2),
                        "priority": "medium",
                        "action": f"Investigate: {symbol} volume spike ({vol_ratio:.1f}x mcap)",
                    })

            # Deep discount with momentum
            ath_change = data.get("ath_change", 0) or 0
            change_7d = data.get("change_7d", 0) or 0
            if ath_change < -80 and change_7d > 10:
                triggered.append({
                    "trigger": "recovery_signal",
                    "symbol": symbol,
                    "value": {"ath_change": ath_change, "change_7d": change_7d},
                    "priority": "high",
                    "action": f"Recovery watch: {symbol} at {ath_change:.0f}% from ATH, up {change_7d:.0f}% this week",
                })

        return triggered

    async def execute_triggered_research(self, triggers: list) -> list:
        """Execute research based on triggered conditions."""
        results = []
        high_priority = [t for t in triggers if t.get("priority") == "high"]

        for trigger in high_priority[:3]:  # Max 3 per cycle
            symbol = trigger.get("symbol", "")

            # Generate alert
            alert_id = push_alert(
                title=f"Auto-Research: {trigger['action']}",
                content=(
                    f"Trigger: {trigger['trigger']}\n"
                    f"Symbol: {symbol}\n"
                    f"Value: {trigger['value']}\n"
                    f"Action: {trigger['action']}"
                ),
                severity="opportunity" if trigger["trigger"] in ("price_spike", "recovery_signal") else "info",
                source="autonomous-research",
            )

            results.append({
                "trigger": trigger["trigger"],
                "symbol": symbol,
                "alert_id": alert_id,
                "status": "alert_generated",
            })

        return results


# ===== PORTFOLIO-AWARE ALERTS =====

class SmartAlerts:
    """
    Generates alerts based on portfolio context, not just price.
    Knows what you hold, your risk limits, and your targets.
    """

    ALERT_RULES = [
        {
            "name": "position_stop_hit",
            "description": "Alert when a position approaches stop loss",
            "threshold_pct": 2.0,  # Alert when within 2% of stop
        },
        {
            "name": "position_target_near",
            "description": "Alert when position approaches take profit target",
            "threshold_pct": 3.0,
        },
        {
            "name": "portfolio_drawdown",
            "description": "Alert when portfolio drawdown exceeds threshold",
            "threshold_pct": 10.0,
        },
        {
            "name": "concentration_warning",
            "description": "Alert when single position exceeds portfolio %",
            "threshold_pct": 30.0,
        },
        {
            "name": "correlation_risk",
            "description": "Alert when correlated positions are too large",
            "threshold_pct": 50.0,
        },
    ]

    def check_portfolio_alerts(self, portfolio: list, prices: dict) -> list:
        """Check portfolio against alert rules."""
        alerts = []
        total_value = sum(p.get("value", 0) or 0 for p in portfolio)
        if total_value == 0:
            return alerts

        for pos in portfolio:
            symbol = pos.get("symbol", "").upper()
            value = pos.get("value", 0) or 0
            entry = pos.get("entry_price", 0) or 0
            stop = pos.get("stop_loss", 0)
            target = pos.get("target", 0)
            current = 0

            # Get current price
            price_data = prices.get(symbol, {})
            if isinstance(price_data, dict):
                current = price_data.get("price", 0) or 0

            if not current or not entry:
                continue

            pnl_pct = (current / entry - 1) * 100
            weight = value / total_value * 100

            # Stop loss proximity
            if stop and current > 0:
                distance_to_stop = (current - stop) / current * 100
                if 0 < distance_to_stop < 3:
                    alerts.append({
                        "type": "stop_proximity",
                        "symbol": symbol,
                        "severity": "warning",
                        "message": f"{symbol} is {distance_to_stop:.1f}% from stop loss (${stop:.2f})",
                        "current_price": current,
                        "stop_loss": stop,
                    })

            # Target proximity
            if target and current > 0:
                distance_to_target = (target - current) / current * 100
                if 0 < distance_to_target < 5:
                    alerts.append({
                        "type": "target_proximity",
                        "symbol": symbol,
                        "severity": "opportunity",
                        "message": f"{symbol} is {distance_to_target:.1f}% from target (${target:.2f})",
                        "current_price": current,
                        "target": target,
                    })

            # Concentration warning
            if weight > 30:
                alerts.append({
                    "type": "concentration",
                    "symbol": symbol,
                    "severity": "warning",
                    "message": f"{symbol} is {weight:.1f}% of portfolio — consider rebalancing",
                    "weight": weight,
                })

            # Large unrealized loss
            if pnl_pct < -15:
                alerts.append({
                    "type": "unrealized_loss",
                    "symbol": symbol,
                    "severity": "warning",
                    "message": f"{symbol} is down {pnl_pct:.1f}% — review thesis",
                    "pnl_pct": pnl_pct,
                })

            # Large unrealized gain (take profit?)
            if pnl_pct > 50:
                alerts.append({
                    "type": "unrealized_gain",
                    "symbol": symbol,
                    "severity": "opportunity",
                    "message": f"{symbol} is up {pnl_pct:.1f}% — consider taking partial profits",
                    "pnl_pct": pnl_pct,
                })

        return alerts

    async def run_smart_alerts(self) -> list:
        """Full smart alert cycle: load portfolio + prices, check rules."""
        try:
            portfolio = fb_read("/fundHQ/portfolio") or []
            if isinstance(portfolio, dict):
                portfolio = list(portfolio.values())
            prices = fb_read("/fundHQ/marketData/prices") or {}
        except:
            return []

        alerts = self.check_portfolio_alerts(portfolio, prices)

        # Push critical alerts to Firebase
        for alert in alerts:
            if alert.get("severity") in ("warning", "opportunity"):
                push_alert(
                    title=f"Smart Alert: {alert['message'][:60]}",
                    content=alert["message"],
                    severity=alert["severity"],
                    source="smart-alerts",
                    alert_type="smart",
                )

        return alerts


# ===== API PLATFORM =====

class APIPlatform:
    """
    External API for Fund HQ data.
    Exposes read-only endpoints for dashboards, bots, and integrations.
    """

    def __init__(self):
        self.api_keys = {}  # key -> permissions
        self.rate_limits = {}  # key -> {count, reset_time}

    def validate_key(self, key: str) -> bool:
        """Validate API key. In production, check against stored keys."""
        # For now, any non-empty key works (local use only)
        return bool(key)

    def check_rate_limit(self, key: str, limit: int = 60) -> bool:
        """Simple rate limiting: N requests per minute."""
        now = datetime.now(timezone.utc)
        if key not in self.rate_limits:
            self.rate_limits[key] = {"count": 0, "reset": now + timedelta(minutes=1)}

        rl = self.rate_limits[key]
        if now > rl["reset"]:
            rl["count"] = 0
            rl["reset"] = now + timedelta(minutes=1)

        rl["count"] += 1
        return rl["count"] <= limit

    def get_portfolio_summary(self) -> dict:
        """API: Portfolio summary."""
        try:
            portfolio = fb_read("/fundHQ/portfolio") or []
            if isinstance(portfolio, dict):
                portfolio = list(portfolio.values())
            total = sum(p.get("value", 0) or 0 for p in portfolio)
            return {
                "total_value": total,
                "positions": len(portfolio),
                "assets": [{"symbol": p.get("symbol"), "value": p.get("value")}
                          for p in portfolio],
                "updated": now_iso(),
            }
        except:
            return {"error": "unable_to_fetch"}

    def get_signals(self, min_grade: str = "C") -> list:
        """API: Active signals above minimum grade."""
        try:
            signals = fb_read("/fundHQ/signals") or []
            if isinstance(signals, dict):
                signals = list(signals.values())
            from shared.config import grade_passes
            return [s for s in signals if grade_passes(s.get("grade", "?"), min_grade)]
        except:
            return []

    def get_market_snapshot(self) -> dict:
        """API: Current market data snapshot."""
        try:
            return fb_read("/fundHQ/marketData") or {}
        except:
            return {}

    def get_risk_metrics(self) -> dict:
        """API: Latest risk dashboard data."""
        try:
            return fb_read("/fundHQ/riskDashboard") or {}
        except:
            return {}

    def get_performance(self) -> dict:
        """API: Trading performance metrics."""
        try:
            return fb_read("/fundHQ/performance") or {}
        except:
            return {}
