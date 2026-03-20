# Fund HQ

AI-powered Conviction Engine for asymmetric trades — 5 AI agents discover, research, score, and execute high-conviction opportunities in crypto and equities.

## Stack
- **Frontend:** `fund-hq.html` (single file, vanilla JS, dark theme)
- **Backend:** `agents/server.py` — FastAPI server (port 8888) with 5 phases of trading infrastructure
- **Database:** Firebase Realtime Database + localStorage fallback
- **Hosting:** GitHub Pages (free) — `jumparo1.github.io/JumpTools/fund-hq.html`
- **AI Agents:** 5-agent system via Claude Haiku tool_use API, 8-turn multi-tool loop, intent-based routing
- **Scheduled Tasks:** 4 Claude Code scheduled tasks writing alerts via Firebase REST API
- **APIs:** CoinGecko (crypto), FMP `/stable/` (stocks), Arkham Intelligence (wallet identity/labels), Moralis (EVM holders), Dexscreener (DEX pairs), Hyperliquid (perps/whales), Anthropic Claude (AI research + web search), DefiLlama (TVL + raises), Binance Futures (funding + OI), Alternative.me (Fear & Greed)
- **Knowledge Base:** 10 SKILL.md files in `.claude/skills/`
- **Users:** Jumparo (crypto) & Tihomir (equities)

## Architecture — 5-Agent Intelligence OS (Live)
| Agent | Icon | Tools | Mission |
|-------|------|-------|---------|
| **Pamela** (Router) | P | 8 shared | Intent classification, delegates to specialists, handles general queries |
| **Analyst** | A | 10 | Fundamental research, 5-lens filter, reports, valuations, peer comparison |
| **Sentinel** | S | 8 | On-chain intelligence, whale tracking, entity profiling, HL + Binance data |
| **Trader** | T | 10 | Trade setups, position sizing, confluence scoring, learning loop from trade log |
| **VC** | V | 6 | Fundraising rounds, investor portfolios, VC trends, 100x gem filtering |

## Pages (Restructured)
| Page | Section | Description |
|------|---------|-------------|
| Dashboard | Command Center | Stats, quick actions, watchlist, reports at a glance |
| Intelligence | Discover | 5 tabs: Overview, Token Intel, Hyperliquid (5 sub-tabs incl. Wallet Hunter), Entity Tracker, Dexscreener |
| Market Data | Discover | Live search/discovery, CoinGecko + FMP fundamentals |
| Watchlist | Research | Tracked assets with scores, detail view, Firebase sync |
| Reports | Research | AI research reports + Templates tab (4 templates built in), Substack, Trash |
| Catalysts | Research | Event tracking (8 types), impact/time filters, summary cards, Firebase sync |
| Trading | Execute | 5 tabs: Market Regime, Setup Scanner, Playbooks, Confluence, Trade Log |
| Portfolio | Execute | Holdings tracker, allocation breakdown, P&L tracking, cash management |
| Signals & Alerts | Alerts | 3 tabs: Alerts (scheduled scans + Pamela), Signal Feed, Flow Monitor |
| Docs | — | GitBook-style docs + Operations sub-tabs (About, Tasks, Roadmap, Progress) |
| Settings | — | API status grid, keys by category (AI/Research/On-Chain), Firebase sync, backup |

## Agent System
- **Model:** Claude Haiku 4.5 (fast + cheap, ~$0.005/query)
- **Pattern:** Agent Registry — `AGENT_REGISTRY` with shared `runAgent(agentName, message)` runner
- **Routing:** `routedAgent(message)` → Router classifies intent → delegates to specialist
- **Shared tools (8):** create_item, update_item, delete_item, find_items, search_all, navigate_to_page, get_fund_stats, create_alert
- **Analyst tools (10):** search_crypto, get_crypto_data, search_stocks, get_stock_data, add_to_watchlist, get_watchlist, save_research, get_reports, get_report_content, get_conviction
- **Sentinel tools (8):** hl_scan_wallet, hl_whale_positions, hl_saved_wallets, get_entities, get_signals, create_signal, search_crypto, get_crypto_data
- **Trader tools (11):** create_setup, get_setups, update_setup, log_trade, get_trade_log, get_trade_stats, get_confluence, position_size, get_market_regime, search_crypto, get_crypto_data
- **VC tools (6):** get_raises, search_raises, get_investor_portfolio, get_raise_stats, search_crypto, get_crypto_data
- **All agents** also get web_search (Claude built-in, max 3 per conversation)
- **Multi-turn:** Up to 8 tool-use turns per conversation

