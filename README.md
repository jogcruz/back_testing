# Stock Trading Strategy Backtester

A comprehensive backtesting tool for simulating a dollar-cost averaging strategy with automated profit targets on any stock ticker (default: TQQQ - ProShares UltraPro QQQ ETF).

## Strategy Overview

### Core Strategy
- **Initial Capital**: $20,000 (configurable)
- **Daily Investment**: $2,000 (configurable, default 10% of initial capital)
- **Entry Time**: 10:00 AM market time every trading day
- **Exit Strategy**: 10 automated sell orders at incremental profit targets
- **Stock Ticker**: Any ticker symbol (default: TQQQ)
- **Market Filter**: Any ticker for 50 DMA filter (default: QQQ)

### Execution Logic

1. **Daily Buy Order (Configurable Time - Default 10:00 AM)**:
   - ⏰ **Optimization Note**: Testing shows 2:00 PM (14:00) performs +0.73% better than 10:00 AM (see `BUY_TIME_ANALYSIS.md`)
   - **Check cash availability**: Only execute if portfolio has at least the daily investment amount in cash
   - **Check market conditions**: Only buy if market filter ticker closed above its 50-day moving average (50 DMA) on the previous trading day
   - If insufficient cash OR bearish market conditions, skip the buy for that day
   - If both conditions met, buy stock shares with the daily investment amount
   - Calculate shares purchased: `shares = int(daily_investment / current_price)` (**integer shares only**)
   - Minimum: 10 shares required (to create 10 sell orders)

2. **Automated Sell Orders** (Immediately after buy):
   - Create 10 sell orders with **integer shares** distributed as evenly as possible
   - Example: 21 shares → 9 orders of 2 shares + 1 order of 3 shares
   - Target prices: `buy_price + increment`, `buy_price + 2×increment`, ..., `buy_price + 10×increment`
   - Default increment: $1.00 (configurable: $0.25, $0.50, $1.00, $2.00, etc.)
   - Orders remain active until executed or portfolio is closed

3. **Order Execution & Cash Management**:
   - Sell orders execute when the high price of any 5-minute interval reaches the target
   - **Cash from sales is immediately added back to portfolio**
   - This replenished cash can be used for future buy orders
   - Remaining sell orders stay active

## Features

✅ **Any Stock Ticker**: Test strategy on TQQQ, SOXL, UPRO, or any other ticker  
✅ **Customizable Market Filter**: Use any ticker for 50 DMA trend filter (QQQ, SPY, SOX, etc.)  
✅ **Historical Data**: Uses 5-minute/1-hour/daily interval data from Yahoo Finance  
✅ **Realistic Simulation**: Accounts for market hours and trading days  
✅ **Integer Shares Only**: No fractional shares - matches real broker constraints  
✅ **50 DMA Trend Filter**: Only buys when filter ticker is above its 50-day moving average  
✅ **Flexible Capital**: Configure initial capital and daily investment amounts  
✅ **Cash Management**: Prevents buying when portfolio cash < daily investment  
✅ **Customizable Buy Time**: Test any time from 9:30 AM to 3:00 PM (optimal: 2:00 PM)  
✅ **Flexible Date Ranges**: Backtest any historical period (subject to data availability)  
✅ **Adjustable Profit Targets**: Configure sell order increments ($0.25 to $2.00+)  
✅ **Buy-and-Hold Comparison**: Compare strategy performance vs simple buy-and-hold  
✅ **Detailed Tracking**: Records every buy and sell transaction  
✅ **Monthly Performance**: Calculates returns for each month  
✅ **Trade Statistics**: Analyzes win rate and average profits  
✅ **CSV Export**: Exports complete trade history  

## Installation

### Prerequisites
- Python 3.8 or higher
- Virtual environment activated

### Install Dependencies

```bash
# From the project root
pip install -r requirements.txt
```

Or install the package in development mode:
```bash
pip install -e .
```

## Usage

### Option 1: Custom Buy Time (Recommended) ⭐

**Test the strategy with customizable parameters** - includes all optimizations and full customization:

