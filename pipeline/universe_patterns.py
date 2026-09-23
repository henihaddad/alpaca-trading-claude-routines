"""Symbol -> regex (compiled case-insensitively by the caller) for every symbol in universe.ALL.

Rules: cashtag always matches; bare ticker only when 4+ letters and not an English word;
word-like/short tickers match only via cashtag + company names."""
from .universe import ALL

# (symbol, bare_ticker_ok, extra name alternatives)
_STOCKS = {
    "AAPL": (True, r"\bapple\b|\biphone\b|tim cook"),
    "ABBV": (True, r"\babbvie\b"),
    "ABT": (False, r"abbott lab"),
    "ACN": (False, r"\baccenture\b"),
    "ADBE": (True, r"\badobe\b"),
    "AIG": (False, r"american international group"),
    "AMD": (False, r"\bamd\b|advanced micro devices|lisa su"),
    "AMGN": (True, r"\bamgen\b"),
    "AMT": (False, r"american tower"),
    "AMZN": (True, r"\bamazon\b|\baws\b|jassy"),
    "AVGO": (True, r"\bbroadcom\b"),
    "AXP": (False, r"american express|\bamex\b"),
    "BA": (False, r"\bboeing\b"),
    "BAC": (False, r"bank of america|\bbofa\b"),
    "BK": (False, r"bny mellon|bank of new york"),
    "BKNG": (True, r"booking holdings|booking\.com"),
    "BLK": (False, r"\bblackrock\b|larry fink"),
    "BMY": (False, r"bristol[- ]myers"),
    "BRK.B": (False, r"\bberkshire\b|warren buffett|\$brk\.?b\b|\bbrk\.b\b|\$brk\b"),
    "C": (False, r"\bcitigroup\b|\bcitibank\b"),
    "CAT": (False, r"\bcaterpillar\b"),
    "CHTR": (True, r"charter communications"),
    "CL": (None, r"\bcolgate\b"),  # $CL is mostly crude-oil futures chatter: name only
    "CMCSA": (True, r"\bcomcast\b"),
    "COF": (False, r"capital one"),
    "COP": (False, r"\bconocophillips\b"),
    "COST": (False, r"\bcostco\b"),
    "CRM": (False, r"\bsalesforce\b|marc benioff"),
    "CSCO": (True, r"\bcisco\b"),
    "CVS": (False, r"cvs health"),
    "CVX": (False, r"\bchevron\b"),
    "DE": (False, r"john deere|\bdeere\b"),
    "DHR": (False, r"\bdanaher\b"),
    "DIS": (False, r"\bdisney\b"),
    "DUK": (False, r"duke energy"),
    "EMR": (False, r"emerson electric"),
    "FDX": (False, r"\bfedex\b"),
    "GD": (False, r"general dynamics"),
    "GE": (False, r"general electric|ge aerospace"),
    "GILD": (False, r"gilead"),
    "GM": (False, r"general motors"),
    "GOOGL": (True, r"\bgoogle\b|\balphabet\b|\bgoog\b|\bgemini\b(?= (?:ai|model|3|2))|sundar pichai|\bwaymo\b"),
    "GS": (False, r"goldman sachs"),
    "HD": (False, r"home depot"),
    "HON": (False, r"\bhoneywell\b"),
    "IBM": (False, r"\bibm\b"),
    "INTC": (True, r"\bintel\b"),
    "INTU": (True, r"\bintuit\b|turbotax"),
    "ISRG": (True, r"intuitive surgical"),
    "JNJ": (False, r"johnson ?& ?johnson|\bj&j\b"),
    "JPM": (False, r"jpmorgan|jp morgan|jamie dimon"),
    "KO": (False, r"coca[- ]cola"),
    "LIN": (False, r"\blinde\b"),
    "LLY": (False, r"eli lilly|\blilly\b"),
    "LMT": (False, r"lockheed"),
    "LOW": (False, r"lowe's|\blowes\b"),
    "MA": (False, r"\bmastercard\b"),
    "MCD": (False, r"mcdonald's|\bmcdonalds\b"),
    "MDLZ": (True, r"\bmondelez\b"),
    "MDT": (False, r"\bmedtronic\b"),
    "MET": (False, r"\bmetlife\b"),
    "META": (False, r"meta platforms|\bfacebook\b|\bzuckerberg\b|\binstagram\b|\bwhatsapp\b"),
    "MMM": (False, r"\b3m company\b|\b3m co\b"),
    "MO": (False, r"\baltria\b"),
    "MRK": (False, r"\bmerck\b"),
    "MS": (False, r"morgan stanley"),
    "MSFT": (True, r"\bmicrosoft\b|satya nadella"),
    "NEE": (False, r"nextera"),
    "NFLX": (True, r"\bnetflix\b"),
    "NKE": (False, r"\bnike\b"),
    "NOW": (False, r"\bservicenow\b"),
    "NVDA": (True, r"\bnvidia\b|jensen huang"),
    "ORCL": (True, r"\boracle\b|larry ellison"),
    "PEP": (False, r"\bpepsico\b|\bpepsi\b"),
    "PFE": (False, r"\bpfizer\b"),
    "PG": (False, r"procter"),
    "PLTR": (True, r"\bpalantir\b"),
    "PM": (False, r"philip morris"),
    "PYPL": (True, r"\bpaypal\b"),
    "QCOM": (True, r"\bqualcomm\b"),
    "RTX": (False, r"\brtx corp|\braytheon\b"),
    "SBUX": (True, r"\bstarbucks\b"),
    "SCHW": (True, r"charles schwab|\bschwab\b"),
    "SO": (False, r"southern company"),
    "SPG": (False, r"simon property"),
    "T": (False, r"\bat&t\b|\bat&amp;t\b"),
    "TGT": (False, r"target corp"),
    "TMO": (False, r"thermo fisher"),
    "TMUS": (True, r"t-mobile"),
    "TSLA": (True, r"\btesla\b|elon musk|\bcybertruck\b|\brobotaxi\b"),
    "TXN": (False, r"texas instruments"),
    "UNH": (False, r"unitedhealth"),
    "UNP": (False, r"union pacific"),
    "UPS": (False, r"united parcel service"),
    "USB": (False, r"u\.s\. bancorp|us bancorp"),
    "V": (False, r"\bvisa\b(?! (?:application|applications|holders?|policy|ban|bans|program|rules|fee|fees|restrictions|requirements?|free))"),
    "VZ": (False, r"\bverizon\b"),
    "WFC": (False, r"wells fargo"),
    "WMT": (False, r"\bwalmart\b"),
    "XOM": (False, r"exxon"),
    "COIN": (False, r"\bcoinbase\b"),
    "MSTR": (True, r"microstrategy|strategy inc|michael saylor|\bsaylor\b"),
    "HOOD": (False, r"\brobinhood\b"),
    "SMCI": (True, r"super micro|supermicro"),
    "ARM": (False, r"arm holdings"),
    "UBER": (True, r""),
    "ABNB": (True, r"\bairbnb\b"),
    "SHOP": (False, r"\bshopify\b"),
    "SNOW": (False, r"\bsnowflake\b(?= (?:inc|stock|shares|earnings|data|ai))"),
    "MU": (False, r"\bmicron\b"),
    "MRVL": (True, r"marvell"),
    "DELL": (False, r"dell technologies|\bdell\b(?= (?:stock|shares|earnings|servers?))|michael dell"),
    "CRWD": (True, r"crowdstrike"),
    "PANW": (True, r"palo alto networks"),
    "SOFI": (True, r""),
    "RIVN": (True, r"\brivian\b"),
    "LCID": (True, r"lucid motors|lucid group"),
    "GME": (False, r"\bgamestop\b"),
    "AMC": (False, r"amc entertainment|amc theatres"),
    "RBLX": (True, r"\broblox\b"),
    "SPOT": (False, r"\bspotify\b"),
    "NIO": (False, r"nio inc"),
    "BABA": (False, r"\balibaba\b"),
    "TSM": (False, r"\btsmc\b|taiwan semi"),
    "ASML": (True, r""),
    "NVO": (False, r"novo nordisk|\bwegovy\b|\bozempic\b"),
    "AVAV": (True, r"aerovironment"),
    "IREN": (True, r"iris energy"),
    "CRCL": (True, r"circle internet"),
    "BMNR": (True, r"bitmine"),
    "RKLB": (True, r"rocket lab"),
    "ASTS": (True, r"ast spacemobile"),
    "OKLO": (True, r""),
}

