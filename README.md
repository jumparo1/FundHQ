# Fund HQ

AI-powered institutional research operating system for crypto and equities. Three research divisions — On-Chain Intelligence, Fundamental Research, and Technical Analysis — working together to surface asymmetric opportunities.

## Architecture

| Division | Purpose | Agent |
|----------|---------|-------|
| **On-Chain Intel** | Smart money tracking, flow analysis, venue intelligence | Sentinel |
| **Research** | Fundamental deep dives, tokenomics, catalysts, valuation | Analyst |
| **Technical** | Market regime, trade setups, playbooks, confluence scoring | Quant |

## Features

- **On-Chain Intel** — Hyperliquid whale tracker (wallet scanner, whale discovery, saved wallets, perp positioning), Entity Tracker, Flow Monitor, Signal Feed
- **Market Data** — Live search across crypto (CoinGecko) and stocks (FMP) with auto-scoring
- **Research Templates** — Crypto (16s), Stock (14s), Commodity (12s), Quick Thesis (5s) with AI-powered section analysis
- **Reports** — AI-generated research reports with rating, conviction, Substack publishing, soft-delete trash
- **Technical Analysis** — Market regime detection, setup scanner, strategy playbooks, 4-factor confluence scoring, trade log
- **AI Assistant** — "Pamela" Claude-powered agent with 20 tools, multi-turn reasoning, web search
- **Scheduled Tasks** — Daily market scans, watchlist refresh, weekly deep dives via Claude Code cron
- **Dashboard** — Fund overview with watchlist, reports, tasks, quick actions
- **Operations** — Kanban tasks, milestone roadmap, daily progress log

## Tech Stack

- Single HTML file — no build tools, no frameworks
- **Firebase Realtime Database** for cloud sync
- **localStorage** fallback for offline use
- **Anthropic Claude API** for AI research + Pamela agent
- **Hyperliquid API** for on-chain data
- **Python agent** for persistent monitoring + WebSocket alerts
- Vanilla JavaScript, CSS custom properties, dark theme

## Live

**https://jumparo1.github.io/JumpTools/fund-hq.html**

## Run Locally

```bash
cd FundHQ
python3 -m http.server 8080
# Open http://localhost:8080/fund-hq.html
```

Firebase syncs automatically when online. API keys stored in browser localStorage (Settings page).
