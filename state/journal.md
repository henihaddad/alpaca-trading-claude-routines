# Trading journal (agent memory)

## Positions
| symbol | qty | entry | stop | target / time limit | thesis | invalidation | opened |
|---|---|---|---|---|---|---|---|
| BTC/USD | 0.0015052 | 64977.12 | 78000 (trailing, below 20d low) | reassess weekly | legacy $100 test position from 2026-08-08; now +32% | close below 20-day low | 2026-08-08 |
| QQQ | 5 | 725.68 | 715 | reassess 2026-09-29 | legacy position, no thesis recorded by the old routine | close below 20-day low | 2026-08-10/14 |
| SPY | 4 | 772.93 | 757 | reassess 2026-09-29 | legacy position, no thesis recorded by the old routine | close below 20-day low | 2026-08-10 |

## Watchlist
| symbol | waiting for |
|---|---|
| ETH/USD | attention spike with flows/policy catalyst and price within 3% of 20-day high |
| NVDA | earnings or policy catalyst with attention >= 2x and breakout |

## Run log
| date (UTC) | equity | decisions | why |
|---|---|---|---|
| 2026-09-22 | 100130 | none (journal created) | review found 27 idle runs; strategy v2 defined |

## Lessons
- 2026-08-19..21: BTC +34% in 3 days after ETF-inflow and policy-summit headlines clustered over 48h. The old routine ran every day and never added. Attention clusters plus breakout are the signal; single headlines are not.
- 2026-08-14: QQQ was bought on "record highs" headlines and fell 2.8% over 5 days. Buying euphoria with no catalyst tag is not an entry.
