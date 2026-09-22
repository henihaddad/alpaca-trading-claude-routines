# Signal backtest

Events: hourly z-score >= 2.0 and >= 5 mentions. Entry at the next hourly bar. Baseline = every hour with data.


## BTC/USD

| signal | events | +4h mean / win | +24h mean / win | +72h mean / win | strat 72h/stop: trades, total, avg |
|---|---|---|---|---|---|
| baseline (all hours) | 1195 | +0.11% / 55% | +0.65% / 58% | +1.87% / 57% | 17, +26.3%, +1.55% |
| attention spike: alpaca_news | 3 | +0.54% / 100% | +4.09% / 67% | +7.18% / 100% | 1, +13.0%, +13.00% |
| bullish tilt: alpaca_news | 2 | +0.65% / 100% | +2.85% / 50% | +7.52% / 100% | 1, +13.0%, +13.00% |
| attention spike: reddit | 69 | +0.05% / 54% | +0.96% / 61% | +2.32% / 62% | 11, +20.1%, +1.83% |
| bullish tilt: reddit | 19 | +0.15% / 39% | +0.94% / 47% | +1.47% / 59% | 9, +4.0%, +0.44% |
| bearish tilt: reddit | 2 | -1.48% / 0% | -0.27% / 50% | +2.79% / 50% | 2, +5.2%, +2.60% |
| attention spike: telegram | 37 | +0.15% / 53% | +0.77% / 56% | +2.20% / 55% | 11, +15.7%, +1.43% |
| bearish tilt: telegram | 1 | +0.62% / 100% | -1.51% / 0% | -1.59% / 0% | 1, -1.6%, -1.59% |
| combined z_all >= 4 | 125 | +0.19% / 62% | +1.16% / 64% | +2.85% / 72% | 16, +24.6%, +1.54% |
| catalyst: fed (>=3) | 3 | +0.09% / 67% | +2.17% / 100% | +6.58% / 100% | 1, +7.6%, +7.61% |
| catalyst: macro_data (>=3) | 2 | +0.01% / 50% | -0.24% / 50% | +2.38% / 50% | 2, +4.8%, +2.38% |
| catalyst: policy (>=3) | 5 | +0.63% / 80% | +3.40% / 80% | +7.12% / 100% | 2, +14.4%, +7.22% |
| catalyst: geopolitics (>=3) | 2 | -0.40% / 0% | -0.72% / 50% | -1.05% / 0% | 2, -2.1%, -1.05% |
| catalyst: flows (>=3) | 3 | +0.87% / 67% | +2.26% / 33% | +1.64% / 33% | 3, +4.9%, +1.64% |
| 24h attention top decile (z24 >= 53.7) | 4 | +0.15% / 75% | +1.85% / 75% | +2.92% / 100% | 2, +8.0%, +3.99% |

## QQQ

| signal | events | +4h mean / win | +24h mean / win | +72h mean / win | strat 72h/stop: trades, total, avg |
|---|---|---|---|---|---|
| baseline (all hours) | 324 | +0.06% / 37% | +0.23% / 54% | +0.47% / 59% | 16, +4.0%, +0.25% |
| attention spike: alpaca_news | 2 | -0.17% / 0% | +0.27% / 100% | +0.10% / 50% | 2, +0.2%, +0.10% |
| combined z_all >= 4 | 63 | +0.01% / 28% | +0.10% / 52% | +0.06% / 45% | 11, -0.9%, -0.08% |
| 24h attention top decile (z24 >= 34.1) | 3 | -0.04% / 33% | +0.39% / 67% | -0.36% / 33% | 3, -1.1%, -0.36% |

## SPY

| signal | events | +4h mean / win | +24h mean / win | +72h mean / win | strat 72h/stop: trades, total, avg |
|---|---|---|---|---|---|
| baseline (all hours) | 484 | +0.02% / 33% | +0.07% / 47% | +0.14% / 52% | 15, +2.2%, +0.15% |
| attention spike: alpaca_news | 39 | -0.00% / 44% | +0.14% / 59% | +0.24% / 56% | 10, +2.1%, +0.21% |
| combined z_all >= 4 | 47 | +0.07% / 39% | +0.16% / 57% | +0.21% / 54% | 10, +4.1%, +0.41% |
| catalyst: fed (>=3) | 16 | +0.00% / 56% | +0.14% / 62% | +0.38% / 56% | 7, +5.2%, +0.75% |
| catalyst: macro_data (>=3) | 16 | +0.01% / 50% | +0.10% / 50% | +0.10% / 50% | 7, +2.2%, +0.32% |
| catalyst: geopolitics (>=3) | 6 | -0.10% / 17% | -0.00% / 67% | +0.46% / 67% | 3, +1.4%, +0.45% |
| 24h attention top decile (z24 >= 33.7) | 3 | -0.07% / 33% | +0.21% / 33% | +0.21% / 67% | 3, +0.6%, +0.21% |
