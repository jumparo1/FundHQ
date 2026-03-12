# Crypto Fundamental Analysis — Research Playbook

## Goal
Fully automated 18-section crypto research report. Claude gathers all data, fills the template, saves to Fund HQ.

## Template Sections
0. Intro | 1. Overview | 2. TL;DR | 3. Tokenomics | 4. Technology | 5. Team | 6. Governance
7. Ecosystem | 8. Backers & Funding | 9. Competitive Landscape & Valuation | 10. Users/Growth/Revenue
11. Social Sentiment | 12. Top Holders & Whale Activity | 13. Chart & TA | 14. Catalysts & FUD
15. Final Thesis | 16. Signal | 17. Sources

## Business Model Classification
Before diving into data, classify the project type — different models = different fee structures:
- **L1/L2 Chain** — gas fees, MEV, staking yield (e.g., ETH, SOL, AVAX)
- **DEX** — trading fees split between protocol + LPs (e.g., Uniswap, GMX)
- **Lending** — interest spread between borrowers/lenders (e.g., Aave, Compound)
- **Liquid Staking** — % cut of staking rewards (e.g., Lido, Rocket Pool)
- **NFT Marketplace** — marketplace fees + creator royalties (e.g., Blur, OpenSea)
- **Oracle / Infra** — service fees, data subscriptions (e.g., Chainlink, Pyth)
- **AI / DePIN** — compute/resource fees, subnet economics (e.g., TAO, Render)
- **Gaming / Social** — in-app purchases, platform fees

The business model determines which metrics matter most and how revenue flows.

## Data Sources & What To Do There

### Free APIs (auto-fetch)
- **CoinGecko** (`api.coingecko.com/api/v3/coins/{id}`) — price, mcap, FDV, volume, ATH, supply, links, description. Use for sections 1, 3
- **DefiLlama** (`api.llama.fi/protocol/{name}`) — TVL, chain breakdown, revenue. Use for sections 7, 10

### Websites to Scrape/Read
- **CoinGecko page** (`coingecko.com/en/coins/{id}`) — categories, exchanges listed, developer stats, community stats
- **Messari** (`messari.io/asset/{ticker}`) — governance, profile, fundraising history. Sections 5, 6, 8
- **CryptoRank** (`cryptorank.io/price/{id}`) — funding rounds, investor list, ROI. Section 8
- **DeFiLlama** (`defillama.com/protocol/{name}`) — TVL chart, chain breakdown. Section 7, 10
- **Token Terminal** (`tokenterminal.com/terminal/projects/{name}`) — fees, revenue, earnings, P/S, P/E, active users, developers. Sections 9, 10
- **L2Beat** (`l2beat.com/scaling/projects/{name}`) — L2 TVL if applicable. Section 7
- **Token Unlocks** (`token.unlocks.app/{name}`) — vesting schedule, upcoming unlocks, emission calendar. Section 3

### Financial Metrics to Extract (Section 10)
Build a crypto "income statement" for the project:
```
Total Fees [A]               — all economic value received (trading fees, gas, commissions)
Less: Supply-Side Fees [B]   — fees paid to LPs, stakers, validators, node operators
= Protocol Revenue [C]       — revenue the protocol actually keeps [A] - [B]
Less: Token Incentives [D]   — cost of emissions used to bootstrap growth
= Earnings [E]               — bottom-line profitability [C] - [D]
```
Key ratios to calculate:
- **Fees Growth %** — (current year fees / prior year fees) - 1
- **Revenue Growth %** — (current year revenue / prior year revenue) - 1
- **Protocol Margin %** — protocol revenue / total fees (how much does the protocol keep?)
- **Net Income Margin %** — earnings / total fees
- **Treasury Size & Burn Rate** — how long can they survive at current spend?

### Valuation Multiples (Section 9)
Calculate and compare to sector peers:
- **P/S (total)** — FDV / annualized total revenue
- **P/S (protocol)** — FDV / annualized protocol revenue
- **P/E** — FDV / annualized earnings
- **MCap/TVL** — circulating mcap / total value locked
- **FDV/TVL** — fully diluted valuation / TVL
- **Revenue multiple** — FDV / annualized fees (how many years of fees to justify valuation?)

Rule of thumb: compare to 3-5 closest competitors. Lower ratio = "cheaper" but needs context.
A discount might mean the market sees risk. A premium might be justified by faster growth.

### Tokenomics Deep Dive (Section 3)
Beyond basic supply numbers, analyze:

**Supply side:**
- Token allocation breakdown — % to team, investors, community, treasury, ecosystem
- Centralization risk — is >30% held by insiders/VCs?
- Vesting/unlock schedule — when do big tranches unlock? Check token.unlocks.app
- Emission schedule — annual inflation rate, how fast does supply grow?
- Upcoming dilution events — any cliff unlocks in next 3-6 months?