```bash
# Basic: Just buy time (Jan 1, 2025 to today, $1 increment, TQQQ/QQQ)
python src/run_backtest_custom_time.py 14 0        # 2:00 PM - BEST PERFORMANCE
python src/run_backtest_custom_time.py 10 0        # 10:00 AM - Original
python src/run_backtest_custom_time.py 12 0        # Noon
python src/run_backtest_custom_time.py 11 30       # 11:30 AM

# With custom ticker and filter
python src/run_backtest_custom_time.py 14 0 --ticker SOXL --filter SOX         # SOXL at 2 PM
python src/run_backtest_custom_time.py 14 0 --ticker UPRO --filter SPY         # UPRO at 2 PM
python src/run_backtest_custom_time.py 10 0 --ticker TECL --filter QQQ         # TECL at 10 AM

# With custom price increment
python src/run_backtest_custom_time.py 14 0 0.5 --ticker SOXL --filter SOX     # $0.50 increment
python src/run_backtest_custom_time.py 14 0 2.0 --ticker TQQQ                  # $2.00 increment

# With custom date range
python src/run_backtest_custom_time.py 14 0 2024-01-01 2024-12-31 --ticker SOXL --filter SOX

# With custom date range AND price increment
python src/run_backtest_custom_time.py 14 0 2025-01-01 2025-10-05 0.5 --ticker SOXL --filter SOX

# Without market filter
python src/run_backtest_custom_time.py 10 0 --no-filter

# Complete example with all options
python src/run_backtest_custom_time.py 14 0 2025-01-01 2025-10-05 0.5 --ticker SOXL --filter SOX

# Get help
python src/run_backtest_custom_time.py --help
```

#### Parameters

**Positional Arguments:**

| Parameter | Required | Default | Description | Example |
|-----------|----------|---------|-------------|---------|
| `hour` | ✅ Yes | - | Buy time hour (9-15, Eastern) | `14` (2 PM) |
| `minute` | ✅ Yes | - | Buy time minute (0-59) | `0` or `30` |
| `start_date` | ❌ No | `2025-01-01` | Start date (YYYY-MM-DD) | `2024-01-01` |
| `end_date` | ❌ No | Today | End date (YYYY-MM-DD) | `2025-12-31` |
| `price_increment` | ❌ No | `1.0` | Sell order price increment ($) | `0.5`, `1.0`, `2.0` |

**Optional Flags:**

| Argument | Short | Default | Description |
|----------|-------|---------|-------------|
| `--ticker` | `-t` | `TQQQ` | Stock ticker to backtest |
| `--filter` | `-f` | `QQQ` | Filter ticker for 50 DMA |
| `--no-filter` | - | `False` | Disable 50 DMA filter |

**💡 Smart Parameter Detection**: When you pass 3 arguments, the script automatically detects if the 3rd argument is a number (price_increment) or a date (start_date). This allows you to skip the date parameters when you only want to change the price increment!

#### Price Increment Explanation

The price increment determines the spacing between sell orders:
- **$0.50**: Sell at `buy_price + $0.50`, `+$1.00`, ..., `+$5.00` (faster profit-taking)
- **$1.00**: Sell at `buy_price + $1.00`, `+$2.00`, ..., `+$10.00` (balanced - default)
- **$2.00**: Sell at `buy_price + $2.00`, `+$4.00`, ..., `+$20.00` (larger targets)

#### Popular Ticker Combinations

- **TQQQ** + **QQQ** (Nasdaq-100 3x leveraged)
- **SOXL** + **SOX** (Semiconductor 3x leveraged)
- **UPRO** + **SPY** (S&P 500 3x leveraged)
- **TECL** + **QQQ** (Technology 3x leveraged)

**Benefits**:
- ✅ Customize buy time, ticker, filter, date range, and profit targets
- ✅ Test any stock with appropriate market filter
- ✅ 50 DMA filter (enabled by default, can disable)
- ✅ Cash management (always active)
- ✅ Export trades to CSV with custom filename including ticker
- ✅ Easy to compare different configurations

**See Also**:
- `CUSTOM_TIME_USAGE.md` - Complete usage guide with examples
- `CUSTOM_DATE_RANGE_FEATURE.md` - Date range customization details
- `PRICE_INCREMENT_FEATURE.md` - Price increment strategy guide

### Option 2: Default Backtest with Command-Line Arguments

**Flexible backtesting with command-line arguments** - customize ticker, filter, dates, and capital:

