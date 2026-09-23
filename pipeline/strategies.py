"""Strategy lab: run classic strategy families on the same daily bars, same capital, same window.

    python3 -m pipeline.strategies --start 2026-08-08

Each strategy decides once per day at the close and trades at the next day's open. Stops are checked
against the next days' lows. Costs: 0.05% per side (spread/slippage). $100k, same risk caps as the live agent.
"""
import argparse, glob, json, os, math, statistics as st
from collections import defaultdict
from datetime import date

COST = 0.0005
ETFS = {"SPY", "QQQ", "VOO", "IWM", "DIA"}

def load(d):
    out = {}
    for f in glob.glob(os.path.join(d, "*.json")):
        sym = os.path.basename(f)[:-5].replace("-", "/")
        j = json.load(open(f)); b = j.get("bars", j)
        if isinstance(b, dict): b = next(iter(b.values()), [])
        rows = {}
        for x in b: rows[x["t"][:10]] = (x["o"], x["h"], x["l"], x["c"])
        if len(rows) >= 25: out[sym] = rows
    return out

def rsi(closes, n=2):
    g = [max(0, closes[i] - closes[i - 1]) for i in range(1, len(closes))][-n:]
    l = [max(0, closes[i - 1] - closes[i]) for i in range(1, len(closes))][-n:]
    ag, al = sum(g) / n, sum(l) / n
    return 100.0 if al == 0 else 100 - 100 / (1 + ag / al)

class Book:
    def __init__(self, cash): self.cash = cash; self.pos = {}; self.trades = []; self.curve = []
    def value(self, px): return self.cash + sum(p["qty"] * px.get(s, p["entry"]) for s, p in self.pos.items())
    def buy(self, s, price, value, day, stop=None, meta=None):
        value = min(value, self.cash)
        if value < 100 or s in self.pos: return
        price *= 1 + COST; q = value / price; self.cash -= value
        self.pos[s] = {"qty": q, "entry": price, "day": day, "stop": stop, "hi": price, **(meta or {})}
    def sell(self, s, price, day, why):
        p = self.pos.pop(s); price *= 1 - COST
        self.cash += p["qty"] * price
        self.trades.append((s, p["day"], day, p["entry"], price, (price / p["entry"] - 1) * 100, p["qty"] * (price - p["entry"]), why))

def run(name, bars, days, start, decide, manage, equity0=100000.0):
    """decide(ctx) -> list of (sym, value, stop, meta); manage(ctx, sym, pos) -> exit reason or None."""
    bk = Book(equity0); pending_buys, pending_sells = [], []
    for i, d in enumerate(days):
        if d < start: continue
        px_open = {s: bars[s][d][0] for s in bars if d in bars[s]}
        px_close = {s: bars[s][d][3] for s in bars if d in bars[s]}
        # 1) execute yesterday's decisions at today's open
        for s, why in pending_sells:
            if s in bk.pos and s in px_open: bk.sell(s, px_open[s], d, why)
        for s, value, stop_pct, meta in pending_buys:
            if s in px_open and s not in bk.pos:
                o = px_open[s]; bk.buy(s, o, value, d, stop=o * (1 - stop_pct) if stop_pct else None, meta=meta)
        pending_buys, pending_sells = [], []
        # 2) intraday stops
        for s in list(bk.pos):
            p = bk.pos[s]
            if s in bars and d in bars[s] and p["stop"] and bars[s][d][2] <= p["stop"]:
                bk.sell(s, min(p["stop"], bars[s][d][0]), d, "stop")
        # 3) end of day: update highs, strategy management, new decisions
        hist = {s: [bars[s][x][3] for x in days[:i + 1] if x in bars[s]] for s in bars}
        eq = bk.value(px_close); bk.curve.append((d, eq))
        ctx = {"day": d, "hist": hist, "equity": eq, "book": bk, "px": px_close, "bars": bars, "days": days[:i + 1]}
        for s, p in list(bk.pos.items()):
            if s in px_close: p["hi"] = max(p["hi"], px_close[s])
            why = manage(ctx, s, p)
            if why: pending_sells.append((s, why))
        free = [c for c in decide(ctx) if c[0] not in bk.pos]
        pending_buys = free
    last = days[-1]
    for s in list(bk.pos):
        bk.sell(s, bars[s][last][3] / (1 - COST) if last in bars[s] else bk.pos[s]["entry"], last, "open@end")
    peak, dd = 0, 0
    for _, e in bk.curve: peak = max(peak, e); dd = max(dd, (peak - e) / peak)
    ret = (bk.cash / equity0 - 1) * 100
    wins = sum(1 for t in bk.trades if t[6] > 0)
    # daily returns for a Sharpe-like number
    rets = [bk.curve[k][1] / bk.curve[k - 1][1] - 1 for k in range(1, len(bk.curve))]
    sharpe = (st.mean(rets) / st.pstdev(rets) * math.sqrt(252)) if len(rets) > 2 and st.pstdev(rets) > 0 else 0
    return {"name": name, "trades": len(bk.trades), "wins": wins, "pnl": bk.cash - equity0, "ret": ret, "dd": dd * 100,
            "sharpe": sharpe, "trade_list": bk.trades, "curve": bk.curve}