## Scheduled Tasks (Claude Code)
| Task | Schedule | What it does |
|------|----------|--------------|
| daily-market-scan | 8am weekdays | Top movers, unusual volume, narrative shifts, asymmetric setups |
| vc-feed-scan | 9am daily | Fetch DefiLlama raises, update Firebase vcFeed |
| watchlist-refresh | 8pm daily | Price changes, score shifts, breakout/breakdown signals |
| weekly-deep-dive | Sunday 10am | Sector rotation, new narratives, top 3 opportunities with full scoring |

All write alerts to Firebase via REST API → appear in Fund HQ Alerts page in real-time.

## Scoring System
- **Crypto:** momentum / liquidity / value / position / recovery (5 stars)
- **Stock:** valuation / profitability / health / momentum / yield (5 stars)
- **AI overlay:** ±0.5★ from research report analysis (SCORE_JSON parsing)
- **5-Lens Filter:** Catalyst / Valuation / Momentum / Risk:Reward / Narrative (each 1-5, total /25)

## Deploy
- **Live URL:** https://jumparo1.github.io/JumpTools/fund-hq.html
- **Source repo:** `jumparo1/FundHQ` (public)
- **Deploy repo:** `jumparo1/JumpTools` (GitHub Pages on `main`)
- **Deploy flow:** `cp fund-hq.html ~/deploy/ && cd ~/deploy && git add . && git commit && git push`
- GitHub Pages auto-builds in ~30s
- API keys stored in browser localStorage (per-domain)

