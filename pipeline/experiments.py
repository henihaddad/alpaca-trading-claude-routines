"""Run a grid of named simulate.py configurations and print a markdown table.

    python3 -m pipeline.experiments [--bars DIR] [--features FILE] [--start YYYY-MM-DD]
"""
import argparse, json
from pipeline import simulate

CONFIGS = [
    ("12-symbols baseline", {"symbols": "SPY,QQQ,AAPL,MSFT,NVDA,AMZN,GOOGL,META,TSLA,AMD,BTC/USD,ETH/USD", "max_positions": 99}),
    ("all symbols max8", {"max_positions": 8}),
    ("all symbols max8 crypto-only", {"max_positions": 8, "_filter": "crypto"}),
    ("all symbols max8 no-crypto", {"max_positions": 8, "_filter": "nocrypto"}),
    ("all symbols max5", {"max_positions": 5}),
    ("all symbols max12 cap10%", {"max_positions": 12, "cap": 0.10}),
    ("stock stop 2.5/5", {"stop_stock": 0.025, "trail_stock": 0.05}),
    ("stock stop 4/8", {"stop_stock": 0.04, "trail_stock": 0.08}),
    ("z24>=6 only", {"z": 6.0, "ratio": 1e9}),
    ("ratio>=3 only", {"ratio": 3.0, "z": 1e9}),
    ("start 2026-08-22", {"start": "2026-08-22"}),
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars"); ap.add_argument("--features"); ap.add_argument("--start")
    o = ap.parse_args()
    base = simulate.build_parser().parse_args([])
    if o.bars: base.bars = o.bars
    if o.features: base.features = o.features
    feats = json.load(open(base.features)); bars = simulate.load_bars(base.bars)
    print("| config | universe | trades | wins | P&L $ | return % | max DD % |\n|---|---|---|---|---|---|---|")
    for name, cfg in CONFIGS:
        a = argparse.Namespace(**vars(base))
        if o.start: a.start = o.start
        filt = cfg.get("_filter")
        for k, v in cfg.items():
            if not k.startswith("_"): setattr(a, k, v)
        if filt:
            a.symbols = ",".join(s for s in bars if ("/" in s) == (filt == "crypto"))
        R = simulate.run(a, feats_raw=feats, bars_all=bars)
        t = R["trades"]; pnl = sum(x[6] for x in t); wins = sum(1 for x in t if x[6] > 0)
        print(f"| {name} | {R['universe']} | {len(t)} | {wins} | {pnl:+,.0f} | {(R['final_equity']/a.equity-1)*100:+.2f} | {R['max_dd']:.2f} |")

if __name__ == "__main__":
    main()
