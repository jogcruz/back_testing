# Troubleshooting Guide

## Common Issues and Solutions

### 1. AttributeError: 'tuple' object has no attribute 'lower'

**Error:**
```
AttributeError: 'tuple' object has no attribute 'lower'
```

**Cause:** Newer versions of `yfinance` return MultiIndex columns.

**Solution:** ✅ **FIXED** - The code now handles both old and new yfinance formats automatically.

**What was changed:**
```python
# Old code (would fail with new yfinance)
df.columns = [col.lower() for col in df.columns]

# New code (handles both formats)
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)
df.columns = [col.lower() if isinstance(col, str) else col for col in df.columns]
```

### 2. FutureWarning: auto_adjust default changed

**Warning:**
```
FutureWarning: YF.download() has changed argument auto_adjust default to True
```

**Impact:** This is just a warning, not an error. Your backtest will still run correctly.

**To suppress:** You can ignore this warning, or update to explicitly set `auto_adjust`:
```python
df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)
```

### 3. ModuleNotFoundError: No module named 'backtrader'

**Error:**
```
ModuleNotFoundError: No module named 'backtrader'
```

**Solution:**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux

# Install dependencies
pip install -r ../../requirements.txt
```

### 4. No data found for ticker

**Error:**
```
Error: No data found for TICKER-NAME
```

**Possible causes:**
1. Ticker symbol is incorrect
2. Start date is too early for that asset
3. Ticker format is wrong

**Solutions:**
- Verify ticker on [Yahoo Finance](https://finance.yahoo.com/)
- For crypto, use format: `BTC-USD`, `ETH-USD` (with hyphen and USD)
- Try a more recent start date: `--start 2020-01-01`
- Check if the asset was trading during your date range

**Examples:**
```bash
# ✅ Correct
python backtest.py --ticker BTC-USD
python backtest.py --ticker ETH-USD
python backtest.py --ticker TQQQ

# ❌ Incorrect
python backtest.py --ticker BTCUSD    # Missing hyphen
python backtest.py --ticker BTC       # Missing -USD
python backtest.py --ticker eth-usd   # Use uppercase
```

### 5. KeyError: 'open' / 'close' / etc.

**Error:**
```
KeyError: 'open'
```

**Cause:** Downloaded data doesn't have expected columns.

**Solution:** Check if ticker is valid and has OHLC data:
```bash
# Test with a known-good ticker first
python backtest.py --ticker BTC-USD
```

### 6. ImportError: cannot import name 'MysticPulseV2Strategy'

**Error:**
```
ImportError: cannot import name 'MysticPulseV2Strategy' from 'strategy'
```

**Solution:** Make sure you're in the correct directory:
```bash
cd /Users/jorge.gomez/Documents/personales/back_testing/src/Mystic_Pulse_V2.0_Strategy
python backtest.py --ticker BTC-USD
```

### 7. Empty DataFrame / No trades executed

**Issue:** Backtest runs but shows no trades.

**Possible causes:**
1. Not enough data (need at least ~30 bars)
2. Strategy conditions never met
3. Start date too recent

**Solutions:**
```bash
# Use longer date range
python backtest.py --ticker BTC-USD --start 2020-01-01

# Check if data was downloaded
# Should show: "Data downloaded: XXX bars from ..."
```

### 8. Unrealistic returns

**Issue:** Strategy shows unrealistic profits or losses.

**Causes:**
1. Commission too low or zero
2. Slippage not realistic
3. Leveraged ETF decay not considered
4. Small sample size

**Solutions:**
```bash
# Add realistic commission
python backtest.py --ticker BTC-USD --commission 0.002  # 0.2%

# Test over longer period
python backtest.py --ticker BTC-USD --start 2018-01-01

# Use appropriate commission for asset type
# Crypto: 0.001-0.005 (0.1%-0.5%)
# Stocks: 0.0-0.001 (0%-0.1%)
# ETFs: 0.0-0.001 (0%-0.1%)
```

### 9. Permission denied / externally-managed-environment

**Error:**
```
error: externally-managed-environment
```

**Solution:** Use virtual environment (recommended):
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Now install packages
pip install -r ../../requirements.txt
```

### 10. Strategy takes too long to run

**Issue:** Backtest is very slow.

**Causes:**
1. Very long date range
2. Complex indicator calculations on each bar
3. Large dataset (crypto 24/7 data)

**Solutions:**
```bash
# Use shorter date range
python backtest.py --ticker BTC-USD --start 2023-01-01

# Test with smaller dataset first
python backtest.py --ticker TQQQ --start 2024-01-01
```

## Verification Commands

### Test if everything is installed correctly:

```bash
# 1. Check Python version (should be 3.8+)
python3 --version

# 2. Check if in virtual environment
which python

# 3. Test imports
python3 -c "import pandas, numpy, backtrader, yfinance; print('All packages installed!')"

# 4. Run test script
python test_strategy.py

# 5. Run simple backtest
python backtest.py --ticker TQQQ --start 2024-01-01
```

### Check data availability:

```python
# Quick test in Python
import yfinance as yf

# Test ticker
df = yf.download('BTC-USD', start='2020-01-01')
print(f"Downloaded {len(df)} bars")
print(df.head())
```

## Getting More Help

### Enable detailed error messages:

Add this at the top of `backtest.py`:
```python
import warnings
warnings.filterwarnings('ignore')  # Suppress warnings
```

### Check versions:

```bash
pip list | grep -E "backtrader|yfinance|pandas|numpy"
```

Expected versions:
- pandas >= 2.2.0
- numpy >= 1.26.0
- yfinance >= 0.2.32
- backtrader >= 1.9.78.123

### Run in debug mode:

Edit `backtest.py` and change `printlog=True` to get detailed trade logs.

## Quick Fixes Summary

| Issue | Quick Fix |
|-------|-----------|
| MultiIndex error | ✅ Already fixed in code |
| Module not found | Install in virtual environment |
| No data found | Check ticker format (BTC-USD) |
| No trades | Use longer date range |
| Too slow | Shorter date range |
| Permission error | Use virtual environment |

## Still Having Issues?

1. Check you're in the right directory:
   ```bash
   pwd
   # Should show: .../back_testing/src/Mystic_Pulse_V2.0_Strategy
   ```

2. Verify all files exist:
   ```bash
   ls -la
   # Should show: backtest.py, strategy.py, etc.
   ```

3. Test with known-good parameters:
   ```bash
   python backtest.py --ticker TQQQ --start 2023-01-01 --end 2024-01-01
   ```

4. Check Python environment:
   ```bash
   python3 --version
   pip list
   ```

---

**Most issues are solved by:**
1. Using a virtual environment
2. Installing all requirements
3. Using correct ticker format (BTC-USD, not BTCUSD)
4. Running from the correct directory