## Recent Changes
- 2026-03-20: **Report table UI upgrade** — `renderTable()` rewritten with rounded card borders, accent-colored headers, color-coded scores (green 8-10, purple 6-7, amber 4-5, red 1-3), Yes/No coloring, +/- percentage colors, bold TOTAL rows with accent highlight, hover effects, alternating row backgrounds. All report tables (scoreboard, non-crypto comparison, peer comparison) now render as styled HTML tables. Reports converted from space-aligned to pipe-delimited format. Substack TOC added.
- 2026-03-20: **Data-driven research template** — Added Valuation Scoreboard (10-dimension 1-10 scoring vs 3 crypto peers, total /100), Non-Crypto Comparison (project FDV as % of TradFi/Web2 giants like NVIDIA $4.4T, OpenAI $850B, Anthropic $380B), and strict data-driven rules (every claim needs API data, honest conviction ratings, BULLISH/BEARISH signal lists). Substack template updated with scoreboard + on-chain sections.
- 2026-03-20: **FET deep data analysis** — Binance Futures 14-day taker flow (Buy $1.53B vs Sell $1.56B = net -$29M), 30-day OI history (+9.1%), top trader L/S ratio 30d trend (LONG→NEUTRAL→recovering), spot volume profile (6 net-buy days Mar 10-16, then profit-taking). Whale accumulation rated honestly at 6.5/10 with explicit bullish/bearish signal lists. Perp positioning section added to both reports.
- 2026-03-20: **Valuation Scoreboard** — FET 82/100 vs TAO 70 vs RENDER 65 vs AKT 65 across 10 dimensions. Non-crypto comparison: FET at 0.06% of OpenAI, 0.01% of NVIDIA. "If decentralized AI captures 0.1% of $700B hyperscaler capex = $700M revenue vs $20B crypto AI sector MCap." Added to both main and Substack reports.
- 2026-03-20: **Report timestamps** — `fmtDate()` now shows hours:minutes alongside date across all report cards and alerts. Deployed to GitHub Pages.
- 2026-03-20: **FUNDAMENTAL-ANALYSIS.md upgraded** — Updated crypto research playbook with backend valuation engine (DCF, revenue multiples), multi-factor scorer (5 dimensions), position sizer, auto-discovery, score calibration. Added 5 new report sections: Backend Valuation Model, Entity Intelligence, Position Sizing + Asymmetric Case, Risk Assessment, Backend Multi-Factor Score.
- 2026-03-20: **FET/ASI research report** — Comprehensive 17-section report saved to Firebase (`rpt_fet_1773996921`). Rating: Buy, Conviction: High, Score: 8/10. Includes valuation scoreboard, non-crypto comparison, deep whale analysis (6.5/10), perp positioning, social sentiment.
- 2026-03-20: **FET Substack article** — 15-section newsletter version (`rpt_fet_sub_1773997203`). Clean copy-paste format with scoreboard, whale verdict, perp data. In Substack tab.
- 2026-03-20: **24/7 Agent System planned** — Architecture designed for autonomous Mac Mini agents (`PLAN-24-7-AGENTS.md`). Daemon process with 3 workers (Sentinel/Analyst/Trader), agent memory, learning loops, threshold evolution, launchd auto-start. ~$6/month Claude Haiku cost.
- 2026-03-20: **Frontend ↔ Backend Integration** — Full wiring of all 5 backend phases into the frontend. Backend URL config with auto-detection + `backendFetch()`/`backendPost()` helpers. Dashboard: macro intelligence row (Fear & Greed, BTC Dominance, DeFi TVL, backend status), auto-discovery widget. Portfolio: Risk Dashboard (VaR, correlation matrix, per-position risk), Position Sizer (capital/risk/entry/stop → size + R-multiples, works offline too). Trading: Performance tab with win rate, profit factor, expectancy, by-setup breakdown, score calibration runner — includes local fallback from trade log. Alerts: Smart Alerts tab (stop proximity, target proximity, concentration, drawdown). Market Data: Auto-Discovery Scanner (deep value coins + undervalued DeFi from CoinGecko/DeFiLlama). Watchlist detail: Valuation button (DCF + revenue multiple + composite verdict) and Multi-Factor Score button (5 dimensions, grade A-F, signal). Settings: Backend Server section with URL config + test. API status grid includes backend status. All features gracefully degrade when backend is offline.
- 2026-03-19: **Phases 1-5 Backend Complete** — FastAPI server (`agents/server.py`, port 8888) with all 5 roadmap phases implemented. Phase 1: real-time data feeds (CoinGecko, Binance, DeFiLlama, Fear & Greed, HL) with auto-refresh. Phase 2: crypto valuation engine (DCF, revenue multiples, TVL), multi-factor scorer (5 dimensions), auto-discovery scanner. Phase 3: historical VaR, correlation matrix, liquidity scoring, portfolio optimizer, position sizer. Phase 4: trade feedback loop (win rate, profit factor, by-setup analysis), score calibration, backtest bridge. Phase 5: autonomous research triggers, portfolio-aware smart alerts, external API platform. 4 background loops: prices (2min), full data (10min), smart alerts (5min), auto-research (15min). All data pushed to Firebase for frontend consumption.
- 2026-03-19: **4th scheduled task** — vc-feed-scan (daily 9am): fetches DefiLlama raises, writes to Firebase vcFeed
- 2026-03-19: **Mac Mini infrastructure setup** — SSH keys, repo clones (FundHQ, Backtesting, TradingJournal, JumpTools deploy), .env API key storage, Claude memory files, launch.json with backend config
- 2026-03-18: **Auto Market Regime** — Live regime detection (Risk-On/Neutral/Risk-Off) from 5 indicators: BTC funding rate (Hyperliquid), OI trend 48h (Binance), BTC dominance (CoinGecko), Fear & Greed index (alternative.me), BTC vs 200D SMA (CoinGecko). Each indicator votes +1/0/-1, sum determines regime. 5 indicator cards with status badges. Refresh button with 5-min cache. `get_market_regime` Trader agent tool. Auto-populates `ta-btc-regime` for `computeTraderScore()` and confluence scoring. Loads on page init + regime tab switch.
- 2026-03-17: **VC Due Diligence template** — 18-section professional template: executive summary, deal terms & cap table, team, problem & market, product & tech, traction, tokenomics, competitive analysis, backers, GTM, roadmap, risk assessment (6 dimensions /30), legal, return modeling (scenario table), 100x filter (/25), DD checklist (10 items), investment verdict. Raw text format + structured workspace format.
- 2026-03-17: **VC Watchlist page** — Track fundraising rounds with intelligence sources (CryptoRank VCs, DefiLlama Raises, CryptoRank Rounds, RootData + custom). Stats cards (tracked, total raised, Tier 1, 100x). Filters by round/category/status. Status tracking (watching/researching/invested/passed). 18 raises pre-loaded. track_raise + get_vc_watchlist agent tools.
- 2026-03-17: **Sidebar restructured by agent** — 4 agent sections (Sentinel, Analyst, Trader, VC) with colored badges. Dashboard at top, Docs + Settings at bottom. Alerts section separate.
- 2026-03-17: **Trader agent** — 10 tools: create_setup, get_setups, update_setup, log_trade, get_trade_log, get_trade_stats, get_confluence, position_size. Dynamic learning loop injects win rate + playbook stats into system prompt. 7 playbook archetypes.
- 2026-03-17: **VC/Fundraising agent** — 8 tools: get_raises, search_raises, get_investor_portfolio, get_raise_stats, track_raise, get_vc_watchlist. DefiLlama raises API with Firebase cache + web_search fallback (CORS/paywall workaround). Investor tier system (Tier 1-3). 100x gem filter.
- 2026-03-17: **5-agent system complete** — Router routes to analyst, sentinel, trader, VC. Colored agent badges in chat. Each agent has dedicated system prompt with domain expertise.
- 2026-03-17: **Stage 4: Agentify** — Agent Registry pattern with `runAgent(agentName, message)`. Router (Pamela) classifies intent and delegates to Analyst or Sentinel. Analyst agent: fundamental research with 5-lens filter, crypto income statement, report template (10 tools). Sentinel agent: on-chain intelligence with Senpi learnings, signal hierarchy, wallet scoring (8 tools). New tools: get_entities, get_signals, create_signal, get_conviction. Agent badge on chat responses. Saved Wallets / Entity Tracker separation with name prompt on save and Promote to Entity flow. Source tags on entities.
- 2026-03-17: **Stage 3: Modularize** — 22 CRUD helper functions (dbGet/dbFind/dbAdd/dbUpdate/dbRemove/dbSync + entity/signal/watchlist/report/trade/setup helpers). Unified Conviction Engine: Investor Score (/100, 5 factors) + Trader Score (/100, 5 factors) replacing 5 disconnected scoring systems. Entity auto-sync from HL wallet saves. Conviction badge on watchlist cards.
- 2026-03-17: **Stage 2: Simplify (Intelligence OS restructure)** — sidebar reorganized: Command Center / Discover / Research / Execute / Alerts. Pages reduced from 17 to 11. Templates merged into Reports as tab. Signal Feed + Flow Monitor merged into Signals & Alerts page. About, Tasks, Roadmap, Progress moved under Docs as sub-tabs. Legacy URL redirects for all moved pages.
- 2026-03-17: **500-wallet Token Intel scan** — expanded from 30→500 wallets ($10K min), concurrent batches of 5 for speed, coin-specific scoring (filters fills by scanned ticker), coin stats row in results
- 2026-03-17: **Track Entity in Wallet Scanner** — Track Entity button + quality score card (grade, type, trades/day, consistency, leverage) on wallet profile page
- 2026-03-17: **Arkham Intelligence integration** — wallet identity labels on Token Intel whales + entities, Arkham token holders endpoint, Alpha Summary identity insights, Wallet Hunter Arkham enrichment, Settings key + test
- 2026-03-17: **Wallet Hunter** — new HL sub-tab: systematically scans leaderboard, fetches trade history, scores wallets (0-100), auto-classifies (Fund/Insider/MM/Copyable/Degen/Whale), Arkham identity enrichment, bulk import to Entity Tracker
- 2026-03-17: **Whale Quality Scoring** — `whaleScoreWallet()` engine: win rate, PnL consistency, trade frequency, leverage analysis → composite quality score + auto-grade (A+ to C) + auto-type classification
- 2026-03-17: **Token Intel whale scoring** — discovered whales now scored & classified with quality badge, type tag, win rate, trade stats; sorted by quality; one-click Track with auto-grade
- 2026-03-17: **Degen entity type** — 7th entity type added across all selects and displays (orange badge)
- 2026-03-17: **Wallet detail modal** — click any address in Token Intel to see full profile: account value, all positions, win rate, PnL, last 30 trades, + Track Entity button
- 2026-03-17: **Clickable addresses** — HL whale addresses open wallet modal, Moralis holder addresses link to block explorer (Etherscan, Basescan, etc.)
- 2026-03-17: **Settings API section** — reorganized into separate card with status grid (green/gray dots), grouped by category (AI, Research, On-Chain Intelligence), auto-populates saved keys
- 2026-03-17: **Token Intel diagnostics** — Data Sources status bar shows which APIs returned data and which didn't, error tracking on all fetch calls
- 2026-03-17: **Moralis integration** — top token holders on EVM chains (Ethereum, Base, BSC, Polygon), % supply, concentration analysis, whale categories
- 2026-03-17: **Birdeye integration** — top Solana DEX traders (inactive — user focused on EVM for now)
- 2026-03-16: **Dexscreener integration** — search tokens, trending, new pairs; 6th tab in On-Chain Intel, free API
- 2026-03-16: **Auto-confluence scoring** — pulls entity grades, regime, setups, catalysts, reports to pre-fill sliders
- 2026-03-16: **Conviction Report generator** — markdown report with breakdown bars, smart money, catalysts; copy/save to Reports
- 2026-03-16: **Link Setup to Confluence** — pick active setup, auto-fill asset + run auto-score
- 2026-03-16: **Portfolio live pricing** — CoinGecko (60+ crypto symbol mappings) + FMP (stocks) refresh button
- 2026-03-16: **Auto-signal generation** — entity scans + catalyst proximity auto-create Signal Feed entries
- 2026-03-16: **Cross-division intelligence** — entities → signals, catalysts → confluence, setups → reports
- 2026-03-16: **3-Division Architecture** — restructured entire platform into On-Chain Intel, Research, and Technical Analysis
- 2026-03-16: **Portfolio page** — holdings tracker with allocation breakdown, P&L, cash management, visual allocation bar chart
- 2026-03-16: **Signal Feed** — functional on-chain signal aggregation with type/conviction filters, status tracking, win/loss outcome tracking
- 2026-03-16: **Flow Monitor** — aggregate entity flow scanning via HL API, accumulation/distribution detection, net flow by asset, auto-signal generation for $100K+ positions
- 2026-03-16: **Trade Log** — full CRUD trade logging with P&L, R:R calculation, playbook linkage, win rate stats, best playbook mining
- 2026-03-16: **Catalyst Tracker** — event tracking with 8 types, impact/time filters, summary cards (This Week/Month/Positive/Negative), Firebase sync
- 2026-03-16: **Confluence Scoring** — 4 weighted range sliders (On-Chain 25%, Fundamental 25%, TA 30%, Regime 20%), color-coded verdicts, position sizing
- 2026-03-16: **Entity Tracker** — full CRUD entity management, import from HL Saved Wallets, live position scanning, grade/type filtering
- 2026-03-16: **Setup Scanner** — trade setup cards with entry/stop/target, auto R:R, playbook linkage, status cycling (Watching/Active/Triggered/Closed)
- 2026-03-16: **Agent scaffolding** — Sentinel, Analyst, Quant Python agents + ENTITY-INVESTIGATION.md, TRADE-PLAN.md skills
- 2026-03-16: **On-Chain Intel page** — Overview dashboard (regime, entities, signals, venues), Hyperliquid preserved as sub-module
- 2026-03-16: **Technical Analysis page** — Market Regime (risk-on/neutral/risk-off rules), Setup Scanner, Playbooks (3 strategies + Momo Short backlog), Confluence (4-factor scoring), Trade Log
- 2026-03-16: **Sidebar restructured** — On-Chain Intel, Research, Technical, Operations sections (renamed from Management)
- 2026-03-16: **Stock template upgraded** — expanded from 10 to 14 sections with institutional research rigor
- 2026-03-16: **Report Trash** — soft-delete with 30-day retention, restore, permanent delete, auto-purge
- 2026-03-16: **Perp Positioning** — new Hyperliquid tab showing 190 active perps with OI, funding, volume
- 2026-03-16: **Hyperliquid Agent v2** — rewritten with Market Regime, Pattern Detector, Copy-Trade Signals, enhanced scoring
- 2026-03-16: **Logo navigation** — click logo returns to Dashboard
- 2026-03-16: **Docs changelog** — updated with all March 16 changes
- 2026-03-15: Fix login modal bug — was using CSS class `show` instead of `open`, modal never appeared
- 2026-03-15: Oil research report posted to Firebase — 12-section commodity analysis, tactical short thesis, QA'd against live data
- 2026-03-15: Commodity Research template — 12 sections for oil, gold, natgas
- 2026-03-15: Hyperliquid page — wallet scanner, whale discovery, saved wallets, perp positioning
- 2026-03-15: Python agent + Firebase sync + Pamela HL tools (20 total)
- 2026-03-12: About page — Fund HQ mission, operating principles, scale trajectory as own tab under Overview
- 2026-03-12: Full 5-phase roadmap — 35 items across Data Infrastructure, Quant Models, Risk Framework, Learning & Edge, Full Autonomy
- 2026-03-12: Phase 0: Prototype marked complete (8 items)
- 2026-03-12: Alerts page — severity-colored cards (info/warning/opportunity), expand/dismiss, filters, browser notifications
- 2026-03-12: create_alert Pamela tool (17 tools total) — writes alerts to Firebase
- 2026-03-12: Scheduled tasks write alerts via Firebase REST API
- 2026-03-12: Pamela knowledge base — 5-lens filter, setup archetypes, anti-patterns, position sizing, live context injection
- 2026-03-12: Added save_research, get_reports, get_report_content tools
- 2026-03-12: SKILL.md files: MISSION, ASYMMETRIC-SETUPS, TRADING-EDGE
- 2026-03-12: Pamela upgraded from regex bot to Claude tool_use AI agent (17 tools, multi-turn)
- 2026-03-12: Removed ~480 lines dead regex router code
- 2026-03-12: Web search integration — AI research pulls live data + cites sources
- 2026-03-11: Progress page, Watchlist page, Dashboard redesign, Research workspace, Templates, Scoring system
- 2026-03-11: Migrated Netlify → GitHub Pages, AI research, Market Data, FMP stock support
- 2026-02-27: Initial SKILL.md, pushed to GitHub

