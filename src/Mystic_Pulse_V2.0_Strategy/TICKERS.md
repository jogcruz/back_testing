# Cryptocurrency and Asset Ticker Reference

## Quick Reference for Yahoo Finance Tickers

### 🪙 Major Cryptocurrencies (vs USD)

| Ticker | Name | Notes |
|--------|------|-------|
| `BTC-USD` | Bitcoin | The original cryptocurrency |
| `ETH-USD` | Ethereum | Smart contract platform |
| `BNB-USD` | Binance Coin | Binance exchange token |
| `SOL-USD` | Solana | High-speed blockchain |
| `XRP-USD` | Ripple | Payment protocol |
| `ADA-USD` | Cardano | Research-driven blockchain |
| `DOGE-USD` | Dogecoin | Meme coin |
| `AVAX-USD` | Avalanche | DeFi platform |
| `MATIC-USD` | Polygon | Ethereum scaling |
| `DOT-USD` | Polkadot | Multi-chain protocol |
| `LINK-USD` | Chainlink | Oracle network |
| `UNI-USD` | Uniswap | DEX protocol |
| `LTC-USD` | Litecoin | Bitcoin fork |
| `ATOM-USD` | Cosmos | Internet of blockchains |
| `ALGO-USD` | Algorand | Pure proof-of-stake |

### 💱 Crypto Trading Pairs

| Ticker | Description |
|--------|-------------|
| `ETH-BTC` | Ethereum vs Bitcoin |
| `BNB-BTC` | Binance Coin vs Bitcoin |
| `SOL-BTC` | Solana vs Bitcoin |
| `ADA-BTC` | Cardano vs Bitcoin |

### 📈 Leveraged ETFs

| Ticker | Name | Leverage |
|--------|------|----------|
| `TQQQ` | ProShares UltraPro QQQ | 3x Nasdaq |
| `SOXL` | Direxion Daily Semiconductor Bull | 3x Semiconductors |
| `UPRO` | ProShares UltraPro S&P500 | 3x S&P 500 |
| `SPXL` | Direxion Daily S&P 500 Bull | 3x S&P 500 |
| `TECL` | Direxion Daily Technology Bull | 3x Technology |
| `WEBL` | Direxion Daily Dow Jones Internet Bull | 3x Internet |

### 📊 Major Indices

| Ticker | Name |
|--------|------|
| `SPY` | S&P 500 ETF |
| `QQQ` | Nasdaq 100 ETF |
| `DIA` | Dow Jones ETF |
| `IWM` | Russell 2000 ETF |
| `VTI` | Total Stock Market ETF |

### 🏢 Popular Stocks

| Ticker | Name |
|--------|------|
| `AAPL` | Apple |
| `MSFT` | Microsoft |
| `GOOGL` | Alphabet (Google) |
| `AMZN` | Amazon |
| `NVDA` | NVIDIA |
| `TSLA` | Tesla |
| `META` | Meta (Facebook) |

## Usage Examples

### Command Line

```bash
# Bitcoin
python backtest.py --ticker BTC-USD

# Ethereum
python backtest.py --ticker ETH-USD

# Ethereum vs Bitcoin pair
python backtest.py --ticker ETH-BTC

# Custom date range for crypto
python backtest.py --ticker BTC-USD --start 2017-01-01

# Lower commission for crypto (typical exchange fees)
python backtest.py --ticker BTC-USD --commission 0.001

# Solana with custom parameters
python backtest.py --ticker SOL-USD --start 2021-01-01 --cash 5000
```

### Interactive Menu

```bash
python run.py
# Then select option 5 for BTC-USD, 6 for ETH-USD, or 7 for SOL-USD
```

### List All Available Crypto Tickers

```bash
python backtest.py --list-crypto
```

## Important Notes

### Cryptocurrency Trading

1. **24/7 Markets**: Crypto trades 24/7, unlike stocks
2. **Higher Volatility**: Crypto is much more volatile than traditional assets
3. **Data Availability**:
   - Bitcoin (BTC-USD): ~2014 onwards
   - Ethereum (ETH-USD): ~2017 onwards
   - Most altcoins: 2017-2021 onwards
4. **Commission Rates**: 
   - Typical crypto exchange: 0.1% - 0.5% (use `--commission 0.001` to `0.005`)
   - Traditional brokers: 1% (default in script)

### Trading Pairs

- **vs USD**: Most common, shows value in US dollars
- **vs BTC**: Shows value relative to Bitcoin
- **vs ETH**: Shows value relative to Ethereum

When using BTC or ETH pairs, you're trading the relative performance between two cryptocurrencies.

### Backtesting Tips

1. **Start with Bitcoin/Ethereum**: Most reliable data
2. **Check data availability**: Use recent start dates for newer coins
3. **Adjust commission rates**: Crypto exchanges typically charge less than 1%
4. **Account for volatility**: Crypto can have extreme drawdowns
5. **Test different timeframes**: Crypto markets behave differently

## Commission Guidelines

| Asset Class | Typical Commission | Backtest Flag |
|-------------|-------------------|---------------|
| Stocks | 0% - 0.1% | `--commission 0.0` to `0.001` |
| Leveraged ETFs | 0% - 0.1% | `--commission 0.001` |
| Crypto (Major exchanges) | 0.1% - 0.5% | `--commission 0.001` to `0.005` |
| Crypto (High frequency) | 0.02% - 0.1% | `--commission 0.0002` to `0.001` |

## Example Workflows

### Test Bitcoin Strategy
```bash
# Full history with typical exchange fees
python backtest.py --ticker BTC-USD --start 2017-01-01 --commission 0.002

# Recent period with lower fees
python backtest.py --ticker BTC-USD --start 2022-01-01 --commission 0.001
```

### Compare ETH vs BTC
```bash
# Ethereum price action
python backtest.py --ticker ETH-USD --start 2018-01-01 --commission 0.002

# Ethereum vs Bitcoin pair
python backtest.py --ticker ETH-BTC --start 2018-01-01 --commission 0.002
```

### Test Leveraged ETFs
```bash
# TQQQ with default settings
python backtest.py --ticker TQQQ

# SOXL with higher capital
python backtest.py --ticker SOXL --cash 25000 --commission 0.001
```

## Data Sources

All data is pulled from **Yahoo Finance** using the `yfinance` library. Yahoo Finance provides:
- Historical OHLCV data
- Daily timeframe (1D bars)
- Adjusted prices for splits and dividends (stocks)
- Real-time and historical crypto data

## Troubleshooting

### "No data found" Error
- Check the ticker symbol is correct
- Verify the start date (coin might not have data that far back)
- Try a more recent start date

### Unrealistic Results
- Check commission rates are realistic for your asset class
- Verify slippage settings
- Remember: Past performance doesn't guarantee future results

### Missing Data
- Some altcoins have gaps in historical data
- Use major cryptocurrencies (BTC, ETH) for most reliable backtests
- Check Yahoo Finance website to verify data availability

## Getting Started

1. **List available tickers:**
   ```bash
   python backtest.py --list-crypto
   ```

2. **Test with Bitcoin:**
   ```bash
   python backtest.py --ticker BTC-USD
   ```

3. **Try the interactive menu:**
   ```bash
   python run.py
   ```

4. **Customize parameters:**
   ```bash
   python backtest.py --ticker ETH-USD --start 2020-01-01 --cash 5000 --commission 0.0025
   ```

---

**Note**: Always verify ticker symbols on [Yahoo Finance](https://finance.yahoo.com/) before backtesting.

