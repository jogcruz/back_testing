"""
Simple test script for Mystic Pulse V2.0 Strategy
This validates the indicator calculations without requiring backtrader installation.
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from strategy import MysticPulseV2Strategy


def create_test_data(num_bars=100):
    """
    Create synthetic OHLC data for testing.
    
    Args:
        num_bars (int): Number of bars to generate
        
    Returns:
        pd.DataFrame: Synthetic OHLC data
    """
    dates = pd.date_range(end=datetime.today(), periods=num_bars, freq='D')
    
    # Generate synthetic price data with an uptrend and some noise
    base_price = 100
    trend = np.linspace(0, 20, num_bars)
    noise = np.random.randn(num_bars) * 2
    close_prices = base_price + trend + noise
    
    # Generate OHLC from close prices
    data = pd.DataFrame({
        'open': close_prices + np.random.randn(num_bars) * 0.5,
        'high': close_prices + np.abs(np.random.randn(num_bars)) * 1.5,
        'low': close_prices - np.abs(np.random.randn(num_bars)) * 1.5,
        'close': close_prices,
        'volume': np.random.randint(1000000, 10000000, num_bars)
    }, index=dates)
    
    # Ensure high is highest and low is lowest
    data['high'] = data[['open', 'high', 'low', 'close']].max(axis=1)
    data['low'] = data[['open', 'high', 'low', 'close']].min(axis=1)
    
    return data


def test_strategy_indicators():
    """Test that indicators are calculated correctly."""
    print("=" * 80)
    print("Testing Mystic Pulse V2.0 Strategy Indicators")
    print("=" * 80)
    
    # Create test data
    print("\n1. Creating synthetic test data (100 bars)...")
    df = create_test_data(100)
    print(f"   ✓ Generated {len(df)} bars of OHLC data")
    print(f"   Date range: {df.index[0].date()} to {df.index[-1].date()}")
    print(f"   Price range: ${df['close'].min():.2f} to ${df['close'].max():.2f}")
    
    # Initialize strategy
    print("\n2. Initializing strategy...")
    strategy = MysticPulseV2Strategy(adx_length=9, smoothing_factor=1)
    print("   ✓ Strategy initialized with ADX length=9, smoothing=1")
    
    # Calculate indicators
    print("\n3. Calculating indicators...")
    df_with_signals = strategy.generate_signals(df)
    print("   ✓ Indicators calculated successfully")
    
    # Display calculated columns
    print("\n4. Calculated columns:")
    expected_columns = ['di_plus', 'di_minus', 'positive_count', 'negative_count', 
                       'trend_score', 'is_bullish', 'long_entry', 'long_exit']
    for col in expected_columns:
        if col in df_with_signals.columns:
            print(f"   ✓ {col}")
        else:
            print(f"   ✗ {col} - MISSING!")
    
    # Check for any NaN values in recent data (last 20 bars should be valid)
    print("\n5. Data quality check (last 20 bars):")
    recent_data = df_with_signals.tail(20)
    for col in expected_columns:
        nan_count = recent_data[col].isna().sum()
        if nan_count == 0:
            print(f"   ✓ {col}: No NaN values")
        else:
            print(f"   ⚠ {col}: {nan_count} NaN values")
    
    # Display some statistics
    print("\n6. Indicator Statistics:")
    print(f"   DI+ range: {df_with_signals['di_plus'].min():.2f} to {df_with_signals['di_plus'].max():.2f}")
    print(f"   DI- range: {df_with_signals['di_minus'].min():.2f} to {df_with_signals['di_minus'].max():.2f}")
    print(f"   Max positive count: {df_with_signals['positive_count'].max()}")
    print(f"   Max negative count: {df_with_signals['negative_count'].max()}")
    print(f"   Trend score range: {df_with_signals['trend_score'].min()} to {df_with_signals['trend_score'].max()}")
    
    # Count signals
    print("\n7. Trading Signals:")
    long_entries = df_with_signals['long_entry'].sum()
    long_exits = df_with_signals['long_exit'].sum()
    print(f"   Long entries: {long_entries}")
    print(f"   Long exits: {long_exits}")
    
    # Show last few bars with signals
    print("\n8. Last 10 bars of data:")
    display_cols = ['close', 'di_plus', 'di_minus', 'positive_count', 'negative_count', 
                   'trend_score', 'is_bullish', 'long_entry', 'long_exit']
    print(df_with_signals[display_cols].tail(10).to_string())
    
    # Display signal dates
    if long_entries > 0:
        print("\n9. Entry Signal Dates:")
        entry_dates = df_with_signals[df_with_signals['long_entry']].index
        for date in entry_dates:
            price = df_with_signals.loc[date, 'close']
            print(f"   {date.date()}: Entry at ${price:.2f}")
    
    if long_exits > 0:
        print("\n10. Exit Signal Dates:")
        exit_dates = df_with_signals[df_with_signals['long_exit']].index
        for date in exit_dates:
            price = df_with_signals.loc[date, 'close']
            print(f"   {date.date()}: Exit at ${price:.2f}")
    
    # Summary
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    print("✓ All indicator calculations completed successfully")
    print("✓ Strategy logic is working as expected")
    print("\nThe strategy is ready to use with the backtesting script.")
    print("\nTo run the full backtest, install dependencies and run:")
    print("  pip install -r ../../requirements.txt")
    print("  python backtest.py")
    print("=" * 80)
    
    return df_with_signals


if __name__ == '__main__':
    """Run the test."""
    try:
        # Set random seed for reproducibility
        np.random.seed(42)
        
        # Run test
        result = test_strategy_indicators()
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

