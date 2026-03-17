# VC Intelligence Skill

## Trigger
"who raised", "VC investments", "fundraising rounds", "investor portfolio", "100x gems", "seed rounds", "a16z"

## Purpose
Track venture capital funding flows in crypto — who raised, how much, from whom, and what it signals about where the market is going next.

## Data Source
- DefiLlama Raises API (`https://api.llama.fi/raises`) — 5000+ rounds
- CORS-blocked from browser → cached in Firebase `vcRaises` or fallback to web_search
- Free public data, no API key needed (server-side only)

## Investor Tier System
- **Tier 1**: a16z, Paradigm, Polychain, Multicoin Capital, Sequoia, Dragonfly, Framework, Pantera
- **Tier 2**: Binance Labs, Coinbase Ventures, Galaxy Digital, Hack VC, Electric Capital, Variant
- **Tier 3**: Animoca, Jump Crypto, DWF Labs, OKX Ventures, Wintermute
- Tier 1 lead = highest signal. Multiple tier 1 co-invest = very high conviction.

## Round Types
- **Seed** ($1-5M): Earliest stage, highest risk/reward, 100x potential
- **Series A** ($5-20M): Validated product, team survived — "the project is real" filter
- **Series B+** ($20M+): Scaling, lower multiple potential but safer
- **Strategic**: Often exchange/protocol investment, signals listing or integration

## 100x Filter
Flag projects matching:
1. Seed round from Tier 1 VC
2. Novel category or first-mover in emerging trend
3. Low valuation relative to category leaders
4. Multiple chain deployment (cross-chain = larger TAM)
5. Strong team (founders from top protocols)

## Sector Signals
- 3+ raises in same category in 30 days = emerging narrative
- Chain concentration = where ecosystem grows next
- VC thesis clustering = where smart money sees alpha

## Tools
- `get_raises` — Recent rounds filtered by category/chain/round/amount/days
- `search_raises` — Search by project or investor name
- `get_investor_portfolio` — All deals by a specific VC + category breakdown
- `get_raise_stats` — Market overview: total raised, top categories, most active investors

## Key Rules
- Always contextualize raises: compare to similar rounds, sector averages
- Flag 100x candidates prominently with reasoning
- Use tables for multi-project comparisons
- Create alerts (severity: opportunity) for Tier 1 VC-backed seed rounds in hot sectors
