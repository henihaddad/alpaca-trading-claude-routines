"""Simulate the v2 routine rules as a portfolio over the collected history.

Decision times: 01:00, 13:00, 20:00 UTC daily (the live schedule). At each one, per symbol:
  attention: 24h mentions (excl. stocktwits) >= RATIO x prior-72h daily avg, or z24 >= Z; plus a catalyst tag other than price_level
  geopolitics filter: skip if geo share > 50% and no flows/fed/earnings
  price: last close within 3% of 20-day high and 5-day return > 0
  entry next hourly bar; stop 3% (crypto) / 2% (stocks); time limit 5 trading days (exit if below entry); one position per symbol
  size: risk 0.5% of equity / stop distance, cap 8% of equity
Stocks only trade while the US market is open (13:30-20:00 UTC), so the 01:00 decision is crypto-only.

    python3 -m pipeline.simulate --features data/features/hourly.json --bars analysis/data/bars_hourly
"""
import argparse, json, os, glob
from collections import defaultdict
from datetime import datetime, timedelta, timezone

def ts(s): return datetime.fromisoformat(s.replace("Z", "+00:00"))

def load_bars(d):
    out = {}
    for f in glob.glob(os.path.join(d, "*.json")):
        sym = os.path.basename(f)[:-5].replace("-", "/")
        j = json.load(open(f)); b = j.get("bars", j)
        if isinstance(b, dict): b = next(iter(b.values()))
        out[sym] = [(ts(x["t"]), float(x["o"]), float(x["h"]), float(x["l"]), float(x["c"])) for x in b]
    return out

def daily_closes(bars):
    byday = {}
    for t, o, h, l, c in bars: byday[t.date()] = c
    return sorted(byday.items())

