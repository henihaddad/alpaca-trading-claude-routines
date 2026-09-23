"""Build the situational brief the trading agent reads at the start of each run.

    python3 -m pipeline.collect --hours 96 --out data/live
    python3 -m pipeline.signals --raw data/live --out data/live/hourly.json
    python3 -m pipeline.brief --features data/live/hourly.json --raw data/live --out data/live/brief.md
"""
import argparse, json, os
from collections import defaultdict
from datetime import datetime, timedelta, timezone

def ts(s): return datetime.fromisoformat(s.replace("Z", "+00:00"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", default="data/live/hourly.json"); ap.add_argument("--raw", default="data/live")
    ap.add_argument("--out", default="data/live/brief.md"); ap.add_argument("--symbols", default="")
    ap.add_argument("--top", type=int, default=20, help="show the top N symbols by attention score (growth x log mentions)")
    ap.add_argument("--held", default="", help="comma-separated symbols to always include (current positions)")
    a = ap.parse_args()
    feats = json.load(open(a.features)); now = datetime.now(timezone.utc)
    import math
    if not a.symbols:
        from .universe import ALL
        a.symbols = ",".join(ALL)
    lines = [f"# Signal brief — {now:%Y-%m-%d %H:%M} UTC\n",
             "Attention = mentions in the last 24h vs the previous 72h (per source). z24 = sum of hourly z-scores over 24h.",
             "Tilt = (bullish - bearish) / mentions, from Stocktwits labels and keyword sentiment. Catalysts = tagged headline types.\n",
             "Mentions and the ratio exclude Stocktwits (its history is too short for a baseline); tilt includes it. geo share = geopolitics share of catalyst tags.\n",
             ]
    per = defaultdict(list)
    for k, f in feats.items():
        s, h = k.split("|"); per[s].append((ts(h), f))
    rows_out, details = [], {}
    for s in a.symbols.split(","):
        rows = sorted(per.get(s, []))
        last = [(t, f) for t, f in rows if t > now - timedelta(hours=24)]
        prior = [(t, f) for t, f in rows if now - timedelta(hours=96) < t <= now - timedelta(hours=24)]
        # Stocktwits only reaches back a day or two, so it would inflate any "vs prior" ratio; use it for tilt only.
        def n_hist(f): return sum(v for k, v in f.items() if k.startswith("n_") and k not in ("n_all", "n_stocktwits"))
        n24 = sum(n_hist(f) for _, f in last); nprior = sum(n_hist(f) for _, f in prior) / 3
        n24_all = sum(f.get("n_all", 0) for _, f in last)
        z24 = sum(v for _, f in last for k, v in f.items() if k.startswith("z_") and k not in ("z_all", "z_stocktwits"))
        bull = sum(f.get("bull_all", 0) for _, f in last); bear = sum(f.get("bear_all", 0) for _, f in last)
        tilt = (bull - bear) / n24_all if n24_all else 0
        cats = defaultdict(int)
        for _, f in last:
            for k, v in f.items():
                if k.startswith("cat_"): cats[k[4:]] += v
        catstr = ", ".join(f"{c}:{int(v)}" for c, v in sorted(cats.items(), key=lambda kv: -kv[1])[:4]) or "-"
        tot_cats = sum(cats.values()); geo_share = cats.get("geopolitics", 0) / tot_cats if tot_cats else 0
        ratio = f"{n24 / nprior:.1f}x" if nprior >= 3 else "n/a (no baseline)"
        score = (n24 / nprior if nprior >= 3 else 1.0) * math.log1p(n24)
        if n24 == 0 and s not in a.held.split(","): continue
        rows_out.append((score, s, f"| {s} | {int(n24)} (+{int(n24_all - n24)} stocktwits) | {ratio} | {z24:+.1f} | {tilt:+.2f} | {catstr} | {geo_share:.0%} | {score:.1f} |"))
        tops = sorted([x for _, f in last for x in f.get("top", [])], reverse=True)[:5]
        if tops: details[s] = [f"\n### {s} — most-engaged items, last 24h"] + [f"- [{src}, {sc}] {text}" for sc, src, text, url in tops]
    held = [x for x in a.held.split(",") if x]
    rows_out.sort(key=lambda r: -r[0])
    chosen = [r for r in rows_out[:a.top]] + [r for r in rows_out[a.top:] if r[1] in held]
    lines.append(f"Ranked by score = 24h growth vs prior 72h x log(mentions). Showing top {a.top} of {len(rows_out)} symbols with activity, plus held positions.\n")
    lines += ["| symbol | 24h mentions | vs prior 72h avg/day | z24 | tilt | catalysts (24h) | geo share | score |", "|---|---|---|---|---|---|---|---|"]
    lines += [r[2] for r in chosen]
    for _, s, _ in chosen: lines += details.get(s, [])
    pm = os.path.join(a.raw, "polymarket.jsonl")
    if os.path.exists(pm):
        lines.append("\n### Prediction markets (Polymarket, probability of YES)")
        for line in open(pm):
            it = json.loads(line)
            if it.get("p_yes") is not None: lines.append(f"- {it['p_yes']:.0%} — {it['text']}")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w").write("\n".join(lines) + "\n"); print("\n".join(lines))

if __name__ == "__main__":
    main()