```bash
# Basic usage (defaults: TQQQ with QQQ filter)
python src/tqqq_backtest.py

# Test different tickers
python src/tqqq_backtest.py --ticker SOXL                    # Backtest SOXL with QQQ filter
python src/tqqq_backtest.py --ticker UPRO                    # Backtest UPRO with QQQ filter
python src/tqqq_backtest.py --ticker TQQQ --filter SPY       # TQQQ with SPY filter

# Custom ticker with matching filter
python src/tqqq_backtest.py --ticker SOXL --filter SOX       # SOXL with SOX 50 DMA filter
python src/tqqq_backtest.py --ticker UPRO --filter SPY       # UPRO with SPY 50 DMA filter

# Disable market filter
python src/tqqq_backtest.py --ticker TQQQ --no-filter        # No 50 DMA filter

# Custom date range
python src/tqqq_backtest.py --start-date 2024-01-01 --end-date 2024-12-31

# Custom capital and investment amounts
python src/tqqq_backtest.py --capital 50000 --investment 5000

# Combine multiple options
python src/tqqq_backtest.py --ticker SOXL --filter SOX --capital 30000 --investment 3000 --start-date 2024-06-01
```

#### Command-Line Arguments

| Argument | Short | Default | Description |
|----------|-------|---------|-------------|
| `--ticker` | `-t` | `TQQQ` | Stock ticker to backtest |
| `--filter` | `-f` | `QQQ` | Ticker for 50 DMA market filter |
| `--no-filter` | - | `False` | Disable 50 DMA market filter |
| `--start-date` | - | `2025-01-01` | Start date (YYYY-MM-DD) |
| `--end-date` | - | Today | End date (YYYY-MM-DD) |
| `--capital` | - | `20000` | Initial capital ($) |
| `--investment` | - | `2000` | Daily investment amount ($) |

**Examples**:
```bash
# Help message with all options
python src/tqqq_backtest.py --help

# Short form arguments
python src/tqqq_backtest.py -t SOXL -f SOX

# Test different leveraged ETFs
python src/tqqq_backtest.py -t SOXL  # Semiconductor 3x
python src/tqqq_backtest.py -t UPRO  # S&P 500 3x
python src/tqqq_backtest.py -t TECL  # Technology 3x
```

**Benefits**:
- ✅ Test any stock ticker without modifying code
- ✅ Use appropriate market filter for each ticker
- ✅ Flexible capital and investment amounts
- ✅ Easy A/B testing of different strategies
- ✅ Automated CSV export with ticker name

### Option 3: With Visualizations

```bash
# Run backtest and generate charts
python src/visualize_backtest.py
```

This will:
- Run the complete backtest
- Generate a comprehensive analysis chart (`tqqq_backtest_analysis.png`)
- Display 6 different visualizations:
  1. Portfolio Value Over Time
  2. Monthly Returns (%)
  3. Trade Distribution
  4. Cumulative Realized Profit
  5. Current Portfolio Allocation (Cash vs Shares)
  6. Profit Distribution per Trade

### Custom Parameters

You can modify the script to test different parameters:

```python
# Edit tqqq_backtest.py main() function
backtester = TQQQBacktester(
    initial_capital=50000,  # Try $50,000 initial capital
    daily_investment=5000   # Invest $5,000 daily
)

# Custom date range
backtester.run_backtest(
    start_date="2024-01-01",
    end_date="2024-12-31"
)
```

## Output

### Console Output (run_backtest_custom_time.py)

```
ℹ️  Using 1-hour intervals (278 days)
📅 Period: 2025-01-01 to 2025-10-05
⏰ Buy Time: 14:00
💵 Price Increment: $1.00

================================================================================
🚀 TQQQ TRADING STRATEGY BACKTEST
================================================================================
Initial Capital: $20,000.00
Daily Investment: $2,000.00
Data Interval: 1h
QQQ 50 DMA Filter: ENABLED
Period: 2025-01-01 to 2025-10-05
================================================================================
```

**Trade Execution**:
```
✅ BUY  2025-01-02 14:00:00: 28.45 shares @ $70.31 = $2,000.00
   Created 10 sell orders: 2.85 shares each at $71.31 to $80.31
   Cash remaining: $18,000.00, Total shares: 28.45
💰 SELL 2025-01-03 14:15:00: 2.85 shares @ $71.31 = $203.23 (Profit: $2.85)
⚠️  SKIPPED - Market condition on 2025-01-13: QQQ below 50 DMA (bearish signal)
⚠️  SKIPPED - Insufficient cash on 2025-02-04: $1375.91 (need $2000.00)
```

