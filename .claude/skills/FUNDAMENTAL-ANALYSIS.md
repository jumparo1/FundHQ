# Crypto Fundamental Analysis — Research Playbook

## Goal
Fully automated 19-section crypto research report. Claude gathers all data, fills the template, saves to Fund HQ.

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
- **Token Unlocks** (`token.unlocks.app/{name}`) — vesting schedule, upcoming unlocks, emission calendar. Section 7

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

### Social Sentiment (Section 11)
- **Grok on X** — use this prompt:
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
- Copy Grok output → paste into section 11

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

---

## Report Template

```
PROJECT: [TOKEN NAME] | TICKER: $[TICKER] | CHAIN: [Chain] | DATE: [YYYY-MM-DD] | ANALYST: Jumparo
TYPE: [DEX / L1-L2 / Lending / LST / NFT / AI-DePIN / Oracle-Infra / Gaming-Social]

═══════════════════════════════════════════════════
0. INTRO
═══════════════════════════════════════════════════
[2-3 sentence hook — why this project matters right now]

═══════════════════════════════════════════════════
1. OVERVIEW
═══════════════════════════════════════════════════
What it does: [1-2 sentences]
FDV: [$] | Market Cap: [$] | FDV/MC Ratio: [x]
Volume 24h: [$] ([+/-%]) | Volume 7d: [$] ([+/-%])
X: [@handle] | Website: [url]

═══════════════════════════════════════════════════
2. TL;DR
═══════════════════════════════════════════════════
* What it is: [simple definition]
* How it works: [1-liner mechanism]
* Why it matters: [value prop or opportunity]

═══════════════════════════════════════════════════
3. PRODUCT & FEATURES
═══════════════════════════════════════════════════
* Core product: [what it builds/provides]
* How miners/nodes contribute: [tasks + rewards]
* How validators secure it: [mechanism]
* Tech stack: [infra, SDKs, tools]
* Key features: [real-world utility, what makes it useful]

═══════════════════════════════════════════════════
4. MOATS
═══════════════════════════════════════════════════
* Data Advantage: [proprietary? hard to replicate? feedback loops?]
* Model/Tech Differentiation: [unique architecture, novel methods?]
* Trust Barrier: [transparent scoring? hard-to-copy evaluation?]
* Incentive Lock-in: [are participants aligned long-term?]
* Fork Resistance: [could a competitor easily clone + attract users?]

═══════════════════════════════════════════════════
5. TEAM
═══════════════════════════════════════════════════
* Founders: [Names, roles, background]
* Key experience: [crypto, AI, Web2, notable companies]
* Links: [X, LinkedIn]
* Credibility: [why this team? track record?]

═══════════════════════════════════════════════════
6. GOVERNANCE
═══════════════════════════════════════════════════
* Governance model: [on-chain / off-chain / multisig / DAO / foundation-led]
* Token voting: [1 token = 1 vote? veToken? delegated?]
* Key decisions made: [recent governance proposals, fee changes, upgrades]
* Decentralization level: [who really controls the protocol?]
* Treasury governance: [how are funds allocated? community vote or team discretion?]

═══════════════════════════════════════════════════
7. TOKENOMICS
═══════════════════════════════════════════════════
SUPPLY:
Launch Date: [Date] | Launch Price: [$] | Current Price: [$]
Circulating Supply: [#] ([%]) | Max Supply: [#] | FDV: [$] | Market Cap: [$]
FDV / MCap ratio: [Xx — >3x = heavy future dilution]
Supply type: [Capped / Inflationary / Deflationary / Dynamic]
Distribution: Team [%] | Investors [%] | Community [%] | Treasury [%] | Ecosystem [%]
Centralization risk: [>30% insider/VC? flag it]
Foundation overlap: [does core team = foundation board?]

VESTING & UNLOCKS:
Vesting type: [time-based / trigger-based (TGE, mainnet, listing)]
Next Unlock: [Date] | Amount: [# tokens, $value] | % of Circ: [%]
Cliff unlocks next 6mo: [dates + amounts]
Source: token.unlocks.app

EMISSIONS & MONETARY POLICY:
Emissions: Daily [#] | Yearly [#] | Inflation Rate: [%]
Burn mechanism: [auto-burn / fee burn / buyback-burn / none]
Net emission: [inflationary or deflationary after burns?]
Airdrop history: [past drops, % allocated, sybil filtering used?]

DEMAND & VALUE ACCRUAL:
* Buy-and-burn: [does protocol buy back + burn with revenue?]
* Fee distribution: [are fees shared with stakers/holders?]
* Revenue share model: [% to LPs / % to holders / % to DAO]
* Staking: [% staked] | Real Yield: [% from protocol revenue, not emissions]
* veToken / lock mechanics: [lock for boosted rewards or voting power?]
* Protocol participation: [is token required to use the protocol?]
* Token utility: [governance / toll-fee / currency / access / earnings]
* Two-token model? [if yes: what does each token do?]
* Key question: Does holding give a claim on cash flows, or just governance + speculation?

═══════════════════════════════════════════════════
8. BACKERS & FUNDING
═══════════════════════════════════════════════════
* Lead investors: [Names]
* Round details: [Stage, size, valuation]
* Other notable backers: [Angels, DAOs, funds]
* Treasury size: [$] | Burn rate: [$X/mo] | Runway: [X months]
* Status: [Early/Stealth/Well-funded/No data]

═══════════════════════════════════════════════════
9. COMPETITIVE LANDSCAPE & VALUATION
═══════════════════════════════════════════════════
NARRATIVE FIT:
Macro theme: [DePIN / DeAI / DeFi / Gaming / Infra / etc.]
Why relevant now: [narrative timing, market demand]

PEER COMPARISON TABLE:
| Project | FDV | Ann. Revenue | P/S | P/E | MCap/TVL | Edge |
|---------|-----|-------------|-----|-----|----------|------|
| [This]  | [$] | [$]         | [x] | [x] | [x]     | —    |
| [Peer1] | [$] | [$]         | [x] | [x] | [x]     | [?]  |
| [Peer2] | [$] | [$]         | [x] | [x] | [x]     | [?]  |
| [Peer3] | [$] | [$]         | [x] | [x] | [x]     | [?]  |

VALUATION VERDICT:
* P/S vs peers: [cheap / fair / expensive]
* P/E vs peers: [cheap / fair / expensive / N/A if unprofitable]
* Premium/discount justified? [why or why not]

COMPETITIVE EDGE:
* [What makes this different from peers]
* [Hard-to-replicate design features]
* [Where asymmetric upside may lie]

═══════════════════════════════════════════════════
10. USERS, GROWTH & REVENUE
═══════════════════════════════════════════════════
USAGE METRICS:
Active miners/nodes: [#] | Validators: [#] | DAU: [#] | TVL: [$]
30d trend: [rising/flat/falling] | Early traction signals: [X followers, demo, validator competition]

CRYPTO INCOME STATEMENT:
Total Fees (annualized): [$] | Fees Growth YoY: [%]
Less: Supply-Side Fees: [$] (paid to LPs/stakers/validators)
= Protocol Revenue: [$] | Revenue Growth YoY: [%]
Less: Token Incentives: [$] (emission cost to bootstrap growth)
= Earnings: [$] | Profitable: [Yes/No]

KEY RATIOS:
Protocol Margin: [%] (protocol revenue / total fees — how much does protocol keep?)
Net Income Margin: [%] (earnings / total fees)
Revenue Multiple: [x] (FDV / annualized fees — years of fees to justify valuation)

REVENUE MODEL:
* Fee structure: [what users pay, how it splits between protocol + supply-side]
* Demand side: [who consumes output? real buyers or speculative?]
* On-chain revenue: [visible fees/volume? or purely emission-driven?]
* Self-sustaining? [can it survive without token emissions?]

═══════════════════════════════════════════════════
11. SOCIAL SENTIMENT
═══════════════════════════════════════════════════
* Community vibe: [positive / hyped / skeptical / quiet]
* Influencer engagement: [who is talking? bullish or bearish?]
* Public alpha: [any leaks, insider threads, stealth updates?]
* FUD / warnings: [recurring concerns on CT?]
Signal Rating: [Strong / Moderate / Weak]

═══════════════════════════════════════════════════
12. TOP HOLDERS & WHALE ACTIVITY
═══════════════════════════════════════════════════
Top 10 concentration: [%] | Top 30 concentration: [%]
* Whale wallets: [# flagged as whale, team, or CEX]
* Behavior: [accumulating / distributing / idle]
* Red flags: [high centralization? active sell-offs? unknown multisigs?]

PERP POSITIONING (Hyperdash):
* OI: [$] | Funding: [%] | Long/Short ratio: [x]
* Whale cohort ($1M+): [% long / % short]
* Retail cohort ($10K-$100K): [% long / % short]
* Smart money divergence: [whales vs retail — same direction or opposite?]
* Liquidation clusters: Longs [$X-$Y] | Shorts [$X-$Y]

TOP TRADER PnL:
Entry clusters: [$X-$Y range] | Avg PnL: [+/-X%] | Whales holding or selling: [status]

═══════════════════════════════════════════════════
13. CHART & TECHNICAL ANALYSIS
═══════════════════════════════════════════════════
* Trend: [direction + strength]
* Support: [$, $] | Resistance: [$, $]
* Entry zone: [breakout / retest / DCA level]
* Stop loss: [$]
* Volume / momentum: [insight]
* Targets: [TP1: $, TP2: $]
BTC Pair: [Outperforming / Underperforming] | Market Structure: [Accumulation / Markup / Distribution / Markdown]

═══════════════════════════════════════════════════
14. CATALYSTS & FUD
═══════════════════════════════════════════════════
POSITIVE CATALYSTS:
* [Catalyst 1 - product launch, listing, partnership, upgrade]
* [Catalyst 2 - unlock, airdrop, mainnet, SDK release]
* [Catalyst 3 - CT hype, influencer thread, narrative shift]

RISKS / FUD:
* [Risk 1 - regulatory, tech failure, team drama]
* [Risk 2 - whale dumping, low usage, competitor launch]
* [Risk 3 - upcoming token unlock, high emissions dilution]

═══════════════════════════════════════════════════
15. FINAL THESIS
═══════════════════════════════════════════════════
BULLISH:
* [Strength 1]
* [Strength 2]
* [Strength 3]

BEARISH:
* [Risk 1]
* [Risk 2]
* [Risk 3]

═══════════════════════════════════════════════════
16. SIGNAL
═══════════════════════════════════════════════════
VERDICT: [BUY / SPECULATE / HOLD-WAIT / AVOID]
Conviction: [High / Medium / Low] | Timeframe: [Short / Medium / Long]
One-liner: [core reason for the call]

═══════════════════════════════════════════════════
17. SOURCES
═══════════════════════════════════════════════════
CoinGecko | DefiLlama | Artemis | TokenTerminal | Token Unlocks | Dexscreener | DropsTab | SpotOnChain | Etherscan | Holderscan | Crunchbase | CoinCarp | CryptoRank | Hyperdash | Cookie.fun | GoatIndex | Coindar | Coinmarketcal | Tokenomist.ai | Official Docs | X (Twitter)

═══════════════════════════════════════════════════
18. SUBSTACK ONE-PAGER
═══════════════════════════════════════════════════
[Rewrite sections 0-17 as a Substack article in the Asymmetric Jump voice — see Writing Style below]
```

