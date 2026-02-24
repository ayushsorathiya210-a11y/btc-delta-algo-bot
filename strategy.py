import numpy as np
import pandas as pd
from config import EMA_PERIOD, ATR_PERIOD, ATR_ROLLING

def strong_candle(df, idx):
    r = df.iloc[idx]
    body = abs(r["close"] - r["open"])
    rng = r["high"] - r["low"]
    return body > 0.5 * rng if rng != 0 else False

def prepare_indicators(df, df1h, df4h):

    df["ema200"] = df["close"].ewm(span=EMA_PERIOD, adjust=False).mean()
    df1h["ema200_1h"] = df1h["close"].ewm(span=EMA_PERIOD, adjust=False).mean()
    df4h["ema200_4h"] = df4h["close"].ewm(span=EMA_PERIOD, adjust=False).mean()
    df4h["ema_slope"] = df4h["ema200_4h"].diff(5)

    df = pd.merge_asof(df.sort_values("time"),
                       df1h[["time","ema200_1h"]].sort_values("time"),
                       on="time", direction="backward")

    df = pd.merge_asof(df.sort_values("time"),
                       df4h[["time","ema200_4h","ema_slope"]].sort_values("time"),
                       on="time", direction="backward")

    df["prev_close"] = df["close"].shift(1)

    df["tr"] = np.maximum.reduce([
        df["high"] - df["low"],
        abs(df["high"] - df["prev_close"]),
        abs(df["low"] - df["prev_close"])
    ])

    df["atr"] = df["tr"].rolling(ATR_PERIOD).mean()
    df["atr_pct"] = df["atr"] / df["close"]

    df["atr_percentile"] = df["atr_pct"].rolling(ATR_ROLLING).apply(
        lambda x: pd.Series(x).rank(pct=True).iloc[-1]
    )

    return df
