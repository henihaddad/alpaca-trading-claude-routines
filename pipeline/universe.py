"""Tradeable universe for the signal pipeline: US large caps people actually talk about, the index ETFs,
and the cryptos Alpaca trades. Name/ticker regexes live in universe_patterns.py (generated + hand-checked)."""

ETFS = ["SPY", "QQQ", "VOO", "IWM", "DIA"]

# S&P 100 (Sep 2026 constituents, minus duplicates) + widely traded retail favourites.
STOCKS = [
    "AAPL","ABBV","ABT","ACN","ADBE","AIG","AMD","AMGN","AMT","AMZN","AVGO","AXP","BA","BAC","BK","BKNG","BLK","BMY",
    "BRK.B","C","CAT","CHTR","CL","CMCSA","COF","COP","COST","CRM","CSCO","CVS","CVX","DE","DHR","DIS","DUK","EMR","FDX",
    "GD","GE","GILD","GM","GOOGL","GS","HD","HON","IBM","INTC","INTU","ISRG","JNJ","JPM","KO","LIN","LLY","LMT","LOW",
    "MA","MCD","MDLZ","MDT","MET","META","MMM","MO","MRK","MS","MSFT","NEE","NFLX","NKE","NOW","NVDA","ORCL","PEP","PFE",
    "PG","PLTR","PM","PYPL","QCOM","RTX","SBUX","SCHW","SO","SPG","T","TGT","TMO","TMUS","TSLA","TXN","UNH","UNP","UPS",
    "USB","V","VZ","WFC","WMT","XOM",
    # retail favourites / high-attention names
    "COIN","MSTR","HOOD","SMCI","ARM","UBER","ABNB","SHOP","SNOW","MU","MRVL","DELL","CRWD","PANW","SOFI","RIVN","LCID",
    "GME","AMC","RBLX","SPOT","NIO","BABA","TSM","ASML","NVO","AVAV","IREN","CRCL","BMNR","RKLB","ASTS","OKLO",
]

CRYPTO = ["BTC/USD","ETH/USD","SOL/USD","DOGE/USD","LTC/USD","BCH/USD","LINK/USD","AVAX/USD","UNI/USD","AAVE/USD","DOT/USD","SHIB/USD","XRP/USD"]

ALL = ETFS + STOCKS + CRYPTO
