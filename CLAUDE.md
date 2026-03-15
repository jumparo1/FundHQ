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

## Pages
| Page | Section | Description |
|------|---------|-------------|
| Dashboard | Overview | Stats, quick actions, watchlist, reports, tasks, projects at a glance |
| About | Overview | Mission, operating principles, scale trajectory |
| Project Dump | Pipeline | Quick capture for project ideas |
| Watchlist | Pipeline | Tracked assets with scores, detail view, Firebase sync |
| Alerts | Pipeline | Signals from scheduled scans + Pamela, severity levels, browser notifications |
| Templates | Research | 3 templates (Crypto 18s, Stock 10s, Quick Thesis 5s), view/edit modes |
| Reports | Research | AI-generated research reports, rating, conviction |
| Market Data | Market | Live search/discovery, CoinGecko + FMP fundamentals |
| Hyperliquid | Market | On-chain whale tracker — wallet scanner, whale discovery, saved wallets, perp positioning |
| Tasks | Management | Kanban board with milestones, priority, assignee |
| Roadmap | Management | Tasks grouped by milestone with progress bars |
| Progress | Management | Daily work log, timeline, streak tracking |
| Help | Tools | Visual 5-step research pipeline guide |
| Settings | Tools | API keys, Firebase config |

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
- 2026-03-15: Perp Positioning tab — aggregate OI, funding rates, volume, premium across 190 perps (Crypto + XYZ dex)
- 2026-03-15: Hyperliquid page — on-chain whale tracker with 4 tabs (Wallet Scanner, Whale Discovery, Saved Wallets, Perp Positioning)
- 2026-03-15: Wallet Scanner — paste any 0x address, see account value, positions, PnL, win rate, trade history
- 2026-03-15: Whale Discovery — scans top coins via Hyperliquid API, finds $500K+ positions, sortable by size/PnL/leverage
- 2026-03-15: Saved Wallets — label & track wallets with live position updates, Firebase sync
- 2026-03-15: Python agent (`agents/hyperliquid/agent.py`) — wallet profiling, whale discovery, WebSocket monitoring, Firebase alerts
- 2026-03-15: Firebase sync — saved wallets + discovered whales shared between frontend and Python agent
- 2026-03-15: Pamela Hyperliquid tools (20 total) — hl_scan_wallet, hl_whale_positions, hl_saved_wallets
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
