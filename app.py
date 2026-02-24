import time
from delta_client import DeltaClient
from data import fetch_candles
from strategy import generate_signal
from risk import calculate_position
from execution import apply_slippage
from config import SYMBOL

client = DeltaClient()

print("🚀 Delta India Testnet Bot Started")

while True:
    try:
        df = fetch_candles()

        signal, stop = generate_signal(df)

        if signal:

            balance_data = client.get_balance()

            # Extract USDT balance
            balances = balance_data["result"]
            usdt_balance = next(
                (float(x["available_balance"]) for x in balances if x["asset_symbol"] == "USDT"),
                0
            )

            entry_price = df.iloc[-1]["close"]
            entry_price = apply_slippage(entry_price, signal)

            size = calculate_position(usdt_balance, entry_price, stop)

            if size > 0:
                print(f"Placing {signal.upper()} Order | Size: {size}")
                response = client.place_market_order(SYMBOL, signal, size)
                print(response)

        time.sleep(60)

    except Exception as e:
        print("Error:", e)
        time.sleep(30)