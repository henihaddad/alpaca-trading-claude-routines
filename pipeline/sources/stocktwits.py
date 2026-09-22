"""Stocktwits symbol streams (keyless). 30 messages per page, walk back with max=cursor.
Carries user-labelled Bullish/Bearish sentiment, which is the useful part."""
from .. import http
from ..config import STOCKTWITS_SYMBOLS
from .common import item, parse_iso

URL = "https://api.stocktwits.com/api/2/streams/symbol/{sym}.json"

def fetch_symbol(alpaca_sym, st_sym, start, end, max_pages=int(__import__("os").environ.get("STOCKTWITS_MAX_PAGES", "120"))):
    out, cursor = [], None
    for _ in range(max_pages):
        data = http.get(URL.format(sym=st_sym), {"max": cursor} if cursor else None, delay=0.5)
        msgs = data.get("messages") or []
        if not msgs: break
        for m in msgs:
            ts = parse_iso(m["created_at"])
            if ts > end: continue
            if ts < start: return out
            sent = ((m.get("entities") or {}).get("sentiment") or {}).get("basic")
            out.append(item("stocktwits", st_sym, m["id"], ts, m.get("body", ""),
                            url=f"https://stocktwits.com/message/{m['id']}",
                            score=(m.get("likes") or {}).get("total", 0),
                            sentiment={"Bullish": "bull", "Bearish": "bear"}.get(sent),
                            symbols=[alpaca_sym]))
        cur = data.get("cursor") or {}
        if not cur.get("more"): break
        cursor = cur.get("max")
    return out

def fetch(start, end, symbols=None, log=print):
    out = []
    for a, s in (symbols or STOCKTWITS_SYMBOLS).items():
        try:
            got = fetch_symbol(a, s, start, end); log(f"stocktwits/{s}: {len(got)}"); out += got
        except Exception as e:
            log(f"stocktwits/{s}: FAILED {e}")
    return out
