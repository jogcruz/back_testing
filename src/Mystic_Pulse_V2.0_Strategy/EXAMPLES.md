# Quick Usage Examples

## Running Backtests with Different Tickers

### Method 1: Command Line Arguments (Recommended)

The `backtest.py` script now accepts command-line arguments for easy ticker selection:

```bash
cd src/Mystic_Pulse_V2.0_Strategy
```

#### Leveraged ETFs
```bash
python backtest.py --ticker TQQQ
python backtest.py --ticker SOXL
python backtest.py --ticker UPRO
```

#### Cryptocurrencies
```bash
# Bitcoin
python backtest.py --ticker BTC-USD

# Ethereum
python backtest.py --ticker ETH-USD

# Solana
python backtest.py --ticker SOL-USD

# Ethereum vs Bitcoin pair
python backtest.py --ticker ETH-BTC
```

#### Stocks
```bash
python backtest.py --ticker AAPL
python backtest.py --ticker TSLA
python backtest.py --ticker NVDA
```

#### With Custom Parameters
```bash
# Bitcoin with custom date range and lower commission
python backtest.py --ticker BTC-USD --start 2018-01-01 --commission 0.002

# Ethereum with higher capital
python backtest.py --ticker ETH-USD --cash 25000 --commission 0.0025

# TQQQ with custom parameters
python backtest.py --ticker TQQQ --start 2022-01-01 --cash 50000 --commission 0.001
```

### Method 2: Interactive Menu

Use the interactive menu for easy selection:

```bash
python run.py
```

Then select from the menu:
1. TQQQ (3x Nasdaq)
2. SOXL (3x Semiconductors)
3. QQQ (Nasdaq)
4. SPY (S&P 500)
5. BTC-USD (Bitcoin)
6. ETH-USD (Ethereum)
7. SOL-USD (Solana)
8. Custom ticker

### Method 3: Help and Documentation

```bash
# View all available options
python backtest.py --help

# List popular cryptocurrency tickers
python backtest.py --list-crypto
```

## Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--ticker` | `-t` | Ticker symbol | TQQQ |
| `--start` | `-s` | Start date (YYYY-MM-DD) | 2020-01-01 |
| `--end` | `-e` | End date (YYYY-MM-DD) | Today |
| `--cash` | `-c` | Initial capital | 10000.0 |
| `--commission` | | Commission rate | 0.01 (1%) |
| `--slippage` | | Slippage percentage | 0.0001 |
| `--adx-length` | | ADX smoothing length | 9 |
| `--smoothing` | | OHLC SMA smoothing | 1 |
| `--list-crypto` | | List crypto tickers | - |

## Real-World Examples

### 1. Test Bitcoin Long-Term Performance
```bash
python backtest.py \
  --ticker BTC-USD \
  --start 2017-01-01 \
  --cash 10000 \
  --commission 0.002
```

Expected output:
- Full Bitcoin bull/bear cycle analysis
- Lower commission for crypto exchange fees (0.2%)
- Starting from when Bitcoin gained mainstream attention

### 2. Test Ethereum vs Bitcoin Pair
```bash
python backtest.py \
  --ticker ETH-BTC \
  --start 2018-01-01 \
  --cash 1 \
  --commission 0.001
```

This tests whether Ethereum outperforms Bitcoin when denominated in BTC.

### 3. Recent TQQQ Performance
```bash
python backtest.py \
  --ticker TQQQ \
  --start 2023-01-01 \
  --cash 25000 \
  --commission 0.0005
```

Tests performance on recent market conditions with realistic low commission.

### 4. Compare Multiple Tickers

Create a simple batch script:

**test_multiple.sh:**
```bash
#!/bin/bash
echo "Testing multiple tickers..."

python backtest.py --ticker BTC-USD --commission 0.002
python backtest.py --ticker ETH-USD --commission 0.002
python backtest.py --ticker TQQQ --commission 0.001
python backtest.py --ticker SOXL --commission 0.001
```

Run with:
```bash
chmod +x test_multiple.sh
./test_multiple.sh
```

### 5. Test with Realistic Crypto Fees

Different exchanges have different fee structures:

```bash
# Coinbase Pro / Advanced (0.5%)
python backtest.py --ticker BTC-USD --commission 0.005

# Binance (0.1% with BNB discount)
python backtest.py --ticker ETH-USD --commission 0.001

# Kraken (0.25%)
python backtest.py --ticker SOL-USD --commission 0.0025
```

## Output Interpretation

When you run a backtest, you'll see:

```
================================================================================
Backtesting Mystic Pulse V2.0 Strategy
================================================================================
Ticker: BTC-USD
Period: 2020-01-01 to 2024-12-01
Initial Capital: $10,000.00
Commission: 0.20%
Slippage: 0.0100%
================================================================================

Downloading data for BTC-USD...
Data downloaded: 1795 bars from 2020-01-01 to 2024-11-30

Starting Portfolio Value: $10,000.00

2020-03-15, BUY CREATE, Price: 5234.56
2020-03-16, BUY EXECUTED, Price: 5234.56, Cost: 9990.00, Comm: 19.98
...

Final Portfolio Value: $45,678.90

================================================================================
PERFORMANCE METRICS
================================================================================
Total Return: 356.79%
Sharpe Ratio: 1.234
Max Drawdown: 45.67%
Total Trades: 23
Winning Trades: 15
Losing Trades: 8
Win Rate: 65.22%
Average Win: $3,456.78
Average Loss: $-1,234.56
================================================================================
```

## Tips for Different Asset Classes

### For Cryptocurrencies:
- Use `--commission 0.001` to `0.005` (0.1% to 0.5%)
- Expect higher volatility and drawdowns
- Bitcoin data reliable from 2014+, Ethereum from 2017+
- Consider 24/7 market hours (no gaps)

### For Leveraged ETFs:
- Use `--commission 0.0` to `0.001` (most brokers free to 0.1%)
- Be aware of decay in sideways markets
- Higher volatility than underlying index
- Consider tracking error and expense ratios

### For Regular Stocks/ETFs:
- Use `--commission 0.0` (most brokers commission-free)
- More stable than crypto or leveraged products
- Longer reliable history available
- Consider dividends (automatically adjusted in data)

## Troubleshooting

### No data found
```bash
# Try different date range
python backtest.py --ticker SOL-USD --start 2021-01-01
```

### Unrealistic results
```bash
# Add realistic commission
python backtest.py --ticker BTC-USD --commission 0.002 --slippage 0.0005
```

### Want to see what's available
```bash
# List crypto tickers
python backtest.py --list-crypto

# Check Yahoo Finance for other tickers
# https://finance.yahoo.com/
```

## Next Steps

1. **Start simple**: Test with default parameters
   ```bash
   python backtest.py --ticker BTC-USD
   ```

2. **Adjust for realism**: Add appropriate commission rates
   ```bash
   python backtest.py --ticker BTC-USD --commission 0.002
   ```

3. **Test multiple assets**: Compare different tickers
4. **Optimize parameters**: Adjust ADX length and smoothing
5. **Analyze results**: Review win rate, drawdown, and returns

## Getting Help

```bash
# See all options
python backtest.py --help

# List crypto tickers
python backtest.py --list-crypto

# Use interactive mode
python run.py
```

---

**Remember**: This is for educational purposes. Past performance doesn't guarantee future results. Always test thoroughly before any real trading!

