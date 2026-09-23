"""Alpaca (Benzinga) news. Uses the live API when ALPACA_API_KEY/ALPACA_SECRET are set,
otherwise falls back to the JSON dumps under analysis/data/news."""
import os, glob, json
from .. import http
from .common import item, parse_iso, iso

API = "https://data.alpaca.markets/v1beta1/news"

def _norm(n):
    return item("alpaca_news", n.get("source", "benzinga"), n["id"], parse_iso(n["created_at"]),
                (n.get("headline") or "") + ". " + (n.get("summary") or ""), url=n.get("url", ""),
                symbols=[s.replace("USD", "/USD") if s.endswith("USD") and len(s) == 6 else s for s in n.get("symbols", [])])

def fetch(start, end, symbols=None, log=print, dump_dir="analysis/data/news"):
    key, sec = os.environ.get("ALPACA_API_KEY"), os.environ.get("ALPACA_SECRET")
    out, seen = [], set()
    if key and sec:
        params = {"start": iso(start), "end": iso(end), "limit": 50, "sort": "asc", "include_content": "false"}
        if symbols: params["symbols"] = ",".join(symbols)
        token = None
        for _ in range(60):
            if token: params["page_token"] = token
            d = http.get(API, params, headers={"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": sec})
            for n in d.get("news", []):
                if n["id"] not in seen: seen.add(n["id"]); out.append(_norm(n))
            token = d.get("next_page_token")
            if not token: break
        log(f"alpaca_news (live): {len(out)}")
        return out
    for f in glob.glob(os.path.join(dump_dir, "*.json")):
        j = json.load(open(f)); ns = j.get("news", j) if isinstance(j, dict) else j
        for n in ns or []:
            ts = parse_iso(n["created_at"])
            if n["id"] in seen or ts < start or ts > end: continue
            seen.add(n["id"]); out.append(_norm(n))
    log(f"alpaca_news (from dump): {len(out)}")
    return out
