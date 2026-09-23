"""One-off fetcher: pull daily/hourly bars for the universe from Alpaca's data API
and write them into analysis/data/bars_daily/ and analysis/data/bars_hourly/,
matching the on-disk shape of the existing files there (inspected before writing this).
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline.universe import ETFS, STOCKS, CRYPTO

API_KEY = os.environ["ALPACA_API_KEY"]
API_SECRET = os.environ["ALPACA_SECRET"]
BASE = "https://data.alpaca.markets"
HEADERS = {"APCA-API-KEY-ID": API_KEY, "APCA-API-SECRET-KEY": API_SECRET}

TODAY = time.strftime("%Y-%m-%d", time.gmtime())
DAILY_START = "2026-07-15"
HOURLY_START = "2026-08-01"

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DAILY_DIR = os.path.join(REPO_ROOT, "analysis", "data", "bars_daily")
HOURLY_DIR = os.path.join(REPO_ROOT, "analysis", "data", "bars_hourly")


def get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def chunked(items, n):
    for i in range(0, len(items), n):
        yield items[i:i + n]


def fetch_stock_bars(symbols, timeframe, start):
    """Fetch bars for up to 50 stock/ETF symbols at a time. Returns {symbol: [bars]}."""
    acc = {s: [] for s in symbols}
    for group in chunked(symbols, 50):
        page_token = None
        while True:
            params = {
                "symbols": ",".join(group),
                "timeframe": timeframe,
                "start": start,
                "end": TODAY,
                "limit": 10000,
                "adjustment": "split",
                "feed": "iex",
            }
            if page_token:
                params["page_token"] = page_token
            url = f"{BASE}/v2/stocks/bars?{urllib.parse.urlencode(params)}"
            data = get(url)
            for sym, bars in (data.get("bars") or {}).items():
                acc[sym].extend(bars)
            page_token = data.get("next_page_token")
            time.sleep(0.3)
            if not page_token:
                break
    return acc


def fetch_crypto_bars(symbols, timeframe, start):
    """Fetch bars for crypto symbols. Returns {symbol: [bars]}."""
    acc = {s: [] for s in symbols}
    page_token = None
    while True:
        params = {
            "symbols": ",".join(symbols),
            "timeframe": timeframe,
            "start": start,
            "limit": 10000,
        }
        if page_token:
            params["page_token"] = page_token
        url = f"{BASE}/v1beta3/crypto/us/bars?{urllib.parse.urlencode(params)}"
        data = get(url)
        for sym, bars in (data.get("bars") or {}).items():
            acc[sym].extend(bars)
        page_token = data.get("next_page_token")
        time.sleep(0.3)
        if not page_token:
            break
    return acc


def write_symbol_file(directory, symbol, bars, feed, timeframe):
    fname = symbol.replace("/", "-") + ".json"
    path = os.path.join(directory, fname)
    if os.path.exists(path):
        try:
            existing = json.load(open(path))
            existing_bars = existing.get("bars", [])
            if isinstance(existing_bars, list) and len(existing_bars) > len(bars):
                return False
        except (json.JSONDecodeError, OSError):
            pass
    payload = {"bars": bars, "feed": feed, "symbol": symbol, "timeframe": timeframe}
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
    return True


def run_stock_group(label, symbols, directory, timeframe, start):
    written, skipped = [], []
    try:
        bars_by_symbol = fetch_stock_bars(symbols, timeframe, start)
    except urllib.error.HTTPError as e:
        print(f"[{label}] HTTP error fetching group: {e}", file=sys.stderr)
        return written, symbols
    for sym in symbols:
        bars = bars_by_symbol.get(sym, [])
        if not bars:
            skipped.append(sym)
            continue
        if write_symbol_file(directory, sym, bars, "iex", timeframe):
            written.append(sym)
        else:
            written.append(sym + " (kept existing, more/equal bars)")
    return written, skipped


def run_crypto_group(symbols, directory, timeframe, start):
    written, skipped = [], []
    try:
        bars_by_symbol = fetch_crypto_bars(symbols, timeframe, start)
    except urllib.error.HTTPError as e:
        print(f"[crypto] HTTP error fetching group: {e}", file=sys.stderr)
        return written, symbols
    for sym in symbols:
        bars = bars_by_symbol.get(sym, [])
        if not bars:
            skipped.append(sym)
            continue
        if write_symbol_file(directory, sym, bars, "crypto-us", timeframe):
            written.append(sym)
        else:
            written.append(sym + " (kept existing, more/equal bars)")
    return written, skipped


def main():
    os.makedirs(DAILY_DIR, exist_ok=True)
    os.makedirs(HOURLY_DIR, exist_ok=True)

    stock_symbols = ETFS + STOCKS

    print("=== Daily: stocks/ETFs ===")
    daily_written, daily_skipped = run_stock_group("daily-stocks", stock_symbols, DAILY_DIR, "1Day", DAILY_START)

    print("=== Hourly: stocks/ETFs ===")
    hourly_written, hourly_skipped = run_stock_group("hourly-stocks", stock_symbols, HOURLY_DIR, "1Hour", HOURLY_START)

    print("=== Daily: crypto ===")
    c_daily_written, c_daily_skipped = run_crypto_group(CRYPTO, DAILY_DIR, "1Day", DAILY_START)

    print("=== Hourly: crypto ===")
    c_hourly_written, c_hourly_skipped = run_crypto_group(CRYPTO, HOURLY_DIR, "1Hour", HOURLY_START)

    print("\n=== SUMMARY ===")
    print(f"Daily written ({len(daily_written) + len(c_daily_written)}): {daily_written + c_daily_written}")
    print(f"Daily skipped/unsupported ({len(daily_skipped) + len(c_daily_skipped)}): {daily_skipped + c_daily_skipped}")
    print(f"Hourly written ({len(hourly_written) + len(c_hourly_written)}): {hourly_written + c_hourly_written}")
    print(f"Hourly skipped/unsupported ({len(hourly_skipped) + len(c_hourly_skipped)}): {hourly_skipped + c_hourly_skipped}")


if __name__ == "__main__":
    main()