**Demand side (value accrual):**
- **Buy-and-burn** — does the protocol buy back and burn tokens with revenue? (e.g., BNB)
- **Fee distribution** — are fees shared with token holders/stakers? (e.g., GMX)
- **Staking yield** — real yield from protocol revenue vs inflationary emissions
- **Governance rights** — can token holders vote on meaningful decisions?
- **Protocol participation** — is the token required to use the protocol?
- **veToken model** — lock tokens for boosted rewards/voting power? (e.g., CRV)

Key question: Does holding the token give you a claim on cash flows, or is it just governance + speculation?

### Social Sentiment (Section 11)
- **Grok on X** — use this prompt for social sentiment:
  ```
  Analyze $[TICKER] Twitter/X sentiment from the last 7 days. Provide:
  1. OVERALL SENTIMENT SPLIT: X% bullish / X% neutral / X% bearish with reasons
  2. VOLUME & ENGAGEMENT: post frequency, avg likes/reposts, trending?
  3. KEY INFLUENCERS: top 5 accounts posting about it with follower count and stance
  4. CATALYSTS BEING DISCUSSED: what topics are driving conversation
  5. RED FLAGS: any FUD, scam accusations, or negative patterns
  6. NARRATIVE STRENGTH: how strong is the current narrative vs 30 days ago
  Format as structured bullet points. Be specific with numbers.
  ```
- Copy Grok output → paste into section 11 of report

### Whale & Perp Positioning (Section 12)
- **Hyperdash** (`hyperdash.com/?chart1={TICKER}`) — perp data for any token with futures:
  - TOP TRADERS tab: whale positions, entry prices, unrealized PnL, liquidation levels
  - COHORTS tab: size cohorts (Apex/Whale/Large/Medium/Small) with long/short % and profit %
  - POSITION CHANGES tab (24H): recent large position opens/closes
  - LIQUIDATIONS tab (Depth view): liquidation cluster levels above/below price
  - Key metrics: OI, funding rate, long/short ratio by count AND notional
  - Alpha: compare whale cohort direction vs retail — divergence = edge

### On-Chain (Section 12)
- **Arkham Intelligence** (`platform.arkintelligence.com`) — wallet labels, whale tracking
- **Nansen** (`app.nansen.ai`) — smart money flows, token god mode (paid)
- **Etherscan/chain explorer** — top holders, token distribution

### Chart & TA (Section 13)
- **TradingView** — weekly/daily chart, key S/R levels, trend structure
- Note: Claude can't access TradingView charts directly. User provides screenshot or describe levels manually.

## Workflow
1. User says: "research [TOKEN]"
2. Classify business model type (DEX/L1/Lending/etc.)
3. Fetch CoinGecko API for basic data (price, mcap, supply, links)
4. Web search for: team, backers, recent news, governance, tech
5. Fetch Token Terminal for financial metrics (fees, revenue, earnings, P/S)
6. Check token.unlocks.app for vesting schedule
7. Fill sections 0-10 from gathered data (including income statement + valuation multiples)
8. Ask user to run Grok prompt for section 11 (or skip if user provides)
9. Check Hyperdash for perp positioning data (section 12)
10. Fill sections 13-17 from analysis
11. Save to Fund HQ via Firebase (`fundHQ/reports/{id}`)
12. Open report in view mode for review

## Report Format
```
PROJECT: {Name} | TICKER: ${TICKER} | CHAIN: {chain} | DATE: {YYYY-MM-DD} | ANALYST: Jumparo
TYPE: {DEX/L1/Lending/LST/NFT/AI/Infra/Gaming}

═══════════════════════════════════════════════════════════════════
0. INTRO
═══════════════════════════════════════════════════════════════════
{2-3 sentence hook}

═══════════════════════════════════════════════════════════════════
1. OVERVIEW
═══════════════════════════════════════════════════════════════════
- What: {description}
- Price: ${price} | MCap: ${mcap} | FDV: ${fdv} | 24h Vol: ${vol}
...
```
- Use ═══ dividers between sections (parser splits on this)
- Bullet points with `- ` prefix
- Bold labels with `Key: value` pattern
- No markdown headers inside sections (breaks view mode parser)

## Scoring Guide
- Rating: Strong Buy / Buy / Speculate / Hold / Sell
- Conviction: High / Medium / Low
- Overall Score: 1-10

## Lessons Learned
- FMP stock API: use `/stable/` endpoints, field names differ from v3 (`marketCap` not `mktCap`)
- CoinGecko free tier: 10-30 calls/min, no API key needed for basic endpoints
- Hyperdash perp data only available for tokens with futures markets
- Smart money divergence from retail is the strongest signal (e.g., whales short while retail long)
- Always note data freshness date — perp positioning changes fast
- Token Terminal is the best single source for crypto financial metrics (fees, revenue, earnings, P/S, P/E)
- Valuation multiples mean nothing in isolation — always compare to 3-5 sector peers
- Upcoming token unlocks are one of the most reliable bearish catalysts — always check vesting
- Real yield (from protocol revenue) vs inflationary yield (from emissions) is a critical distinction
- Projects with earnings > token incentives are genuinely profitable and rare — flag these
