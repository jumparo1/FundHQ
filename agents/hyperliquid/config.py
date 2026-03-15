"""Hyperliquid Agent Configuration"""

# Hyperliquid API
HL_API_URL = "https://api.hyperliquid.xyz/info"
HL_WS_URL = "wss://api.hyperliquid.xyz/ws"

# Firebase — write alerts directly via REST API
FIREBASE_DB_URL = "https://fundhq-8feae-default-rtdb.europe-west1.firebasedatabase.app"
FIREBASE_ALERTS_PATH = "/fundHQ/alerts"
FIREBASE_HL_PATH = "/fundHQ/hyperliquid"

# Agent settings
SCAN_INTERVAL_SECONDS = 300          # Re-scan saved wallets every 5 min
WHALE_MIN_POSITION_USD = 500_000     # Min $500K position to flag as whale
WHALE_MIN_ACCOUNT_USD = 100_000      # Min $100K account value
PROFITABILITY_MIN_TRADES = 20        # Need at least 20 trades to score

# Coins to watch for whale activity (user's focus list)
WATCH_COINS = ["BTC", "ETH", "SOL", "HYPE", "DOGE", "SUI", "AVAX", "LINK", "PEPE", "WIF"]

# Alert thresholds
ALERT_NEW_POSITION_USD = 1_000_000   # Alert when whale opens $1M+ position
ALERT_POSITION_CLOSE_USD = 500_000   # Alert when whale closes $500K+ position
ALERT_PNL_CHANGE_PCT = 20           # Alert when unrealized PnL swings 20%+
