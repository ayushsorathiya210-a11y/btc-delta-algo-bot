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

    try:
        r = requests.get(CANDLE_URL, params=params, timeout=10)
        data = r.json()

        print("CANDLE RESPONSE:", data)  # debug

        if not data.get("success"):
            print("⚠️ Candle API Error:", data)
            return pd.DataFrame()

        df = pd.DataFrame(data["result"])

        if df.empty:
            return pd.DataFrame()

        df["time"] = pd.to_datetime(df["time"], unit="s")

        numeric = ["open", "high", "low", "close", "volume"]
        df[numeric] = df[numeric].astype(float)

        return df.sort_values("time").reset_index(drop=True)

    except Exception as e:
        print("⚠️ Candle Fetch Error:", e)
        return pd.DataFrame()
