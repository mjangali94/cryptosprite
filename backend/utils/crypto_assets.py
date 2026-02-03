# ----------------- Asset Symbols -----------------
asset_symbols = {
    # Tier 1 — Core
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "USDT": "tether",
    "USDC": "usd-coin",
    "BNB": "binancecoin",
    "XRP": "ripple",
    "SOL": "solana",
    "DOGE": "dogecoin",
    "ADA": "cardano",
    "LTC": "litecoin",

    # Layer 1s
    "AVAX": "avalanche-2",
    "DOT": "polkadot",
    "ATOM": "cosmos",
    "XLM": "stellar",
    "TRX": "tron",
    "XTZ": "tezos",
    "NEAR": "near",
    "APT": "aptos",
    "SEI": "sei-network",

    # Layer 2s
    "MATIC": "polygon",
    "ARB": "arbitrum",
    "OP": "optimism",
    "BASE": "base",
    "IMX": "immutable-x",
    "ZK": "zksync-era",

    # Bitcoin ecosystem
    "BCH": "bitcoin-cash",
    "BSV": "bitcoin-cash-sv",
    "WBTC": "wrapped-bitcoin",

    # Memes
    "SHIB": "shiba-inu",
    "PEPE": "pepe",
    "WIF": "dogwifcoin",
    "BONK": "bonk",

    # DeFi Blue Chips
    "UNI": "uniswap",
    "AAVE": "aave",
    "CRV": "curve-dao-token",
    "SNX": "synthetix-network-token",
    "CAKE": "pancakeswap-token",
    "COMP": "compound-governance-token",
    "MKR": "maker",
    "LDO": "lido-dao",

    # Stablecoins
    "DAI": "dai",
    "TUSD": "true-usd",
    "FRAX": "frax",
    "PYUSD": "paypal-usd",

    # GameFi / Metaverse
    "SAND": "the-sandbox",
    "MANA": "decentraland",
    "AXS": "axie-infinity",
    "GALA": "gala",
    "ILV": "illuvium",

    # AI Tokens
    "FET": "fetch-ai",
    "AGIX": "singularitynet",
    "RNDR": "render-token",
    "TAO": "bittensor",
    "OCEAN": "ocean-protocol",

    # Privacy
    "XMR": "monero",
    "ZEC": "zcash",

    # Infrastructure
    "LINK": "chainlink",
    "FIL": "filecoin",
    "ICP": "internet-computer",
    "GRT": "the-graph",
    "INJ": "injective-protocol",
    "KAS": "kaspa",

    # RWA (Real World Assets)
    "ONDO": "ondo-finance",
    "RWA": "rwa-token",

    # Oracles & Data
    "PYTH": "pyth-network",
    "BAND": "band-protocol",

    # Japanese / APAC Favorites
    "QTUM": "qtum",
    "IOTA": "iota",
    "VET": "vechain",

    # Smaller but widely known
    "FTM": "fantom",
    "EGLD": "multiversx",
    "RUNE": "thorchain",
    "DYDX": "dydx",
    "SKL": "skale",
    "KAVA": "kava",
    "ROSE": "oasis-network",
    "ONE": "harmony",
    "CHZ": "chiliz",
    "ENJ": "enjincoin",
}


# ----------------- Asset Resolver -----------------
import re
from difflib import get_close_matches

# Reverse mapping: CoinGecko name → symbol
name_to_symbol = {v.lower(): k for k, v in asset_symbols.items()}

# Search index for fuzzy matching
search_index = list(asset_symbols.keys()) + list(name_to_symbol.keys())


def clean_query(query: str) -> str:
    """Normalize user input for matching."""
    replacements = [
        "price of", "show me", "coin", "crypto",
        "token", "value", "usd", "$"
    ]
    q = query.lower().strip()
    for r in replacements:
        q = q.replace(r, "")
    return q.strip()


def resolve_asset_symbol(query: str) -> dict:
    """
    Resolve a user query to:
    - symbol (e.g., BTC)
    - CoinGecko ID (e.g., bitcoin)
    - full name (e.g., Bitcoin)
    Handles tickers, full names, synonyms, partial matches, and minor typos.
    """
    raw_query = query
    q = clean_query(query)

    # Exact match (symbol)
    if q.upper() in asset_symbols:
        symbol = q.upper()
        return {
            "symbol": symbol,
            "id": asset_symbols[symbol],
            "name": asset_symbols[symbol].replace("-", " ").title(),
            "match": "exact-symbol"
        }

    # Exact match (name)
    if q in name_to_symbol:
        symbol = name_to_symbol[q]
        return {
            "symbol": symbol,
            "id": asset_symbols[symbol],
            "name": q.title(),
            "match": "exact-name"
        }

    # Fuzzy match / partial match
    candidates = get_close_matches(q, search_index, n=1, cutoff=0.45)
    if candidates:
        candidate = candidates[0]
        symbol = candidate.upper() if candidate.upper() in asset_symbols else name_to_symbol.get(candidate)
        return {
            "symbol": symbol,
            "id": asset_symbols[symbol],
            "name": asset_symbols[symbol].replace("-", " ").title(),
            "match": "fuzzy"
        }

    # Nothing matched
    return {
        "symbol": None,
        "id": None,
        "name": None,
        "match": "none",
        "error": f"Could not resolve crypto symbol from '{raw_query}'"
    }
