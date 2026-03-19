#!/usr/bin/env python3
"""
Fund HQ Backend Server
========================
FastAPI server exposing all 5 phases:
  Phase 1: Data feeds, macro intelligence
  Phase 2: Quant models, auto-discovery
  Phase 3: Risk engine, VaR, correlation
  Phase 4: Learning, feedback, backtesting
  Phase 5: Autonomy, smart alerts, API

Run: python server.py
Or:  uvicorn server:app --host 0.0.0.0 --port 8888 --reload
"""

import asyncio
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", ".env"))
except ImportError:
    pass

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.data_feeds import DataFeedManager
from services.quant_models import CryptoValuation, MultiFactorScorer, AutoDiscovery
from services.risk_engine import RiskDashboard, VaRCalculator, CorrelationAnalyzer, PortfolioOptimizer, LiquidityScorer
from services.learning import TradeFeedback, ScoreCalibrator, BacktestBridge
from services.autonomy import AutonomousResearch, SmartAlerts, APIPlatform
from shared.firebase import fb_read, fb_write, now_iso


# ===== BACKGROUND TASKS =====

feed_manager = DataFeedManager()
auto_research = AutonomousResearch()
smart_alerts = SmartAlerts()
background_tasks = set()


async def periodic_price_update():
    """Update prices every 2 minutes."""
    while True:
        try:
            await feed_manager.run_prices_only()
            print(f"[FEEDS] Prices updated — {len(feed_manager.prices)} coins")
        except Exception as e:
            print(f"[FEEDS] Price update error: {e}")
        await asyncio.sleep(120)


async def periodic_full_update():
    """Full data update every 10 minutes."""
    while True:
        try:
            result = await feed_manager.run_full_update()
            print(f"[FEEDS] Full update complete")
        except Exception as e:
            print(f"[FEEDS] Full update error: {e}")
        await asyncio.sleep(600)


async def periodic_smart_alerts():
    """Check smart alerts every 5 minutes."""
    while True:
        try:
            alerts = await smart_alerts.run_smart_alerts()
            if alerts:
                print(f"[ALERTS] {len(alerts)} smart alerts generated")
        except Exception as e:
            print(f"[ALERTS] Error: {e}")
        await asyncio.sleep(300)


