import requests
import pandas as pd
from config import SYMBOL

BASE_URL = "https://api.delta.exchange/v2/history/candles"

def fetch_candles(resolution, limit=400):

    params = {
        "symbol": SYMBOL,
        "resolution": resolution,
        "limit": limit
    }

    try:
        r = requests.get(BASE_URL, params=params, timeout=10)
        data = r.json()

        # 🔹 Check API response
        if "result" not in data:
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
