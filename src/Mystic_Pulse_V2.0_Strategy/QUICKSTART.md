# 🚀 Mystic Pulse V2.0 - Multi-Asset Backtesting Guide

You can now backtest the Mystic Pulse V2.0 strategy on **any ticker** available on Yahoo Finance, including:
- 📈 **Stocks** (AAPL, TSLA, etc.)
- 💹 **ETFs** (SPY, QQQ, etc.)  
- ⚡ **Leveraged ETFs** (TQQQ, SOXL, etc.)
- 🪙 **Cryptocurrencies** (BTC-USD, ETH-USD, etc.)
- 💱 **Crypto pairs** (ETH-BTC, etc.)

## 🎯 Quick Start

### 1️⃣ Simple Command Line Usage

```bash
cd src/Mystic_Pulse_V2.0_Strategy

# Test Bitcoin
python backtest.py --ticker BTC-USD

# Test Ethereum  
python backtest.py --ticker ETH-USD

# Test TQQQ (default)
python backtest.py --ticker TQQQ

# Test any ticker
python backtest.py --ticker YOUR_TICKER
```

### 2️⃣ Interactive Menu

```bash
python run.py
```

Select from pre-configured options:
- TQQQ, SOXL (Leveraged ETFs)
- QQQ, SPY (Major Indices)
- BTC-USD, ETH-USD, SOL-USD (Cryptocurrencies)
- Or enter any custom ticker

### 3️⃣ Advanced Options

```bash
# Custom parameters
python backtest.py \
  --ticker BTC-USD \
  --start 2018-01-01 \
  --cash 25000 \
  --commission 0.002

# View all options
python backtest.py --help

# List crypto tickers
python backtest.py --list-crypto
```

## 🪙 Cryptocurrency Examples

### Bitcoin
```bash
# Full history with realistic fees (0.2%)
python backtest.py --ticker BTC-USD --commission 0.002

# Recent period
python backtest.py --ticker BTC-USD --start 2022-01-01
```

### Ethereum
```bash
python backtest.py --ticker ETH-USD --commission 0.002
```

### Ethereum vs Bitcoin (Trading Pair)
```bash
# Test if ETH outperforms BTC
python backtest.py --ticker ETH-BTC --commission 0.002
```

### Other Popular Cryptos
```bash
python backtest.py --ticker SOL-USD    # Solana
python backtest.py --ticker BNB-USD    # Binance Coin
python backtest.py --ticker ADA-USD    # Cardano
python backtest.py --ticker DOGE-USD   # Dogecoin
python backtest.py --ticker AVAX-USD   # Avalanche
```

## 📊 All Available Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--ticker` | `-t` | Ticker symbol | `BTC-USD`, `ETH-USD`, `TQQQ` |
| `--start` | `-s` | Start date | `2020-01-01` |
| `--end` | `-e` | End date | `2024-12-31` |
| `--cash` | `-c` | Initial capital | `10000` |
| `--commission` | | Fee per trade | `0.002` (0.2%) |
| `--slippage` | | Slippage % | `0.0001` |
| `--adx-length` | | ADX smoothing | `9` |
| `--smoothing` | | OHLC smoothing | `1` |

## 🎓 Real-World Examples

### Example 1: Bitcoin Long-Term Test
```bash
python backtest.py \
  --ticker BTC-USD \
  --start 2017-01-01 \
  --cash 10000 \
  --commission 0.002
```

### Example 2: Ethereum with Higher Capital
```bash
python backtest.py \
  --ticker ETH-USD \
  --start 2018-01-01 \
  --cash 50000 \
  --commission 0.0025
```

### Example 3: Compare ETH vs BTC Performance
```bash
python backtest.py \
  --ticker ETH-BTC \
  --start 2019-01-01 \
  --commission 0.001
```

### Example 4: Recent TQQQ Performance
```bash
python backtest.py \
  --ticker TQQQ \
  --start 2023-01-01 \
  --commission 0.0005
```

## 📋 Popular Ticker Symbols

### Cryptocurrencies (vs USD)
- `BTC-USD` - Bitcoin
- `ETH-USD` - Ethereum  
- `SOL-USD` - Solana
- `BNB-USD` - Binance Coin
- `ADA-USD` - Cardano
- `XRP-USD` - Ripple
- `DOGE-USD` - Dogecoin
- `AVAX-USD` - Avalanche
- `MATIC-USD` - Polygon
- `DOT-USD` - Polkadot

### Crypto Pairs
- `ETH-BTC` - Ethereum vs Bitcoin
- `SOL-BTC` - Solana vs Bitcoin
- `BNB-BTC` - Binance Coin vs Bitcoin

### Leveraged ETFs
- `TQQQ` - 3x Nasdaq
- `SOXL` - 3x Semiconductors
- `UPRO` - 3x S&P 500
- `TECL` - 3x Technology

### Major Indices
- `SPY` - S&P 500
- `QQQ` - Nasdaq 100
- `DIA` - Dow Jones
- `IWM` - Russell 2000

### Stocks
- `AAPL` - Apple
- `MSFT` - Microsoft
- `NVDA` - NVIDIA
- `TSLA` - Tesla
- `GOOGL` - Alphabet
- `AMZN` - Amazon

## 💰 Recommended Commission Rates

| Asset Type | Typical Fee | Backtest Flag |
|------------|-------------|---------------|
| Stocks | 0% - 0.1% | `--commission 0.0` |
| ETFs | 0% - 0.1% | `--commission 0.001` |
| Crypto (Major) | 0.1% - 0.3% | `--commission 0.001` to `0.003` |
| Crypto (Standard) | 0.2% - 0.5% | `--commission 0.002` to `0.005` |

## 📈 Sample Output

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

Starting Portfolio Value: $10,000.00

2020-03-15, BUY CREATE, Price: 5234.56
...

Final Portfolio Value: $45,678.90

================================================================================
PERFORMANCE METRICS
================================================================================
Total Return: 356.79%
Sharpe Ratio: 1.234
Max Drawdown: 45.67%
Total Trades: 23
Win Rate: 65.22%
================================================================================
```

## 📚 Documentation Files

- **EXAMPLES.md** - Detailed usage examples
- **TICKERS.md** - Complete ticker reference guide
- **INSTALL.md** - Installation instructions
- **README.md** - Full strategy documentation
- **SUMMARY.md** - Implementation summary

## 🔍 Getting Help

```bash
# View all command options
python backtest.py --help

# List popular crypto tickers
python backtest.py --list-crypto

# Use interactive menu
python run.py
```

## ⚠️ Important Notes

1. **Data Availability**: 
   - Bitcoin: 2014+ 
   - Ethereum: 2017+
   - Most altcoins: 2017-2021+

2. **Commission Matters**: Use realistic fees for accurate results

3. **Crypto is 24/7**: Unlike stocks, crypto markets never close

4. **Higher Volatility**: Crypto can have extreme price swings

5. **Educational Use**: Always test thoroughly before real trading

## 🎯 Next Steps

1. **Install dependencies** (see INSTALL.md)
2. **Test with default settings**:
   ```bash
   python backtest.py --ticker BTC-USD
   ```
3. **Try different tickers** and compare results
4. **Adjust commission rates** to match your exchange
5. **Analyze the metrics** to understand strategy performance

## 🤝 Need More Help?

- Check **EXAMPLES.md** for detailed usage patterns
- See **TICKERS.md** for complete ticker list
- Review **INSTALL.md** if you have setup issues
- Run `python backtest.py --help` for all options

---

**Happy backtesting! 🚀**

*Remember: This is for educational purposes only. Past performance doesn't guarantee future results.*

