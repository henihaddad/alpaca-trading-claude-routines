"""Tiny stdlib HTTP helper with retries and a polite delay."""
import json, time, urllib.request, urllib.error, urllib.parse
from .config import USER_AGENT

def get(url, params=None, headers=None, retries=3, delay=0.6, timeout=25, as_json=True):
    if params:
        url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params, safe=":/,")
    h = {"User-Agent": USER_AGENT, "Accept": "application/json, text/html;q=0.9"}
    if headers: h.update(headers)
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=h)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read().decode("utf-8", "replace")
            time.sleep(delay)
            return json.loads(body) if as_json else body
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (429, 503, 502, 500):
                time.sleep(2 * (i + 1)); continue
            raise
        except Exception as e:  # network blips
            last = e; time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"GET {url} failed: {last}")
