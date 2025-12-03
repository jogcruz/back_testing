"""
Backtesting script for Mystic Pulse V2.0 Strategy

This script backtests the Mystic Pulse V2.0 strategy using the backtrader framework.

Parameters:
- Long only strategy
- Period: 2020-Today
- Timeframe: 1D (daily)
- Position sizing: 100% of equity per trade
- Commission: 1%
- Slippage: 1 tick
"""

import backtrader as bt
import yfinance as yf
import pandas as pd
from datetime import datetime
import sys
import os

# Add parent directory to path to import strategy
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from strategy import MysticPulseV2Strategy as MysticPulseIndicator


class MysticPulseV2StrategyBT(bt.Strategy):
    """
    Backtrader strategy implementation for Mystic Pulse V2.0
    """
    
    params = (
        ('adx_length', 9),
        ('smoothing_factor', 1),
        ('printlog', True),
        ('debug_signals', False),  # Set to True to debug signal generation
        ('min_count_threshold', 2),  # Minimum count before entering (reduces whipsaws)
        ('min_holding_bars', 2),  # Minimum bars to hold position
    )
    
    def __init__(self):
        """Initialize strategy indicators and variables."""
        # Keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        
        # Persistent state variables (like Pine Script 'var')
        self.smoothed_tr = None
        self.smoothed_dm_plus = None
        self.smoothed_dm_minus = None
        self.positive_count = 0
        self.negative_count = 0
        self.last_bullish = None
        
        # Store previous OHLC smoothed values for calculations
        self.prev_close_s = None
        self.prev_high_s = None
        self.prev_low_s = None
        
        # Track holding period to avoid quick exits
        self.bars_in_position = 0
        
    def log(self, txt, dt=None):
        """Logging function for this strategy."""
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()}, {txt}')
    
    def notify_order(self, order):
        """Notification of order status."""
        if order.status in [order.Submitted, order.Accepted]:
            # Order submitted/accepted - no action required
            return
        
        # Check if an order has been completed
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f'BUY EXECUTED, Size: {order.executed.size:.6f}, '
                    f'Price: ${order.executed.price:.2f}, '
                    f'Total: ${order.executed.value:.2f}, '
                    f'Commission: ${order.executed.comm:.2f}'
                )
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log(
                    f'SELL EXECUTED, Size: {order.executed.size:.6f}, '
                    f'Price: ${order.executed.price:.2f}, '
                    f'Total: ${order.executed.value:.2f}, '
                    f'Commission: ${order.executed.comm:.2f}'
                )
            
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        
        # Reset order
        self.order = None
    
    def notify_trade(self, trade):
        """Notification of trade status."""
        if not trade.isclosed:
            return
        
        self.log(
            f'TRADE CLOSED - P&L: ${trade.pnl:.2f} (gross), '
            f'${trade.pnlcomm:.2f} (net after commission)'
        )
    
    def next(self):
        """Execute strategy logic for each bar - calculate indicators incrementally."""
        # Check if we have an order pending
        if self.order:
            return
        
        # Need minimum bars for smoothing
        if len(self) < self.params.smoothing_factor:
            return
        
        # Get current OHLC smoothed values (SMA)
        if self.params.smoothing_factor == 1:
            open_s = self.data.open[0]
            high_s = self.data.high[0]
            low_s = self.data.low[0]
            close_s = self.data.close[0]
        else:
            # Calculate SMA over smoothing_factor periods
            open_s = sum([self.data.open[-i] for i in range(self.params.smoothing_factor)]) / self.params.smoothing_factor
            high_s = sum([self.data.high[-i] for i in range(self.params.smoothing_factor)]) / self.params.smoothing_factor
            low_s = sum([self.data.low[-i] for i in range(self.params.smoothing_factor)]) / self.params.smoothing_factor
            close_s = sum([self.data.close[-i] for i in range(self.params.smoothing_factor)]) / self.params.smoothing_factor
        
        # Calculate True Range
        if self.prev_close_s is not None:
            tr1 = high_s - low_s
            tr2 = abs(high_s - self.prev_close_s)
            tr3 = abs(low_s - self.prev_close_s)
            true_range = max(tr1, tr2, tr3)
            
            # Calculate Directional Movement
            high_diff = high_s - self.prev_high_s
            low_diff = self.prev_low_s - low_s
            
            if high_diff > low_diff:
                dm_plus = max(high_diff, 0)
                dm_minus = 0
            elif low_diff > high_diff:
                dm_minus = max(low_diff, 0)
                dm_plus = 0
            else:
                dm_plus = 0
                dm_minus = 0
            
            # Wilder smoothing (like Pine Script)
            if self.smoothed_tr is None:
                self.smoothed_tr = true_range
                self.smoothed_dm_plus = dm_plus
                self.smoothed_dm_minus = dm_minus
            else:
                self.smoothed_tr = self.smoothed_tr - (self.smoothed_tr / self.params.adx_length) + true_range
                self.smoothed_dm_plus = self.smoothed_dm_plus - (self.smoothed_dm_plus / self.params.adx_length) + dm_plus
                self.smoothed_dm_minus = self.smoothed_dm_minus - (self.smoothed_dm_minus / self.params.adx_length) + dm_minus
            
            # Calculate DI+ and DI-
            if self.smoothed_tr > 0:
                di_plus = (self.smoothed_dm_plus / self.smoothed_tr) * 100
                di_minus = (self.smoothed_dm_minus / self.smoothed_tr) * 100
            else:
                di_plus = 0
                di_minus = 0
            
            # Store previous DI values for comparison
            if not hasattr(self, 'prev_di_plus'):
                self.prev_di_plus = di_plus
                self.prev_di_minus = di_minus
            
            # Update positive/negative counts (like Pine Script var logic)
            # Positive count increases when DI+ is rising and DI+ > DI-
            if di_plus > self.prev_di_plus and di_plus > di_minus:
                self.positive_count += 1
                self.negative_count = 0
            # Negative count increases when DI- is rising and DI- > DI+
            elif di_minus > self.prev_di_minus and di_minus > di_plus:
                self.negative_count += 1
                self.positive_count = 0
            
            # Update previous DI values
            self.prev_di_plus = di_plus
            self.prev_di_minus = di_minus
            
            # Determine if currently bullish
            current_bullish = self.positive_count >= self.negative_count
            
            # Track bars in position
            if self.position:
                self.bars_in_position += 1
            else:
                self.bars_in_position = 0
            
            # Debug logging
            if self.params.debug_signals and len(self) % 30 == 0:  # Log every 30 bars
                self.log(f'DEBUG: DI+={di_plus:.2f}, DI-={di_minus:.2f}, '
                        f'PosCount={self.positive_count}, NegCount={self.negative_count}, '
                        f'Bullish={current_bullish}, InPosition={bool(self.position)}')
            
            # Trading logic with improved filters to reduce whipsaws
            if not self.position:
                # Not in the market - check for long entry
                # Entry requires:
                # 1. Transition from bearish to bullish
                # 2. Positive count >= threshold (strong signal filter)
                if (current_bullish and 
                    self.last_bullish is not None and 
                    not self.last_bullish and
                    self.positive_count >= self.params.min_count_threshold):
                    
                    cash = self.broker.getcash()
                    price = self.data.close[0]
                    
                    # Account for commission AND price slippage
                    # Reserve extra 1% buffer for price movement between signal and execution
                    commission_rate = 0.002  # Should match the backtest commission parameter
                    safety_buffer = 0.01     # 1% buffer for price slippage
                    available_cash = cash / (1 + commission_rate + safety_buffer)
                    size = available_cash / price
                    
                    if size > 0:
                        self.log(f'BUY CREATE, Price: {price:.2f}, Size: {size:.4f}, '
                               f'PosCount: {self.positive_count} (>= {self.params.min_count_threshold})')
                        self.order = self.buy(size=size)
                    else:
                        self.log(f'BUY SIGNAL but size=0, Cash: {cash:.2f}, Price: {price:.2f}')
                        
                elif self.params.debug_signals and current_bullish and not self.position:
                    # Log why we're NOT entering even though bullish
                    if self.last_bullish is None:
                        self.log(f'NO ENTRY: last_bullish is None, PosCount={self.positive_count}')
                    elif self.last_bullish:
                        if len(self) % 30 == 0:  # Only log occasionally to avoid spam
                            self.log(f'NO ENTRY: Already bullish (no transition), '
                                   f'PosCount={self.positive_count}, NegCount={self.negative_count}')
                    elif self.positive_count < self.params.min_count_threshold:
                        if len(self) % 30 == 0:
                            self.log(f'NO ENTRY: Count too low ({self.positive_count} < {self.params.min_count_threshold})')
            else:
                # In the market - check for exit signal
                # Exit requires:
                # 1. Transition from bullish to bearish
                # 2. Held for minimum bars (avoid quick exit/reentry)
                if (not current_bullish and 
                    self.last_bullish is not None and 
                    self.last_bullish and
                    self.bars_in_position >= self.params.min_holding_bars):
                    
                    self.log(f'SELL CREATE, Price: {self.data.close[0]:.2f}, '
                           f'NegCount: {self.negative_count}, Held: {self.bars_in_position} bars')
                    self.order = self.sell(size=self.position.size)
                    
                elif self.params.debug_signals and not current_bullish and self.bars_in_position < self.params.min_holding_bars:
                    if len(self) % 10 == 0:
                        self.log(f'NO EXIT: Held only {self.bars_in_position} bars (< {self.params.min_holding_bars})')
            
            # Update last state
            self.last_bullish = current_bullish
        
        # Store current smoothed values for next bar
        self.prev_close_s = close_s
        self.prev_high_s = high_s
        self.prev_low_s = low_s
    
    def stop(self):
        """Called when the strategy ends."""
        self.log(
            f'(ADX Length {self.params.adx_length}, Smoothing {self.params.smoothing_factor}) '
            f'Ending Value: {self.broker.getvalue():.2f}',
            dt=self.datas[0].datetime.date(0)
        )


