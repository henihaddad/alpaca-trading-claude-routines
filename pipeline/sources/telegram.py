"""Public Telegram channel previews (t.me/s/<channel>), paged with ?before=<id>. Keyless."""
import re, html
from .. import http
from ..config import TELEGRAM_CHANNELS
from .common import item, parse_iso

_MSG = re.compile(r'data-post="([^"/]+)/(\d+)"(.*?)(?=data-post="|\Z)', re.S)
_TEXT = re.compile(r'class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', re.S)
_TIME = re.compile(r'<time datetime="([^"]+)"')
_VIEWS = re.compile(r'class="tgme_widget_message_views">([^<]+)<')

def _views(s):
    s = s.strip().upper().replace(",", "")
    try:
        if s.endswith("K"): return int(float(s[:-1]) * 1000)
        if s.endswith("M"): return int(float(s[:-1]) * 1e6)
        return int(float(s))
    except ValueError:
        return 0

def fetch_channel(channel, start, end, max_pages=1200):
    out, before = [], None
    for _ in range(max_pages):
        url = f"https://t.me/s/{channel}" + (f"?before={before}" if before else "")
        page = http.get(url, as_json=False, delay=0.4)
        msgs = list(_MSG.finditer(page))
        if not msgs: break
        ids = []
        oldest = None
        for m in msgs:
            ch, mid, body = m.group(1), int(m.group(2)), m.group(3)
            ids.append(mid)
            t = _TIME.search(body); tx = _TEXT.search(body)
            if not t: continue
            ts = parse_iso(t.group(1))
            oldest = ts if oldest is None or ts < oldest else oldest
            if ts < start or ts > end: continue
            text = html.unescape(re.sub(r"<br\s*/?>", "\n", tx.group(1))) if tx else ""
            text = re.sub(r"<[^>]+>", "", text)
            v = _VIEWS.search(body)
            out.append(item("telegram", channel, f"{ch}/{mid}", ts, text,
                            url=f"https://t.me/{ch}/{mid}", score=_views(v.group(1)) if v else 0))
        if oldest is not None and oldest < start: break
        before = min(ids)
    return out

def fetch(start, end, channels=None, log=print):
    out = []
    for ch in (channels or TELEGRAM_CHANNELS):
        try:
            got = fetch_channel(ch, start, end)
            log(f"telegram/{ch}: {len(got)}")
            out += got
        except Exception as e:
            log(f"telegram/{ch}: FAILED {e}")
    return out
