"""Hacker News via Algolia (keyless, historical)."""
from .. import http
from ..config import HN_QUERIES
from .common import item, from_epoch

API = "https://hn.algolia.com/api/v1/search_by_date"

def fetch(start, end, queries=None, log=print):
    out, seen = [], set()
    for q in (queries or HN_QUERIES):
        try:
            page = 0
            while page < 20:
                d = http.get(API, {"query": q, "tags": "story", "hitsPerPage": 100, "page": page,
                                   "numericFilters": f"created_at_i>{int(start.timestamp())},created_at_i<{int(end.timestamp())}"})
                hits = d.get("hits") or []
                for h in hits:
                    if h["objectID"] in seen: continue
                    seen.add(h["objectID"])
                    out.append(item("hackernews", q, h["objectID"], from_epoch(h["created_at_i"]),
                                    (h.get("title") or "") + " " + (h.get("story_text") or "")[:300],
                                    url=h.get("url") or f"https://news.ycombinator.com/item?id={h['objectID']}",
                                    score=(h.get("points") or 0) + (h.get("num_comments") or 0)))
                if page >= d.get("nbPages", 1) - 1: break
                page += 1
            log(f"hackernews/{q}: total so far {len(out)}")
        except Exception as e:
            log(f"hackernews/{q}: FAILED {e}")
    return out
