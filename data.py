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

    r = requests.get(BASE_URL, params=params, timeout=10)
    data = r.json()

    df = pd.DataFrame(data["result"])

    df["time"] = pd.to_datetime(df["time"], unit="s")
    numeric = ["open","high","low","close","volume"]
    df[numeric] = df[numeric].astype(float)

    return df.sort_values("time").reset_index(drop=True)
