from config import RISK_PERCENT, LEVERAGE_CAP

def calculate_position(balance, entry_price, stop_price):

    risk_amount = balance * RISK_PERCENT
    risk_per_unit = abs(entry_price - stop_price)

    if risk_per_unit <= 0:
        return 0

    size = risk_amount / risk_per_unit

    max_position_value = balance * LEVERAGE_CAP

    if size * entry_price > max_position_value:
        size = max_position_value / entry_price

    return round(size, 4)