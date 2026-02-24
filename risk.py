from config import BASE_RISK, MIN_RISK

def dynamic_risk(current_dd, trades, atr_percentile):

    if current_dd < 0.10:
        risk = BASE_RISK
    elif current_dd < 0.20:
        risk = BASE_RISK * 0.75
    elif current_dd < 0.30:
        risk = BASE_RISK * 0.5
    else:
        risk = MIN_RISK

    if len(trades) >= 3:
        if trades[-1] < 0 and trades[-2] < 0 and trades[-3] < 0:
            risk *= 0.5

    if atr_percentile > 0.90:
        risk *= 0.7

    return max(risk, MIN_RISK)