# ---------------- strategies ----------------
def slots(ctx, max_pos): return max(0, max_pos - len(ctx["book"].pos))

def s_buyhold(symbols):
    def decide(ctx):
        if ctx["book"].pos or ctx["book"].trades or "SPY" not in ctx["px"]: return []
        n = len([s for s in symbols if s in ctx["px"]])
        return [(s, ctx["equity"] / n, None, {}) for s in symbols if s in ctx["px"]]
    return decide, lambda ctx, s, p: None

def s_trend(universe, max_pos=8, cap=0.15, stop_stock=0.03, stop_etf=0.02, stop_crypto=0.03):
    """Price-only trend: close within 3% of 20d high, 5d return > 0; rank by 20d return; trail after 5 days."""
    def stop_of(s): return stop_crypto if "/" in s else stop_etf if s in ETFS else stop_stock
    def trail_of(s): return 0.10 if "/" in s else 0.04 if s in ETFS else 0.06
    def decide(ctx):
        c = []
        for s in universe:
            h = ctx["hist"].get(s, [])
            if len(h) < 21: continue
            hi20 = max(h[-20:]); r5 = h[-1] / h[-6] - 1; r20 = h[-1] / h[-21] - 1
            if h[-1] >= hi20 * 0.97 and r5 > 0: c.append((r20, s))
        c.sort(reverse=True)
        return [(s, min(0.005 * ctx["equity"] / stop_of(s), cap * ctx["equity"]), stop_of(s), {}) for _, s in c[:slots(ctx, max_pos)]]
    def manage(ctx, s, p):
        held = len([d for d in ctx["days"] if d >= p["day"]])
        if held >= 5:
            if ctx["px"].get(s, p["entry"]) < p["entry"]: return "timeout"
            p["stop"] = max(p["stop"] or 0, p["hi"] * (1 - trail_of(s)))
        return None
    return decide, manage

def s_meanrev(universe, max_pos=8, cap=0.15, rsi_in=10, exit_days=5):
    """Connors-style: uptrend (above 20d avg of 20 days ago... simplified: close > 20d SMA*0.97) and RSI(2) < rsi_in.
    Exit when close > 5d SMA or after exit_days. Wide 8% disaster stop."""
    def decide(ctx):
        c = []
        for s in universe:
            h = ctx["hist"].get(s, [])
            if len(h) < 21: continue
            sma20 = sum(h[-20:]) / 20; r = rsi(h[-3:], 2)
            if h[-1] > sma20 * 0.97 and r < rsi_in: c.append((r, s))
        c.sort()
        return [(s, cap * ctx["equity"] * 0.7, 0.08, {}) for _, s in c[:slots(ctx, max_pos)]]
    def manage(ctx, s, p):
        h = ctx["hist"][s]; sma5 = sum(h[-5:]) / 5
        held = len([d for d in ctx["days"] if d >= p["day"]])
        if h[-1] > sma5: return "reverted"
        if held >= exit_days: return "timeout"
        return None
    return decide, manage

def s_momentum(universe, top=8, lookback=20, rebalance_every=5):
    """Cross-sectional momentum: every N days hold the top-K by lookback return, equal weight. No stops."""
    state = {"n": 0}
    def decide(ctx):
        state["n"] += 1
        if (state["n"] - 1) % rebalance_every: return []
        sc = []
        for s in universe:
            h = ctx["hist"].get(s, [])
            if len(h) > lookback: sc.append((h[-1] / h[-1 - lookback] - 1, s))
        sc.sort(reverse=True); state["keep"] = {s for _, s in sc[:top]}
        return [(s, ctx["equity"] / top, None, {}) for _, s in sc[:top]]
    def manage(ctx, s, p):
        if (state["n"] - 1) % rebalance_every == 0 and s not in state.get("keep", {s}): return "rebalance"
        return None
    return decide, manage