## Backend Server (Phases 1-5)
FastAPI server at `agents/server.py` — runs on port 8888, pushes data to Firebase.

### Phase 1: Data Infrastructure (COMPLETE)
- `services/data_feeds.py` — Real-time feeds: CoinGecko prices, Binance funding/OI, Fear & Greed, BTC dominance, DeFi TVL, Hyperliquid market data, trending coins
- Auto-updates: prices every 2min, full update every 10min
- Pushes all data to `/fundHQ/marketData` in Firebase

### Phase 2: Quantitative Models (COMPLETE)
- `services/quant_models.py` — DCF valuation, revenue multiple, TVL valuation
- Multi-factor scorer: fundamental / technical / onchain / sentiment / valuation (weighted composite)
- Auto-discovery: scans CoinGecko for deep-value coins, DefiLlama for undervalued DeFi
- Endpoints: `/api/valuation`, `/api/score`, `/api/discovery`

### Phase 3: Risk Framework (COMPLETE)
- `services/risk_engine.py` — Historical VaR (portfolio + per-position)
- Correlation matrix builder (cross-asset)
- Liquidity scoring with position size caps
- Portfolio optimizer: conviction-weighted allocation with risk budgets
- Position sizer: risk-per-trade → exact size + R-multiples
- Endpoints: `/api/risk/var`, `/api/risk/correlation`, `/api/risk/position-size`, `/api/risk/assess`

