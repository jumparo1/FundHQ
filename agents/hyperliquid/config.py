"""Hyperliquid Agent Configuration"""

# Hyperliquid API
HL_API_URL = "https://api.hyperliquid.xyz/info"
HL_WS_URL = "wss://api.hyperliquid.xyz/ws"
HL_LEADERBOARD_URL = "https://stats-data.hyperliquid.xyz/Mainnet/leaderboard"

# Firebase — write alerts directly via REST API
FIREBASE_DB_URL = "https://fundhq-8feae-default-rtdb.europe-west1.firebasedatabase.app"
FIREBASE_ALERTS_PATH = "/fundHQ/alerts"
FIREBASE_HL_PATH = "/fundHQ/hyperliquid"

# Agent settings
SCAN_INTERVAL_SECONDS = 300          # Re-scan saved wallets every 5 min
REGIME_INTERVAL_SECONDS = 600        # Check market regime every 10 min
WHALE_MIN_POSITION_USD = 500_000     # Min $500K position to flag as whale
WHALE_MIN_ACCOUNT_USD = 100_000      # Min $100K account value
PROFITABILITY_MIN_TRADES = 20        # Need at least 20 trades to score

# Coins to watch for whale activity (user's focus list)
WATCH_COINS = ["BTC", "ETH", "SOL", "HYPE", "DOGE", "SUI", "AVAX", "LINK", "PEPE", "WIF"]

# Alert thresholds
ALERT_NEW_POSITION_USD = 1_000_000   # Alert when whale opens $1M+ position
ALERT_POSITION_CLOSE_USD = 500_000   # Alert when whale closes $500K+ position
ALERT_PNL_CHANGE_PCT = 20           # Alert when unrealized PnL swings 20%+

# ===== SMART ALERT FILTERING =====
# Only alert on whales with grade B or above (skip noisy low-quality wallets)
ALERT_MIN_WHALE_GRADE = "C"          # Minimum grade to generate alerts (A, B, C, D, F)
GRADE_RANK = {"A": 5, "B": 4, "C": 3, "D": 2, "F": 1, "?": 0}

# ===== COPY-TRADE SIGNALS =====
# Track A/B-grade wallets and generate signals when they open positions
COPY_MIN_GRADE = "B"                 # Min grade for copy-trade signals
COPY_MIN_POSITION_USD = 200_000      # Min position size for copy signal
COPY_MAX_LEVERAGE = 10               # Skip signals with leverage above this

# ===== MARKET REGIME =====
# Funding rate thresholds (8h rate)
FUNDING_BULLISH_THRESHOLD = 0.0001   # > 0.01% = longs paying = bullish sentiment
FUNDING_BEARISH_THRESHOLD = -0.00005 # < -0.005% = shorts paying = bearish
# OI change thresholds (% change over scan interval)
OI_EXPANDING_PCT = 3.0               # OI up 3%+ = expanding
OI_CONTRACTING_PCT = -3.0            # OI down 3%+ = contracting
# Squeeze detection
SQUEEZE_FUNDING_EXTREME = 0.0005     # Extreme positive funding (shorts getting squeezed)
SQUEEZE_FUNDING_NEGATIVE = -0.0003   # Extreme negative funding (longs getting squeezed)

# ===== PATTERN DETECTION =====
# Accumulation: multiple whales building same-direction positions on same coin
ACCUMULATION_MIN_WHALES = 3          # At least 3 whales in same direction
ACCUMULATION_LOOKBACK_SCANS = 6      # Over last 6 scans (30 min at 5min intervals)
# Stalker mode: quiet building across multiple scans
STALKER_MIN_SIZE_INCREASE_PCT = 20   # Position grew 20%+ across scans
