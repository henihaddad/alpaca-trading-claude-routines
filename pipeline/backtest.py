"""Evaluate each source's attention/sentiment signal against forward returns.

For every (source, symbol): events = hours where z_<source> >= Z and n_<source> >= MIN_N.
Report mean/median forward return at +4h/+24h/+72h vs the unconditional baseline, hit rate,
and a naive long-only strategy (enter at next bar, hold H hours, stop S%).

    python3 -m pipeline.backtest --features data/features/hourly.json --bars analysis/data/bars_hourly --out analysis/backtest_report.md
"""
import argparse, glob, json, os, statistics as st
from collections import defaultdict
from datetime import datetime, timedelta, timezone

def ts(s): return datetime.fromisoformat(s.replace("Z", "+00:00"))

def load_bars(bars_dir):
    out = {}
    for f in glob.glob(os.path.join(bars_dir, "*.json")):
        sym = os.path.basename(f)[:-5].replace("-", "/")
        j = json.load(open(f)); b = j.get("bars", j)
        if isinstance(b, dict): b = next(iter(b.values()))
        out[sym] = [(ts(x["t"]), float(x["c"])) for x in b]
    return out

def px_after(bars, t, hours, max_gap_h=96):
    target = t + timedelta(hours=hours)
    for bt, c in bars:
        if bt >= target:
            return c if (bt - target) <= timedelta(hours=max_gap_h) else None
    return None

def fwd(bars, t, h):
    p0 = px_after(bars, t, 1); p1 = px_after(bars, t, 1 + h)   # enter next bar, exit h hours later
    return (p1 / p0 - 1) * 100 if p0 and p1 else None

def summarize(rets):
    r = [x for x in rets if x is not None]
    if not r: return None
    return {"n": len(r), "mean": round(st.mean(r), 2), "median": round(st.median(r), 2), "win": round(100 * sum(x > 0 for x in r) / len(r))}

def strategy(bars, events, hold_h=72, stop_pct=3.0):
    """One position at a time. Returns list of trade returns (%)."""
    trades, busy_until = [], None
    for t in sorted(events):
        if busy_until and t < busy_until: continue
        p0 = px_after(bars, t, 1)
        if not p0: continue
        entry_i = next(i for i, (bt, _) in enumerate(bars) if bt >= t + timedelta(hours=1))
        exit_ret = None
        for bt, c in bars[entry_i:]:
            r = (c / p0 - 1) * 100
            if r <= -stop_pct: exit_ret = r; busy_until = bt; break
            if bt >= t + timedelta(hours=1 + hold_h): exit_ret = r; busy_until = bt; break
        if exit_ret is None: continue
        trades.append(exit_ret)
    return trades

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", default="data/features/hourly.json"); ap.add_argument("--bars", default="analysis/data/bars_hourly")
    ap.add_argument("--out", default="analysis/backtest_report.md"); ap.add_argument("--z", type=float, default=2.0); ap.add_argument("--min_n", type=int, default=5)
    a = ap.parse_args()
    feats = json.load(open(a.features)); bars = load_bars(a.bars)
    sources = sorted({k[2:] for f in feats.values() for k in f if k.startswith("n_") and k != "n_all"})
    lines = [f"# Signal backtest\n", f"Events: hourly z-score >= {a.z} and >= {a.min_n} mentions. Entry at the next hourly bar. Baseline = every hour with data.\n"]
    for sym in sorted(bars):
        b = bars[sym]
        hours = {ts(k.split("|")[1]): v for k, v in feats.items() if k.split("|")[0] == sym}
        if not hours: continue
        lines.append(f"\n## {sym}\n")
        lines.append(f"Buy-and-hold over the window: {(b[-1][1] / b[0][1] - 1) * 100:+.1f}% ({b[0][0]:%Y-%m-%d} to {b[-1][0]:%Y-%m-%d}).\n")
        base = {h: summarize([fwd(b, t, h) for t in hours]) for h in (4, 24, 72)}
        lines.append("| signal | events | +4h mean / win | +24h mean / win | +72h mean / win | strat 72h/stop: trades, total, avg |")
        lines.append("|---|---|---|---|---|---|")
        def row(name, evs):
            if not evs: return
            s = {h: summarize([fwd(b, t, h) for t in evs]) for h in (4, 24, 72)}
            tr = strategy(b, evs, stop_pct=3.0 if "/" in sym else 2.0)
            cell = lambda x: f"{x['mean']:+.2f}% / {x['win']}%" if x else "n/a"
            lines.append(f"| {name} | {len(evs)} | {cell(s[4])} | {cell(s[24])} | {cell(s[72])} | {len(tr)}, {sum(tr):+.1f}%, {st.mean(tr):+.2f}% |" if tr else
                         f"| {name} | {len(evs)} | {cell(s[4])} | {cell(s[24])} | {cell(s[72])} | no trades |")
        row("baseline (all hours with data)", list(hours))
        for src in sources:
            row(f"attention spike: {src}", [t for t, f in hours.items() if f.get(f"z_{src}", 0) >= a.z and f.get(f"n_{src}", 0) >= a.min_n])
            row(f"bullish tilt: {src}", [t for t, f in hours.items() if f.get(f"n_{src}", 0) >= a.min_n and (f.get(f"bull_{src}", 0) - f.get(f"bear_{src}", 0)) >= 0.4 * f.get(f"n_{src}", 0)])
            row(f"bearish tilt: {src}", [t for t, f in hours.items() if f.get(f"n_{src}", 0) >= a.min_n and (f.get(f"bear_{src}", 0) - f.get(f"bull_{src}", 0)) >= 0.4 * f.get(f"n_{src}", 0)])
        combo = [t for t, f in hours.items() if f.get("z_all", 0) >= 4]
        row("combined z_all >= 4", combo)
        # show the days the combined signal fired, so a human can sanity-check them against known events
        days = sorted({t.date() for t in combo})
        if days: lines.append(f"\nDays the combined signal fired ({len(days)}): " + ", ".join(d.strftime('%m-%d') for d in days) + "\n")
        for c in ("fed", "macro_data", "policy", "geopolitics", "flows"):
            row(f"catalyst: {c} (>=3)", [t for t, f in hours.items() if f.get(f"cat_{c}", 0) >= 3])
        # daily-aggregated attention: sum of z over trailing 24h, top decile
        daily = {}
        for t in hours:
            daily[t] = sum(f.get("z_all", 0) for tt, f in hours.items() if t - timedelta(hours=24) < tt <= t)
        if daily:
            thr = sorted(daily.values())[int(0.9 * len(daily))]
            row(f"24h attention top decile (z24 >= {thr:.1f})", [t for t, v in daily.items() if v >= thr and t.hour == 14])
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))

if __name__ == "__main__":
    main()
