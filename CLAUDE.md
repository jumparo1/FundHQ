# Fund HQ

AI-powered fundamental research engine — discovers asymmetric opportunities in crypto and equities before the market prices them in.

## Stack
- **Frontend:** `fund-hq.html` (single file, vanilla JS, dark theme)
- **Database:** Firebase Realtime Database + localStorage fallback
- **Hosting:** GitHub Pages (free) — `jumparo1.github.io/JumpTools/fund-hq.html`
- **AI Agent:** "Pamela" — Claude Haiku via tool_use API, 17 tools, multi-turn loop (max 8 turns)
- **Scheduled Tasks:** 3 Claude Code cron jobs writing alerts via Firebase REST API
- **APIs:** CoinGecko (crypto), FMP `/stable/` (stocks), DefiLlama (TVL), Anthropic Claude (AI research + web search)
- **Knowledge Base:** 4 SKILL.md files (MISSION, TRADING-EDGE, ASYMMETRIC-SETUPS, FUNDAMENTAL-ANALYSIS)
- **Users:** Jumparo (crypto) & Tihomir (equities)

## Architecture — 3 Research Divisions
| Division | Agent | Mission |
|----------|-------|---------|
| **On-Chain Intel** | Sentinel | Smart money tracking, flow analysis, venue intelligence |
| **Research** | Analyst | Fundamental deep dives, tokenomics, catalysts, valuation |
| **Technical** | Quant | Market regime, setups, playbooks, confluence scoring |

## Pages
| Page | Section | Description |
|------|---------|-------------|
| Dashboard | Overview | Stats, quick actions, watchlist, reports, tasks, projects at a glance |
| About | Overview | Mission, operating principles, scale trajectory |
| Project Dump | Pipeline | Quick capture for project ideas |
| Watchlist | Pipeline | Tracked assets with scores, detail view, Firebase sync |
| Alerts | Pipeline | Signals from scheduled scans + Pamela, severity levels, browser notifications |
| Portfolio | Pipeline | Holdings tracker, allocation breakdown, P&L tracking, cash management |
| On-Chain Intel | On-Chain | 7 tabs: Overview, Token Intel (multi-source scanner with wallet detail modals), Hyperliquid, Entity Tracker, Dexscreener, Flow Monitor, Signal Feed |
| Market Data | Research | Live search/discovery, CoinGecko + FMP fundamentals |
| Templates | Research | 4 templates (Crypto 16s, Stock 14s, Quick Thesis 5s, Commodity 12s), view/edit modes |
| Reports | Research | AI-generated research reports, rating, conviction, Substack, Trash |
| Catalysts | Research | Event tracking (8 types), impact/time filters, summary cards, Firebase sync |
| Technical | Technical | 5 tabs: Market Regime, Setup Scanner, Playbooks, Confluence, Trade Log |
| Tasks | Operations | Kanban board with milestones, priority, assignee |
| Roadmap | Operations | Tasks grouped by milestone with progress bars |
| Progress | Operations | Daily work log, timeline, streak tracking |
| Docs | Tools | GitBook-style documentation with changelog |
| Settings | Tools | API status grid, keys by category (AI/Research/On-Chain), Firebase sync, backup |

## Pamela (AI Agent)
- **Model:** Claude Haiku 4.5 (fast + cheap, ~$0.005/query)
- **20 tools:** search_crypto, get_crypto_data, search_stocks, get_stock_data, create_item, update_item, delete_item, find_items, search_all, add_to_watchlist, get_watchlist, navigate_to_page, get_fund_stats, save_research, get_reports, get_report_content, create_alert, hl_scan_wallet, hl_whale_positions, hl_saved_wallets + web_search
- **System prompt:** 5-lens filter scoring, setup archetypes, anti-patterns, position sizing, live context injection (watchlist prices, recent reports, open tasks, unread alerts)
- **Multi-turn:** Up to 8 tool-use turns per conversation

## Scheduled Tasks (Claude Code)
| Task | Schedule | What it does |
|------|----------|--------------|
| daily-market-scan | 8am weekdays | Top movers, unusual volume, narrative shifts, asymmetric setups |
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

## Roadmap (in Fund HQ Tasks/Roadmap)
- **Phase 0: Prototype** — COMPLETE
- **Phase 1: Data Infrastructure** — Python backend, real data feeds, on-chain analytics, macro
- **Phase 2: Quantitative Models** — Financial statements, DCF, multi-factor scoring, auto-discovery
- **Phase 3: Risk Framework** — VaR, correlations, liquidity, counterparty, portfolio construction
- **Phase 4: Learning & Edge** — Feedback loop, score calibration, backtesting integration
- **Phase 5: Full Autonomy** — Unprompted research, portfolio-aware alerts, multi-user, API platform

## How to Run
```bash
cd JumpTools/FundHQ
python3 -m http.server 8080
# Open http://localhost:8080/fund-hq.html
```
