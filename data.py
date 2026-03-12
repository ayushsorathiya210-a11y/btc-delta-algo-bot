import requests
import pandas as pd
import time
from config import SYMBOL, CANDLE_URL


def fetch_candles(resolution="15m", limit=400):

    sec_map = {
        "15m": 900,
        "1h": 3600,
        "4h": 14400
    }

    end = int(time.time())
    start = end - (limit * sec_map[resolution])

    params = {
        "symbol": SYMBOL,
        "resolution": resolution,
        "start": start,
        "end": end
    }

    r = requests.get(CANDLE_URL, params=params, timeout=10)

    data = r.json()

    if not data.get("success"):
        return pd.DataFrame()

    candles = data["result"]

    df = pd.DataFrame(candles)

    df["time"] = pd.to_datetime(df["time"], unit="s")

    numeric = ["open", "high", "low", "close", "volume"]

    df[numeric] = df[numeric].astype(float)

    return df.sort_values("time").reset_index(drop=True)
