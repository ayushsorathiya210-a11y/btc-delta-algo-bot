import time
import sys
import gc

from delta_client import DeltaClient
from config import *
from state import BotState
from data import fetch_candles
from strategy import prepare_indicators, strong_candle
from risk import dynamic_risk

client = DeltaClient()
state = BotState()

print("[SYSTEM] Trading Bot Started")
sys.stdout.flush()


def log(msg):

    print(msg)
    sys.stdout.flush()

    with open("bot.log", "a") as f:
        f.write(msg + "\n")


def manage_position(price):

    if state.position == "long" and price <= state.stop:

        log("[EXIT] Stop Loss Hit")

        client.place_order(SYMBOL, "sell", state.size)

        state.position = None

    elif state.position == "short" and price >= state.stop:

        log("[EXIT] Stop Loss Hit")

        client.place_order(SYMBOL, "buy", state.size)

        state.position = None


def run_bot():

    while True:

        try:

            df = fetch_candles("15m")
            df1h = fetch_candles("1h")
            df4h = fetch_candles("4h")

            if df.empty or df1h.empty or df4h.empty:
                time.sleep(API_SLEEP)
                continue

            df = prepare_indicators(df, df1h, df4h)

            row = df.iloc[-1]
            prev = df.iloc[-2]

            price = row["close"]

            if state.position:
                manage_position(price)

            current_time = row["time"]

            if state.last_candle_time != current_time:

                state.last_candle_time = current_time

                log(f"[BOT] New 15m Candle {current_time}")

            balance_data = client.get_balance()

            if not balance_data.get("success"):
                time.sleep(API_SLEEP)
                continue

            balances = balance_data["result"]

            usdt_balance = next(
                (float(x["available_balance"])
                 for x in balances
                 if x["asset_symbol"] == "USDT"),
                0
            )

            state.initialize(usdt_balance)

            if state.position is None:

                if row["atr_percentile"] < 0.70:
                    time.sleep(API_SLEEP)
                    continue

                long_signal = (
                    strong_candle(df, -2)
                    and strong_candle(df, -3)
                    and strong_candle(df, -4)
                    and price > row["ema200"]
                    and row["ema_slope"] > 0
                )

                short_signal = (
                    strong_candle(df, -2)
                    and strong_candle(df, -3)
                    and strong_candle(df, -4)
                    and price < row["ema200"]
                    and row["ema_slope"] < 0
                )

                if long_signal or short_signal:

                    entry_price = price

                    stop = prev["low"] if long_signal else prev["high"]

                    risk_per_unit = abs(entry_price - stop)

                    if risk_per_unit == 0:
                        continue

                    risk_pct = dynamic_risk(
                        0,
                        state.trades,
                        row["atr_percentile"]
                    )

                    size = (state.capital * risk_pct) / risk_per_unit

                    state.position = "long" if long_signal else "short"
                    state.entry_price = entry_price
                    state.size = size
                    state.stop = stop

                    client.place_order(
                        SYMBOL,
                        "buy" if long_signal else "sell",
                        size
                    )

                    log(f"[TRADE] ENTRY {state.position} size:{size}")

            time.sleep(API_SLEEP)

            gc.collect()

        except Exception as e:

            log(f"[CRASH] {str(e)}")
            time.sleep(30)


if __name__ == "__main__":
    run_bot()
