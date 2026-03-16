"""
Shared configuration for all FundHQ agents.
Constants that apply across divisions (onchain, research, technical).
"""

# ===== FIREBASE =====
FIREBASE_DB_URL = "https://fundhq-8feae-default-rtdb.europe-west1.firebasedatabase.app"
FIREBASE_ALERTS_PATH = "/fundHQ/alerts"

# ===== GRADE SYSTEM =====
# Universal grading for wallets, signals, entities
GRADE_RANK = {"A": 5, "B": 4, "C": 3, "D": 2, "F": 1, "?": 0}

# ===== WATCH LIST =====
# Coins the fund is actively tracking across all agents
WATCH_COINS = ["BTC", "ETH", "SOL", "HYPE", "DOGE", "SUI", "AVAX", "LINK", "PEPE", "WIF"]

# ===== ALERT SEVERITY =====
SEVERITY_INFO = "info"
SEVERITY_WARNING = "warning"
SEVERITY_OPPORTUNITY = "opportunity"

# ===== REGIME LABELS =====
REGIME_RISK_ON = "risk-on"
REGIME_RISK_OFF = "risk-off"
REGIME_NEUTRAL = "neutral"
REGIME_UNKNOWN = "unknown"

# ===== PROFITABILITY SCORING =====
PROFITABILITY_MIN_TRADES = 20  # Need at least 20 trades to score


def grade_passes(grade: str, min_grade: str) -> bool:
    """Check if a grade meets the minimum threshold."""
    return GRADE_RANK.get(grade, 0) >= GRADE_RANK.get(min_grade, 0)