async def periodic_auto_research():
    """Check autonomous research triggers every 15 minutes."""
    while True:
        try:
            market_data = {"prices": feed_manager.prices}
            triggers = await auto_research.check_triggers(market_data)
            if triggers:
                results = await auto_research.execute_triggered_research(triggers)
                print(f"[AUTO] {len(triggers)} triggers, {len(results)} actions")
        except Exception as e:
            print(f"[AUTO] Error: {e}")
        await asyncio.sleep(900)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start background tasks on server startup."""
    print("=" * 60)
    print("  FUND HQ BACKEND SERVER")
    print(f"  Started: {now_iso()}")
    print("  Phases: Data Feeds | Quant | Risk | Learning | Autonomy")
    print("=" * 60)

    # Initial full update
    try:
        await feed_manager.run_full_update()
        print("[STARTUP] Initial data feed complete")
    except Exception as e:
        print(f"[STARTUP] Initial feed error: {e}")

    # Start background loops
    tasks = [
        asyncio.create_task(periodic_price_update()),
        asyncio.create_task(periodic_full_update()),
        asyncio.create_task(periodic_smart_alerts()),
        asyncio.create_task(periodic_auto_research()),
    ]
    background_tasks.update(tasks)

    yield

    # Cleanup
    for task in tasks:
        task.cancel()


# ===== APP =====

app = FastAPI(
    title="Fund HQ Backend",
    description="Trading infrastructure API — Phases 1-5",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== HEALTH =====

@app.get("/")
async def root():
    return {
        "name": "Fund HQ Backend",
        "status": "running",
        "phases": {
            "1_data_feeds": "active",
            "2_quant_models": "active",
            "3_risk_engine": "active",
            "4_learning": "active",
            "5_autonomy": "active",
        },
        "feeds": feed_manager.get_status(),
        "uptime": now_iso(),
    }


@app.get("/health")
async def health():
    return {"status": "ok", "time": now_iso()}


# ===== PHASE 1: DATA FEEDS =====

@app.get("/api/prices")
async def get_prices():
    """Current prices for all watched coins."""
    if not feed_manager.prices:
        await feed_manager.run_prices_only()
    return feed_manager.prices


@app.get("/api/prices/{symbol}")
async def get_price(symbol: str):
    """Current price for a specific coin."""
    sym = symbol.upper()
    if sym in feed_manager.prices:
        return feed_manager.prices[sym]
    raise HTTPException(404, f"No price data for {sym}")


@app.get("/api/macro")
async def get_macro():
    """Macro intelligence snapshot."""
    if not feed_manager.macro:
        return await feed_manager.get_macro_snapshot()
    return feed_manager.macro


@app.get("/api/feeds/status")
async def feeds_status():
    """Data feed status."""
    return feed_manager.get_status()


@app.post("/api/feeds/refresh")
async def refresh_feeds():
    """Force a full data feed refresh."""
    result = await feed_manager.run_full_update()
    return {"status": "refreshed", "coins": len(result.get("prices", {}))}


# ===== PHASE 2: QUANT MODELS =====

class ValuationRequest(BaseModel):
    revenue: float = 0
    tvl: float = 0
    mcap: float = 0
    sector: str = "Other"
    growth_rate: float = 0.3


@app.post("/api/valuation")
async def run_valuation(req: ValuationRequest):
    """Run full valuation analysis."""
    v = CryptoValuation()
    return v.full_valuation(req.model_dump())


@app.post("/api/valuation/dcf")
async def run_dcf(revenue: float, growth_rate: float = 0.3,
                  discount_rate: float = 0.25, years: int = 5):
    """Run DCF model."""
    v = CryptoValuation()
    return v.dcf_lite(revenue, growth_rate, discount_rate, years=years)


class ScoreRequest(BaseModel):
    symbol: str = ""
    change_24h: float = 0
    change_7d: float = 0
    ath_change: float = 0
    volume_24h: float = 0
    market_cap: float = 0
    fdv: float = 0
    tvl: float = 0
    mcap_tvl: Optional[float] = None
    revenue_growth_30d: float = 0
    tvl_change_7d: float = 0
    whale_positions: int = 0
    funding_rate: float = 0
    oi_change_24h: float = 0
    fear_greed: int = 50
    is_trending: bool = False
    active_development: bool = False


@app.post("/api/score")
async def score_asset(req: ScoreRequest):
    """Multi-factor score an asset."""
    scorer = MultiFactorScorer()
    data = req.model_dump()
    if data.get("mcap_tvl") is None and data.get("market_cap") and data.get("tvl"):
        data["mcap_tvl"] = data["market_cap"] / data["tvl"]
    return scorer.score_asset(data)


@app.get("/api/discovery")
async def auto_discover():
    """Run auto-discovery scan for opportunities."""
    discovery = AutoDiscovery()
    return await discovery.run_full_scan()


@app.get("/api/discovery/defi")
async def discover_defi():
    """Find undervalued DeFi protocols."""
    import aiohttp
    discovery = AutoDiscovery()
    async with aiohttp.ClientSession() as session:
        return await discovery.scan_defi_undervalued(session)


# ===== PHASE 3: RISK ENGINE =====

class PortfolioPosition(BaseModel):
    symbol: str
    value: float
    coin_id: Optional[str] = None


class PortfolioRequest(BaseModel):
    positions: list[PortfolioPosition]
    confidence: float = 0.95


@app.post("/api/risk/var")
async def calculate_var(req: PortfolioRequest):
    """Calculate portfolio Value at Risk."""
    var_calc = VaRCalculator()
    portfolio = [p.model_dump() for p in req.positions]
    return await var_calc.portfolio_var(portfolio, req.confidence)


@app.post("/api/risk/correlation")
async def get_correlations(symbols: list[str] = Query(default=["BTC", "ETH", "SOL"]),
                           days: int = 60):
    """Build correlation matrix."""
    analyzer = CorrelationAnalyzer()
    return await analyzer.build_correlation_matrix(symbols, days)


@app.get("/api/risk/dashboard")
async def risk_dashboard():
    """Full risk dashboard from Firebase."""
    try:
        return fb_read("/fundHQ/riskDashboard") or {"status": "no_data"}
    except:
        return {"status": "error"}


@app.post("/api/risk/assess")
async def assess_risk(req: PortfolioRequest):
    """Run full risk assessment."""
    dashboard = RiskDashboard()
    portfolio = [p.model_dump() for p in req.positions]
    return await dashboard.full_risk_assessment(portfolio)


class PositionSizeRequest(BaseModel):
    capital: float
    risk_per_trade: float = 0.01
    entry: float
    stop_loss: float


@app.post("/api/risk/position-size")
async def position_size(req: PositionSizeRequest):
    """Calculate position size."""
    optimizer = PortfolioOptimizer()
    return optimizer.position_size(req.capital, req.risk_per_trade, req.entry, req.stop_loss)


@app.post("/api/risk/liquidity")
async def score_liquidity(volume_24h: float = 0, market_cap: float = 0,
                          avg_spread_pct: float = 0):
    """Score asset liquidity."""
    scorer = LiquidityScorer()
    return scorer.score({"volume_24h": volume_24h, "market_cap": market_cap,
                         "avg_spread_pct": avg_spread_pct})


# ===== PHASE 4: LEARNING =====

@app.get("/api/performance")
async def get_performance():
    """Analyze trading performance."""
    fb = TradeFeedback()
    return fb.analyze_performance()


@app.get("/api/performance/by-setup")
async def performance_by_setup():
    """Performance breakdown by setup type."""
    fb = TradeFeedback()
    return fb.analyze_by_setup()


@app.get("/api/calibration")
async def get_calibration():
    """Get current score calibration."""
    cal = ScoreCalibrator()
    return cal.load_calibration()


@app.post("/api/calibration/run")
async def run_calibration():
    """Run score calibration on trade history."""
    fb = TradeFeedback()
    trades = fb.load_trades()
    closed = [t for t in trades if t.get("status") == "closed" and t.get("pnl") is not None]
    cal = ScoreCalibrator()
    return cal.calibrate(closed)


@app.get("/api/backtest/strategies")
async def list_strategies():
    """List available backtest strategies."""
    bridge = BacktestBridge()
    return bridge.get_strategies()


@app.get("/api/backtest/{symbol}/{strategy}")
async def run_backtest(symbol: str, strategy: str, days: int = 365):
    """Run backtest for a strategy on a coin."""
    bridge = BacktestBridge()
    return await bridge.run_backtest(symbol.upper(), strategy, days)


# ===== PHASE 5: AUTONOMY =====

@app.get("/api/autonomous/triggers")
async def check_triggers():
    """Check autonomous research triggers."""
    market_data = {"prices": feed_manager.prices}
    return await auto_research.check_triggers(market_data)


@app.post("/api/autonomous/execute")
async def execute_auto_research():
    """Execute autonomous research on triggered conditions."""
    market_data = {"prices": feed_manager.prices}
    triggers = await auto_research.check_triggers(market_data)
    if not triggers:
        return {"status": "no_triggers", "message": "No conditions met for autonomous research"}
    results = await auto_research.execute_triggered_research(triggers)
    return {"triggers": len(triggers), "executed": len(results), "results": results}


@app.get("/api/smart-alerts")
async def get_smart_alerts():
    """Run portfolio-aware smart alerts."""
    return await smart_alerts.run_smart_alerts()


# === External API endpoints ===

api_platform = APIPlatform()

@app.get("/api/v1/portfolio")
async def api_portfolio():
    """External API: Portfolio summary."""
    return api_platform.get_portfolio_summary()


@app.get("/api/v1/signals")
async def api_signals(min_grade: str = "C"):
    """External API: Active signals."""
    return api_platform.get_signals(min_grade)


@app.get("/api/v1/market")
async def api_market():
    """External API: Market snapshot."""
    return api_platform.get_market_snapshot()


@app.get("/api/v1/risk")
async def api_risk():
    """External API: Risk metrics."""
    return api_platform.get_risk_metrics()


@app.get("/api/v1/performance")
async def api_performance():
    """External API: Trading performance."""
    return api_platform.get_performance()


# ===== MAIN =====

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8888,
        reload=True,
        log_level="info",
    )
