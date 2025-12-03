# Debug Mode for Signal Investigation

## Issue: Strategy Stops Trading After Certain Period

If you notice the strategy stops generating signals after a certain date (e.g., trades until Feb 2023, then nothing until end of backtest), you can use debug mode to investigate.

## How to Use Debug Mode

```bash
# Enable debug output
python backtest.py --ticker BTC-USD --commission 0.002 --debug
```

This will print diagnostic information every 30 bars showing:
- DI+ and DI- values
- Positive and negative counts
- Current bullish/bearish state
- Position status

## Example Debug Output

```
2023-02-10, SELL EXECUTED, Price: 21816.82
2023-03-12, DEBUG: DI+=45.32, DI-=12.18, PosCount=0, NegCount=15, Bullish=False, InPosition=False
2023-04-11, DEBUG: DI+=38.67, DI-=18.45, PosCount=0, NegCount=28, Bullish=False, InPosition=False
2023-05-10, DEBUG: DI+=25.89, DI-=32.11, PosCount=0, NegCount=45, Bullish=False, InPosition=False
```

## What to Look For

### Normal Behavior
```
DEBUG: DI+=52.30, DI-=15.20, PosCount=12, NegCount=0, Bullish=True, InPosition=True
```
- Counts are incrementing appropriately
- Bullish state matches position
- DI values are reasonable (typically 0-100)

### Problem Indicators

#### 1. Counts Stuck at Zero
```
DEBUG: DI+=45.00, DI-=55.00, PosCount=0, NegCount=0, Bullish=True, InPosition=False
```
**Issue**: Neither count is incrementing
**Cause**: Comparison logic not working (prev_di values may be wrong)

#### 2. One Count Extremely High
```
DEBUG: DI+=25.00, DI-=35.00, PosCount=0, NegCount=500, Bullish=False, InPosition=False
```
**Issue**: Negative count keeps growing, never resets
**Cause**: Positive count condition never met

#### 3. DI Values Flat
```
DEBUG: DI+=50.00, DI-=50.00, PosCount=0, NegCount=150, Bullish=False, InPosition=False
DEBUG: DI+=50.00, DI-=50.00, PosCount=0, NegCount=151, Bullish=False, InPosition=False
```
**Issue**: DI values not changing
**Cause**: Wilder smoothing may not be updating correctly

## Investigating the Gap

### Step 1: Run with Debug Mode

```bash
python backtest.py --ticker BTC-USD --start 2023-01-01 --end 2024-01-01 --debug
```

### Step 2: Check the Output

Look for patterns in the debug output:
- Are DI+ and DI- changing appropriately?
- Are the counts incrementing when expected?
- Does the bullish state transition correctly?

### Step 3: Analyze the Logic

For entry signal to generate:
1. Must not be in position
2. `positive_count >= negative_count` must be True
3. Previous bar must have been bearish (last_bullish=False)

For positive_count to increment:
1. `di_plus > prev_di_plus` (DI+ rising)
2. `di_plus > di_minus` (DI+ stronger)

## Common Issues

### Issue 1: Counts Never Reset

**Symptom**: negative_count grows to 500+, never resets

**Debug shows**:
```
DEBUG: DI+=30.00, DI-=45.00, PosCount=0, NegCount=523, Bullish=False
```

**Explanation**: 
- For positive_count to start incrementing, BOTH conditions must be met:
  - DI+ > prev_DI+ (DI+ rising)
  - DI+ > DI- (DI+ stronger)
- If DI+ is stronger but falling, or DI+ is rising but weaker, neither count increments
- negative_count stays at its high value indefinitely

**Solution**: This might be correct behavior if market is truly choppy/sideways

### Issue 2: DI Values Not Updating

**Symptom**: DI+ and DI- stay constant for many bars

**Debug shows**:
```
DEBUG: DI+=42.50, DI-=42.50, PosCount=0, NegCount=200, Bullish=False
DEBUG: DI+=42.50, DI-=42.50, PosCount=0, NegCount=201, Bullish=False
```

**Explanation**: Wilder smoothing may have an issue

**Check**:
- Is True Range being calculated correctly?
- Is Directional Movement being calculated correctly?
- Are smoothed values being updated incrementally?

### Issue 3: Prev Values Not Updating

**Symptom**: Counts stuck at 0, no increments

**Debug shows**:
```
DEBUG: DI+=55.00, DI-=30.00, PosCount=0, NegCount=0, Bullish=True
```

**Explanation**: 
- DI+ > DI- (should be bullish)
- But PosCount=0 suggests the increment condition isn't being met
- Likely: `di_plus > prev_di_plus` is always False
- Cause: prev_di_plus might not be updating, or updating at wrong time

**Check**: Verify prev_di_plus and prev_di_minus are updated at END of each bar

## Testing Different Periods

```bash
# Test 2020 (known to work)
python backtest.py --ticker BTC-USD --start 2020-01-01 --end 2021-01-01 --debug

# Test 2023 (problematic period)
python backtest.py --ticker BTC-USD --start 2023-01-01 --end 2024-01-01 --debug

# Test full period
python backtest.py --ticker BTC-USD --start 2020-01-01 --debug
```

## Disable Debug Output

```bash
# Normal run without debug
python backtest.py --ticker BTC-USD --commission 0.002
```

## Next Steps

Based on debug output:
1. If counts are stuck → Check prev_di update logic
2. If DI values flat → Check Wilder smoothing calculation
3. If one count very high → May be correct (choppy market), or check reset logic

---

**Use debug mode to understand WHY the strategy isn't generating signals during certain periods!**

