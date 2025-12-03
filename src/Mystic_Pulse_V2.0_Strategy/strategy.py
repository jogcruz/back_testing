"""
Mystic Pulse V2.0 Strategy - Python Implementation
Based on the Pine Script indicator by chervolino

This strategy uses directional movement indicators (DI+, DI-) with Wilder smoothing
to track positive and negative trend counts for trade signals.
"""

import numpy as np
import pandas as pd


class MysticPulseV2Strategy:
    """
    Mystic Pulse V2.0 Strategy Implementation
    
    The strategy tracks positive and negative momentum using smoothed directional indicators.
    - Entry: When positive_count >= negative_count (bullish trend)
    - Exit: When negative_count > positive_count (bearish trend)
    """
    
    def __init__(self, adx_length=9, smoothing_factor=1):
        """
        Initialize the strategy with parameters.
        
        Args:
            adx_length (int): Length for Wilder smoothing (default: 9)
            smoothing_factor (int): SMA length for OHLC pre-smoothing (default: 1)
        """
        self.adx_length = adx_length
        self.smoothing_factor = smoothing_factor
        
    def calculate_sma(self, series, period):
        """Calculate Simple Moving Average."""
        return series.rolling(window=period).mean()
    
    def smooth_ohlc(self, df):
        """
        Apply SMA smoothing to OHLC data.
        
        Args:
            df (pd.DataFrame): DataFrame with 'open', 'high', 'low', 'close' columns
            
        Returns:
            tuple: (open_s, high_s, low_s, close_s) smoothed values
        """
        open_s = self.calculate_sma(df['open'], self.smoothing_factor)
        high_s = self.calculate_sma(df['high'], self.smoothing_factor)
        low_s = self.calculate_sma(df['low'], self.smoothing_factor)
        close_s = self.calculate_sma(df['close'], self.smoothing_factor)
        
        return open_s, high_s, low_s, close_s
    
    def calculate_indicators(self, df):
        """
        Calculate all indicators needed for the strategy.
        
        Args:
            df (pd.DataFrame): DataFrame with OHLC data
            
        Returns:
            pd.DataFrame: DataFrame with added indicator columns
        """
        # Make a copy to avoid modifying the original
        data = df.copy()
        
        # Smooth OHLC
        open_s, high_s, low_s, close_s = self.smooth_ohlc(data)
        
        # Calculate True Range
        tr1 = high_s - low_s
        tr2 = abs(high_s - close_s.shift(1))
        tr3 = abs(low_s - close_s.shift(1))
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate Directional Movement
        high_diff = high_s - high_s.shift(1)
        low_diff = low_s.shift(1) - low_s
        
        # DM Plus
        dm_plus = pd.Series(0.0, index=data.index)
        dm_plus[high_diff > low_diff] = high_diff[high_diff > low_diff].clip(lower=0)
        
        # DM Minus
        dm_minus = pd.Series(0.0, index=data.index)
        dm_minus[low_diff > high_diff] = low_diff[low_diff > high_diff].clip(lower=0)
        
        # Wilder Smoothing (similar to Pine Script's smoothing)
        smoothed_tr = self.wilder_smoothing(true_range, self.adx_length)
        smoothed_dm_plus = self.wilder_smoothing(dm_plus, self.adx_length)
        smoothed_dm_minus = self.wilder_smoothing(dm_minus, self.adx_length)
        
        # Calculate DI+ and DI-
        di_plus = (smoothed_dm_plus / smoothed_tr * 100).fillna(0)
        di_minus = (smoothed_dm_minus / smoothed_tr * 100).fillna(0)
        
        # Calculate positive and negative counts
        positive_count = pd.Series(0, index=data.index)
        negative_count = pd.Series(0, index=data.index)
        
        pos_count = 0
        neg_count = 0
        
        for i in range(1, len(data)):
            # Positive count increases when DI+ is rising and DI+ > DI-
            if (di_plus.iloc[i] > di_plus.iloc[i-1] and 
                di_plus.iloc[i] > di_minus.iloc[i] and
                not pd.isna(di_plus.iloc[i]) and 
                not pd.isna(di_plus.iloc[i-1])):
                pos_count += 1
                neg_count = 0
            
            # Negative count increases when DI- is rising and DI- > DI+
            if (di_minus.iloc[i] > di_minus.iloc[i-1] and 
                di_minus.iloc[i] > di_plus.iloc[i] and
                not pd.isna(di_minus.iloc[i]) and 
                not pd.isna(di_minus.iloc[i-1])):
                neg_count += 1
                pos_count = 0
            
            positive_count.iloc[i] = pos_count
            negative_count.iloc[i] = neg_count
        
        # Add calculated values to dataframe
        data['di_plus'] = di_plus
        data['di_minus'] = di_minus
        data['positive_count'] = positive_count
        data['negative_count'] = negative_count
        
        # Calculate trend score
        data['trend_score'] = positive_count - negative_count
        
        # Generate signals
        # Long entry: when positive_count >= negative_count (bullish)
        # Long exit: when negative_count > positive_count (bearish)
        data['is_bullish'] = positive_count >= negative_count
        
        # Signal changes
        data['long_entry'] = (data['is_bullish'] == True) & (data['is_bullish'].shift(1) == False)
        data['long_exit'] = (data['is_bullish'] == False) & (data['is_bullish'].shift(1) == True)
        
        return data
    
    def wilder_smoothing(self, series, period):
        """
        Apply Wilder's smoothing method (similar to Pine Script implementation).
        
        Args:
            series (pd.Series): Input series
            period (int): Smoothing period
            
        Returns:
            pd.Series: Smoothed series
        """
        smoothed = pd.Series(0.0, index=series.index)
        
        for i in range(len(series)):
            if i == 0 or pd.isna(smoothed.iloc[i-1]):
                smoothed.iloc[i] = series.iloc[i]
            else:
                # Wilder smoothing formula: prev - (prev / period) + current
                smoothed.iloc[i] = smoothed.iloc[i-1] - (smoothed.iloc[i-1] / period) + series.iloc[i]
        
        return smoothed
    
    def generate_signals(self, df):
        """
        Generate trading signals for the strategy.
        
        Args:
            df (pd.DataFrame): DataFrame with OHLC data
            
        Returns:
            pd.DataFrame: DataFrame with signals
        """
        return self.calculate_indicators(df)


def get_strategy_signals(df, adx_length=9, smoothing_factor=1):
    """
    Convenience function to get trading signals from OHLC data.
    
    Args:
        df (pd.DataFrame): DataFrame with OHLC data
        adx_length (int): ADX smoothing length
        smoothing_factor (int): OHLC SMA length
        
    Returns:
        pd.DataFrame: DataFrame with indicators and signals
    """
    strategy = MysticPulseV2Strategy(adx_length=adx_length, smoothing_factor=smoothing_factor)
    return strategy.generate_signals(df)

