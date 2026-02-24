# state.py

class BotState:
    def __init__(self):
        self.equity_peak = 0
        self.current_drawdown = 0
        self.losing_streak = 0
        self.cooldown_bars = 0
        self.last_candle_time = None

    def update_equity(self, balance):
        if balance > self.equity_peak:
            self.equity_peak = balance
        
        if self.equity_peak > 0:
            self.current_drawdown = (self.equity_peak - balance) / self.equity_peak