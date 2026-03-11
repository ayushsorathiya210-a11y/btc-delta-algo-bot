import time
import sys
from delta_client import DeltaClient

from config import *
from state import BotState
from data import fetch_candles
from strategy import prepare_indicators, strong_candle
from risk import dynamic_risk

client = DeltaClient()
state = BotState()

print("🚀 BACKGROUND WORKER BOT STARTED")
sys.stdout.flush()


# ================= LOGGING =================
def log_message(msg):
    print(msg)
    sys.stdout.flush()

    with open("bot.log", "a") as f:
        f.write(msg + "\n")


def log_candle(row, equity):
    msg = (
        f"[{row['time']}] 15m Candle | "
        f"O:{row['open']:.2f} H:{row['high']:.2f} "
        f"L:{row['low']:.2f} C:{row['close']:.2f} | "
        f"ATR%:{row['atr_percentile']:.2f} | "
        f"Equity:{equity:.2f}"
    )
    log_message(msg)


def log_entry(position, price, size, stop, equity, risk_pct):
    msg = (
        f"🟢 ENTRY {position.upper()} | "
        f"Price:{price:.2f} Size:{size:.4f} Stop:{stop:.2f} | "
        f"Equity:{equity:.2f} Risk%:{risk_pct*100:.2f}"
    )
    log_message(msg)


def log_exit(position, exit_price, pnl, equity):
    msg = (
        f"🔴 EXIT {position.upper()} | "
        f"Price:{exit_price:.2f} PnL:{pnl:.2f} | "
        f"Equity:{equity:.2f}"
    )
    log_message(msg)


# ================= BOT LOOP =================
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
            balances = balance_data.get("result", None)

            if balances is None:
                log_message(f"⚠️ Failed balance fetch: {balance_data}")
                time.sleep(60)
                continue

            usdt_balance = next(
                (float(x["available_balance"])
                 for x in balances if x["asset_symbol"] == "USDT"), 0
            )

            state.initialize(usdt_balance)

            equity = state.capital

            if state.position == "long":
                equity += (row["close"] - state.entry_price) * state.size

            elif state.position == "short":
                equity += (state.entry_price - row["close"]) * state.size

            state.peak = max(state.peak, equity)
            current_dd = (state.peak - equity) / state.peak
            state.max_dd = max(state.max_dd, current_dd)

            log_candle(row, equity)

            if state.cooldown > 0:
                state.cooldown -= 1
                time.sleep(60)
                continue

            # ================= ENTRY =================
            if state.position is None:

                if row["atr_percentile"] < 0.70 or abs(row["ema_slope"]) <= row["close"] * 0.001:
                    time.sleep(60)
                    continue

                long_signal = (
                    strong_candle(df, -2)
                    and strong_candle(df, -3)
                    and strong_candle(df, -4)
                    and row["close"] > row["ema200"]
                    and row["close"] > row["ema200_1h"]
                    and row["ema_slope"] > 0
                )

                short_signal = (
                    strong_candle(df, -2)
                    and strong_candle(df, -3)
                    and strong_candle(df, -4)
                    and row["close"] < row["ema200"]
                    and row["close"] < row["ema200_1h"]
                    and row["ema_slope"] < 0
                )

                if long_signal or short_signal:

                    risk_pct = dynamic_risk(
                        current_dd,
                        state.trades,
                        row["atr_percentile"]
                    )

                    entry_price = (
                        row["close"] * (1 + SLIPPAGE)
                        if long_signal
                        else row["close"] * (1 - SLIPPAGE)
                    )

                    stop = (
                        prev["low"] - 0.2 * row["atr"]
                        if long_signal
                        else prev["high"] + 0.2 * row["atr"]
                    )

                    risk_per_unit = max(abs(entry_price - stop), row["atr"] * 0.8)

                    risk_capital = state.capital * risk_pct

                    size = risk_capital / risk_per_unit

                    if size * entry_price > state.capital * LEVERAGE_CAP:
                        size = (state.capital * LEVERAGE_CAP) / entry_price

                    state.position = "long" if long_signal else "short"
                    state.entry_price = entry_price
                    state.size = size
                    state.entry_risk = risk_per_unit

                    client.place_market_order(
                        SYMBOL,
                        "buy" if long_signal else "sell",
                        size
                    )

                    log_entry(
                        state.position,
                        entry_price,
                        size,
                        stop,
                        equity,
                        risk_pct
                    )

            # ================= EXIT =================
            else:

                exit_price = None

                if state.position == "long":
                    stop = prev["low"] - 0.2 * row["atr"]
                    if row["close"] < stop:
                        exit_price = stop

                if state.position == "short":
                    stop = prev["high"] + 0.2 * row["atr"]
                    if row["close"] > stop:
                        exit_price = stop

                if exit_price:

                    pnl = (
                        (exit_price - state.entry_price) * state.size
                        if state.position == "long"
                        else (state.entry_price - exit_price) * state.size
                    )

                    fee = (
                        abs(state.size * state.entry_price) * FEE_RATE
                        + abs(state.size * exit_price) * FEE_RATE
                    )

                    pnl -= fee

                    state.capital += pnl
                    state.capital = max(state.capital, 0)

                    state.trades.append(pnl)

                    if pnl < 0:
                        state.losing_streak += 1
                    else:
                        state.losing_streak = 0

                    client.place_market_order(
                        SYMBOL,
                        "sell" if state.position == "long" else "buy",
                        state.size
                    )

                    log_exit(
                        state.position,
                        exit_price,
                        pnl,
                        state.capital
                    )

                    state.position = None
                    state.cooldown = COOLDOWN_BARS

            time.sleep(60)

        except Exception as e:

            log_message(f"Bot Error: {e}")
            time.sleep(30)


if __name__ == "__main__":
    run_bot()