### Template Format Rules
- Use ═══ dividers between sections (parser splits on this)
- Bullet points with `* ` or `- ` prefix
- Bold labels with `Key: value` pattern
- No markdown headers inside sections (breaks view mode parser)

---

## Substack Writing Style (Asymmetric Jump)

Section 18 rewrites the full report as a Substack-ready article. Match this voice:

### Tone & Structure
- **Provocative title** with specific numbers ("The $4.5B 'Bitcoin of AI' That's Down 72%...")
- **Opinionated, direct, no-BS.** Tell the reader what data MEANS, not just what it says
- **"You're buying a bet that..."** framing — make the investment thesis concrete
- **Moat scoring** with numbers (0-100 scale or /10)
- **Explicit risk/reward** with allocation guidance and sizing
- **Shorter paragraphs, punchy sentences.** If you can say it in one line, don't use three
- **Bold for key terms** and emphasis throughout
- **Clean ## headings** without numbered prefixes
- **Real analysis over data dumps** — always follow data with "What this means:"

### Sections to Include
- Hook title + subtitle line
- What you're actually buying (thesis framing)
- Moat scoring (scored categories, total /100)
- Tokenomics — The Good, The Bad, The Ugly
- Backers & smart money
- Valuation problem (peer table + honest assessment)
- What smart money is doing (perp positioning)
- Chart says [wait/go/run]
- Catalysts that could change everything
- The Verdict (rating /10, conviction, action, bull/bear/base case)
- Disclaimer: "AI-assisted and refined by the researcher. Not financial advice — DYOR."

### What NOT to Do
- Don't just reformat — rewrite in voice
- Don't be neutral. Have an opinion
- Don't dump tables without context
- Don't use section numbers (0, 1, 2...) — use descriptive headings
- Don't make it too long — tight and focused, ~1500-2000 words

---

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
11. Write section 18 Substack one-pager in Asymmetric Jump voice
12. Save to Fund HQ via Firebase (`fundHQ/reports/{id}`)
13. Open report in view mode for review

## Report Storage
- Firebase RTDB: `https://fundhq-8feae-default-rtdb.europe-west1.firebasedatabase.app/fundHQ/reports/{id}`
- Content stored as single string with ═══ dividers
- CRYPTO_SECTIONS array (19 items): ['Intro', 'Overview', 'TL;DR', 'Product & Features', 'Moats', 'Team', 'Governance', 'Tokenomics', 'Backers & Funding', 'Competitive Landscape & Valuation', 'Users, Growth & Revenue', 'Social Sentiment', 'Top Holders & Whale Activity', 'Chart & Technical Analysis', 'Catalysts & FUD', 'Final Thesis', 'Signal', 'Sources', 'Substack One-Pager']

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
