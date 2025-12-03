# Critical Fix: Incremental Indicator Calculation

## Problem: Strategy Stopped Trading After Few Months

The strategy was only making trades for a few months (e.g., until October 2020 or February 2023), then sitting in cash for YEARS until the end of the backtest.

## Root Cause: Recalculating vs Incremental Updates

### What the Original Pine Script Does

Pine Script uses `var` keyword for persistent state variables:
```pinescript
var float smoothed_true_range = na
var float smoothed_dm_plus    = na
var float smoothed_dm_minus   = na
var int   positive_count      = 0
var int   negative_count      = 0
```

These variables are **updated incrementally** on each new bar:
- Wilder smoothing uses previous smoothed values
- Counts accumulate across the ENTIRE chart
- State persists from first bar to last bar

### What the Python Backtest Was Doing (WRONG)

The old implementation was **recalculating everything from scratch** on every bar:

```python
# OLD (BROKEN) - Recalculate on every bar
def next(self):
    df = self.get_dataframe(lookback=500)  # Get 500 bars
    df_signals = self.mystic_pulse.generate_signals(df)  # Recalculate EVERYTHING
    current_bullish = df_signals['is_bullish'].iloc[-1]  # Use last value
```

This approach had fatal flaws:
1. **Lost state between bars** - Wilder smoothing was reset
2. **Counts recalculated** - positive/negative counts started from scratch on each lookback window
3. **Inconsistent signals** - Same bar could produce different signals depending on lookback window
4. **Slow performance** - Recalculating 500 bars on every tick

## The Solution: Incremental Calculation

✅ **NEW**: Calculate indicators incrementally, just like Pine Script:

```python
# NEW (FIXED) - Incremental calculation
class MysticPulseV2StrategyBT(bt.Strategy):
    def __init__(self):
        # Persistent state variables (like Pine Script 'var')
        self.smoothed_tr = None
        self.smoothed_dm_plus = None
        self.smoothed_dm_minus = None
        self.positive_count = 0
        self.negative_count = 0
    
    def next(self):
        # Calculate current bar's values
        # Update Wilder smoothing incrementally
        self.smoothed_tr = self.smoothed_tr - (self.smoothed_tr / adx_length) + true_range
        
        # Update counts incrementally
        if di_plus > prev_di_plus and di_plus > di_minus:
            self.positive_count += 1
            self.negative_count = 0
```

### Key Differences

| Aspect | Old (Broken) | New (Fixed) |
|--------|-------------|-------------|
| State | Recalculated | Persistent |
| Wilder Smoothing | Wrong | Correct incremental |
| Counts | Reset each bar | Cumulative |
| Performance | Slow (500 bars) | Fast (1 bar) |
| Accuracy | Inconsistent | Matches Pine Script |

## Why This Fixes the "Stuck" Problem

### Old Behavior (Broken)
1. Strategy sells on 2020-10-07
2. On next bar, recalculates indicators on 500-bar window
3. Counts are recalculated and might show different pattern
4. `is_bullish` never transitions to True again
5. **Strategy stuck in cash for 5 years**

### New Behavior (Fixed)
1. Strategy sells on 2020-10-07
2. On next bar, updates indicators incrementally
3. Counts continue to accumulate properly
4. When DI+ starts rising and DI+ > DI-, positive_count increments
5. **Strategy enters when positive_count >= negative_count**
6. Trading continues throughout the backtest period

## Technical Details

### Wilder Smoothing Formula

Pine Script:
```pinescript
smoothed_true_range := na(smoothed_true_range[1]) ? true_range : 
    (smoothed_true_range[1] - (smoothed_true_range[1] / adx_length) + true_range)
```

Python (Fixed):
```python
if self.smoothed_tr is None:
    self.smoothed_tr = true_range
else:
    self.smoothed_tr = self.smoothed_tr - (self.smoothed_tr / self.params.adx_length) + true_range
```

### Positive/Negative Count Logic

Pine Script:
```pinescript
if (di_plus > di_plus[1] and di_plus > di_minus)
    positive_count += 1
    negative_count := 0
```

Python (Fixed):
```python
if di_plus > self.prev_di_plus and di_plus > di_minus:
    self.positive_count += 1
    self.negative_count = 0
```

## Verification

Run a backtest and check for:

✅ **Continuous trading** throughout the period
```
2020-02-24, BUY EXECUTED
2020-02-26, SELL EXECUTED
2020-03-26, BUY EXECUTED
... trades throughout 2020-2025 ...
2024-11-15, SELL EXECUTED
2025-01-10, BUY EXECUTED
2025-11-30, Final position
```

❌ **NOT this** (broken - gaps of years):
```
2020-10-07, SELL EXECUTED
... nothing for 5 years ...
2025-11-30, Ending Value
```

## Performance Improvement

### Old (Broken)
- Recalculate 500 bars on every iteration
- For 2000-bar backtest: 2000 × 500 = 1,000,000 calculations
- Very slow

### New (Fixed)
- Calculate 1 bar on every iteration
- For 2000-bar backtest: 2000 × 1 = 2,000 calculations
- **500x faster!**

## Code Changes Summary

1. **Added persistent state variables** in `__init__`:
   - `self.smoothed_tr`, `self.smoothed_dm_plus`, `self.smoothed_dm_minus`
   - `self.positive_count`, `self.negative_count`
   - `self.prev_di_plus`, `self.prev_di_minus`

2. **Rewrote `next()` method** to calculate incrementally:
   - Calculate current bar's OHLC smoothed values
   - Update Wilder smoothing using previous values
   - Update DI+ and DI-
   - Update positive/negative counts
   - Generate signals from current state

3. **Removed `get_dataframe()` and pandas dependency** from strategy:
   - No longer needed
   - Direct backtrader data access
   - More efficient

## Testing

```bash
# Should now show continuous trading
python backtest.py --ticker BTC-USD --commission 0.002

# Bitcoin 2020-2021 bull run should have multiple trades
python backtest.py --ticker BTC-USD --start 2020-01-01 --end 2022-01-01

# Should see trades throughout, not just at the beginning
python backtest.py --ticker TQQQ --commission 0.001
```

## Expected Results

With BTC-USD from 2020-01-01:
- ✅ Trades throughout 2020
- ✅ Captures 2020-2021 bull run
- ✅ Trades during 2022 bear market  
- ✅ Trades in 2023-2024 recovery
- ✅ No multi-year gaps without trading

---

**Status**: ✅ Fixed - Incremental calculation now matches Pine Script behavior
**Impact**: Strategy now works correctly throughout entire backtest period
**Performance**: 500x faster calculation
**Date**: December 1, 2025

