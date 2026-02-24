import time
import threading
import os
from flask import Flask
from delta_client import DeltaClient

from config import *
from state import BotState
from data import fetch_candles
from strategy import prepare_indicators, strong_candle
from risk import dynamic_risk

client = DeltaClient()
state = BotState()

print("🚀 FULL 1:1 BACKTEST ALIGNED BOT STARTED")

app = Flask(__name__)

@app.route("/")
def home():
    return "Institutional Bot Running 🚀"

def run_bot():

    while True:
        try:

            df = fetch_candles("15m")
            df1h = fetch_candles("1h")
            df4h = fetch_candles("4h")

            df = prepare_indicators(df, df1h, df4h)

            row = df.iloc[-1]
            prev = df.iloc[-2]

            current_time = row["time"]

            if state.last_candle_time == current_time:
                time.sleep(60)
                continue

            state.last_candle_time = current_time

            balance_data = client.get_balance()
            balances = balance_data["result"]

            usdt_balance = next(
                (float(x["available_balance"]) for x in balances if x["asset_symbol"]=="USDT"),0)

            state.initialize(usdt_balance)

            equity = state.capital

            if state.position == "long":
                equity += (row["close"] - state.entry_price) * state.size
            elif state.position == "short":
                equity += (state.entry_price - row["close"]) * state.size

            state.peak = max(state.peak, equity)
            current_dd = (state.peak - equity) / state.peak
            state.max_dd = max(state.max_dd, current_dd)

            if state.cooldown > 0:
                state.cooldown -= 1
                time.sleep(60)
                continue

            if state.position is None:

                if row["atr_percentile"] < 0.70 or \
                   abs(row["ema_slope"]) <= row["close"]*0.001:
                    time.sleep(60)
                    continue

                long_signal = (
                    strong_candle(df, -2) and
                    strong_candle(df, -3) and
                    strong_candle(df, -4) and
                    row["close"] > row["ema200"] and
                    row["close"] > row["ema200_1h"] and
                    row["ema_slope"] > 0
                )

                short_signal = (
                    strong_candle(df, -2) and
                    strong_candle(df, -3) and
                    strong_candle(df, -4) and
                    row["close"] < row["ema200"] and
                    row["close"] < row["ema200_1h"] and
                    row["ema_slope"] < 0
                )

                if long_signal or short_signal:

                    risk_pct = dynamic_risk(
                        current_dd,
                        state.trades,
                        row["atr_percentile"]
                    )

                    entry_price = row["close"]*(1+SLIPPAGE) \
                        if long_signal else row["close"]*(1-SLIPPAGE)

                    stop = prev["low"] - 0.2*row["atr"] \
                        if long_signal else prev["high"] + 0.2*row["atr"]

                    risk_per_unit = max(abs(entry_price-stop), row["atr"]*0.8)
                    risk_capital = state.capital*risk_pct
                    size = risk_capital/risk_per_unit

                    if size*entry_price > state.capital*LEVERAGE_CAP:
                        size = (state.capital*LEVERAGE_CAP)/entry_price

                    state.position = "long" if long_signal else "short"
                    state.entry_price = entry_price
                    state.size = size
                    state.entry_risk = risk_per_unit

                    client.place_market_order(
                        SYMBOL,
                        "buy" if long_signal else "sell",
                        size
                    )

            else:

                exit_price = None

                if state.position == "long":
                    stop = prev["low"] - 0.2*row["atr"]
                    if row["close"] < stop:
                        exit_price = stop

                if state.position == "short":
                    stop = prev["high"] + 0.2*row["atr"]
                    if row["close"] > stop:
                        exit_price = stop

                if exit_price:

                    pnl = (exit_price-state.entry_price)*state.size \
                        if state.position=="long" else \
                        (state.entry_price-exit_price)*state.size

                    fee = abs(state.size*state.entry_price)*FEE_RATE + \
                          abs(state.size*exit_price)*FEE_RATE

                    pnl -= fee

                    state.capital += pnl
                    state.capital = max(state.capital,0)

                    state.trades.append(pnl)

                    if pnl < 0:
                        state.losing_streak += 1
                    else:
                        state.losing_streak = 0

                    client.place_market_order(
                        SYMBOL,
                        "sell" if state.position=="long" else "buy",
                        state.size
                    )

                    state.position = None
                    state.cooldown = COOLDOWN_BARS

            time.sleep(60)

        except Exception as e:
            print("Bot Error:", e)
            time.sleep(30)

threading.Thread(target=run_bot).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
