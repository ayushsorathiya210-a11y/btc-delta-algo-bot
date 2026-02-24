import pandas as pd
import numpy as np

def generate_signal(df_15m, df_1h, df_4h):

    df_15m["ema200"] = df_15m["close"].ewm(span=200).mean()
    df_1h["ema200"] = df_1h["close"].ewm(span=200).mean()
    df_4h["ema200"] = df_4h["close"].ewm(span=200).mean()

    # EMA slope (4h)
    slope = df_4h["ema200"].iloc[-1] - df_4h["ema200"].iloc[-5]

    # ATR
    df_15m["atr"] = (df_15m["high"] - df_15m["low"]).rolling(14).mean()
    atr_percentile = df_15m["atr"].rank(pct=True).iloc[-1]

    # Trend alignment
    if (
        df_15m["close"].iloc[-1] > df_15m["ema200"].iloc[-1]
        and df_1h["close"].iloc[-1] > df_1h["ema200"].iloc[-1]
        and slope > 0
        and atr_percentile > 0.7
    ):
        stop = df_15m["low"].iloc[-1] - 0.2 * df_15m["atr"].iloc[-1]
        return "buy", stop

    return None, None
