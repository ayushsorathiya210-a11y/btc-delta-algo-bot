class BotState:

    def __init__(self):

        self.capital = None
        self.peak = None

        self.position = None
        self.entry_price = 0
        self.size = 0
        self.stop = 0

        self.last_candle_time = None
        self.entry_candle = None

        self.trades = []

    def initialize(self, balance):

        if self.capital is None:
            self.capital = balance
            self.peak = balance