### Phase 4: Learning & Edge (COMPLETE)
- `services/learning.py` — Trade feedback loop: win rate, profit factor, expectancy, by-setup analysis
- Score calibration: adjusts multi-factor weights based on which factors predicted winners
- Backtest bridge: connects to Backtesting engine, falls back to simple simulation
- Endpoints: `/api/performance`, `/api/calibration`, `/api/backtest/{symbol}/{strategy}`

### Phase 5: Full Autonomy (COMPLETE)
- `services/autonomy.py` — Autonomous research triggers: price spikes, volume surges, recovery signals
- Smart alerts: portfolio-aware (stop proximity, target proximity, concentration, drawdown)
- API platform: external read-only endpoints for bots/dashboards
- Background loops: auto-research every 15min, smart alerts every 5min
- Endpoints: `/api/autonomous/triggers`, `/api/smart-alerts`, `/api/v1/*`

### Backend Endpoints Summary
| Endpoint | Method | Phase | Description |
|----------|--------|-------|-------------|
| `/api/prices` | GET | 1 | All watched coin prices |
| `/api/macro` | GET | 1 | Fear & Greed, BTC dominance, DeFi TVL |
| `/api/feeds/refresh` | POST | 1 | Force data refresh |
| `/api/valuation` | POST | 2 | Full valuation (DCF + multiples) |
| `/api/score` | POST | 2 | Multi-factor asset score |
| `/api/discovery` | GET | 2 | Auto-discovery scan |
| `/api/risk/var` | POST | 3 | Portfolio VaR calculation |
| `/api/risk/correlation` | POST | 3 | Cross-asset correlation matrix |
| `/api/risk/position-size` | POST | 3 | Position size calculator |
| `/api/risk/assess` | POST | 3 | Full risk assessment |
| `/api/performance` | GET | 4 | Trading performance analysis |
| `/api/calibration/run` | POST | 4 | Calibrate scoring weights |
| `/api/backtest/{s}/{t}` | GET | 4 | Run backtest |
| `/api/autonomous/triggers` | GET | 5 | Check auto-research triggers |
| `/api/smart-alerts` | GET | 5 | Portfolio-aware alerts |
| `/api/v1/portfolio` | GET | 5 | External API: portfolio |
| `/api/v1/signals` | GET | 5 | External API: signals |
| `/api/v1/market` | GET | 5 | External API: market data |

