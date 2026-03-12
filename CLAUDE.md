# Fund HQ

Central dashboard for fund management — projects, reports, tasks, roadmap, live market data.

## Stack
- **Frontend:** `fund-hq.html` (single file, ~195KB)
- **Database:** Firebase Realtime Database + localStorage fallback
- **Hosting:** GitHub Pages (free) — `jumparo1.github.io/JumpTools/fund-hq.html`
- **Users:** Jumparo (crypto) & Tihomir (equities)
- **Assistant:** "Pamela" chat bot for navigation, search, CRUD, price lookup
- **APIs:** CoinGecko (crypto, free), Financial Modeling Prep (stocks, free key, `/stable/` endpoints), DefiLlama (TVL), Anthropic Claude (AI research)

## Status
- [x] Project dump (quick capture)
- [x] Reports (stock + crypto analysis templates)
- [x] Task management (Kanban + Roadmap)
- [x] Chat assistant "Pamela"
- [x] Firebase real-time sync
- [x] Market Data page — live crypto/stock fundamentals
- [x] Watchlist with Firebase sync
- [x] Create reports pre-filled with market data
- [x] Stock support via FMP API (stable endpoints, key in Settings)
- [x] Pamela commands: price lookup, watchlist add
- [x] AI-powered crypto research (Claude API, model selector: Haiku/Sonnet/Opus)
- [x] "Research with AI" button in report modal — full 18-section report generation
- [x] Pamela command: "research {coin}" for instant AI reports
- [x] 3-action search results: + Watch, + Dump, AI Report
- [x] Settings: Save buttons for API keys, autocomplete=off to prevent browser autofill
- [x] Logo click refreshes page
- [x] Migrated from Netlify to GitHub Pages (free, no bandwidth limits)
- [x] Hybrid fundamental scoring system (5-star quant + AI overlay)
- [x] Research workspace — clickable templates open section-by-section editor
- [x] 3 research templates: Crypto (18 sections), Stock (10), Quick Thesis (5)
- [x] Per-section AI research — run individual or all sections with Claude
- [x] Section prompts, bullet guides, progress tracking, enable/disable toggles
- [x] Live market data + score card in workspace header (auto-fetched)
- [x] Export workspace to report (Save as Report button)
- [x] Template View mode — read-only preview with expandable sections
- [x] Template Edit mode — modify titles, prompts, bullets; add/remove/reorder sections
- [x] Custom template persistence (localStorage) with Reset to Default
- [x] Help page — visual 5-step research pipeline, detail cards, quick reference
- [x] Redesigned Dashboard — watchlist, reports, tasks, projects at a glance + quick actions
- [x] Dedicated Watchlist page (under Pipeline) — separated from Market Data
- [x] Market Data = search/discovery, Watchlist = tracked assets with detail view
- [x] Progress page (under Roadmap) — daily work log with timeline, stats, streak tracking
- [x] Web search integration — AI research pulls live web data and cites sources
- [x] Pamela upgraded to AI agent — Claude tool_use with 13 tools, multi-turn loop, natural language

## Deploy
- **Live URL:** https://jumparo1.github.io/JumpTools/fund-hq.html
- **GitHub repo:** `jumparo1/FundHQ` (source) + `jumparo1/JumpTools` (deploy/Pages)
- **Deploy flow:** Copy `fund-hq.html` to `~/deploy/`, commit & push to `jumparo1/JumpTools`
- GitHub Pages auto-builds from `main` branch (takes ~30s)
- API keys stored in browser localStorage (per-domain, need re-entry if domain changes)

