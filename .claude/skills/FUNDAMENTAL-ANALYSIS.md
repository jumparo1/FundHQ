# Crypto Fundamental Analysis — Research Playbook

## Goal
Fully automated 19-section crypto research report. Claude gathers all data, fills the template, saves to Fund HQ. Now enhanced with backend quantitative models for systematic valuation, multi-factor scoring, and risk assessment.

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

The business model determines which metrics matter most, which sector medians to use for valuation, and how revenue flows.

## Data Sources & What To Do There

### Backend API (Phase 2 — Quantitative Models)
When the backend is running (port 8888), use these endpoints for systematic analysis:

**Valuation Engine** (`POST /api/valuation`):
```json
{ "revenue": 50000000, "tvl": 1000000000, "mcap": 500000000, "sector": "DEX", "growth_rate": 0.3 }
```
Returns: Revenue multiple (P/S vs sector median), TVL valuation (MCap/TVL vs sector), DCF-lite (5-year discounted cash flow), and composite verdict (STRONG BUY / UNDERVALUED / FAIR / OVERVALUED / AVOID).

Sector medians built in: DEX (P/S 15, MCap/TVL 0.8), Lending (12, 0.3), L1 (50, 5.0), L2 (40, 3.0), Derivatives (20, 1.0), LST (25, 0.15), Bridge (10, 0.5).

**Multi-Factor Scorer** (`POST /api/score`):
```json
{ "symbol": "UNI", "change_24h": 2.5, "change_7d": 8.0, "ath_change": -45,
  "volume_24h": 500000000, "market_cap": 5000000000, "fdv": 6000000000,
  "tvl": 4000000000, "mcap_tvl": 1.25, "revenue_growth_30d": 15,
  "tvl_change_7d": 5, "whale_positions": 3, "funding_rate": 0.00015,
  "oi_change_24h": 8.5, "fear_greed": 60, "is_trending": true }
```
Returns: Composite score (1-5), 5 factor scores (fundamental / technical / onchain / sentiment / valuation), grade (A-F), signal (STRONG BUY / BUY / HOLD / AVOID), detailed scoring rationale.

Scoring dimensions:
- **Fundamental** (25%): Revenue growth, TVL trend, active development
- **Technical** (20%): 7d/24h momentum, ATH distance (recovery potential), volume/mcap ratio
- **On-chain** (20%): Whale positions, funding rate (contrarian signal), OI expansion
- **Sentiment** (15%): Fear & Greed (contrarian — extreme fear = bullish), trending status, social score
- **Valuation** (20%): MCap/TVL ratio, FDV/MCap dilution risk

**Auto-Discovery** (`GET /api/discovery`):
Scans CoinGecko for deep-value coins (high ATH discount + strong recent momentum) and DeFiLlama for undervalued DeFi (low MCap/TVL ratio). Use this to find research candidates.

### Backend API (Phase 3 — Risk Engine)
**Position Sizer** (`POST /api/risk/position-size`):
```json
{ "capital": 50000, "risk_per_trade": 0.01, "entry": 45000, "stop_loss": 43000 }
```
Returns: Risk amount, position size in USD, number of units, R-multiples (1R through 5R). Use for section 13 trade setup.

**VaR Calculator** (`POST /api/risk/var`):
Historical Value-at-Risk for portfolio with position-level breakdown. Use when assessing risk in section 15.

### Backend API (Phase 4 — Learning)
**Score Calibration** (`POST /api/calibration/run`):
Adjusts multi-factor weights based on which factors actually predicted winners in trade history. After calibration, the scorer uses updated weights. Reference calibrated weights in reports for credibility.

### Free APIs (auto-fetch)
- **CoinGecko** (`api.coingecko.com/api/v3/coins/{id}`) — price, mcap, FDV, volume, ATH, supply, links, description. Use for sections 1, 3
- **DefiLlama** (`api.llama.fi/protocol/{name}`) — TVL, chain breakdown, revenue. Use for sections 7, 10
- **Backend `/api/prices`** — cached prices from backend (faster, no rate limits vs direct CoinGecko)
- **Backend `/api/macro`** — Fear & Greed, BTC dominance, DeFi TVL, total market cap (pre-aggregated)

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

### Valuation Framework (Section 9)

#### Manual Valuation (always do this)
Calculate and compare to sector peers:
- **P/S (total)** — FDV / annualized total revenue
- **P/S (protocol)** — FDV / annualized protocol revenue
- **P/E** — FDV / annualized earnings
- **MCap/TVL** — circulating mcap / total value locked
- **FDV/TVL** — fully diluted valuation / TVL
- **Revenue multiple** — FDV / annualized fees (how many years of fees to justify valuation?)