**Monthly Performance Breakdown**:
```
📈 MONTHLY PERFORMANCE
Month           Start Value     End Value       Return          Return %  
2025-01         $   20,000.00 $   20,454.17 $      454.17     2.27%
2025-02         $   20,454.17 $   18,800.93 $   -1,653.24    -8.08%
2025-03         $   18,800.93 $   14,658.94 $   -4,141.99   -22.03%
2025-04         $   14,658.94 $   14,080.99 $     -577.95    -3.94%
2025-05         $   14,080.99 $   17,645.02 $    3,564.04    25.31%
2025-06         $   17,645.02 $   20,694.54 $    3,049.52    17.28%
2025-07         $   20,694.54 $   22,172.02 $    1,477.48     7.14%
2025-08         $   22,172.02 $   22,846.26 $      674.24     3.04%
2025-09         $   22,846.26 $   25,926.94 $    3,080.68    13.48%
2025-10         $   25,926.94 $   26,155.95 $      229.02     0.88%
```

**Final Results**:
```
📊 FINAL RESULTS
Total Return:           $6,155.95 (+30.78%)
Win Rate:               99.6%
Total Buy Trades:       58
Skipped Buys (no cash): 248
Skipped Buys (QQQ<50DMA): 6
Total Sell Trades:      493
```

### CSV Export

Trade history is automatically exported:
- `run_backtest_custom_time.py`: Creates `tqqq_trades_HH_MM.csv` (e.g., `tqqq_trades_14_00.csv`)
- `tqqq_backtest.py`: Creates `tqqq_trades.csv`

Example format:

| Date | Type | Shares | Price | Amount |
|------|------|--------|-------|--------|
| 2025-01-02 10:00:00 | BUY | 28.45 | 70.31 | 2000.00 |
| 2025-01-03 14:15:00 | SELL | 2.85 | 71.31 | 203.23 |

## Understanding the Results

### Key Metrics

- **Initial Capital**: Starting cash ($20,000)
- **Final Portfolio Value**: Cash + (shares × current price)
- **Total Return**: Final value - Initial capital
- **Return %**: (Total return / Initial capital) × 100
- **Pending Sell Orders**: Unfilled sell orders still active

### Performance Analysis

1. **Monthly Returns**: Shows how the strategy performed each month
2. **Win Rate**: Percentage of profitable sell trades
3. **Average Profit**: Average profit per sell transaction
4. **Trade Frequency**: Number of buy/sell transactions

### Interpreting Results

- **Positive Return**: Strategy outperformed holding cash
- **vs. Buy-and-Hold**: Compare to buying $20,000 of TQQQ on Jan 1
- **Consistency**: Look at monthly performance variance
- **Execution Rate**: Ratio of sell orders filled vs. created

## Data Considerations

### Market Hours
- Only trades during regular market hours (9:30 AM - 4:00 PM ET)
- Skips weekends and market holidays
- Uses 5-minute interval data

### Data Limitations
- Yahoo Finance data may have gaps or delays
- 5-minute data available for limited historical periods
- Recent data more reliable than older data

### Slippage & Fees
⚠️ **Important**: This backtest does NOT account for:
- Trading commissions and fees
- Bid-ask spreads
- Slippage on order execution
- Market impact on large orders
- Taxes on realized gains

Real-world returns will be lower than backtested results.

## Customization

### Test Different Buy Times, Periods, and Price Increments

Use `run_backtest_custom_time.py` to test various configurations:

**Format:** `python run_backtest_custom_time.py <hour> <minute> [start_date] [end_date] [price_increment]`

```bash
# Test different buy times (Jan 1, 2025 to today, $1 increment)
python src/run_backtest_custom_time.py 14 0   # 2:00 PM - Best (+30.78%)
python src/run_backtest_custom_time.py 12 0   # Noon - Second best
python src/run_backtest_custom_time.py 11 30  # 11:30 AM - Third best
python src/run_backtest_custom_time.py 10 0   # 10:00 AM - Original (+29.02%)

# Test different date ranges (with 2:00 PM buy time)
python src/run_backtest_custom_time.py 14 0 2024-01-01 2024-12-31   # Full year 2024
python src/run_backtest_custom_time.py 14 0 2025-06-01 2025-09-30   # Summer 2025
python src/run_backtest_custom_time.py 14 0 2025-01-01 2025-03-31   # Q1 2025

# Test different profit-taking strategies (Sept 15 - Oct 5, 2025)
python src/run_backtest_custom_time.py 14 0 2025-09-15 2025-10-05 0.5   # Fast: $0.50 increments
python src/run_backtest_custom_time.py 14 0 2025-09-15 2025-10-05 1.0   # Balanced: $1.00 increments
python src/run_backtest_custom_time.py 14 0 2025-09-15 2025-10-05 2.0   # Patient: $2.00 increments
```

**All tests automatically include**:
- ✅ QQQ 50 DMA filter (always enabled)
- ✅ Cash management (always enabled)
- ✅ Complete monthly breakdown
- ✅ Trade history export

