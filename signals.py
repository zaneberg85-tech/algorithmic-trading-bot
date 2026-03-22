import pandas as pd
import numpy as np

class SignalGenerator:
    def __init__(self, data):
        self.data = data

    def moving_average(self, window):
        return self.data['close'].rolling(window=window).mean()

    def rsi(self, period=14):
        delta = self.data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def generate_signals(self):
        self.data['signal'] = 0  # Default to no signal
        self.data['ma'] = self.moving_average(20)
        self.data['rsi'] = self.rsi()

        # Buy signal: when price is above moving average and RSI is below 30
        self.data.loc[(self.data['close'] > self.data['ma']) & (self.data['rsi'] < 30), 'signal'] = 1  
        # Sell signal: when price is below moving average and RSI is above 70
        self.data.loc[(self.data['close'] < self.data['ma']) & (self.data['rsi'] > 70), 'signal'] = -1
        return self.data

# Example usage:
# df = pd.DataFrame({'close': [/* price data */]})
# signal_generator = SignalGenerator(df)
# signals = signal_generator.generate_signals()