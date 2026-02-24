import requests
import pandas as pd
from config import BASE_URL, SYMBOL, TIMEFRAME, EMA_PERIOD, ATR_PERIOD

def fetch_candles():
    url = f"{BASE_URL}/v2/history/candles"
    params = {
        "symbol": SYMBOL,
        "resolution": TIMEFRAME,
        "limit": 300
    }

    r = requests.get(url, params=params)
    data = r.json()

    df = pd.DataFrame(data["result"])

    numeric = ["open","high","low","close","volume"]
    df[numeric] = df[numeric].astype(float)

    df["ema"] = df["close"].ewm(span=EMA_PERIOD).mean()

    df["prev_close"] = df["close"].shift(1)
    df["tr"] = df[["high","low","prev_close"]].apply(
        lambda x: max(
            x["high"]-x["low"],
            abs(x["high"]-x["prev_close"]),
            abs(x["low"]-x["prev_close"])
        ), axis=1
    )

    df["atr"] = df["tr"].rolling(ATR_PERIOD).mean()

    return df