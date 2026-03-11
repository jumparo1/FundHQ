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

## Deploy
- **Live URL:** https://jumparo1.github.io/JumpTools/fund-hq.html
- **GitHub repo:** `jumparo1/FundHQ` (source) + `jumparo1/JumpTools` (deploy/Pages)
- **Deploy flow:** Copy `fund-hq.html` to `~/deploy/`, commit & push to `jumparo1/JumpTools`
- GitHub Pages auto-builds from `main` branch (takes ~30s)
- API keys stored in browser localStorage (per-domain, need re-entry if domain changes)

## Recent Changes
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