Rule of thumb: compare to 3-5 closest competitors. Lower ratio = "cheaper" but needs context.
A discount might mean the market sees risk. A premium might be justified by faster growth.

#### Backend Valuation (run when backend is available)
After gathering revenue, TVL, and MCap data, call `POST /api/valuation` with:
- `revenue`: annualized protocol revenue (from Token Terminal or calculated)
- `tvl`: total value locked (from DeFiLlama)
- `mcap`: current market cap (from CoinGecko)
- `sector`: business model type (DEX/Lending/L1/L2/Derivatives/LST/Bridge/Other)
- `growth_rate`: estimated revenue growth rate (0.3 = 30% default, adjust based on data)

The backend returns:
1. **Revenue Multiple** — fair value MCap based on sector median P/S ratio
2. **TVL Valuation** — fair value based on sector median MCap/TVL ratio
3. **DCF-Lite** — 5-year discounted cash flow with 25% crypto discount rate, decaying growth, terminal value
4. **Composite Verdict** — STRONG BUY (>40% undervalued) / UNDERVALUED (>15%) / FAIR / OVERVALUED / AVOID

Include backend valuation results in section 9 alongside manual peer comparison. The DCF provides a forward-looking anchor that peer multiples miss.

### Multi-Factor Score (run after filling sections 1-12)
Call `POST /api/score` with all gathered data points. The 5-dimension score (fundamental / technical / onchain / sentiment / valuation) provides a systematic cross-check against your qualitative analysis.

Include the backend grade (A-F) and signal in section 16 alongside your manual conviction rating. If the backend score disagrees with your thesis, explain why (e.g., "Backend rates C due to low volume, but upcoming catalyst should change this").

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
- **Fund HQ Entity Tracker** — check tracked entities for positions on this token
- **Fund HQ Sentinel agent** — `hl_whale_positions` tool can pull live Hyperliquid whale data

### On-Chain (Section 12)
- **Arkham Intelligence** (`platform.arkintelligence.com`) — wallet labels, whale tracking
- **Nansen** (`app.nansen.ai`) — smart money flows, token god mode (paid)
- **Etherscan/chain explorer** — top holders, token distribution
- **Fund HQ Token Intel** — 500-wallet scan with whale quality scoring and entity tracking

### Chart & TA (Section 13)
- **TradingView** — weekly/daily chart, key S/R levels, trend structure
- Note: Claude can't access TradingView charts directly. User provides screenshot or describe levels manually.
- Include **position sizing** from backend: `POST /api/risk/position-size` with entry, stop, and capital to get exact USD size + R-multiples

---

## Report Template

