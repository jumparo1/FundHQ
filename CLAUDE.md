# Fund HQ

Central dashboard for fund management — deals, research, tasks, roadmap, live market data.

## Stack
- **Frontend:** `fund-hq.html` (single file, ~195KB)
- **Database:** Firebase Realtime Database + localStorage fallback
- **Users:** Jumparo (crypto) & Tihomir (equities)
- **Assistant:** "Pamela" chat bot for navigation, search, CRUD, price lookup
- **APIs:** CoinGecko (crypto, free), Financial Modeling Prep (stocks, free key), DefiLlama (TVL), Anthropic Claude (AI research)

## Status
- [x] Deal flow pipeline (Kanban: Sourcing → Closed/Passed)
- [x] Project dump (quick capture)
- [x] Research notes (structured DD templates)
- [x] Reports (stock + crypto analysis templates)
- [x] Task management (Kanban + Roadmap)
- [x] Chat assistant "Pamela"
- [x] Firebase real-time sync
- [x] Deployed to Netlify
- [x] Market Data page — live crypto/stock fundamentals
- [x] Watchlist with Firebase sync
- [x] Auto-fill research notes with live data
- [x] Create reports pre-filled with market data
- [x] Stock support via FMP API (key in Settings)
- [x] Pamela commands: price lookup, watchlist add
- [x] AI-powered crypto research (Claude API, model selector: Haiku/Sonnet/Opus)
- [x] "Research with AI" button in report modal — full 18-section report generation
- [x] Pamela command: "research {coin}" for instant AI reports

## Recent Changes
- 2026-03-11: Added AI crypto research via Claude API (direct browser access, key in Settings)
- 2026-03-11: Model selector (Haiku/Sonnet/Opus) in report editor for cost/quality tradeoff
- 2026-03-11: "Research with AI" button generates full 18-section report with live CoinGecko data
- 2026-03-11: Pamela "research solana" command creates AI report automatically
- 2026-03-11: Added Market Data page with live fundamentals (CoinGecko + FMP + DefiLlama)
- 2026-03-11: Added watchlist (add/remove/refresh, Firebase synced, offline fallback)
- 2026-03-11: Added auto-fill for Research Notes (fetches live data into empty fields)
- 2026-03-11: Added "Create Report" from market detail (pre-fills template with live data)
- 2026-03-11: Added FMP API key management in Settings (stocks require free key)
- 2026-03-11: Added Pamela commands: "price bitcoin", "watch ethereum"
- 2026-03-11: In-memory cache with 5-min TTL to avoid API rate limits
- 2026-02-27: Added SKILL.md, pushed to GitHub

## Next Steps
- Historical data tracking (daily snapshots in Firebase, sparkline charts)
- Scheduled auto-refresh for watchlist
- Alert rules on metric thresholds (browser Notification API)
- Macro dashboard (Fear & Greed, BTC dominance, DXY, VIX)
- Portfolio tracker with live P&L
- Add portfolio analytics
- Enhance Pamela with more commands

## How to Run
```bash
cd JumpTools/FundHQ
python3 -m http.server 8080
# Open http://localhost:8080/fund-hq.html
```