def run_backtest(ticker='TQQQ', start_date='2020-01-01', end_date=None, 
                 initial_cash=10000.0, commission=0.01, slippage_perc=0.0001,
                 debug_signals=False, min_count_threshold=2, min_holding_bars=2):
    """
    Run backtest for Mystic Pulse V2.0 Strategy.
    
    Args:
        ticker (str): Stock ticker symbol
        start_date (str): Start date for backtest (YYYY-MM-DD)
        end_date (str): End date for backtest (YYYY-MM-DD), None for today
        initial_cash (float): Initial capital
        commission (float): Commission rate (0.01 = 1%)
        slippage_perc (float): Slippage percentage
        
    Returns:
        cerebro: Backtrader cerebro instance with results
    """
    # Set end date to today if not provided
    if end_date is None:
        end_date = datetime.today().strftime('%Y-%m-%d')
    
    print(f"\n{'='*80}")
    print(f"Backtesting Mystic Pulse V2.0 Strategy")
    print(f"{'='*80}")
    print(f"Ticker: {ticker}")
    print(f"Period: {start_date} to {end_date}")
    print(f"Initial Capital: ${initial_cash:,.2f}")
    print(f"Commission: {commission*100:.2f}%")
    print(f"Slippage: {slippage_perc*100:.4f}%")
    print(f"{'='*80}\n")
    
    # Download data
    print(f"Downloading data for {ticker}...")
    df = yf.download(ticker, start=start_date, end=end_date, progress=False)
    
    if df.empty:
        print(f"Error: No data found for {ticker}")
        return None
    
    # Prepare data for backtrader
    # Handle MultiIndex columns from yfinance (newer versions)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # Convert column names to lowercase
    df.columns = [col.lower() if isinstance(col, str) else col for col in df.columns]
    
    # Select required columns
    df = df[['open', 'high', 'low', 'close', 'volume']]
    
    print(f"Data downloaded: {len(df)} bars from {df.index[0].date()} to {df.index[-1].date()}\n")
    
    # Create a Data Feed
    data = bt.feeds.PandasData(dataname=df)
    
    # Create a cerebro entity
    cerebro = bt.Cerebro()
    
    # Add strategy with parameters
    cerebro.addstrategy(MysticPulseV2StrategyBT, 
                       debug_signals=debug_signals,
                       min_count_threshold=min_count_threshold,
                       min_holding_bars=min_holding_bars)
    
    # Add data feed
    cerebro.adddata(data)
    
    # Set initial cash
    cerebro.broker.setcash(initial_cash)
    
    # Set commission - 1% per trade
    cerebro.broker.setcommission(commission=commission)
    
    # Allow fractional shares (important for crypto and expensive assets)
    cerebro.broker.set_checksubmit(False)
    
    # Add slippage (1 tick slippage approximated as percentage)
    cerebro.broker.set_slippage_perc(perc=slippage_perc)
    
    # Add analyzers
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', riskfreerate=0.0)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    
    # Print starting conditions
    print(f'Starting Portfolio Value: ${cerebro.broker.getvalue():,.2f}')
    
    # Run backtest
    results = cerebro.run()
    strat = results[0]
    
    # Print final results
    final_value = cerebro.broker.getvalue()
    print(f'\nFinal Portfolio Value: ${final_value:,.2f}')
    
    # Calculate Buy & Hold comparison
    initial_price = df.iloc[0]['close']
    final_price = df.iloc[-1]['close']
    buy_hold_return = ((final_price - initial_price) / initial_price) * 100
    
    # Calculate how many shares could be bought with initial cash (accounting for commission)
    shares_bought = initial_cash * (1 - commission) / initial_price
    buy_hold_final_value = shares_bought * final_price
    buy_hold_total_return = ((buy_hold_final_value - initial_cash) / initial_cash) * 100
    
    # Print performance metrics
    print(f"\n{'='*80}")
    print("PERFORMANCE METRICS")
    print(f"{'='*80}")
    
    # Total Return
    total_return = (final_value - initial_cash) / initial_cash * 100
    print(f"Strategy Total Return: {total_return:.2f}%")
    print(f"Buy & Hold Return: {buy_hold_total_return:.2f}%")
    
    # Performance comparison
    outperformance = total_return - buy_hold_total_return
    if outperformance > 0:
        print(f"Outperformance: +{outperformance:.2f}% ✓")
    elif outperformance < 0:
        print(f"Underperformance: {outperformance:.2f}%")
    else:
        print(f"Performance: Equal to Buy & Hold")
    
    print(f"\n--- Buy & Hold Comparison ---")
    print(f"Buy & Hold Initial Investment: ${initial_cash:,.2f}")
    print(f"Buy & Hold Final Value: ${buy_hold_final_value:,.2f}")
    print(f"Buy & Hold Shares Purchased: {shares_bought:.4f} @ ${initial_price:.2f}")
    print(f"Buy & Hold Final Price: ${final_price:.2f}")
    print(f"Price Change: {buy_hold_return:.2f}%")
    
    print(f"\n--- Strategy vs Buy & Hold ---")
    print(f"Strategy Final Value: ${final_value:,.2f}")
    print(f"Buy & Hold Final Value: ${buy_hold_final_value:,.2f}")
    print(f"Difference: ${final_value - buy_hold_final_value:,.2f}")
    
    # Sharpe Ratio
    sharpe = strat.analyzers.sharpe.get_analysis()
    sharpe_ratio = sharpe.get('sharperatio', 0)
    if sharpe_ratio is None:
        sharpe_ratio = 0
    print(f"\nSharpe Ratio: {sharpe_ratio:.3f}")
    
    # Drawdown
    drawdown = strat.analyzers.drawdown.get_analysis()
    print(f"Max Drawdown: {drawdown.max.drawdown:.2f}%")
    
    # Trade Analysis
    trade_analysis = strat.analyzers.trades.get_analysis()
    
    # Safely get total trades (might be 0 if no trades executed)
    try:
        total_trades = trade_analysis.total.closed if hasattr(trade_analysis, 'total') else 0
    except (KeyError, AttributeError):
        total_trades = 0
    
    print(f"Total Trades: {total_trades}")
    
    if total_trades > 0:
        try:
            won = trade_analysis.won.total if hasattr(trade_analysis, 'won') else 0
        except (KeyError, AttributeError):
            won = 0
            
        try:
            lost = trade_analysis.lost.total if hasattr(trade_analysis, 'lost') else 0
        except (KeyError, AttributeError):
            lost = 0
            
        win_rate = (won / total_trades * 100) if total_trades > 0 else 0
        print(f"Winning Trades: {won}")
        print(f"Losing Trades: {lost}")
        print(f"Win Rate: {win_rate:.2f}%")
        
        try:
            if hasattr(trade_analysis, 'won') and hasattr(trade_analysis.won, 'pnl'):
                avg_win = trade_analysis.won.pnl.average if won > 0 else 0
                print(f"Average Win: ${avg_win:.2f}")
        except (KeyError, AttributeError):
            pass
        
        try:
            if hasattr(trade_analysis, 'lost') and hasattr(trade_analysis.lost, 'pnl'):
                avg_loss = trade_analysis.lost.pnl.average if lost > 0 else 0
                print(f"Average Loss: ${avg_loss:.2f}")
        except (KeyError, AttributeError):
            pass
    else:
        print("⚠️  WARNING: No trades executed!")
        print(f"   Consider:")
        print(f"   - Lowering --min-count (current: {min_count_threshold})")
        print(f"   - Lowering --min-hold (current: {min_holding_bars})")
        print(f"   - Checking if strategy logic is working correctly")
    
    print(f"{'='*80}\n")
    
    # Plot results (optional - commented out for now)
    # cerebro.plot(style='candlestick')
    
    return cerebro


