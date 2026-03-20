# 24/7 Autonomous Agent System — Mac Mini

## Context
FundHQ has 5 frontend agents (Router, Analyst, Sentinel, Trader, VC) that only run on user request, plus a FastAPI backend with 4 data loops. The goal is to make agents work autonomously 24/7 on the Mac Mini — continuously discovering, researching, scoring, learning, and writing results to Firebase so the frontend updates in real-time.

## Architecture

```
Mac Mini (always-on)
├── agents/server.py (EXISTING) — FastAPI :8888, data feeds, API endpoints
├── agents/daemon.py (NEW) — Autonomous agent orchestrator
│   ├── Sentinel Worker — on-chain scanning every 30min
│   ├── Analyst Worker — scoring + research every 2h
│   └── Trader Worker — setups + learning every 1h
├── launchd plists — auto-start both on boot, restart on crash
│
└──→ Firebase Realtime DB ←── fund-hq.html (reads, no changes needed)
```

**Key decision:** Separate daemon process (not extending server.py). Server stays lightweight for HTTP/data; daemon handles long-running Claude API work. Both share Firebase as communication bus + `services/` modules.

## Files to Create

| File | Purpose |
|------|---------|
| `agents/daemon.py` | Orchestrator — runs 3 workers, heartbeat, error handling, cost tracking |
| `agents/workers/__init__.py` | Package init |
| `agents/workers/sentinel_worker.py` | Autonomous on-chain: whale scanning, funding extremes, OI changes, signal generation |
| `agents/workers/analyst_worker.py` | Autonomous research: score refresh, score-shift detection, auto-discovery, research briefs |
| `agents/workers/trader_worker.py` | Autonomous trading: setup scanning, outcome tracking, calibration triggers |
| `agents/shared/claude_client.py` | Shared Claude Haiku caller — rate limiting, cost tracking, prompt injection of memories |
| `agents/shared/queue.py` | Work queue — deduplication, cooldowns, priority levels |
| `agents/shared/memory.py` | Agent memory CRUD — learnings, mistakes, evolved thresholds (Firebase-backed) |
| `~/Library/LaunchAgents/com.fundhq.daemon.plist` | macOS auto-start for daemon |
| `~/Library/LaunchAgents/com.fundhq.server.plist` | macOS auto-start for server |

## Files to Modify

| File | Change |
|------|--------|
| `agents/services/quant_models.py` | `MultiFactorScorer` loads calibrated weights from Firebase if available |
| `agents/services/learning.py` | Add `load_calibrated_weights()` method |
| `agents/services/autonomy.py` | Load evolved thresholds from agent memory |
| `agents/shared/config.py` | Add daemon config (cycle intervals, cost limits, thresholds) |
| `fund-hq.html` | Dashboard: agent status widget (reads `/fundHQ/agentStatus`) — heartbeat, worker status, cost |

## Worker Designs

### Sentinel Worker (every 30min)
1. Read prices from Firebase → check for anomalies (>15% spike, volume >3x MCap)
2. Scan Hyperliquid whale positions for watched coins
3. Monitor funding rate extremes (>0.05% or deeply negative)
4. Check OI changes (>20% in 24h)
5. **If trigger fires:** Call Claude Haiku for 1-paragraph signal assessment
6. Write signal to `/fundHQ/signals/{id}` + alert to `/fundHQ/alerts/{id}`

### Analyst Worker (every 2h)
1. Read watchlist from Firebase
2. Pull fresh CoinGecko + DefiLlama data per asset
3. Run `MultiFactorScorer.score_asset()` with latest data
4. Compare new vs previous score — detect shifts > 0.5
5. **If score shift:** Call Claude Haiku for research brief (why did score change?)
6. Every 6h: run `AutoDiscovery.run_full_scan()` for new opportunities
7. Write scores to `/fundHQ/watchlist/{id}/autoScore`, discoveries to `/fundHQ/discoveries`

### Trader Worker (every 1h)
1. Read active setups — check stop/target proximity against current prices
2. Check for newly closed trades → run `TradeFeedback.analyze_performance()`
3. Run `ScoreCalibrator.calibrate()` when 5+ new closed trades since last run
4. Scan for setup opportunities: watchlist score > 3.5 + active catalyst
5. **If setup found:** Call Claude Haiku to draft entry/stop/targets
6. Track open signal outcomes (close after 7 days, record result)
7. Write to `/fundHQ/setups`, `/fundHQ/performance`, `/fundHQ/agentMemory/trader/`

