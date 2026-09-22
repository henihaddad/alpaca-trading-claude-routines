"""Collect every source for a time window into data/raw/<source>.jsonl.

    python3 -m pipeline.collect --start 2026-08-01 --end 2026-09-22 --out data/raw
    python3 -m pipeline.collect --hours 72 --out data/raw            # live window
"""
import argparse, json, os, sys
from datetime import datetime, timedelta, timezone
from .sources import telegram, reddit, stocktwits, hackernews, polymarket, alpaca_news

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start"); ap.add_argument("--end"); ap.add_argument("--hours", type=int)
    ap.add_argument("--out", default="data/raw")
    ap.add_argument("--sources", default="telegram,reddit,stocktwits,hackernews,polymarket,alpaca_news")
    a = ap.parse_args()
    now = datetime.now(timezone.utc)
    end = datetime.fromisoformat(a.end).replace(tzinfo=timezone.utc) + timedelta(days=1) if a.end else now
    start = datetime.fromisoformat(a.start).replace(tzinfo=timezone.utc) if a.start else now - timedelta(hours=a.hours or 72)
    end = min(end, now)
    os.makedirs(a.out, exist_ok=True)
    log = lambda m: print(m, file=sys.stderr, flush=True)
    log(f"window {start:%Y-%m-%d %H:%M} -> {end:%Y-%m-%d %H:%M} UTC")
    mods = {"telegram": telegram, "reddit": reddit, "stocktwits": stocktwits, "hackernews": hackernews,
            "alpaca_news": alpaca_news}
    for name in a.sources.split(","):
        if name == "polymarket":
            items, hist = polymarket.fetch(start, end, log=log)
            json.dump(hist, open(os.path.join(a.out, "polymarket_history.json"), "w"))
        else:
            items = mods[name].fetch(start, end, log=log)
        with open(os.path.join(a.out, f"{name}.jsonl"), "w") as f:
            for it in sorted(items, key=lambda x: x["ts"]):
                f.write(json.dumps(it, ensure_ascii=False) + "\n")
        log(f"== {name}: {len(items)} items written")

if __name__ == "__main__":
    main()