## Recent Changes
- 2026-03-12: Pamela upgraded from regex chat bot to AI agent — Claude tool_use with multi-turn loop (max 8 turns)
- 2026-03-12: 13 Pamela tools: search_crypto, get_crypto_data, search_stocks, get_stock_data, create_item, update_item, delete_item, find_items, search_all, add_to_watchlist, get_watchlist, navigate_to_page, get_fund_stats
- 2026-03-12: Pamela system prompt focused on asymmetric opportunity hunting (5-lens framework)
- 2026-03-12: Pamela now handles natural language, comparisons ("compare ETH vs SOL"), chained actions, web search
- 2026-03-12: Removed ~480 lines of regex router (chatProcess), kept helper functions as tool execution layer
- 2026-03-12: Web search integration — AI research now searches the web for recent news/data and cites sources (Anthropic web_search tool)
- 2026-03-12: Web Search toggle in research workspace (off by default, always on for Pamela "research X")
- 2026-03-12: Sections show "AI+Web" badge when generated with web search
- 2026-03-12: Pamela research reports auto-include SOURCES section with cited URLs
- 2026-03-11: Progress page (Roadmap section) — daily work log, timeline grouped by date, stats (items/days/streak), Firebase sync
- 2026-03-11: Dedicated Watchlist page (Pipeline section) — search, add, track assets with detail view, scores, refresh
- 2026-03-11: Market Data simplified to search/discovery only, Watchlist is now its own page
- 2026-03-11: Redesigned Dashboard — stats (watchlist/reports/tasks/projects), quick actions, top watchlist, recent reports, open tasks, recent projects
- 2026-03-11: Template View mode (read-only preview) and Edit mode (modify titles, prompts, bullets, add/remove/reorder sections)
- 2026-03-11: Custom template edits saved to localStorage with getTemplateDef() merge layer
- 2026-03-11: Help page with visual 5-step pipeline flow and quick reference
- 2026-03-11: Research workspace — templates are now clickable, open section-by-section editor with prompts, bullets, AI per-section
- 2026-03-11: 3 templates: Crypto Research (18 sections), Stock Research (10), Quick Thesis (5)
- 2026-03-11: Per-section AI: run Claude on individual sections or "Run All with AI" / "Fill Empty Only"
- 2026-03-11: Workspace auto-fetches live market data + shows score card (quant scoring) in header
- 2026-03-11: Export workspace sections as a formatted report (Save as Report)
- 2026-03-11: Hybrid fundamental scoring: 5-star rating (crypto: momentum/liquidity/value/position/recovery, stock: valuation/profitability/health/momentum/yield)
- 2026-03-11: Score stars on watchlist cards and market detail view
- 2026-03-11: AI score overlay (±0.5★) from research reports via SCORE_JSON parsing
- 2026-03-11: Migrated hosting from Netlify to GitHub Pages (hit Netlify bandwidth limit)
- 2026-03-11: Simplified UI — removed Deal Flow and Research Notes from sidebar
- 2026-03-11: 3-action search results: + Watch (watchlist), + Dump (project dump), AI Report
- 2026-03-11: Fixed FMP stable API field mapping (marketCap vs mktCap, fallback field names)
- 2026-03-11: Fixed crash: null-safe badge updates after removing nav items
- 2026-03-11: Settings: explicit Save Key buttons, autocomplete=off to prevent autofill
- 2026-03-11: Fixed FMP search endpoint (`/stable/search-symbol` not `/stable/search`)
- 2026-03-11: Added AI crypto research via Claude API (direct browser access, key in Settings)
- 2026-03-11: Model selector (Haiku/Sonnet/Opus) in report editor
- 2026-03-11: Added Market Data page with live fundamentals (CoinGecko + FMP + DefiLlama)
- 2026-03-11: Added watchlist, Pamela commands, in-memory cache
- 2026-02-27: Added SKILL.md, pushed to GitHub

## Next Steps
- Historical data tracking (daily snapshots in Firebase, sparkline charts)
- Scheduled auto-refresh for watchlist
- Alert rules on metric thresholds (browser Notification API)
- Macro dashboard (Fear & Greed, BTC dominance, DXY, VIX)
- Portfolio tracker with live P&L
- Enhance Pamela with more commands

## How to Run
```bash
cd JumpTools/FundHQ
python3 -m http.server 8080
# Open http://localhost:8080/fund-hq.html
```
