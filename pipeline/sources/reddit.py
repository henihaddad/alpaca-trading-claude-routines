"""Reddit via the arctic-shift archive API (keyless, historical, minutes of lag)."""
from .. import http
from ..config import SUBREDDITS
from .common import item, from_epoch, iso

API = "https://arctic-shift.photon-reddit.com/api/posts/search"

def fetch_sub(sub, start, end, max_pages=200):
    out, after = [], iso(start)
    for _ in range(max_pages):
        data = http.get(API, {"subreddit": sub, "after": after, "before": iso(end), "limit": 100, "sort": "asc"})
        posts = data.get("data") or []
        if not posts: break
        for p in posts:
            ts = from_epoch(p["created_utc"])
            text = p.get("title", "") + "\n" + (p.get("selftext") or "")[:600]
            out.append(item("reddit", sub, p["id"], ts, text, url="https://reddit.com" + p.get("permalink", ""),
                            score=(p.get("score") or 0) + (p.get("num_comments") or 0)))
        if len(posts) < 100: break
        after = iso(from_epoch(posts[-1]["created_utc"] + 1))
    return out

def fetch(start, end, subs=None, log=print):
    out = []
    for s in (subs or SUBREDDITS):
        try:
            got = fetch_sub(s, start, end); log(f"reddit/{s}: {len(got)}"); out += got
        except Exception as e:
            log(f"reddit/{s}: FAILED {e}")
    return out
