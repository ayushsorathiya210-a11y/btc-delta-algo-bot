import requests
import pandas as pd
import time
from config import SYMBOL, CANDLE_URL

def fetch_candles(resolution="15m", limit=400):

    sec_map = {
        "1m": 60,
        "3m": 180,
        "5m": 300,
        "15m": 900,
        "30m": 1800,
        "1h": 3600,
        "2h": 7200,
        "4h": 14400
    }

    if resolution not in sec_map:
        print("⚠️ Invalid resolution:", resolution)
        return pd.DataFrame()

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
        r.raise_for_status()

        data = r.json()

        if not data.get("success"):
            print("⚠️ Candle API Error:", data)
            return pd.DataFrame()

        candles = data.get("result", [])

        if not candles:
            print("⚠️ Candle data missing")
            return pd.DataFrame()

        print(f"📊 Candles received: {len(candles)}")

        df = pd.DataFrame(candles)

        df["time"] = pd.to_datetime(df["time"], unit="s")

        numeric_cols = ["open", "high", "low", "close", "volume"]
        df[numeric_cols] = df[numeric_cols].astype(float)

        df = df.sort_values("time").reset_index(drop=True)

        return df

    except requests.exceptions.RequestException as e:
        print("⚠️ Candle Fetch Error:", e)
        return pd.DataFrame()
