import os

# =====================================
# DELTA INDIA TESTNET (DEMO)
# =====================================
BASE_URL = "https://cdn-ind.testnet.deltaex.org"

API_KEY = os.getenv("DELTA_API_KEY")
API_SECRET = os.getenv("DELTA_API_SECRET")

SYMBOL = "BTCUSDT"
TIMEFRAME = "15m"

# Strategy Parameters
EMA_PERIOD = 200
ATR_PERIOD = 14

# Risk
RISK_PERCENT = 0.01
LEVERAGE_CAP = 3
FEE_RATE = 0.0004
SLIPPAGE = 0.0005