**See also**:
- `BUY_TIME_ANALYSIS.md` - Why 2:00 PM is optimal
- `CUSTOM_TIME_USAGE.md` - Complete parameter guide
- `PRICE_INCREMENT_FEATURE.md` - Profit-taking strategy guide

### Enable/Disable QQQ Filter (Advanced)

To modify the QQQ filter, edit `run_backtest_custom_time.py` line 179:

```python
# With QQQ 50 DMA filter (default - recommended)
use_nasdaq_filter=True  # Only buy when QQQ > 50 DMA

# Without filter
use_nasdaq_filter=False  # Buy regardless of trend
```

See `STRATEGY_COMPARISON.md` for detailed comparison of results with/without the filter.

### Modify Strategy Parameters

Edit the `TQQQBacktester` class to customize:

```python
# Change sell order targets
def create_sell_orders(self, shares: float, buy_price: float, dt: datetime):
    shares_per_order = shares / 10
    
    # Example: Use percentage targets instead
    targets = [1.01, 1.02, 1.03, 1.05, 1.07, 1.10, 1.15, 1.20, 1.25, 1.30]
    for multiplier in targets:
        target_price = buy_price * multiplier
        # ... create order
```

### Test Different Tickers

```python
# In download_data method, change:
ticker = yf.Ticker("TQQQ")  # Change to "SPY", "QQQ", etc.
```

### Adjust Buy Timing

```python
# In should_buy method, change:
buy_window_start = time(10, 0)  # Change to different time
```

## Troubleshooting

### Common Issues

1. **"No data downloaded"**
   - Check internet connection
   - Verify date range is valid
   - Ensure TQQQ ticker is correct

2. **Import errors**
   - Install dependencies: `pip install -r requirements.txt`
   - Activate virtual environment

3. **Limited historical data**
   - Yahoo Finance limits 5-minute data to ~60 days
   - Use 1-hour or daily intervals for longer periods
   - Modify `interval` parameter in `download_data()`

4. **Performance issues**
   - Large date ranges with 5-minute data can be slow
   - Consider using larger intervals (15m, 1h, 1d)

## Advanced Features

### Export to Different Formats

```python
# Add to calculate_results method
import json

# Export portfolio snapshot
portfolio_snapshot = {
    'final_value': final_value,
    'total_return': total_return,
    'return_pct': return_pct,
    'monthly_performance': monthly_performance
}

with open('portfolio_snapshot.json', 'w') as f:
    json.dump(portfolio_snapshot, f, indent=2)
```

### Visualization

Add plotting capabilities:

```python
import matplotlib.pyplot as plt

def plot_performance(self):
    dates = sorted(self.portfolio.daily_values.keys())
    values = [self.portfolio.daily_values[d] for d in dates]
    
    plt.figure(figsize=(12, 6))
    plt.plot(dates, values)
    plt.title('Portfolio Value Over Time')
    plt.xlabel('Date')
    plt.ylabel('Portfolio Value ($)')
    plt.grid(True)
    plt.savefig('portfolio_performance.png')
```

## Disclaimer

⚠️ **This is for educational purposes only.**

- Past performance does not guarantee future results
- This backtest uses simplified assumptions
- Real trading involves risks, fees, and complexities not modeled
- Consult a financial advisor before making investment decisions
- The author is not responsible for trading losses

## Generated Files

**Trade History & Data**:
- `tqqq_trades_HH_MM.csv` - Trade history with buy time (from run_backtest_custom_time.py)
- `tqqq_trades.csv` - Trade history (from tqqq_backtest.py)
- `buy_time_optimization_results.csv` - All 13 tested buy times with results

**Visualizations**:
- `tqqq_backtest_analysis.png` - 6-panel strategy performance chart
- `buy_time_optimization_chart.png` - 4-panel buy time analysis

**Documentation**: See the complete list of `.md` files for comprehensive guides

## Future Enhancements

Potential improvements:
- [ ] Add stop-loss orders
- [ ] Implement trailing stop-loss
- [ ] Account for transaction costs
- [ ] Add position sizing based on volatility
- [ ] Support multiple tickers simultaneously
- [ ] Implement portfolio rebalancing
- [ ] Add technical indicators (RSI, MACD, etc.)
- [ ] Compare to buy-and-hold benchmark
- [ ] Monte Carlo simulation for risk analysis

## License

This backtesting tool is provided as-is for educational purposes.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the code comments
3. Verify your Python environment and dependencies

---

**Happy Backtesting! 📈**
