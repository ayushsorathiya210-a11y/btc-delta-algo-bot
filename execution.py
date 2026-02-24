from config import FEE_RATE, SLIPPAGE

def apply_slippage(price, side):
    if side == "buy":
        return price * (1 + SLIPPAGE)
    else:
        return price * (1 - SLIPPAGE)

def estimate_fee(size, price):
    return abs(size * price) * FEE_RATE