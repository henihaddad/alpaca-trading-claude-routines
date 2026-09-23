"""Turn raw items into hourly per-symbol features.

Features per (symbol, hour):
  n_<source>        mentions from that source
  bull_<source>, bear_<source>  labelled sentiment counts (stocktwits) or keyword sentiment (others)
  cat_<tag>         catalyst-tagged mentions (fed, macro_data, policy, geopolitics, flows, earnings, price_level)
  z_<source>        z-score of n_<source> against the trailing 7-day hourly baseline
  z_all             sum of z over sources that had a baseline

    python3 -m pipeline.signals --raw data/raw --out data/features/hourly.json
"""
import argparse, glob, json, os, re, statistics as st
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from .config import SYMBOL_PATTERNS, CATALYST_PATTERNS

SYM_RE = {s: re.compile(p, re.I) for s, p in SYMBOL_PATTERNS.items()}
CAT_RE = {c: re.compile(p, re.I) for c, p in CATALYST_PATTERNS.items()}
BULL = re.compile(r"\b(bullish|moon|rally|surge|soar|breakout|buy(ing)? the dip|calls|long|pump|ath|all[- ]time high|green)\b", re.I)
BEAR = re.compile(r"\b(bearish|crash|dump|plunge|tank|puts|short|sell[- ]off|red|recession|liquidated)\b", re.I)

def tag_symbols(it):
    syms = set(it.get("symbols") or [])
    text = it.get("text", "")
    for s, r in SYM_RE.items():
        if r.search(text): syms.add(s)
    return [s for s in syms if s in SYMBOL_PATTERNS]

def tag_cats(text):
    return [c for c, r in CAT_RE.items() if r.search(text)]

def sentiment(it):
    if it.get("sentiment"): return it["sentiment"]
    b, r = bool(BULL.search(it.get("text", ""))), bool(BEAR.search(it.get("text", "")))
    return "bull" if b and not r else "bear" if r and not b else None

def hour_key(ts):
    return ts[:13] + ":00:00Z"

def load_items(raw_dir):
    seen = set()
    for f in sorted(glob.glob(os.path.join(raw_dir, "*.jsonl"))):
        with open(f) as fh:
            for line in fh:
                if not line.strip(): continue
                it = json.loads(line); key = (it["source"], it["id"])
                if key in seen: continue
                seen.add(key); yield it

def build(raw_dir, baseline_days=7):
    feats = defaultdict(lambda: defaultdict(float))   # (symbol, hour) -> feature -> value
    top = defaultdict(list)                             # (symbol, hour) -> top items
    sources = set()
    for it in load_items(raw_dir):
        src = it["source"]; sources.add(src)
        syms = tag_symbols(it); cats = tag_cats(it["text"])
        if not syms and ({"fed", "macro_data"} & set(cats)):
            syms = ["SPY", "QQQ"]          # macro headlines move the indexes even when they never name them
        if not syms: continue
        hk = hour_key(it["ts"]); sent = sentiment(it)
        for s in syms:
            f = feats[(s, hk)]
            f[f"n_{src}"] += 1; f["n_all"] += 1
            if sent: f[f"{sent}_{src}"] += 1; f[f"{sent}_all"] += 1
            for c in cats: f[f"cat_{c}"] += 1
            top[(s, hk)].append((it.get("score", 0), src, it["text"][:160].replace("\n", " "), it.get("url", "")))
    # z-scores against trailing baseline of the same hour-of-day is overkill; use trailing 7d hourly mean/std per (symbol, source)
    by_sym = defaultdict(dict)
    for (s, hk), f in feats.items(): by_sym[s][hk] = f
    out = {}
    for s, hours in by_sym.items():
        keys = sorted(hours)
        for hk in keys:
            f = hours[hk]; t = datetime.fromisoformat(hk.replace("Z", "+00:00"))
            lo = t - timedelta(days=baseline_days)
            window = [hours[k] for k in keys if lo <= datetime.fromisoformat(k.replace("Z", "+00:00")) < t]
            nhours = max(1, int(baseline_days * 24))
            zsum, zn = 0.0, 0
            for src in sources:
                col = f"n_{src}"
                vals = [w.get(col, 0.0) for w in window] + [0.0] * max(0, nhours - len(window))
                if len(window) < 24: continue
                mu = st.mean(vals); sd = st.pstdev(vals)
                z = (f.get(col, 0.0) - mu) / sd if sd > 0 else 0.0
                f[f"z_{src}"] = round(z, 2); zsum += z; zn += 1
            f["z_all"] = round(zsum, 2) if zn else 0.0
            tot = f.get("n_all", 0)
            f["bull_ratio"] = round((f.get("bull_all", 0) - f.get("bear_all", 0)) / tot, 3) if tot else 0.0
            f["top"] = sorted(top[(s, hk)], reverse=True)[:5]
            out[f"{s}|{hk}"] = dict(f)
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--raw", default="data/raw"); ap.add_argument("--out", default="data/features/hourly.json")
    a = ap.parse_args()
    feats = build(a.raw)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(feats, open(a.out, "w"))
    syms = defaultdict(int)
    for k in feats: syms[k.split("|")[0]] += 1
    print(f"{len(feats)} symbol-hours; per symbol: {dict(syms)}")

if __name__ == "__main__":
    main()
