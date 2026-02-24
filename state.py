class BotState:
    def __init__(self):
        self.capital = None
        self.peak = None
        self.max_dd = 0

        self.position = None
        self.entry_price = 0
        self.size = 0
        self.entry_risk = 0

        self.cooldown = 0
        self.last_candle_time = None

        self.trades = []
        self.losing_streak = 0

    def initialize(self, balance):
        if self.capital is None:
            self.capital = balance
            self.peak = balance