## Learning & Evolution

### Score Calibration (exists — wire in)
- `ScoreCalibrator` already computes which factors predict winners
- Trader worker triggers calibration after 5 new closed trades
- `MultiFactorScorer` loads calibrated weights from `/fundHQ/calibration` instead of hardcoded defaults

### Agent Memory (new — Firebase-backed)
```
/fundHQ/agentMemory/{agent}/
  learnings/    — validated insights (e.g., "negative SOL funding preceded 15%+ rallies 3/4 times")
  mistakes/     — failed signals with post-mortem
  thresholds/   — evolved trigger values (Sentinel adjusts spike % per coin type)
  stats/        — running accuracy metrics
```
Last 10 learnings injected into each Claude Haiku system prompt per cycle.

### Threshold Evolution
- Start with hardcoded triggers (15% price spike, 3x volume)
- After 20+ signal outcomes: adjust thresholds based on accuracy
- If 80%+ accuracy → lower threshold (catch more); if <50% → raise it (reduce noise)
- Store in `/fundHQ/agentMemory/{agent}/thresholds`

### Signal Outcome Tracking
Every signal gets: `price_at_signal`, `prediction`, `outcome` (filled after 7 days), `correct` boolean. This is the primary feedback loop.

## Firebase New Paths

```
/fundHQ/
  agentStatus/         — heartbeat + worker status (Dashboard reads this)
  agentMemory/         — long-term learnings per agent
  agentLog/            — last 500 actions (auto-pruned)
  agentCosts/          — daily/monthly API spend tracking
  discoveries/         — auto-discovered opportunities
```

## Cost Estimate

| Agent | Calls/Day | Cost/Day | Cost/Month |
|-------|-----------|----------|------------|
| Sentinel | 6-12 | $0.06 | $1.80 |
| Analyst | 8-15 | $0.08 | $2.40 |
| Trader | 4-8 | $0.04 | $1.20 |
| Existing scheduled tasks | 4-5 | $0.03 | $0.90 |
| **Total** | **22-40** | **~$0.21** | **~$6.30** |

Claude Haiku at ~$0.005/query. Even 3x activity during volatile markets stays under $20/month.

## Reliability

- **launchd** auto-starts both processes on boot, restarts on crash (`KeepAlive: true`)
- **Heartbeat** every 5min to `/fundHQ/agentStatus` — frontend shows agent online/offline
- **Error budget:** 5 consecutive failures → double cycle interval, push warning alert, reset on success
- **Graceful degradation:** Claude API down → skip AI steps, still run scoring; Firebase down → queue writes in memory; Mac Mini reboots → launchd restarts, resume from Firebase state
- **Log rotation:** stdout/stderr to `~/logs/fundhq-daemon.log`, rotated weekly

## Rollout Phases

### Phase A: Foundation (daemon + shared modules)
- `shared/claude_client.py`, `shared/queue.py`, `shared/memory.py`
- `daemon.py` — basic orchestrator with heartbeat loop
- Test: daemon starts, writes heartbeat, survives kill + restart

### Phase B: Sentinel Autonomy
- `workers/sentinel_worker.py` — whale scanning, funding, OI, signal generation
- Test: signals appear in Firebase Alerts page automatically

### Phase C: Analyst Autonomy
- `workers/analyst_worker.py` — score refresh, discovery, research briefs
- Test: watchlist scores update, discoveries appear

### Phase D: Trader Autonomy + Learning
- `workers/trader_worker.py` — outcome tracking, setups, calibration
- Wire calibrated weights into MultiFactorScorer
- Test: closed trades trigger recalibration, evolved weights used

### Phase E: Frontend + Production
- Dashboard agent status widget
- launchd plists for auto-start
- Log rotation, cost tracking display
- 48h monitoring period

## Verification
1. Start daemon: `python3 agents/daemon.py` — confirm heartbeat in Firebase
2. Check `/fundHQ/agentStatus` shows all 3 workers with last_run timestamps
3. Wait 30min — Sentinel should have run, check `/fundHQ/agentLog` for entries
4. Kill daemon, confirm launchd restarts it within 10s
5. Check Dashboard shows agent status widget with green/red indicators
6. After 24h: verify `/fundHQ/agentCosts/daily/{date}` shows reasonable spend
7. After 7 days: check `/fundHQ/agentMemory/sentinel/stats` for signal accuracy tracking
