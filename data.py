import requests
import pandas as pd
import time
from config import SYMBOL

BASE_URL = "https://api.delta.exchange/v2/history/candles"

def fetch_candles(resolution="15m", limit=400):

    now = int(time.time())
    
    # seconds per candle
    sec_map = {
        "15m": 900,
        "1h": 3600,
        "4h": 14400
    }

    end = now
    start = now - (limit * sec_map[resolution])

    params = {
        "symbol": SYMBOL,
        "resolution": resolution,
        "start": start,
        "end": end
    }

    try:
        r = requests.get(BASE_URL, params=params, timeout=10)
        data = r.json()

        if not data.get("success"):
            print("⚠️ Candle API Error:", data)
            return pd.DataFrame()

        df = pd.DataFrame(data["result"])

        if df.empty:
            return df

        df["time"] = pd.to_datetime(df["time"], unit="s")

        numeric = ["open","high","low","close","volume"]
        df[numeric] = df[numeric].astype(float)

        return df.sort_values("time").reset_index(drop=True)

    except Exception as e:
        print("⚠️ Candle Fetch Error:", e)
        return pd.DataFrame()
