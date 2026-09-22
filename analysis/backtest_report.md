# Signal backtest — findings (2026-08-01 to 2026-09-22)

Data: 55,100 items (Reddit 24,749 posts from 6 subreddits via arctic-shift; Telegram 12,140 messages from
8 public channels, 8,983 of them financialjuice; Alpaca/Benzinga news 3,023; Hacker News 206; Polymarket 25
markets with 16,411 hourly probability points). Stocktwits is evaluated separately because its public API only
reaches back about five days. Prices: Alpaca hourly bars (IEX feed for stocks). Window: 7 weeks, one crypto
bull run (BTC +34%), flat-to-up indexes (SPY +3.0%, QQQ +8.1%).

## What the numbers say

1. **Crypto: crowd attention carries a modest, real-looking edge over 3 days.** BTC hours where several
   sources spike together (combined z >= 4) returned +2.98% over the next 72h with a 72% hit rate, against
   +1.87% / 57% for all hours. Reddit attention spikes alone: +2.89% / 66% (69 events). Telegram: +2.20% / 55%.
   Alpaca news spikes: +7.2% but only 3 events. The 4 days in the top decile of 24h attention returned +2.9%
   with 4/4 wins, and include Aug 19-21 (the move the old routine missed).
2. **But the combined signal is not selective.** It fired on 40 of 51 days for BTC and 29 of 36 trading days
   for SPY. With a threshold that loose, "signal" mostly means "long in a bull market". The strategy sim
   (enter on signal, hold 72h, 3% stop) made +24.3% on BTC versus +26.3% for entering every hour, i.e. it did
   not beat being long. Hit rate improved; total return did not.
3. **Index ETFs: nothing usable at this horizon.** Best rows on SPY are +0.2 to +0.4% over 3 days versus
   +0.16% baseline, on 40-100 events. That is inside noise and smaller than real-world slippage. QQQ Fed-catalyst
   clusters: +0.72% vs +0.43% (96 events) is the largest, still marginal.
4. **Sentiment tilt (bullish/bearish wording) has no measurable value.** Samples are tiny once a 40% tilt is
   required, and where they exist they go both ways.
5. **Geopolitics catalyst clusters are negative on every symbol** (small n). Worth testing as a "do not add
   risk today" filter, not as a short signal.
6. **Speed is irrelevant at this scale.** The +4h column is near zero for everything on indexes and under
   +0.2% for crypto. Whatever edge exists is a multi-day drift, not a headline reaction.

## What this means for the routine

- Use the pipeline as a **filter and a context brief**, not a trigger. Entries still need price confirmation
  (near 20-day high) and a written thesis with a stop, per routines/daily-paper-trading-v2.md.
- The only source-level edge worth acting on today is **crypto attention from Reddit and Telegram**, sized small.
- **Seven weeks of one bull run is not enough evidence.** Run the pipeline every day, log the brief and the
  decisions, and rerun this backtest at 3 months before trusting any of these numbers.
- The honest expectation is "avoids buying euphoria, catches multi-day attention clusters in crypto", not
  "wins good money".

---

# Signal backtest

Events: hourly z-score >= 2.0 and >= 5 mentions. Entry at the next hourly bar. Baseline = every hour with data.


## BTC/USD

Buy-and-hold over the window: +36.8% (2026-08-01 to 2026-09-22).

| signal | events | +4h mean / win | +24h mean / win | +72h mean / win | strat 72h/stop: trades, total, avg |
|---|---|---|---|---|---|
| baseline (all hours with data) | 1196 | +0.11% / 55% | +0.65% / 58% | +1.87% / 57% | 17, +26.3%, +1.55% |
| attention spike: alpaca_news | 3 | +0.54% / 100% | +4.09% / 67% | +7.18% / 100% | 1, +13.0%, +13.00% |
| bullish tilt: alpaca_news | 2 | +0.65% / 100% | +2.85% / 50% | +7.52% / 100% | 1, +13.0%, +13.00% |
| attention spike: reddit | 69 | +0.05% / 48% | +1.04% / 61% | +2.89% / 66% | 11, +19.2%, +1.75% |
| bullish tilt: reddit | 21 | +0.14% / 40% | +0.65% / 42% | +1.21% / 58% | 10, +0.5%, +0.05% |
| bearish tilt: reddit | 1 | -0.37% / 0% | +2.06% / 100% | +8.39% / 100% | 1, +8.4%, +8.39% |
| attention spike: telegram | 37 | +0.15% / 53% | +0.77% / 56% | +2.20% / 55% | 11, +15.7%, +1.43% |
| bearish tilt: telegram | 1 | +0.62% / 100% | -1.51% / 0% | -1.59% / 0% | 1, -1.6%, -1.59% |
| combined z_all >= 4 | 125 | +0.19% / 61% | +1.20% / 64% | +2.98% / 72% | 16, +24.3%, +1.52% |

Days the combined signal fired (40): 08-02, 08-03, 08-04, 08-05, 08-06, 08-07, 08-10, 08-12, 08-13, 08-14, 08-15, 08-17, 08-18, 08-19, 08-20, 08-21, 08-24, 08-25, 08-26, 08-28, 08-31, 09-01, 09-02, 09-03, 09-04, 09-05, 09-06, 09-07, 09-09, 09-10, 09-11, 09-12, 09-14, 09-15, 09-16, 09-17, 09-18, 09-20, 09-21, 09-22

