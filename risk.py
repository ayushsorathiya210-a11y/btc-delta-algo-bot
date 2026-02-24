# risk.py

BASE_RISK = 0.01

def dynamic_risk(balance, drawdown, losing_streak):
    risk = BASE_RISK

    if drawdown > 0.2:
        risk *= 0.5

    if losing_streak >= 3:
        risk *= 0.5

    return balance * risk


def calculate_position(balance, entry_price, stop, drawdown, losing_streak):
    risk_amount = dynamic_risk(balance, drawdown, losing_streak)

    stop_distance = abs(entry_price - stop)

    if stop_distance == 0:
        return 0

    size = risk_amount / stop_distance

    max_position_value = balance * 3
    if size * entry_price > max_position_value:
        size = max_position_value / entry_price

    return round(size, 3)
