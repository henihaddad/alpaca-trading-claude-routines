"""Polymarket prediction markets (keyless). Snapshot of matching markets plus hourly
probability history from the CLOB, which lets us backtest 'crowd odds' as a signal."""
import json, re
from .. import http
from ..config import POLYMARKET_KEYWORDS
from .common import item, from_epoch

GAMMA = "https://gamma-api.polymarket.com/markets"
CLOB = "https://clob.polymarket.com/prices-history"

def matching_markets(limit_pages=8):
    out, pat = [], re.compile(POLYMARKET_KEYWORDS, re.I)
    for page in range(limit_pages):
        ms = http.get(GAMMA, {"closed": "false", "active": "true", "limit": 100, "offset": page * 100,
                              "order": "volume24hr", "ascending": "false"})
        if not ms: break
        for m in ms:
            if pat.search(m.get("question", "")):
                out.append(m)
    return out

def fetch(start, end, log=print, max_markets=25):
    """Returns (items, histories). Items are snapshots; histories map question -> [(ts, prob_yes)]."""
    items, hist = [], {}
    try:
        markets = matching_markets()
    except Exception as e:
        log(f"polymarket: FAILED {e}"); return items, hist
    markets.sort(key=lambda m: -(m.get("volume24hr") or 0))
    for m in markets[:max_markets]:
        try:
            prices = json.loads(m.get("outcomePrices") or "[]")
            tokens = json.loads(m.get("clobTokenIds") or "[]")
            p_yes = float(prices[0]) if prices else None
            items.append(item("polymarket", "market", m["id"], end, m["question"], url="https://polymarket.com/market/" + m.get("slug", ""),
                              score=int(m.get("volume24hr") or 0), sentiment=None))
            items[-1]["p_yes"] = p_yes
            if tokens:
                h = http.get(CLOB, {"market": tokens[0], "startTs": int(start.timestamp()), "endTs": int(end.timestamp()), "fidelity": 60})
                hist[m["question"]] = [(from_epoch(x["t"]).strftime("%Y-%m-%dT%H:%M:%SZ"), x["p"]) for x in h.get("history", [])]
        except Exception as e:
            log(f"polymarket/{m.get('question','')[:40]}: FAILED {e}")
    log(f"polymarket: {len(items)} markets, {sum(len(v) for v in hist.values())} history points")
    return items, hist
