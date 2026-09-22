"""Static configuration for the signal pipeline. Everything here is keyless."""

# Symbols we trade / track. Keys are Alpaca symbols.
SYMBOL_PATTERNS = {
    "BTC/USD": r"\b(bitcoin|btc|\$btc|btc\.x)\b",
    "ETH/USD": r"\b(ethereum|eth|\$eth|eth\.x)\b",
    "SPY": r"\b(spy|\$spy|s&p ?500|sp500|s&p|spx)\b",
    "QQQ": r"\b(qqq|\$qqq|nasdaq(?: ?100)?|ndx)\b",
    "NVDA": r"\b(nvidia|nvda|\$nvda)\b",
    "TSLA": r"\b(tesla|tsla|\$tsla)\b",
    "AAPL": r"\b(apple|aapl|\$aapl)\b",
    "MSFT": r"\b(microsoft|msft|\$msft)\b",
    "AMZN": r"\b(amazon|amzn|\$amzn)\b",
    "META": r"\b(meta platforms|\$meta|\bmeta\b)\b",
    "GOOGL": r"\b(google|alphabet|googl|\$googl)\b",
    "AMD": r"\b(amd|\$amd)\b",
}

# Catalyst tags: these are the headline types that historically move markets,
# as opposed to opinion/recap pieces.
CATALYST_PATTERNS = {
    "fed": r"\b(fed|fomc|powell|warsh|rate (hike|cut|hold)|basis points|bps)\b",
    "macro_data": r"\b(cpi|ppi|inflation|payrolls|jobs report|nonfarm|unemployment|gdp|retail sales|pce)\b",
    "policy": r"\b(tariff|sanction|executive order|white house|congress|senate|sec\b|clarity act|regulat)\b",
    "geopolitics": r"\b(iran|israel|hormuz|ukraine|russia|china|taiwan|ceasefire|missile|strike)\b",
    "flows": r"\b(etf (in|out)flow|inflows|outflows|liquidat|short squeeze|whale|treasury (buy|purchase)|buys? \d+ bitcoin)\b",
    "earnings": r"\b(earnings|guidance|revenue|eps|quarterly results|beats|misses)\b",
    "price_level": r"\b(hits|cracks|breaks|tops|reclaims|all-time high|record high|\$\d{2,3},?\d{3})\b",
}

# Reddit subreddits pulled from the arctic-shift archive (keyless, historical).
SUBREDDITS = ["wallstreetbets", "stocks", "StockMarket", "investing", "Bitcoin", "CryptoCurrency"]

# Telegram public channels with preview enabled (t.me/s/<name> returns messages).
TELEGRAM_CHANNELS = {
    "financialjuice": "macro headline squawk",
    "bloomberg": "Bloomberg news",
    "markets_today": "market headlines",
    "tradingview": "TradingView news",
    "disclosetv": "breaking/politics",
    "spectatorindex": "breaking/geopolitics",
    "watcherguru": "crypto/markets breaking",
    "unfolded": "crypto news",
    "bitcoin": "bitcoin news",
    "whale_alert_io": "large on-chain transfers",
    "wublockchainenglish": "crypto/Asia news",
}

# Stocktwits symbol streams (their symbol notation).
STOCKTWITS_SYMBOLS = {"SPY": "SPY", "QQQ": "QQQ", "BTC/USD": "BTC.X", "ETH/USD": "ETH.X",
                      "NVDA": "NVDA", "TSLA": "TSLA"}

# Hacker News queries.
HN_QUERIES = ["bitcoin", "stock market", "nasdaq", "federal reserve", "tariff"]

# Polymarket: markets whose question matches any of these are tracked.
POLYMARKET_KEYWORDS = r"(bitcoin|btc|ethereum|fed |rate cut|rate hike|fomc|recession|s&p|nasdaq|tariff|iran|inflation|cpi)"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36 research-pipeline/0.1"
