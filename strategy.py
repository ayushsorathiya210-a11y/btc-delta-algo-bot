def strong_candle(row):
    body = abs(row["close"] - row["open"])
    rng = row["high"] - row["low"]
    return body > 0.5 * rng if rng != 0 else False

def generate_signal(df):

    if len(df) < 250:
        return None, None

    row = df.iloc[-1]
    prev1 = df.iloc[-2]
    prev2 = df.iloc[-3]
    prev3 = df.iloc[-4]

    strong_sequence = (
        strong_candle(prev1) and
        strong_candle(prev2) and
        strong_candle(prev3)
    )

    if strong_sequence:

        if row["close"] > row["ema"]:
            stop = prev1["low"] - 0.2 * row["atr"]
            return "buy", stop

        if row["close"] < row["ema"]:
            stop = prev1["high"] + 0.2 * row["atr"]
            return "sell", stop

    return None, None