```
PROJECT: [TOKEN NAME] | TICKER: $[TICKER] | CHAIN: [Chain] | DATE: [YYYY-MM-DD] | ANALYST: Jumparo
TYPE: [DEX / L1-L2 / Lending / LST / NFT / AI-DePIN / Oracle-Infra / Gaming-Social]
BACKEND SCORE: [Grade] [Signal] ([composite_score]/5) | VALUATION: [Verdict]

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

BACKEND VALUATION MODEL:
* Revenue Multiple: Fair MCap [$] (sector median P/S: [x]) → [% premium/discount]
* TVL Valuation: Fair MCap [$] (sector median MCap/TVL: [x]) → [% premium/discount]
* DCF-Lite: Fair MCap [$] (25% discount rate, [x]% initial growth, 5yr) → Terminal [%] of value
* Composite Verdict: [STRONG BUY / UNDERVALUED / FAIR / OVERVALUED / AVOID] (confidence: [high/medium/low])
* Agreement with manual analysis: [yes/no — if no, explain divergence]

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

FUND HQ ENTITY INTELLIGENCE:
* Tracked entities with positions: [list any Fund HQ entities holding this token]
* Entity grades: [A+/A/B/C grades of whales in this token]
* Wallet Hunter signals: [any Hyperliquid leaderboard wallets with this position]

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

POSITION SIZING (from backend or manual):
* Capital: [$] | Risk per trade: [%]
* Entry: [$] | Stop: [$] | Risk distance: [%]
* Position size: [$] | Units: [#]
* R-Multiples: 1R = [$], 2R = [$], 3R = [$], 5R = [$]

ASYMMETRIC CASE:
* Downside to stop: [-X%] | Upside to TP1: [+X%] | R:R at TP1: [X:1]
* Max conviction size: [X% of portfolio]
* If wrong: [what invalidates the thesis]
* If right: [what 2R/3R/5R looks like in dollar terms]

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

RISK ASSESSMENT:
* Biggest single risk: [what keeps you up at night]
* Probability of thesis failure: [low/medium/high]
* Time decay risk: [does this thesis expire? when?]

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

BACKEND MULTI-FACTOR SCORE:
* Composite: [X.XX/5] | Grade: [A-F] | Signal: [STRONG BUY / BUY / HOLD / AVOID]
* Fundamental: [X/5] | Technical: [X/5] | On-chain: [X/5] | Sentiment: [X/5] | Valuation: [X/5]
* Key scoring details: [top 3 factors from backend rationale]
* Score vs thesis alignment: [agree / disagree — explain if divergent]

═══════════════════════════════════════════════════
17. SOURCES
═══════════════════════════════════════════════════
CoinGecko | DefiLlama | Artemis | TokenTerminal | Token Unlocks | Dexscreener | DropsTab | SpotOnChain | Etherscan | Holderscan | Crunchbase | CoinCarp | CryptoRank | Hyperdash | Cookie.fun | GoatIndex | Coindar | Coinmarketcal | Tokenomist.ai | Fund HQ Backend (Phases 2-3) | Official Docs | X (Twitter)

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
- **Include backend valuation verdict** — readers respect systematic models backing up qualitative opinions
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
- Valuation problem (peer table + backend valuation model results + honest assessment)
- What smart money is doing (perp positioning + Fund HQ entity intel)
- Chart says [wait/go/run] — with position sizing and R-multiples
- Catalysts that could change everything
- The Verdict (rating /10, conviction, action, bull/bear/base case + backend grade for cross-check)
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
7. **If backend online**: Run `POST /api/valuation` with revenue + TVL + MCap + sector
8. **If backend online**: Run `POST /api/score` with all gathered metrics
9. Fill sections 0-10 from gathered data (including income statement + valuation multiples + backend valuation)
10. Ask user to run Grok prompt for section 11 (or skip if user provides)
11. Check Hyperdash for perp positioning data (section 12)
12. Check Fund HQ Entity Tracker for whale intelligence on this token
13. **If backend online**: Run `POST /api/risk/position-size` with entry/stop for section 13
14. Fill sections 13-17 from analysis (including backend multi-factor score in section 16)
15. Write section 18 Substack one-pager in Asymmetric Jump voice
16. Save to Fund HQ via Firebase (`fundHQ/reports/{id}`)
17. Open report in view mode for review

## Report Storage
- Firebase RTDB: `https://fundhq-8feae-default-rtdb.europe-west1.firebasedatabase.app/fundHQ/reports/{id}`
- Content stored as single string with ═══ dividers
- CRYPTO_SECTIONS array (19 items): ['Intro', 'Overview', 'TL;DR', 'Product & Features', 'Moats', 'Team', 'Governance', 'Tokenomics', 'Backers & Funding', 'Competitive Landscape & Valuation', 'Users, Growth & Revenue', 'Social Sentiment', 'Top Holders & Whale Activity', 'Chart & Technical Analysis', 'Catalysts & FUD', 'Final Thesis', 'Signal', 'Sources', 'Substack One-Pager']

## Scoring Guide
- Rating: Strong Buy / Buy / Speculate / Hold / Sell
- Conviction: High / Medium / Low
- Overall Score: 1-10
- Backend Grade: A (≥4.0) / B (≥3.5) / C (≥3.0) / D (≥2.5) / F (<2.5)
- Backend Signal: STRONG BUY (A) / BUY (B) / HOLD (C) / AVOID (D/F)

## Backend Valuation Verdicts
- **STRONG BUY** — avg >40% undervalued across all methods (rare, high conviction)
- **UNDERVALUED** — avg 15-40% below fair value (good entry, standard size)
- **FAIR** — within ±15-30% of fair value (wait for better entry or hold)
- **OVERVALUED** — 30-80% above fair value (avoid new positions, consider trimming)
- **AVOID** — >80% above fair value (exit or short candidate)

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
- Backend DCF uses 25% discount rate (crypto-appropriate) with 20% annual growth decay — conservative by design
- Backend sector medians are approximate and should be validated against current market conditions
- When backend score disagrees with manual thesis, always explain why — the divergence itself is insight
- Backend auto-discovery (`GET /api/discovery`) is a great starting point for finding research candidates
- Score calibration (`POST /api/calibration/run`) should be run periodically as more trades are logged — it adjusts factor weights based on actual outcomes
- Position sizing from backend includes R-multiples — always present risk in R terms, not just dollar amounts
