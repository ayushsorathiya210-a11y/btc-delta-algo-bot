import os

# =====================================
# DELTA INDIA TESTNET (DEMO)
# =====================================
BASE_URL = "https://cdn-ind.testnet.deltaex.org"

API_KEY = os.getenv("DELTA_API_KEY")
API_SECRET = os.getenv("DELTA_API_SECRET")

SYMBOL = "BTCUSDT"

EMA_PERIOD = 200
ATR_PERIOD = 14
ATR_ROLLING = 300

BASE_RISK = 0.01
MIN_RISK = 0.004

LEVERAGE_CAP = 3
FEE_RATE = 0.0004
SLIPPAGE = 0.0005

COOLDOWN_BARS = 6
