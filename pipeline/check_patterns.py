"""Precision check: tag data/raw/*.jsonl with universe patterns; print counts + random samples per symbol.
Usage: python3 -m pipeline.check_patterns [--raw data/raw] [--n 3] [--only SYM,SYM]"""
import argparse, glob, json, random
from collections import defaultdict
from .signals import SYM_RE

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="data/raw"); ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--only", default=""); ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args(); random.seed(a.seed)
    only = set(filter(None, a.only.split(",")))
    hits = defaultdict(list); total = 0
    for f in glob.glob(f"{a.raw}/*.jsonl"):
        for line in open(f, encoding="utf-8"):
            try: t = json.loads(line).get("text", "") or ""
            except Exception: continue
            total += 1
            for s, r in SYM_RE.items():
                if (not only or s in only) and r.search(t): hits[s].append(t)
    print(f"items={total} symbols_tagged={len(hits)}")
    for s, ts in sorted(hits.items(), key=lambda kv: -len(kv[1])):
        print(f"\n== {s}: {len(ts)}")
        for t in random.sample(ts, min(a.n, len(ts))): print("   ", t[:120].replace("\n", " "))

if __name__ == "__main__":
    main()