## Roadmap
- **Phase 0: Prototype** — COMPLETE
- **Phase 1: Data Infrastructure** — COMPLETE
- **Phase 2: Quantitative Models** — COMPLETE
- **Phase 3: Risk Framework** — COMPLETE
- **Phase 4: Learning & Edge** — COMPLETE
- **Phase 5: Full Autonomy** — COMPLETE
- **Phase 6: 24/7 Autonomous Agents** — NEXT (see `PLAN-24-7-AGENTS.md`)
  - [ ] Phase A: Foundation — daemon.py + shared modules (claude_client, queue, memory)
  - [ ] Phase B: Sentinel Autonomy — whale scanning, funding extremes, signal generation (30min cycle)
  - [ ] Phase C: Analyst Autonomy — score refresh, discovery scans, research briefs (2h cycle)
  - [ ] Phase D: Trader Autonomy + Learning — outcome tracking, setup scanning, calibration (1h cycle)
  - [ ] Phase E: Learning Loop — agent memory injection, threshold evolution, cost tracking
  - [ ] Phase F: Production — launchd auto-start, Dashboard agent status widget, 48h monitoring

## How to Run
```bash
# Frontend (static)
cd JumpTools/FundHQ
python3 -m http.server 8080
# Open http://localhost:8080/fund-hq.html

# Backend (FastAPI — all 5 phases)
cd JumpTools/FundHQ/agents
python3 server.py
# API at http://localhost:8888
# Docs at http://localhost:8888/docs
```
