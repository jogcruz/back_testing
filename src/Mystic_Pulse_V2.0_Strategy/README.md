# Mystic Pulse V2.0 Strategy

Python implementation of the Mystic Pulse V2.0 indicator and trading strategy, originally developed in Pine Script by chervolino.

## Overview

The Mystic Pulse V2.0 strategy is a trend-following system that uses directional movement indicators with Wilder smoothing to identify bullish and bearish market conditions. It tracks positive and negative momentum counts to generate trading signals.

## Strategy Logic

### Indicator Calculations

1. **OHLC Smoothing**: Applies Simple Moving Average (SMA) to OHLC data
2. **True Range (TR)**: Calculated as the maximum of:
   - High - Low
   - |High - Previous Close|
   - |Low - Previous Close|
3. **Directional Movement**:
   - **DM+**: Positive directional movement (upward price moves)
   - **DM-**: Negative directional movement (downward price moves)
4. **Wilder Smoothing**: Applied to TR, DM+, and DM- using exponential decay
5. **Directional Indicators**:
   - **DI+**: (Smoothed DM+ / Smoothed TR) × 100
   - **DI-**: (Smoothed DM- / Smoothed TR) × 100

### Trend Counting Logic

- **Positive Count**: Increments when DI+ is rising and DI+ > DI-
- **Negative Count**: Increments when DI- is rising and DI- > DI+
- When one count increases, the other resets to zero

### Trading Signals (Long Only)

- **Entry**: When trend changes from bearish to bullish
  - Condition: `positive_count >= negative_count` (after being bearish)
- **Exit**: When trend changes from bullish to bearish
  - Condition: `negative_count > positive_count` (after being bullish)

## Files

- `strategy.py`: Core strategy implementation with indicator calculations
- `backtest.py`: Backtesting script using backtrader framework
- `Indicator.ps`: Original Pine Script indicator code

## Installation

1. Install required dependencies:

```bash
pip install -r requirements.txt
```

Required packages:
- `pandas>=2.2.0`
- `numpy>=1.26.0`
- `yfinance>=0.2.32`
- `backtrader>=1.9.78.123`
- `matplotlib>=3.7.0`

## Usage

### Running the Backtest

To run the backtest with default parameters (TQQQ from 2020-01-01 to today):

```bash
cd src/Mystic_Pulse_V2.0_Strategy
python backtest.py
```

### Customizing Parameters

Edit the parameters in `backtest.py`:

```python
# Default parameters
TICKER = 'TQQQ'  # Or 'SOXL', 'SPY', etc.
START_DATE = '2020-01-01'
INITIAL_CASH = 10000.0
COMMISSION = 0.01  # 1%
SLIPPAGE = 0.0001  # 0.01% (approximation for 1 tick)
```

### Strategy Parameters

The strategy accepts the following parameters:

- `adx_length` (default: 9): Length for Wilder smoothing
- `smoothing_factor` (default: 1): SMA length for OHLC pre-smoothing

These can be adjusted in the `MysticPulseV2StrategyBT` class initialization.

## Backtest Configuration

The backtest is configured with the following specifications:

- **Period**: 2020-01-01 to Today
- **Timeframe**: 1D (daily bars)
- **Position Sizing**: 100% of available equity per trade
- **Commission**: 1% per trade
- **Slippage**: 1 tick (approximated as 0.01%)
- **Strategy Type**: Long only (no short positions)

## Performance Metrics

The backtest provides the following performance metrics:

- **Total Return**: Overall percentage return
- **Sharpe Ratio**: Risk-adjusted return metric
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Total Trades**: Number of completed trades
- **Win Rate**: Percentage of winning trades
- **Average Win/Loss**: Average profit per winning/losing trade

## Example Output

```
================================================================================
Backtesting Mystic Pulse V2.0 Strategy
================================================================================
Ticker: TQQQ
Period: 2020-01-01 to 2024-12-01
Initial Capital: $10,000.00
Commission: 1.00%
Slippage: 0.0100%
================================================================================

Downloading data for TQQQ...
Data downloaded: 1234 bars from 2020-01-02 to 2024-11-29

Starting Portfolio Value: $10,000.00

2020-03-15, BUY CREATE, Price: 25.50, Size: 392
2020-03-16, BUY EXECUTED, Price: 25.50, Cost: 9996.00, Comm: 99.96
...

Final Portfolio Value: $15,234.56

================================================================================
PERFORMANCE METRICS
================================================================================
Total Return: 52.35%
Sharpe Ratio: 0.875
Max Drawdown: 28.45%
Total Trades: 45
Winning Trades: 28
Losing Trades: 17
Win Rate: 62.22%
Average Win: $456.78
Average Loss: $234.56
================================================================================
```

## Strategy Testing on Different Tickers

The strategy can be tested on any ticker available through Yahoo Finance:

```python
# Leveraged ETFs
run_backtest(ticker='TQQQ')  # 3x Nasdaq
run_backtest(ticker='SOXL')  # 3x Semiconductors
run_backtest(ticker='UPRO')  # 3x S&P 500

# Regular ETFs
run_backtest(ticker='QQQ')   # Nasdaq
run_backtest(ticker='SPY')   # S&P 500

# Individual Stocks
run_backtest(ticker='AAPL')  # Apple
run_backtest(ticker='TSLA')  # Tesla
```

## Code Structure

### strategy.py

The `MysticPulseV2Strategy` class implements the core indicator logic:

- `calculate_indicators()`: Calculates all indicators and signals
- `smooth_ohlc()`: Applies SMA smoothing to OHLC data
- `wilder_smoothing()`: Implements Wilder's smoothing method
- `generate_signals()`: Generates entry/exit signals

### backtest.py

The `MysticPulseV2StrategyBT` class integrates with backtrader:

- `__init__()`: Initializes strategy and indicators
- `next()`: Executes strategy logic for each bar
- `notify_order()`: Handles order execution notifications
- `notify_trade()`: Handles trade completion notifications

The `run_backtest()` function orchestrates the backtest execution.

## Notes

1. **Long Only**: This strategy only takes long positions (no short selling)
2. **Full Position Sizing**: Each trade uses 100% of available cash
3. **No Stop Loss**: The original indicator does not include stop loss logic
4. **Trend Following**: Works best in trending markets
5. **Whipsaw Risk**: May generate false signals in choppy/sideways markets

## Original Pine Script

The original Pine Script indicator is included in `Indicator.ps` and is subject to the Mozilla Public License 2.0.

© chervolino

## License

This Python implementation follows the same Mozilla Public License 2.0 as the original Pine Script code.

## Disclaimer

This strategy is for educational and research purposes only. Past performance does not guarantee future results. Always do your own research and consult with a financial advisor before trading.

