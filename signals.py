import pandas as pd
import numpy as np

class SignalGenerator:
    def __init__(self, data):
        """
        Initialize SignalGenerator with price data.
        
        Args:
            data (pd.DataFrame): DataFrame with 'close' column containing price data
        """
        if data is None or data.empty:
            raise ValueError("Data cannot be empty")
        if 'close' not in data.columns:
            raise ValueError("Data must contain 'close' column")
        
        self.data = data.copy()

    def moving_average(self, window):
        """
        Calculate simple moving average.
        
        Args:
            window (int): Window size for MA calculation
            
        Returns:
            pd.Series: Moving average values
        """
        if window <= 0:
            raise ValueError("Window must be positive")
        return self.data['close'].rolling(window=window).mean()

    def rsi(self, period=14):
        """
        Calculate Relative Strength Index (RSI).
        Fixed to handle division by zero and NaN values.
        
        Args:
            period (int): Period for RSI calculation (default: 14)
            
        Returns:
            pd.Series: RSI values (0-100)
        """
        if period <= 0:
            raise ValueError("Period must be positive")
        
        delta = self.data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        # Fix division by zero: when loss is 0, RSI should be 100
        rs = np.where(loss != 0, gain / loss, np.inf)
        rsi = 100 - (100 / (1 + rs))
        
        # Handle infinite values
        rsi = np.where(np.isinf(rsi), 100, rsi)
        
        return pd.Series(rsi, index=self.data.index)

    def macd(self, fast=12, slow=26, signal=9):
        """
        Calculate MACD (Moving Average Convergence Divergence).
        
        Args:
            fast (int): Fast EMA period (default: 12)
            slow (int): Slow EMA period (default: 26)
            signal (int): Signal line EMA period (default: 9)
            
        Returns:
            tuple: (macd_line, signal_line, histogram)
        """
        ema_fast = self.data['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = self.data['close'].ewm(span=slow, adjust=False).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram

    def bollinger_bands(self, window=20, num_std=2):
        """
        Calculate Bollinger Bands.
        
        Args:
            window (int): Period for moving average (default: 20)
            num_std (float): Number of standard deviations (default: 2)
            
        Returns:
            tuple: (upper_band, middle_band, lower_band)
        """
        if window <= 0:
            raise ValueError("Window must be positive")
        if num_std <= 0:
            raise ValueError("Standard deviation multiplier must be positive")
        
        middle_band = self.data['close'].rolling(window=window).mean()
        std_dev = self.data['close'].rolling(window=window).std()
        
        upper_band = middle_band + (std_dev * num_std)
        lower_band = middle_band - (std_dev * num_std)
        
        return upper_band, middle_band, lower_band

    def generate_signals(self):
        """
        Generate trading signals based on multiple indicators.
        
        Returns:
            pd.DataFrame: DataFrame with signal column and indicator values
                signal: 1 (buy), -1 (sell), 0 (hold)
        """
        try:
            self.data['signal'] = 0  # Default to no signal
            
            # Calculate indicators
            self.data['ma'] = self.moving_average(20)
            self.data['rsi'] = self.rsi()
            
            macd_line, signal_line, histogram = self.macd()
            self.data['macd'] = macd_line
            self.data['macd_signal'] = signal_line
            self.data['macd_histogram'] = histogram
            
            upper_band, middle_band, lower_band = self.bollinger_bands()
            self.data['bb_upper'] = upper_band
            self.data['bb_middle'] = middle_band
            self.data['bb_lower'] = lower_band
            
            # Buy signal: MA crossover + RSI < 30 + MACD positive + Price near lower BB
            buy_condition = (
                (self.data['close'] > self.data['ma']) & 
                (self.data['rsi'] < 30) & 
                (self.data['macd_histogram'] > 0) &
                (self.data['close'] < self.data['bb_middle'])
            )
            self.data.loc[buy_condition, 'signal'] = 1
            
            # Sell signal: MA crossover + RSI > 70 + MACD negative + Price near upper BB
            sell_condition = (
                (self.data['close'] < self.data['ma']) & 
                (self.data['rsi'] > 70) & 
                (self.data['macd_histogram'] < 0) &
                (self.data['close'] > self.data['bb_middle'])
            )
            self.data.loc[sell_condition, 'signal'] = -1
            
            return self.data
        
        except Exception as e:
            raise RuntimeError(f"Error generating signals: {str(e)}")


# Example usage:
# df = pd.DataFrame({'close': [/* price data */]})
# signal_generator = SignalGenerator(df)
# signals = signal_generator.generate_signals()
# print(signals[['close', 'signal', 'rsi', 'macd', 'bb_upper', 'bb_lower']])