if __name__ == '__main__':
    """Main execution."""
    import argparse
    
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Backtest Mystic Pulse V2.0 Strategy',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Leveraged ETFs
  python backtest.py --ticker TQQQ
  python backtest.py --ticker SOXL
  
  # Cryptocurrencies
  python backtest.py --ticker BTC-USD
  python backtest.py --ticker ETH-USD
  python backtest.py --ticker SOL-USD
  
  # Stocks
  python backtest.py --ticker AAPL --start 2022-01-01
  python backtest.py --ticker TSLA --cash 25000
  
  # Custom parameters
  python backtest.py --ticker BTC-USD --start 2020-01-01 --cash 10000 --commission 0.005
        """
    )
    
    parser.add_argument(
        '--ticker', '-t',
        type=str,
        default='TQQQ',
        help='Ticker symbol (e.g., TQQQ, BTC-USD, ETH-USD, AAPL). Default: TQQQ'
    )
    parser.add_argument(
        '--start', '-s',
        type=str,
        default='2020-01-01',
        help='Start date (YYYY-MM-DD). Default: 2020-01-01'
    )
    parser.add_argument(
        '--end', '-e',
        type=str,
        default=None,
        help='End date (YYYY-MM-DD). Default: Today'
    )
    parser.add_argument(
        '--cash', '-c',
        type=float,
        default=10000.0,
        help='Initial cash. Default: 10000.0'
    )
    parser.add_argument(
        '--commission',
        type=float,
        default=0.01,
        help='Commission rate (e.g., 0.01 for 1%%). Default: 0.01'
    )
    parser.add_argument(
        '--slippage',
        type=float,
        default=0.0001,
        help='Slippage percentage. Default: 0.0001 (0.01%%)'
    )
    parser.add_argument(
        '--adx-length',
        type=int,
        default=9,
        help='ADX smoothing length. Default: 9'
    )
    parser.add_argument(
        '--smoothing',
        type=int,
        default=1,
        help='OHLC SMA smoothing factor. Default: 1'
    )
    parser.add_argument(
        '--list-crypto',
        action='store_true',
        help='List popular cryptocurrency tickers'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output for signal generation'
    )
    parser.add_argument(
        '--min-count',
        type=int,
        default=2,
        help='Minimum positive count threshold before entering (default: 2, reduces whipsaw trades)'
    )
    parser.add_argument(
        '--min-hold',
        type=int,
        default=2,
        help='Minimum bars to hold position before exiting (default: 2, prevents quick exits)'
    )
    
    args = parser.parse_args()
    
    # List crypto tickers if requested
    if args.list_crypto:
        print("\n" + "="*80)
        print(" Popular Cryptocurrency Tickers (Yahoo Finance format)")
        print("="*80)
        print("\nMajor Cryptocurrencies:")
        print("  BTC-USD   - Bitcoin")
        print("  ETH-USD   - Ethereum")
        print("  BNB-USD   - Binance Coin")
        print("  SOL-USD   - Solana")
        print("  XRP-USD   - Ripple")
        print("  ADA-USD   - Cardano")
        print("  DOGE-USD  - Dogecoin")
        print("  AVAX-USD  - Avalanche")
        print("  MATIC-USD - Polygon")
        print("  DOT-USD   - Polkadot")
        print("  LINK-USD  - Chainlink")
        print("  UNI-USD   - Uniswap")
        print("\nLeveraged ETFs:")
        print("  TQQQ      - 3x Nasdaq")
        print("  SOXL      - 3x Semiconductors")
        print("  UPRO      - 3x S&P 500")
        print("  SPXL      - 3x S&P 500")
        print("\nNote: Use ticker-USD format for crypto (e.g., BTC-USD)")
        print("="*80)
        sys.exit(0)
    
    # Convert ticker to uppercase
    ticker = args.ticker.upper()
    
    # Run backtest
    cerebro = run_backtest(
        ticker=ticker,
        start_date=args.start,
        end_date=args.end,
        initial_cash=args.cash,
        commission=args.commission,
        slippage_perc=args.slippage,
        debug_signals=args.debug,
        min_count_threshold=args.min_count,
        min_holding_bars=args.min_hold
    )
    
    if cerebro:
        print("\nBacktest completed successfully!")
        print(f"\nTo run another backtest:")
        print(f"  python backtest.py --ticker YOUR_TICKER")
        print(f"  python backtest.py --list-crypto  # See crypto tickers")
    else:
        print("\nBacktest failed! Please check the ticker symbol and date range.")

