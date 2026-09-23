"""Rolling-start robustness test: run each strategy from many start dates for a fixed holding window and
report the distribution of outcomes instead of one lucky (or unlucky) number.

    python3 -m pipeline.rolling --bars <dir> --months 6 --every 14
"""
import argparse, statistics as st
from datetime import date, timedelta
from . import strategies as S

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars", default="analysis/data/bars_daily_2y"); ap.add_argument("--months", type=int, default=6)
    ap.add_argument("--every", type=int, default=14, help="days between start dates"); ap.add_argument("--first", default="2024-10-15")
    a = ap.parse_args()
    bars = S.load(a.bars); alldays = sorted({d for b in bars.values() for d in b})
    syms = sorted(bars); etfs = [s for s in syms if s in S.ETFS]; stocks = [s for s in syms if s not in S.ETFS and "/" not in s]
    strat = {
        "Buy & hold SPY": lambda: S.s_buyhold(["SPY"]),
        "Momentum top8/20d weekly": lambda: S.s_momentum(syms),
        "Momentum top15/10d weekly": lambda: S.s_momentum(syms, top=15, lookback=10),
        "Breakout 20/10": lambda: S.s_breakout(syms),
        "Trend price-only": lambda: S.s_trend(syms),
        "Mean reversion RSI2 ETFs": lambda: S.s_meanrev(etfs, max_pos=3, cap=0.3),
    }
    starts = []; d = date.fromisoformat(a.first); last = date.fromisoformat(alldays[-1]) - timedelta(days=30 * a.months)
    while d <= last: starts.append(d.isoformat()); d += timedelta(days=a.every)
    res = {k: [] for k in strat}
    for s0 in starts:
        end = (date.fromisoformat(s0) + timedelta(days=30 * a.months)).isoformat()
        days = [x for x in alldays if x <= end]
        for k, mk in strat.items():
            dec, man = mk(); r = S.run(k, bars, days, s0, dec, man); res[k].append((s0, r["ret"], r["dd"]))
    spy = {s0: r for s0, r, _ in res["Buy & hold SPY"]}
    print(f"# Rolling test: {len(starts)} start dates every {a.every} days from {starts[0]} to {starts[-1]}, {a.months}-month windows, {len(bars)} symbols\n")
    print("| strategy | median return | worst window | best window | % windows > 0 | % windows beat SPY | median max DD | worst max DD |")
    print("|---|---|---|---|---|---|---|---|")
    for k, rows in res.items():
        r = [x[1] for x in rows]; dd = [x[2] for x in rows]
        beat = sum(1 for s0, x, _ in rows if x > spy[s0]) / len(rows) * 100
        print(f"| {k} | {st.median(r):+.1f}% | {min(r):+.1f}% | {max(r):+.1f}% | {sum(1 for x in r if x > 0)/len(r)*100:.0f}% | {beat:.0f}% | {st.median(dd):.1f}% | {max(dd):.1f}% |")

if __name__ == "__main__":
    main()
