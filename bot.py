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


def run_bot():

    while True:

        log("[BOT] Checking market...")

        try:

            df = fetch_candles("15m")
            df1h = fetch_candles("1h")
            df4h = fetch_candles("4h")

            if df.empty or df1h.empty or df4h.empty:

                log("[WARN] Candle data missing")
                time.sleep(60)
                continue

            df = prepare_indicators(df, df1h, df4h)

            row = df.iloc[-1]
            prev = df.iloc[-2]

            current_time = row["time"]

            if state.last_candle_time == current_time:
                time.sleep(30)
                continue

            state.last_candle_time = current_time

            balance_data = client.get_balance()

            if not balance_data.get("success"):

                log("[ERROR] Balance fetch failed")
                time.sleep(60)
                continue

            balances = balance_data["result"]

            usdt_balance = next(
                (float(x["available_balance"])
                 for x in balances
                 if x["asset_symbol"] == "USDT"),
                0
            )

            state.initialize(usdt_balance)

            equity = state.capital

            log(f"[ACCOUNT] Equity:{equity}")

            if state.cooldown > 0:
                state.cooldown -= 1
                time.sleep(60)
                continue

            if state.position is None:

                if row["atr_percentile"] < 0.70:
                    continue

                long_signal = (
                    strong_candle(df, -2)
                    and strong_candle(df, -3)
                    and strong_candle(df, -4)
                    and row["close"] > row["ema200"]
                    and row["ema_slope"] > 0
                )

                short_signal = (
                    strong_candle(df, -2)
                    and strong_candle(df, -3)
                    and strong_candle(df, -4)
                    and row["close"] < row["ema200"]
                    and row["ema_slope"] < 0
                )

                if long_signal or short_signal:

                    risk_pct = dynamic_risk(
                        0,
                        state.trades,
                        row["atr_percentile"]
                    )

                    entry_price = row["close"]

                    stop = prev["low"] if long_signal else prev["high"]

                    risk_per_unit = abs(entry_price - stop)

                    size = (state.capital * risk_pct) / risk_per_unit

                    state.position = "long" if long_signal else "short"
                    state.entry_price = entry_price
                    state.size = size

                    client.place_market_order(
                        SYMBOL,
                        "buy" if long_signal else "sell",
                        size
                    )

                    log(f"[TRADE] ENTRY {state.position} size:{size}")

            time.sleep(60)

            del df
            del df1h
            del df4h

            gc.collect()

        except Exception as e:

            log(f"[CRASH] {str(e)}")
            time.sleep(30)


if __name__ == "__main__":
    run_bot()