| catalyst: fed (>=3) | 3 | +0.09% / 67% | +2.17% / 100% | +6.58% / 100% | 1, +7.6%, +7.61% |
| catalyst: macro_data (>=3) | 2 | +0.01% / 50% | -0.24% / 50% | +2.38% / 50% | 2, +4.8%, +2.38% |
| catalyst: policy (>=3) | 5 | +0.63% / 80% | +3.40% / 80% | +7.12% / 100% | 2, +14.4%, +7.22% |
| catalyst: geopolitics (>=3) | 2 | -0.40% / 0% | -0.72% / 50% | -1.05% / 0% | 2, -2.1%, -1.05% |
| catalyst: flows (>=3) | 3 | +0.87% / 67% | +2.26% / 33% | +1.64% / 33% | 3, +4.9%, +1.64% |
| 24h attention top decile (z24 >= 54.1) | 4 | +0.15% / 75% | +1.85% / 75% | +2.92% / 100% | 2, +8.0%, +3.99% |

## QQQ

Buy-and-hold over the window: +8.1% (2026-08-03 to 2026-09-22).

| signal | events | +4h mean / win | +24h mean / win | +72h mean / win | strat 72h/stop: trades, total, avg |
|---|---|---|---|---|---|
| baseline (all hours with data) | 714 | +0.04% / 27% | +0.19% / 51% | +0.43% / 60% | 16, +4.1%, +0.26% |
| attention spike: alpaca_news | 5 | +0.14% / 20% | +1.94% / 100% | +1.31% / 80% | 3, +2.3%, +0.77% |
| attention spike: reddit | 4 | +0.51% / 75% | +0.73% / 100% | +1.48% / 100% | 3, +4.2%, +1.41% |
| bearish tilt: reddit | 1 | +0.23% / 100% | +0.48% / 100% | +0.46% / 100% | 1, +0.5%, +0.46% |
| attention spike: telegram | 49 | +0.10% / 38% | +0.11% / 60% | +0.10% / 55% | 11, +3.4%, +0.31% |
| combined z_all >= 4 | 60 | +0.09% / 42% | +0.44% / 63% | +0.30% / 54% | 11, -0.6%, -0.05% |

Days the combined signal fired (28): 08-03, 08-04, 08-05, 08-06, 08-07, 08-12, 08-13, 08-14, 08-17, 08-19, 08-20, 08-21, 08-25, 08-26, 08-27, 08-28, 08-29, 09-01, 09-02, 09-03, 09-04, 09-05, 09-09, 09-10, 09-11, 09-14, 09-16, 09-21

| catalyst: fed (>=3) | 96 | +0.14% / 50% | +0.25% / 62% | +0.72% / 67% | 15, +5.0%, +0.34% |
| catalyst: macro_data (>=3) | 123 | +0.07% / 31% | +0.18% / 58% | +0.31% / 55% | 14, +7.9%, +0.56% |
| catalyst: policy (>=3) | 1 | +1.55% / 100% | +1.59% / 100% | +3.24% / 100% | 1, +3.2%, +3.24% |
| catalyst: geopolitics (>=3) | 3 | +0.00% / 0% | -0.41% / 0% | -0.67% / 33% | 3, -2.7%, -0.90% |
| 24h attention top decile (z24 >= 34.9) | 3 | -0.04% / 67% | -0.19% / 33% | +0.39% / 67% | 3, +1.2%, +0.39% |

## SPY

Buy-and-hold over the window: +3.0% (2026-08-03 to 2026-09-22).

| signal | events | +4h mean / win | +24h mean / win | +72h mean / win | strat 72h/stop: trades, total, avg |
|---|---|---|---|---|---|
| baseline (all hours with data) | 831 | +0.02% / 23% | +0.07% / 44% | +0.16% / 52% | 15, +1.5%, +0.10% |
| attention spike: alpaca_news | 41 | +0.02% / 46% | +0.20% / 61% | +0.33% / 59% | 10, +3.2%, +0.32% |
| attention spike: reddit | 14 | +0.17% / 43% | -0.01% / 29% | +0.19% / 50% | 7, +1.1%, +0.15% |
| bullish tilt: reddit | 3 | +0.23% / 67% | +0.55% / 33% | +0.57% / 67% | 1, +1.6%, +1.59% |
| bearish tilt: reddit | 1 | +0.15% / 100% | +0.30% / 100% | +0.30% / 100% | 1, +0.3%, +0.30% |
| attention spike: telegram | 51 | +0.06% / 38% | +0.07% / 58% | +0.04% / 49% | 11, +1.8%, +0.17% |
| combined z_all >= 4 | 73 | +0.11% / 52% | +0.31% / 61% | +0.37% / 57% | 11, +3.6%, +0.32% |

Days the combined signal fired (29): 08-03, 08-04, 08-05, 08-06, 08-07, 08-11, 08-12, 08-13, 08-14, 08-17, 08-18, 08-19, 08-20, 08-25, 08-26, 08-27, 08-28, 08-29, 08-31, 09-01, 09-02, 09-03, 09-04, 09-10, 09-11, 09-14, 09-16, 09-17, 09-21

| catalyst: fed (>=3) | 105 | +0.06% / 48% | +0.07% / 51% | +0.25% / 59% | 15, +3.4%, +0.23% |
| catalyst: macro_data (>=3) | 133 | +0.03% / 30% | +0.05% / 49% | +0.09% / 48% | 14, +3.9%, +0.28% |
| catalyst: policy (>=3) | 1 | +1.28% / 100% | +1.12% / 100% | +1.65% / 100% | 1, +1.7%, +1.65% |
| catalyst: geopolitics (>=3) | 11 | -0.05% / 27% | -0.02% / 45% | +0.25% / 55% | 5, +1.9%, +0.38% |
| 24h attention top decile (z24 >= 46.4) | 4 | +0.12% / 75% | +0.29% / 50% | +0.77% / 100% | 2, +2.1%, +1.06% |
