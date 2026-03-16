# Entity Investigation Skill

## Trigger
"investigate wallet", "who is this entity", "entity deep dive", "profile this address"

## Purpose
Cross-venue entity deep dive for the On-Chain Intel division. Takes a wallet address or entity name and produces a comprehensive Entity Dossier.

## Workflow
1. Look up the address on Hyperliquid API (`clearinghouseState` + `userFills`)
2. Compute wallet metrics: account value, open positions, PnL, win rate, trade count
3. Grade the wallet using power-law scoring:
   - Profit factor weighted 35pts
   - Win/loss ratio 15pts
   - Selectivity bonus for <120 trades
   - Penalty for >400 trades
4. Classify entity type: whale, fund, market maker, protocol, insider, copyable trader
5. Detect behavioral patterns: accumulation (stalker mode), distribution, squeeze setups
6. Check regime alignment: does this entity trade with or against the current market regime?

## Inputs
- Wallet address (0x...) OR entity name from Entity Tracker
- Optional: time period for analysis

## Outputs
- Entity Dossier with:
  - Identity: address, label, type, grade
  - Financial: account value, total PnL, win rate, avg trade size
  - Positions: current open positions with entry, size, uPnL
  - Behavior: trading frequency, directional bias, position sizing pattern
  - Pattern: accumulation/distribution/neutral
  - Regime alignment: aligned/misaligned with current regime
  - Recommendation: track/ignore/copy-trade grade

## Key Rules
- Power-law principle: fewer trades + higher conviction = better trader (from Senpi research)
- Grade hierarchy: A+ (elite, <50 trades, >3x profit factor) → A → B+ → B → C
- Always check regime before recommending copy-trade
- Entity types: whale (large individual), fund (institutional), mm (market maker), protocol (treasury), insider (team/early), copyable (consistent edge)

## Hyperliquid API Reference
- `clearinghouseState`: { type: 'clearinghouseState', user: '0x...' }
- `userFills`: { type: 'userFills', user: '0x...' }
- `metaAndAssetCtxs`: { type: 'metaAndAssetCtxs' } (for regime data)
- Endpoint: POST https://api.hyperliquid.xyz/info