def attention(feats_sym, t, ratio_thr, z_thr):
    last = [(k, f) for k, f in feats_sym.items() if t - timedelta(hours=24) < k <= t]
    prior = [(k, f) for k, f in feats_sym.items() if t - timedelta(hours=96) < k <= t - timedelta(hours=24)]
    n = lambda f: sum(v for kk, v in f.items() if kk.startswith("n_") and kk not in ("n_all", "n_stocktwits"))
    n24 = sum(n(f) for _, f in last); nprior = sum(n(f) for _, f in prior) / 3
    z24 = sum(v for _, f in last for kk, v in f.items() if kk.startswith("z_") and kk not in ("z_all", "z_stocktwits"))
    cats = defaultdict(float)
    for _, f in last:
        for kk, v in f.items():
            if kk.startswith("cat_"): cats[kk[4:]] += v
    tot = sum(cats.values()); geo = cats.get("geopolitics", 0) / tot if tot else 0
    has_cat = any(c != "price_level" and v > 0 for c, v in cats.items())
    hot = (nprior >= 3 and n24 >= ratio_thr * nprior) or z24 >= z_thr
    blocked = geo > 0.5 and not any(cats.get(c, 0) for c in ("flows", "fed", "earnings"))
    return hot and has_cat and not blocked, n24, nprior, z24, geo

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", default="data/features/hourly.json"); ap.add_argument("--bars", default="analysis/data/bars_hourly")
    ap.add_argument("--equity", type=float, default=100000); ap.add_argument("--ratio", type=float, default=2.0); ap.add_argument("--z", type=float, default=4.0)
    ap.add_argument("--risk", type=float, default=0.005); ap.add_argument("--start", default="2026-08-08")
    ap.add_argument("--trail_crypto", type=float, default=0.10, help="after time limit, trail stop this fraction below the highest close (0 = breakeven rule)")
    ap.add_argument("--trail_stock", type=float, default=0.04)
    a = ap.parse_args()
    feats = defaultdict(dict)
    for k, f in json.load(open(a.features)).items():
        s, h = k.split("|"); feats[s][ts(h)] = f
    bars = load_bars(a.bars); daily = {s: daily_closes(b) for s, b in bars.items()}
    equity, cash = a.equity, a.equity
    open_pos, trades, log = {}, [], []
    t0 = datetime.fromisoformat(a.start).replace(tzinfo=timezone.utc)
    end = max(b[-1][0] for b in bars.values())
    decisions = []
    d = t0
    while d <= end:
        for hr in (1, 13, 20): decisions.append(d.replace(hour=hr, minute=0))
        d += timedelta(days=1)
    for t in decisions:
        # 1) manage open positions bar by bar up to t (stops, time limits)
        for sym in list(open_pos):
            p = open_pos[sym]
            for bt, o, h, l, c in bars[sym]:
                if bt <= p["last_checked"] or bt > t: continue
                p["last_checked"] = bt
                p["hi"] = max(p.get("hi", p["entry"]), c)
                trail = a.trail_crypto if "/" in sym else a.trail_stock
                if trail and bt >= p["t_in"] + timedelta(days=7):
                    p["stop"] = max(p["stop"], p["hi"] * (1 - trail))
                if l <= p["stop"]:
                    px = min(p["stop"], o); r = (px / p["entry"] - 1); pnl = p["qty"] * (px - p["entry"])
                    cash += p["qty"] * px; trades.append((sym, p["t_in"], bt, p["entry"], px, r * 100, pnl, "stop")); del open_pos[sym]; break
            if sym in open_pos and t >= p["t_in"] + timedelta(days=7):
                c = next((c for bt, o, h, l, c in reversed(bars[sym]) if bt <= t), None)
                if c and c < p["entry"]:
                    pnl = p["qty"] * (c - p["entry"]); cash += p["qty"] * c
                    trades.append((sym, p["t_in"], t, p["entry"], c, (c / p["entry"] - 1) * 100, pnl, "timeout")); del open_pos[sym]
                elif c and not (a.trail_crypto if "/" in sym else a.trail_stock):  # breakeven rule
                    p["stop"] = max(p["stop"], p["entry"])
        # 2) mark equity
        mv = sum(p["qty"] * next((c for bt, o, h, l, c in reversed(bars[s]) if bt <= t), p["entry"]) for s, p in open_pos.items())
        equity = cash + mv
        # 3) entries
        for sym in bars:
            if sym in open_pos or sym not in feats: continue
            is_crypto = "/" in sym
            if not is_crypto and t.hour == 1: continue
            ok, n24, nprior, z24, geo = attention(feats[sym], t, a.ratio, a.z)
            if not ok: continue
            dc = [(dd, c) for dd, c in daily[sym] if dd < t.date()][-20:]
            if len(dc) < 20: continue
            closes = [c for _, c in dc]; last = closes[-1]; hi20 = max(closes); r5 = last / closes[-6] - 1
            if last < hi20 * 0.97 or r5 <= 0: continue
            nxt = next(((bt, o) for bt, o, h, l, c in bars[sym] if bt > t), None)
            if not nxt: continue
            entry = nxt[1]; stop_pct = 0.03 if is_crypto else 0.02
            value = min(a.risk * equity / stop_pct, 0.08 * equity, cash)
            if value < 100: continue
            qty = value / entry; cash -= value
            open_pos[sym] = {"qty": qty, "entry": entry, "stop": entry * (1 - stop_pct), "t_in": nxt[0], "last_checked": nxt[0]}
            log.append(f"{t:%m-%d %H:%M} ENTER {sym} @ {entry:.2f} size {value:,.0f} (n24 {n24:.0f} vs {nprior:.0f}/day, z24 {z24:.0f}, geo {geo:.0%})")
    # close remaining at last price
    for sym, p in open_pos.items():
        c = bars[sym][-1][4]; pnl = p["qty"] * (c - p["entry"]); cash += p["qty"] * c
        trades.append((sym, p["t_in"], bars[sym][-1][0], p["entry"], c, (c / p["entry"] - 1) * 100, pnl, "open@end"))
    equity = cash
    print(f"# v2 rule simulation {a.start} -> {end:%Y-%m-%d}  (ratio>={a.ratio}x or z24>={a.z}; risk {a.risk*100:.1f}%/trade)\n")
    for l in log: print("- " + l)
    print("\n| symbol | in | out | entry | exit | ret | pnl $ | why |\n|---|---|---|---|---|---|---|---|")
    for s, ti, to, e, x, r, pnl, why in trades: print(f"| {s} | {ti:%m-%d %H:%M} | {to:%m-%d %H:%M} | {e:.2f} | {x:.2f} | {r:+.2f}% | {pnl:+,.0f} | {why} |")
    wins = [x for x in trades if x[6] > 0]
    print(f"\nTrades: {len(trades)}, wins {len(wins)}, total P&L ${sum(x[6] for x in trades):+,.0f}, final equity ${equity:,.0f} ({(equity/a.equity-1)*100:+.2f}%)")
    for sym in bars:
        d0 = next((c for dd, c in daily[sym] if dd >= t0.date()), None); print(f"buy&hold {sym}: {(bars[sym][-1][4]/d0-1)*100:+.1f}%")

if __name__ == "__main__":
    main()
