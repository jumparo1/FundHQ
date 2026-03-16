# Hyperliquid Agent — Domain Knowledge

## Senpi Learnings (22 agents, $22K real capital, 5000+ trades — March 2026)

### Core Truth: Fewer Trades + Higher Conviction = Better Results
- Every agent above 400 trades was deeply negative
- Every agent below 120 trades was positive
- More trades = more churn, more fees, more noise exposure
- A 43% win rate prints money when avg winner is 10x avg loser (power law)

### Power Law Returns
- 3-5 trades produce ALL the profit across top agents
- Everything else is small losses cut fast
- Example: Fox's 3 best trades earned +$350, other 46 trades combined lost -$100, net: +$248
- Design for: enter with conviction, cut losers fast, let winners trail

### Real-Time Smart Money Is THE Edge
- Watching where top traders' profits concentrate in real-time beats all other signals
- Agents that ignored smart money data (pure technical) all lost
- Agents using stale/historical whale data also lost
- What works: real-time detection of smart money rotation into an asset

### Two Entry Modes (Stalker + Striker)
- **Stalker mode**: quiet accumulation — multiple whales slowly building positions before the crowd arrives (biggest winners come from here)
- **Striker mode**: violent breakout with volume confirmation — enter as explosion happens, but only if real volume backs it up (filters fake pumps)
- A single entry mode forces you to optimize for one and miss the other

### Mean Reversion Struggles on Perps
- Hyperliquid perps trend more than they revert
- Buying dips in downtrends is the most expensive mistake
- Fix: macro regime filter — don't buy dips when BTC 4H trend is bearish
- This filter would have prevented 50% of losing trades in mean-reversion agents

### Agents Self-Modify and Always Make It Worse
- When agents hit losing streaks, they loosen filters, raise leverage, remove gates
- Every single time this accelerated losses
- Solution: protective gates must be in code (hard limits), not configurable parameters

### Winning Config Pattern
- Stagnation take-profit (exit positions that go nowhere)
- 10% daily loss limit (hard gate)
- DSL High Water stops (lock % of peak unrealized PnL)
- Single-asset hunters with lifecycle: hunt -> ride -> stalk -> reload

## Hyperliquid API Capabilities
- `clearinghouseState` — wallet positions, margin, PnL
- `userFills` — trade history with closedPnl per fill
- `metaAndAssetCtxs` — all perps: OI, funding, volume, mark/oracle price
- `recentTrades` — recent trades per coin (includes buyer/seller addresses)
- WebSocket: real-time trade stream per coin
- Leaderboard: `stats-data.hyperliquid.xyz/Mainnet/leaderboard` (32K traders, free)

## Agent Architecture
- Python async (aiohttp + websockets)
- Firebase REST API for alerts and data persistence
- Fund HQ frontend reads same Firebase paths
- CLI: `profile <addr>`, `discover`, `scan`, `regime`, `signals`

## Signal Quality Hierarchy
1. **A-grade whale opens position on coin with bullish regime** — highest conviction
2. **Multiple whales accumulating same coin (stalker mode)** — strong
3. **Single whale opens large position, neutral regime** — moderate
4. **Whale activity in bearish regime** — low conviction, possible contrarian
5. **Raw whale trade with no context** — noise, suppress

## Market Regime Definitions
- **Risk-On**: BTC funding positive, OI rising, volume expanding — favor longs
- **Risk-Off**: BTC funding negative or flat, OI declining, volume contracting — favor shorts or cash
- **Squeeze Setup**: Extreme funding + high short OI on specific coins — fade the crowd
- **Neutral**: Mixed signals — require higher conviction threshold for alerts
