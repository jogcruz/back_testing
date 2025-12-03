# Installation and Setup Guide

This guide will help you set up the environment to run the Mystic Pulse V2.0 Strategy backtest.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation Steps

### Option 1: Using a Virtual Environment (Recommended)

1. **Navigate to the project directory:**
   ```bash
   cd /Users/jorge.gomez/Documents/personales/back_testing
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment:**
   
   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```
   
   On Windows:
   ```bash
   venv\Scripts\activate
   ```

4. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Navigate to the strategy folder:**
   ```bash
   cd src/Mystic_Pulse_V2.0_Strategy
   ```

6. **Run the test script:**
   ```bash
   python test_strategy.py
   ```

7. **Run the backtest:**
   ```bash
   python backtest.py
   ```

### Option 2: Using pipx (For isolated installations)

If you don't want to create a virtual environment manually:

1. **Install pipx (if not already installed):**
   ```bash
   brew install pipx
   pipx ensurepath
   ```

2. **Use pipx to run the scripts:**
   ```bash
   pipx run --spec pandas,numpy,yfinance,backtrader,matplotlib python backtest.py
   ```

### Option 3: System-wide Installation (Not Recommended)

If you have appropriate permissions and want to install system-wide:

```bash
pip3 install --user -r requirements.txt
```

## Testing the Installation

Once dependencies are installed, you can verify everything works:

1. **Test the strategy logic:**
   ```bash
   python test_strategy.py
   ```
   
   This will validate the indicator calculations using synthetic data.

2. **Run the full backtest:**
   ```bash
   python backtest.py
   ```
   
   This will:
   - Download TQQQ data from 2020-01-01 to today
   - Run the backtest with the specified parameters
   - Display performance metrics

## Troubleshooting

### Module Not Found Errors

If you see `ModuleNotFoundError`, ensure you:
1. Have activated the virtual environment (if using one)
2. Have installed all requirements: `pip install -r requirements.txt`

### Permission Errors

If you get permission errors when installing:
1. Use a virtual environment (Option 1 above)
2. Or add `--user` flag: `pip3 install --user -r requirements.txt`

### Data Download Issues

If Yahoo Finance data download fails:
1. Check your internet connection
2. Verify the ticker symbol exists
3. Try a different date range

## Customizing the Backtest

To test different tickers or parameters, edit `backtest.py`:

```python
# Change these variables at the bottom of backtest.py
TICKER = 'SOXL'  # Change to any ticker
START_DATE = '2020-01-01'  # Change start date
INITIAL_CASH = 10000.0  # Change initial capital
```

## Running Different Scenarios

You can create different test scripts for various tickers:

**For TQQQ:**
```bash
python backtest.py
```

**For SOXL:**
Edit `backtest.py` and change `TICKER = 'TQQQ'` to `TICKER = 'SOXL'`, then run:
```bash
python backtest.py
```

## File Structure

```
Mystic_Pulse_V2.0_Strategy/
├── Indicator.ps          # Original Pine Script indicator
├── strategy.py           # Python strategy implementation
├── backtest.py           # Backtesting script
├── test_strategy.py      # Test/validation script
├── README.md             # Strategy documentation
└── INSTALL.md            # This file
```

## Next Steps

After successful installation:
1. Run `test_strategy.py` to verify indicator calculations
2. Run `backtest.py` to see performance on TQQQ
3. Modify parameters in `backtest.py` to test other tickers
4. Review the performance metrics and adjust strategy parameters if needed

## Support

If you encounter any issues:
1. Check that all dependencies are installed
2. Verify Python version is 3.8 or higher: `python3 --version`
3. Ensure you're in the correct directory
4. Check that the virtual environment is activated (if using one)

## Requirements

The following packages will be installed:
- **pandas** (>=2.2.0): Data manipulation
- **numpy** (>=1.26.0): Numerical computations
- **yfinance** (>=0.2.32): Download market data
- **backtrader** (>=1.9.78.123): Backtesting framework
- **matplotlib** (>=3.7.0): Plotting and visualization

