from datetime import datetime, timezone

def iso(dt):
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def parse_iso(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc)

def from_epoch(e):
    return datetime.fromtimestamp(int(e), tz=timezone.utc)

def item(source, channel, id_, ts, text, url="", score=0, sentiment=None, symbols=None):
    """Normalized record shared by every source."""
    return {"source": source, "channel": channel, "id": str(id_), "ts": iso(ts),
            "text": (text or "").strip()[:1500], "url": url, "score": int(score or 0),
            "sentiment": sentiment, "symbols": symbols or []}
