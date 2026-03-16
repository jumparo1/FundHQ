# Fund HQ

AI-powered institutional research operating system for crypto and equities. Three research divisions — On-Chain Intelligence, Fundamental Research, and Technical Analysis — working together to surface asymmetric opportunities.

## Architecture

| Division | Purpose | Agent |
|----------|---------|-------|
| **On-Chain Intel** | Smart money tracking, flow analysis, venue intelligence | Sentinel |
| **Research** | Fundamental deep dives, tokenomics, catalysts, valuation | Analyst |
| **Technical** | Market regime, trade setups, playbooks, confluence scoring | Quant |

## Features

- **Token Intel** — Enter any ticker, scan all sources for smart money activity: tracked entity positions, whale discovery, long/short clusters, on-chain top holders (Moralis), top DEX traders (Birdeye), HL perp data, DEX liquidity, Alpha Summary with automated insights
- **On-Chain Intel** — Hyperliquid (wallet scanner, whale discovery, saved wallets, perp positioning), Dexscreener (search, trending, new pairs), Entity Tracker (full CRUD, import from HL, live scanning), Flow Monitor, Signal Feed
- **Portfolio** — Holdings tracker with allocation breakdown, P&L tracking, cash management, live pricing via CoinGecko (crypto) + FMP (stocks)
- **Market Data** — Live search across crypto (CoinGecko) and stocks (FMP) with auto-scoring
- **Research Templates** — Crypto (16s), Stock (14s), Commodity (12s), Quick Thesis (5s) with AI-powered section analysis
- **Reports** — AI-generated research reports with rating, conviction, Substack publishing, soft-delete trash
- **Catalysts** — Event tracking with 8 types, impact/time filters, summary cards, Firebase sync
- **Technical Analysis** — Market regime detection, setup scanner, strategy playbooks, 4-factor confluence scoring (auto-score from entities/regime/setups/catalysts), conviction report generator, trade log with P&L
- **AI Assistant** — "Pamela" Claude-powered agent with 20 tools, multi-turn reasoning, web search
- **Scheduled Tasks** — Daily market scans, watchlist refresh, weekly deep dives via Claude Code cron
- **Dashboard** — Fund overview with watchlist, reports, tasks, quick actions
- **Operations** — Kanban tasks, milestone roadmap, daily progress log

## Data Sources

| Source | Type | Key Required | What It Provides |
|--------|------|-------------|------------------|
| Hyperliquid | Perp positions | No | Wallet positions, whale discovery, funding, OI, volume |
| Dexscreener | DEX analytics | No | Token search, trending, new pairs, liquidity, price |
| CoinGecko | Crypto prices | No | Live portfolio pricing, market data |
| Moralis | On-chain holders | Free key | Top token holders, % supply, concentration analysis |
| Birdeye | Solana traders | Free key | Top DEX traders, buy/sell volume, trader sentiment |
| FMP | Stock data | Free key | Stock fundamentals, quotes, financial metrics |
| Anthropic Claude | AI | Paid key | Research reports, Pamela agent, web search |

## Tech Stack

- Single HTML file (~11K lines) — no build tools, no frameworks
- **Firebase Realtime Database** for cloud sync
- **localStorage** fallback for offline use
- **Anthropic Claude API** for AI research + Pamela agent
- **Hyperliquid API** + **Dexscreener API** + **Moralis API** + **Birdeye API** for on-chain data
- **Python agents** — Sentinel (on-chain), Analyst (research), Quant (technical)
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