_ETFS = {
    "SPY": r"\bspy\b|\$spy\b|s&p ?500|s&amp;p ?500|\bsp500\b|\bspx\b",
    "QQQ": r"\bqqq\b|\$qqq\b|\bnasdaq(?: ?100)?\b|\bndx\b",
    "VOO": r"\bvoo\b|\$voo\b",
    "IWM": r"\biwm\b|\$iwm\b|russell 2000",
    "DIA": r"\$dia\b|\bdow jones\b|\bthe dow\b",
}

_CRYPTO = {
    "BTC/USD": r"\bbitcoin\b|\bbtc\b|\$btc\b|\bbtc\.x\b|\bbtcusdt?\b",
    "ETH/USD": r"\bethereum\b|\beth\b|\$eth\b|\beth\.x\b|\bethusdt?\b|\bether\b",
    "SOL/USD": r"\bsolana\b|\$sol\b|\bsol\b(?=\s*(?:usd|price|/))|\bsolusdt?\b|\bsol\.x\b",
    "DOGE/USD": r"\bdogecoin\b|\bdoge\b(?!\s+(?:department|cuts?|staff|team|employees))|\$doge\b",
    "LTC/USD": r"\blitecoin\b|\bltc\b|\$ltc\b",
    "BCH/USD": r"bitcoin cash|\bbch\b|\$bch\b",
    "LINK/USD": r"\bchainlink\b|\$link\b|\blinkusdt?\b|\blink\.x\b",
    "AVAX/USD": r"\bavalanche\b(?=\s*(?:avax|\(|price|network|blockchain|crypto|token|coin))|\bavax\b|\$avax\b",
    "UNI/USD": r"\buniswap\b|\$uni\b|\buniusdt?\b",
    "AAVE/USD": r"\baave\b|\$aave\b",
    "DOT/USD": r"\bpolkadot\b|\$dot\b|\bdotusdt?\b",
    "SHIB/USD": r"shiba inu|\bshib\b|\$shib\b",
    "XRP/USD": r"\bxrp\b|\$xrp\b|\bripple\b(?!\s+effects?)",
}


def _stock(sym, bare, names):
    t = re.escape(sym.lower())
    parts = [] if bare is None else [rf"\${t}\b"]
    if bare:
        parts.append(rf"\b{t}\b")
    if names:
        parts.append(names)
    return "|".join(parts)


import re

SYMBOL_PATTERNS: dict[str, str] = {}
SYMBOL_PATTERNS.update(_ETFS)
for _s, (_b, _n) in _STOCKS.items():
    SYMBOL_PATTERNS[_s] = _stock(_s, _b, _n)
for _s, _p in _CRYPTO.items():
    _t = _s.split("/")[0].lower()
    SYMBOL_PATTERNS[_s] = _p + rf"|\${_t}\b|\b{_t}\.x\b|\b{_t}usd\b"

# cashtags must not be glued to a preceding word ("sh$t", "1$t")
SYMBOL_PATTERNS = {k: v.replace(r"\$", r"(?<![\w$])\$") for k, v in SYMBOL_PATTERNS.items()}

_missing = set(ALL) - set(SYMBOL_PATTERNS)
assert not _missing, _missing