def s_breakout(universe, max_pos=8, cap=0.15):
    """Donchian: buy a close above the prior 20d high; exit on close below the 10d low. 2x ATR-ish stop = 6%."""
    def decide(ctx):
        c = []
        for s in universe:
            h = ctx["hist"].get(s, [])
            if len(h) < 22: continue
            if h[-1] > max(h[-21:-1]): c.append((h[-1] / max(h[-21:-1]) - 1, s))
        c.sort(reverse=True)
        return [(s, cap * ctx["equity"] * 0.6, 0.06, {}) for _, s in c[:slots(ctx, max_pos)]]
    def manage(ctx, s, p):
        h = ctx["hist"][s]
        return "10d low" if len(h) > 11 and h[-1] < min(h[-11:-1]) else None
    return decide, manage

def s_combo(universe, max_pos=8):
    """Half the slots trend, half mean reversion (each sized for its own budget)."""
    td, tm = s_trend(universe, max_pos=max_pos // 2, cap=0.12)
    md, mm = s_meanrev(universe, max_pos=max_pos // 2, cap=0.12)
    tags = {}
    def decide(ctx):
        book = ctx["book"]
        nt = sum(1 for p in book.pos.values() if p.get("k") == "t"); nm = sum(1 for p in book.pos.values() if p.get("k") == "m")
        out = []
        saved = book.pos
        out += [(s, v, sp, {"k": "t"}) for s, v, sp, _ in td(ctx)[: max(0, max_pos // 2 - nt)]]
        out += [(s, v, sp, {"k": "m"}) for s, v, sp, _ in md(ctx)[: max(0, max_pos // 2 - nm)] if s not in {o[0] for o in out}]
        return out
    def manage(ctx, s, p): return (tm if p.get("k") == "t" else mm)(ctx, s, p)
    return decide, manage

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars", default="analysis/data/bars_daily"); ap.add_argument("--start", default="2026-08-08")
    ap.add_argument("--detail", default="", help="print the trade list for this strategy name")
    a = ap.parse_args()
    bars = load(a.bars)
    days = sorted({d for b in bars.values() for d in b})
    crypto = sorted(s for s in bars if "/" in s); etfs = sorted(s for s in bars if s in ETFS)
    stocks = sorted(s for s in bars if s not in ETFS and "/" not in s); allsyms = sorted(bars)
    # stocks trade only on weekdays; crypto has weekend bars -> use only days where SPY traded for decisions on stocks
    confs = [
        ("Buy & hold SPY", s_buyhold(["SPY"])),
        ("Buy & hold equal-weight all", s_buyhold(allsyms)),
        ("Buy & hold BTC+ETH", s_buyhold(["BTC/USD", "ETH/USD"])),
        ("Trend (price only), all", s_trend(allsyms)),
        ("Trend (price only), stocks+ETFs", s_trend(stocks + etfs)),
        ("Mean reversion RSI2, stocks+ETFs", s_meanrev(stocks + etfs)),
        ("Mean reversion RSI2, ETFs only", s_meanrev(etfs, max_pos=3, cap=0.3)),
        ("Mean reversion RSI2, all", s_meanrev(allsyms)),
        ("Momentum top8/20d, weekly", s_momentum(allsyms)),
        ("Momentum top8/20d, weekly, stocks", s_momentum(stocks)),
        ("Momentum top15/10d, weekly", s_momentum(allsyms, top=15, lookback=10)),
        ("Breakout Donchian 20/10, all", s_breakout(allsyms)),
        ("Combo trend + mean reversion", s_combo(allsyms)),
    ]
    print(f"# Strategy lab {a.start} -> {days[-1]}, $100k, cost {COST*100:.2f}%/side, {len(bars)} symbols\n")
    print("| strategy | trades | wins | P&L $ | return | max DD | Sharpe (ann.) |\n|---|---|---|---|---|---|---|")
    res = {}
    for name, (d, m) in confs:
        r = run(name, bars, days, a.start, d, m); res[name] = r
        print(f"| {name} | {r['trades']} | {r['wins']} | {r['pnl']:+,.0f} | {r['ret']:+.2f}% | {r['dd']:.1f}% | {r['sharpe']:.1f} |")
    if a.detail in res:
        print(f"\n## {a.detail}\n")
        for t in res[a.detail]["trade_list"]: print(f"- {t[0]} {t[1]}->{t[2]} {t[5]:+.1f}% ${t[6]:+,.0f} {t[7]}")

if __name__ == "__main__":
    main()
