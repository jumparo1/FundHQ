# Fund HQ

Central dashboard for fund management — deals, research, tasks, roadmap.

## Stack
- **Frontend:** `fund-hq.html` (single file, ~147KB)
- **Database:** Firebase Realtime Database + localStorage fallback
- **Users:** Jumparo (crypto) & Tihomir (equities)
- **Assistant:** "Pamela" chat bot for navigation, search, CRUD

## Status
- [x] Deal flow pipeline (Kanban: Sourcing → Closed/Passed)
- [x] Project dump (quick capture)
- [x] Research notes (structured DD templates)
- [x] Reports (stock + crypto analysis templates)
- [x] Task management (Kanban + Roadmap)
- [x] Chat assistant "Pamela"
- [x] Firebase real-time sync
- [x] Deployed to Netlify

## Recent Changes
- 2026-02-27: Added SKILL.md, pushed to GitHub

## Next Steps
- Add portfolio analytics
- Enhance Pamela with more commands

## How to Run
```bash
cd JumpTools/FundHQ
python3 -m http.server 8080
# Open http://localhost:8080/fund-hq.html
```
