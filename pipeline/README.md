# Signal pipeline

Keyless, stdlib-only Python that pulls crowd and news signals, turns them into hourly
per-symbol features, backtests them against Alpaca bars, and writes a brief for the
trading agent.

## Sources (all free, no API keys)

| source | what | how | history |
|---|---|---|---|
| `alpaca_news` | Benzinga headlines via Alpaca | live API when `ALPACA_API_KEY`/`ALPACA_SECRET` are set, else `analysis/data/news` dumps | full |
| `telegram` | 11 public channels (financialjuice, bloomberg, watcherguru, whale_alert_io, ...) | `t.me/s/<channel>` preview pages, paged with `?before=` | full |
| `reddit` | r/wallstreetbets, stocks, StockMarket, investing, Bitcoin, CryptoCurrency | arctic-shift archive API (minutes of lag) | full |
| `stocktwits` | SPY, QQQ, BTC.X, ETH.X, NVDA, TSLA streams with user Bullish/Bearish labels | public stream API, 30 msgs/page | days (volume-limited) |
| `hackernews` | stories matching market queries | Algolia | full |
| `polymarket` | markets matching macro/crypto keywords, with hourly YES-probability history | gamma + CLOB APIs | full |

Reddit's own API blocks cloud IPs, and the `last30days` skill's Telegram lane needs a paid
ScrapeCreators key, so both are replaced by the archive/preview endpoints above.

## Commands

```bash
# 1. collect a window (backtest: since Aug 1; live: last 96h)
python3 -m pipeline.collect --start 2026-08-01 --end 2026-09-22 --out data/raw
python3 -m pipeline.collect --hours 96 --out data/live

# 2. hourly features per symbol (mentions, z-score vs trailing 7d, sentiment tilt, catalyst tags)
python3 -m pipeline.signals --raw data/raw --out data/features/hourly.json

# 3. backtest every source against forward returns (needs hourly bars in analysis/data/bars_hourly)
python3 -m pipeline.backtest --features data/features/hourly.json --out analysis/backtest_report.md

# 4. brief for the agent
python3 -m pipeline.brief --features data/live/hourly.json --raw data/live --out data/live/brief.md
```

Symbols, subreddits, Telegram channels and catalyst keywords live in `pipeline/config.py`.

## Results so far

See `analysis/backtest_report.md`. Short version for the 2026-08-01..09-22 window: crowd attention spikes
(Reddit, Telegram) carry a modest 3-day edge in BTC, nothing usable on SPY/QQQ, sentiment wording carries no
signal, and the combined signal is too loose to beat being long in a bull market. Treat as filters, re-evaluate
at 3 months.

## Portfolio simulation of the live rules

`python3 -m pipeline.simulate --features data/features/hourly.json --bars analysis/data/bars_hourly` replays the v2
routine (decision times, entry filters, stops, sizing, time limits, trailing stops) over the collected history.
2026-08-08..09-22 on $100k, 15% position cap:

| universe | rules | trades | result |
|---|---|---|---|
| BTC, SPY, QQQ | breakeven exit (old) | 8 | +0.37% |
| BTC, SPY, QQQ | trailing 10%/4% | 6 | +2.72% |
| all 12 symbols | trailing 10%/4%, 2% stock stop | 16 | +3.97% |
| crypto + ETFs only | same | 8 | +4.91% |
| all 12 symbols | single stocks 3% stop / 6% trail (live rules) | 15 | +6.11% |

Buy-and-hold over the same window: BTC +32.5%, ETH +43%, QQQ +3.5%, SPY 0%. Crypto supplies most of the profit; single stocks
need wider stops than ETFs or they get stopped out by noise. Pyramiding into winners and resting breakout buy-orders were
both tested and did not help. Sixteen trades is a small sample; retest at 3 months.
Buy-and-hold over the same window: BTC +32.5%, QQQ +3.3%, SPY +0.1%.

### Universe expansion (2026-09-23)

`pipeline/universe.py` lists 151 symbols (S&P 100, retail favourites, 5 ETFs, 13 Alpaca cryptos); `pipeline/universe_patterns.py`
tags text for all of them (`python3 -m pipeline.check_patterns` prints precision samples). Six weeks from 2026-08-08, $100k, 8 positions:

| config | trades | return | max DD |
|---|---|---|---|
| 12 symbols | 17 | +5.30% | 4.8% |
| 150 symbols, rank by z24 | 22 | +4.60% | 5.4% |
| 150 symbols, rank by growth x log(mentions) (live) | 24 | +5.85% | 5.6% |
| 150 symbols, min 50 mentions | 6 | +2.52% | 1.7% |
| 150 symbols, no crypto | 29 | +2.66% | 7.4% |

The number of symbols is not what drives returns; crypto trends and the trailing exit are. The wider universe with the
growth x log(mentions) ranking is live because it is not worse and adds independent chances. `python3 -m pipeline.experiments`
reruns the grid.

### Strategy lab (2026-09-23)

`python3 -m pipeline.strategies [--start YYYY-MM-DD] [--detail "<name>"]` runs classic strategy families on the same daily
bars, $100k, 0.05%/side costs. Results (return / max drawdown):

| strategy | six weeks from 08-08 | last month from 08-24 |
|---|---|---|
| Buy & hold SPY | -0.4% / 3.1% | +0.7% / 2.5% |
| Buy & hold equal-weight 150 | +5.5% / 3.3% | +2.0% / 3.1% |
| Buy & hold BTC+ETH | +39.7% / 5.7% | +9.0% / 5.7% |
| Live attention trend (hourly sim) | +5.9% / 5.6% | +1.8% / 6.8% |
| Trend, price only (no attention filter) | -3.2% / 9.2% | -0.9% / 8.3% |
| Mean reversion RSI(2), stocks+ETFs | -1.8% / 3.4% | +2.9% / 3.0% |
| Momentum top 8 by 20d return, weekly | +6.6% / 7.3% | +8.8% / 9.7% |
| Momentum top 15 by 10d return, weekly | +7.8% / 7.8% | +6.3% / 8.1% |
| Breakout Donchian 20/10 | +7.0% / 7.2% | +8.0% / 5.7% |
| Combo trend + mean reversion | -2.1% / 7.1% | +0.9% / 4.5% |

The attention filter is what makes the trend strategy work: without it, the same rules lose money. Momentum and breakout were
positive in both windows; mean reversion flips sign between windows. Seven weeks is far too short to choose between them.
