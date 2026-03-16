# Trade Plan Skill

## Trigger
"create trade plan", "setup for X", "trade plan", "plan this trade"

## Purpose
Generate a structured trade plan from a playbook + confluence scoring. Used by the Technical Analysis division before any position entry.

## Workflow
1. Identify the asset and direction (long/short)
2. Select applicable playbook (CRT+CISD, Spike Exhaustion, MR Long, Momo Short, or Discretionary)
3. Check market regime alignment:
   - Risk-On: momentum + breakout playbooks active
   - Neutral: mean reversion playbooks active, reduced sizing
   - Risk-Off: defensive only — shorts + hedges
4. Define entry zone, stop loss, and target(s)
5. Calculate risk:reward ratio (minimum 2:1 required)
6. Score confluence across 4 factors:
   - On-Chain signal (25%): entity grade, flow size, regime alignment
   - Fundamental thesis (25%): conviction score, catalyst proximity, risk flags
   - Technical setup (30%): playbook match, R:R ratio, structure quality
   - Regime alignment (20%): does current regime support this trade type?
7. Determine position size based on confluence score:
   - Score < 3.5: NO TRADE
   - Score 3.5-3.9: 1% risk
   - Score 4.0-4.4: 2% risk
   - Score 4.5+: 3% risk (rare, high conviction)

## Inputs
- Asset ticker (e.g., BTC, ETH, SOL)
- Direction (long/short)
- Playbook name
- Entry price, stop price, target price
- Optional: thesis notes, on-chain signal reference

## Outputs
Trade Plan document with:
- Asset, direction, timeframe
- Playbook and regime check (pass/fail)
- Entry zone, stop loss, target(s)
- R:R ratio
- Confluence score breakdown (4 factors, each 1-5)
- Weighted total score
- Position sizing recommendation
- Thesis summary
- Invalidation criteria

## Playbook Reference
| Playbook | Type | Valid Regime | Key Signal |
|----------|------|-------------|------------|
| CRT + CISD | Mean Reversion | Neutral/Range | Liquidity sweep + candle range theory |
| Spike Exhaustion | Mean Reversion | Neutral/Range | 2-of-4: RSI + StochRSI + Momentum + Volume |
| MR Long (Journal) | Mean Reversion | Risk-On pullback | EMA 21 + RSI < 40 + hammer + BB touch |
| Momo Short | Momentum | Risk-Off | Breakdown below support + volume confirm |

## Key Rules
- NEVER trade against the regime without explicit override
- Minimum R:R of 2:1 required
- Minimum confluence of 3.5 required
- Senpi rule: 3-5 trades make all the money — be selective
- Always link to the signal source (on-chain, fundamental, or TA)
