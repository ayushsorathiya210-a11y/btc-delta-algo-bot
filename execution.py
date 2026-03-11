from config import RISK_PER_TRADE
from delta_client import DeltaClient

client = DeltaClient()

def calculate_position_size(balance, atr):

    if atr <= 0:
        return 0

    risk_amount = balance * RISK_PER_TRADE

    position_size = risk_amount / atr

    return round(position_size, 4)


def place_order(symbol, side, size):

    try:

        print(f"[TRADE] Sending Order | {side} | Size: {size}")

        result = client.place_order(
            symbol=symbol,
            side=side,
            size=size
        )

        if not result.get("success"):
            print("❌ Order Failed:", result)
            return None

        print("✅ Order Placed Successfully")

        return result

    except Exception as e:

        print("🚨 Order Exception:", str(e))

        return None


def close_position(symbol):

    try:

        print("[EXIT] Closing Position")

        result = client.close_position(symbol)

        if not result.get("success"):
            print("❌ Close Position Failed:", result)
            return None

        print("✅ Position Closed")

        return result

    except Exception as e:

        print("🚨 Close Position Error:", str(e))

        return None
