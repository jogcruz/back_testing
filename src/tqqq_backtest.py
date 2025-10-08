#!/usr/bin/env python3
"""
Stock Trading Strategy Backtester

Strategy:
- Every day at 10 AM (configurable): Buy 10% of initial capital ($2,000) worth of stock at market price 
  if market filter ticker closed above 50 DMA on previous trading day (trend filter) and portfolio has at least $2,000 cash available
- Immediately place 10 sell orders (each 10% of shares bought) at target prices:
  buy_price + $1, buy_price + $2, ..., buy_price + $10  (increment configurable)
- Sell orders execute when price reaches target
- Cash from sales is immediately added back to portfolio for future buys
- Track performance monthly from January 1, 2025 (date range configurable)

Default tickers: TQQQ (stock to trade) and QQQ (market filter)
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, time, timedelta
from typing import List, Dict, Tuple
from dataclasses import dataclass, field
import warnings
warnings.filterwarnings('ignore')


@dataclass
class SellOrder:
    """Represents a pending sell order"""
    shares: float
    target_price: float
    created_date: datetime
    buy_price: float
    
    def __repr__(self):
        return f"SellOrder({self.shares:.2f} shares @ ${self.target_price:.2f})"


@dataclass
class Trade:
    """Represents a completed trade"""
    trade_type: str  # 'BUY' or 'SELL'
    date: datetime
    shares: float
    price: float
    amount: float
    
    def __repr__(self):
        return f"{self.trade_type}: {self.shares:.2f} shares @ ${self.price:.2f} = ${self.amount:.2f}"


@dataclass
class PortfolioState:
    """Current portfolio state"""
    cash: float
    shares_held: float
    pending_sell_orders: List[SellOrder] = field(default_factory=list)
    trade_history: List[Trade] = field(default_factory=list)
    daily_values: Dict[str, float] = field(default_factory=dict)
    skipped_buys_no_cash: int = 0  # Track number of skipped buys due to insufficient cash
    skipped_buys_market_condition: int = 0  # Track skipped buys due to Nasdaq below 50 DMA
    
    def total_value(self, current_price: float) -> float:
        """Calculate total portfolio value"""
        return self.cash + (self.shares_held * current_price)
    
    def add_trade(self, trade: Trade):
        """Add a trade to history"""
        self.trade_history.append(trade)


class TQQQBacktester:
    """Backtester for stock trading strategy"""
    
    def __init__(self, initial_capital: float = 20000, daily_investment: float = 2000, 
                 data_interval: str = "5m", use_nasdaq_filter: bool = True,
                 price_increment: float = 1.0, ticker: str = "TQQQ", 
                 filter_ticker: str = "QQQ"):
        self.initial_capital = initial_capital
        self.daily_investment = daily_investment
        self.portfolio = PortfolioState(cash=initial_capital, shares_held=0.0)
        self.buy_executed_today = {}  # Track if buy was executed each day
        self.skip_logged_today = {}  # Track if skip message was logged each day (to avoid duplicates)
        self.data_interval = data_interval  # Data interval: "5m", "15m", "1h", "1d"
        self.use_nasdaq_filter = use_nasdaq_filter  # Only buy if filter ticker above 50 DMA
        self.filter_data = None  # Will store filter ticker daily data with 50 DMA
        self.price_increment = price_increment  # Price increment for sell orders ($1, $2, etc.)
        self.ticker = ticker  # Stock ticker to backtest
        self.filter_ticker = filter_ticker  # Ticker to use for 50 DMA filter
        
    def download_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Download stock data at specified intervals"""
        print(f"📊 Downloading {self.ticker} data from {start_date} to {end_date}...")
        print(f"   Interval: {self.data_interval}")
        
        ticker = yf.Ticker(self.ticker)
        
        # Yahoo Finance limitations for intraday data
        interval_limits = {
            "1m": 7,      # 1-minute data: last 7 days
            "2m": 60,     # 2-minute data: last 60 days
            "5m": 60,     # 5-minute data: last 60 days
            "15m": 60,    # 15-minute data: last 60 days
            "30m": 60,    # 30-minute data: last 60 days
            "1h": 730,    # 1-hour data: last 730 days
            "1d": None    # Daily data: no limit
        }
        
        # Check if date range exceeds limitation
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.now()
        days_diff = (end_dt - start_dt).days
        
        limit = interval_limits.get(self.data_interval)
        if limit and days_diff > limit:
            print(f"⚠️  WARNING: Requested {days_diff} days, but {self.data_interval} data limited to {limit} days")
            print(f"   Adjusting start date to last {limit} days...")
            start_date = (end_dt - timedelta(days=limit)).strftime("%Y-%m-%d")
            print(f"   New start date: {start_date}")
        
        try:
            df = ticker.history(start=start_date, end=end_date, interval=self.data_interval)
        except Exception as e:
            print(f"❌ Error downloading data: {e}")
            # Try fallback to daily data
            if self.data_interval != "1d":
                print("   Falling back to daily data...")
                self.data_interval = "1d"
                df = ticker.history(start=start_date, end=end_date, interval="1d")
            else:
                raise
        
        if df.empty:
            raise ValueError("No data downloaded. Check date range and ticker symbol.")
        
        print(f"✅ Downloaded {len(df)} data points")
        print(f"   Date range: {df.index[0]} to {df.index[-1]}")
        
        return df
    
    def download_nasdaq_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Download filter ticker daily data and calculate 50-day moving average"""
        print(f"📊 Downloading {self.filter_ticker} daily data for market filter...")
        
        # Download filter ticker data (daily only for 50 DMA calculation)
        ticker = yf.Ticker(self.filter_ticker)
        
        # Add buffer for 50 DMA calculation (need 50 days before start_date)
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        buffer_start = (start_dt - timedelta(days=100)).strftime("%Y-%m-%d")
        
        df = ticker.history(start=buffer_start, end=end_date, interval="1d")
        
        if df.empty:
            print(f"⚠️  WARNING: Could not download {self.filter_ticker} data, disabling market filter")
            self.use_nasdaq_filter = False
            return pd.DataFrame()
        
        # Calculate 50-day moving average
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        # Create signal: 1 if close > 50 DMA, 0 otherwise
        df['Above_50_DMA'] = (df['Close'] > df['SMA_50']).astype(int)
        
        print(f"✅ Downloaded {self.filter_ticker} data: {len(df)} days")
        print(f"   50 DMA calculated from: {df.index[0].date()} to {df.index[-1].date()}")
        
        return df
    
    def is_nasdaq_above_50dma(self, check_date: datetime.date) -> bool:
        """Check if filter ticker closed above 50 DMA on the previous trading day"""
        if not self.use_nasdaq_filter or self.filter_data is None or self.filter_data.empty:
            return True  # If filter disabled or no data, allow buy
        
        # Find the previous trading day's data
        # Convert check_date to timezone-naive datetime for comparison
        check_datetime = pd.Timestamp(check_date).tz_localize(None)
        
        # Ensure filter_data index is timezone-naive
        filter_index = self.filter_data.index.tz_localize(None) if self.filter_data.index.tz is not None else self.filter_data.index
        
        # Get all dates before check_date
        previous_dates = filter_index[filter_index < check_datetime]
        
        if len(previous_dates) == 0:
            return True  # No previous data, allow buy
        
        # Get the most recent previous trading day
        previous_day_idx = len(previous_dates) - 1
        previous_day = self.filter_data.index[previous_day_idx]
        
        # Check if data exists and 50 DMA is calculated
        if pd.isna(self.filter_data.loc[previous_day, 'SMA_50']):
            return True  # 50 DMA not yet calculated, allow buy
        
        above_50dma = self.filter_data.loc[previous_day, 'Above_50_DMA'] == 1
        
        return above_50dma
    
    def is_market_open_time(self, dt: datetime) -> bool:
        """Check if timestamp is during market hours (9:30 AM - 4:00 PM ET)"""
        market_time = dt.time()
        market_open = time(9, 30)
        market_close = time(16, 0)
        
        # Check if it's a weekday
        if dt.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        return market_open <= market_time <= market_close
    
    def should_buy(self, dt: datetime) -> bool:
        """Check if we should execute buy at this timestamp (around 10 AM)"""
        date_key = dt.date()
        
        # If already bought today, skip
        if date_key in self.buy_executed_today:
            return False
        
        # For daily data, buy at market open
        if self.data_interval == "1d":
            return True
        
        # For intraday data, check if it's 10:00 AM or later (but before 11:00 AM)
        # Note: Yahoo Finance hourly data has timestamps at 10:30 for 1h interval
        market_time = dt.time()
        buy_window_start = time(10, 0)
        buy_window_end = time(11, 0)  # Expanded to catch 10:30 AM timestamp
        
        if buy_window_start <= market_time < buy_window_end:
            return True
        
        return False
    
    def execute_buy(self, dt: datetime, price: float):
        """Execute buy order: buy stock at daily investment amount (only if sufficient cash and market conditions allow)"""
        date_key = dt.date()
        
        # Check 1: Sufficient cash
        if self.portfolio.cash < self.daily_investment:
            # Only print skip message once per day (for intraday data)
            if date_key not in self.skip_logged_today:
                print(f"⚠️  SKIPPED - Insufficient cash on {date_key}: ${self.portfolio.cash:.2f} (need ${self.daily_investment:.2f})")
                self.portfolio.skipped_buys_no_cash += 1
                self.skip_logged_today[date_key] = 'no_cash'
            # Don't mark day as executed so we can retry if cash becomes available
            return
        
        # If we had previously logged a skip for this day but now have cash, clear the skip log
        if date_key in self.skip_logged_today and self.skip_logged_today[date_key] == 'no_cash':
            del self.skip_logged_today[date_key]
        
        # Check 2: Filter ticker above 50 DMA (if filter enabled)
        if self.use_nasdaq_filter and not self.is_nasdaq_above_50dma(date_key):
            # Only print skip message once per day
            if date_key not in self.skip_logged_today:
                print(f"⚠️  SKIPPED - Market condition on {date_key}: {self.filter_ticker} below 50 DMA (bearish signal)")
                self.portfolio.skipped_buys_market_condition += 1
                self.skip_logged_today[date_key] = 'market_condition'
            # Mark day as executed to prevent retry (market condition won't change intraday)
            self.buy_executed_today[date_key] = True
            return
        
        # Calculate shares to buy (MUST be integer - round down)
        shares_to_buy = int(self.daily_investment / price)
        
        # Check if we can buy at least 10 shares (minimum for 10 sell orders)
        if shares_to_buy < 10:
            # Only print skip message once per day
            if date_key not in self.skip_logged_today:
                print(f"⚠️  SKIPPED - Not enough shares on {date_key}: Can only buy {shares_to_buy} shares (need at least 10)")
                self.portfolio.skipped_buys_no_cash += 1
                self.skip_logged_today[date_key] = 'min_shares'
            return
        
        cost = shares_to_buy * price
        
        # Execute buy
        self.portfolio.cash -= cost
        self.portfolio.shares_held += shares_to_buy
        
        # Record trade
        trade = Trade(
            trade_type='BUY',
            date=dt,
            shares=shares_to_buy,
            price=price,
            amount=cost
        )
        self.portfolio.add_trade(trade)
        
        # Mark buy as executed today
        self.buy_executed_today[dt.date()] = True
        
        # Print buy confirmation BEFORE creating sell orders (so logs are in correct order)
        print(f"✅ BUY  {dt.date()} {dt.time()}: {shares_to_buy} shares @ ${price:.2f} = ${cost:.2f}")
        print(f"   Cash remaining: ${self.portfolio.cash:.2f}, Total shares: {self.portfolio.shares_held}")
        
        # Create 10 sell orders with integer shares (prints "Created 10 sell orders...")
        self.create_sell_orders(shares_to_buy, price, dt)
    
    def create_sell_orders(self, shares: int, buy_price: float, dt: datetime):
        """
        Create 10 sell orders with integer shares distributed as evenly as possible
        
        Example: 21 shares → 9 orders of 2 shares + 1 order of 3 shares
        """
        # Calculate base shares per order and remainder
        base_shares = shares // 10  # Integer division
        extra_shares = shares % 10  # Remainder
        
        # Create list of share counts for each order
        # First (10 - extra_shares) orders get base_shares
        # Last extra_shares orders get (base_shares + 1)
        share_distribution = []
        for i in range(10):
            if i < (10 - extra_shares):
                share_distribution.append(base_shares)
            else:
                share_distribution.append(base_shares + 1)
        
        # Create the 10 sell orders
        for i in range(1, 11):
            order_shares = share_distribution[i - 1]
            target_price = buy_price + (i * self.price_increment)
            sell_order = SellOrder(
                shares=order_shares,
                target_price=target_price,
                created_date=dt,
                buy_price=buy_price
            )
            self.portfolio.pending_sell_orders.append(sell_order)
        
        min_price = buy_price + self.price_increment
        max_price = buy_price + (10 * self.price_increment)
        
        # Create summary of distribution
        if extra_shares == 0:
            distribution_msg = f"{base_shares} shares each"
        else:
            distribution_msg = f"{10 - extra_shares} orders of {base_shares} shares, {extra_shares} orders of {base_shares + 1} shares"
        
        print(f"   Created 10 sell orders: {distribution_msg} at ${min_price:.2f} to ${max_price:.2f}")
    
    def check_sell_orders(self, dt: datetime, high_price: float):
        """Check if any pending sell orders should be executed"""
        executed_orders = []
        
        for order in self.portfolio.pending_sell_orders:
            # If high price reached the target price, execute the order
            if high_price >= order.target_price:
                # Execute sell
                proceeds = order.shares * order.target_price
                self.portfolio.cash += proceeds
                self.portfolio.shares_held -= order.shares
                
                # Record trade
                trade = Trade(
                    trade_type='SELL',
                    date=dt,
                    shares=order.shares,
                    price=order.target_price,
                    amount=proceeds
                )
                self.portfolio.add_trade(trade)
                
                profit = (order.target_price - order.buy_price) * order.shares
                print(f"💰 SELL {dt.date()} {dt.time()}: {int(order.shares)} shares @ ${order.target_price:.2f} = ${proceeds:.2f} (Profit: ${profit:.2f})")
                
                executed_orders.append(order)
        
        # Remove executed orders
        for order in executed_orders:
            self.portfolio.pending_sell_orders.remove(order)
    
    def run_backtest(self, start_date: str = "2025-01-01", end_date: str = None):
        """Run the backtest"""
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        print("=" * 80)
        print(f"🚀 {self.ticker} TRADING STRATEGY BACKTEST")
        print("=" * 80)
        print(f"Ticker: {self.ticker}")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Daily Investment: ${self.daily_investment:,.2f}")
        print(f"Data Interval: {self.data_interval}")
        print(f"{self.filter_ticker} 50 DMA Filter: {'ENABLED' if self.use_nasdaq_filter else 'DISABLED'}")
        print(f"Period: {start_date} to {end_date}")
        print("=" * 80)
        print()
        
        # Download filter ticker data for market filter
        if self.use_nasdaq_filter:
            self.filter_data = self.download_nasdaq_data(start_date, end_date)
            print()
        
        # Download stock data
        df = self.download_data(start_date, end_date)
        print()
        
        # Run simulation
        print("🔄 Running simulation...")
        print()
        
        for idx, (timestamp, row) in enumerate(df.iterrows()):
            current_price = row['Close']
            high_price = row['High']
            
            # Skip if not market hours
            if not self.is_market_open_time(timestamp):
                continue
            
            # Check and execute buy orders (at 10 AM)
            if self.should_buy(timestamp):
                self.execute_buy(timestamp, current_price)
            
            # Check and execute sell orders
            self.check_sell_orders(timestamp, high_price)
            
            # Record daily portfolio value (end of day snapshot)
            # For intraday data, check near market close (3:30 PM or later)
            # For daily data, record at end of each day
            should_record = False
            if self.data_interval == "1d":
                should_record = True
            elif timestamp.time() >= time(15, 30):  # Near market close for intraday
                should_record = True
            
            if should_record:
                date_key = timestamp.date().strftime("%Y-%m-%d")
                if date_key not in self.portfolio.daily_values:
                    portfolio_value = self.portfolio.total_value(current_price)
                    self.portfolio.daily_values[date_key] = portfolio_value
        
        print()
        print("=" * 80)
        print("✅ Backtest Complete!")
        print("=" * 80)
        
        # Calculate final results
        self.calculate_results(df)
    
    def calculate_results(self, df: pd.DataFrame):
        """Calculate and display backtest results"""
        final_price = df['Close'].iloc[-1]
        final_value = self.portfolio.total_value(final_price)
        total_return = final_value - self.initial_capital
        return_pct = (total_return / self.initial_capital) * 100
        
        # Calculate buy-and-hold comparison
        first_price = df['Close'].iloc[0]
        buy_and_hold_shares = self.initial_capital / first_price
        buy_and_hold_value = buy_and_hold_shares * final_price
        buy_and_hold_return = buy_and_hold_value - self.initial_capital
        buy_and_hold_return_pct = (buy_and_hold_return / self.initial_capital) * 100
        
        # Count trades
        buy_trades = [t for t in self.portfolio.trade_history if t.trade_type == 'BUY']
        sell_trades = [t for t in self.portfolio.trade_history if t.trade_type == 'SELL']
        
        # Calculate monthly performance
        monthly_performance = self.calculate_monthly_performance(df)
        
        print()
        print("📊 FINAL RESULTS")
        print("-" * 80)
        print(f"Initial Capital:        ${self.initial_capital:,.2f}")
        print(f"Final Portfolio Value:  ${final_value:,.2f}")
        print(f"Total Return:           ${total_return:,.2f} ({return_pct:+.2f}%)")
        print(f"Cash:                   ${self.portfolio.cash:,.2f}")
        print(f"Shares Held:            {int(self.portfolio.shares_held)}")
        print(f"Shares Value:           ${self.portfolio.shares_held * final_price:,.2f}")
        print(f"Pending Sell Orders:    {len(self.portfolio.pending_sell_orders)}")
        print()
        print("🔄 BUY-AND-HOLD COMPARISON")
        print("-" * 80)
        print(f"First Day Price:        ${first_price:.2f}")
        print(f"Last Day Price:         ${final_price:.2f}")
        print(f"Buy-and-Hold Shares:    {buy_and_hold_shares:.2f}")
        print(f"Buy-and-Hold Value:     ${buy_and_hold_value:,.2f}")
        print(f"Buy-and-Hold Return:    ${buy_and_hold_return:,.2f} ({buy_and_hold_return_pct:+.2f}%)")
        print(f"Strategy vs Buy-Hold:   ${total_return - buy_and_hold_return:,.2f} ({return_pct - buy_and_hold_return_pct:+.2f}% difference)")
        print()
        print(f"Total Buy Trades:       {len(buy_trades)}")
        print(f"Skipped Buys (no cash): {self.portfolio.skipped_buys_no_cash}")
        if self.use_nasdaq_filter:
            print(f"Skipped Buys ({self.filter_ticker}<50DMA): {self.portfolio.skipped_buys_market_condition}")
        print(f"Total Sell Trades:      {len(sell_trades)}")
        print()
        
        # Monthly performance
        print("📈 MONTHLY PERFORMANCE")
        print("-" * 80)
        print(f"{'Month':<15} {'Start Value':<15} {'End Value':<15} {'Return':<15} {'Return %':<10}")
        print("-" * 80)
        
        for month_data in monthly_performance:
            month = month_data['month']
            start_val = month_data['start_value']
            end_val = month_data['end_value']
            ret = month_data['return']
            ret_pct = month_data['return_pct']
            
            print(f"{month:<15} ${start_val:>12,.2f} ${end_val:>12,.2f} ${ret:>12,.2f} {ret_pct:>8.2f}%")
        
        print("-" * 80)
        print()
        
        # Trade statistics
        if sell_trades:
            profits = [(t.price - self.find_buy_price_for_sell(t)) * t.shares for t in sell_trades]
            avg_profit = np.mean(profits)
            total_profit = sum(profits)
            winning_trades = len([p for p in profits if p > 0])
            
            print("💹 TRADE STATISTICS")
            print("-" * 80)
            print(f"Average Profit per Sell: ${avg_profit:.2f}")
            print(f"Total Realized Profit:   ${total_profit:.2f}")
            print(f"Winning Trades:          {winning_trades}/{len(sell_trades)} ({100*winning_trades/len(sell_trades):.1f}%)")
            print()
        
        # Pending orders summary
        if self.portfolio.pending_sell_orders:
            print("📋 PENDING SELL ORDERS")
            print("-" * 80)
            total_pending_shares = sum(order.shares for order in self.portfolio.pending_sell_orders)
            avg_target = np.mean([order.target_price for order in self.portfolio.pending_sell_orders])
            print(f"Total Pending Orders:    {len(self.portfolio.pending_sell_orders)}")
            print(f"Total Pending Shares:    {int(total_pending_shares)}")
            print(f"Average Target Price:    ${avg_target:.2f}")
            print(f"Current Price:           ${final_price:.2f}")
            print()
    
    def find_buy_price_for_sell(self, sell_trade: Trade) -> float:
        """Find the original buy price for a sell trade"""
        # Look backwards in trade history to find the corresponding buy
        for trade in reversed(self.portfolio.trade_history):
            if trade.trade_type == 'BUY' and trade.date <= sell_trade.date:
                return trade.price
        return 0.0
    
    def calculate_monthly_performance(self, df: pd.DataFrame) -> List[Dict]:
        """Calculate performance for each month"""
        if not self.portfolio.daily_values:
            return []
        
        # Convert daily values to DataFrame
        dates = sorted(self.portfolio.daily_values.keys())
        values = [self.portfolio.daily_values[d] for d in dates]
        
        df_values = pd.DataFrame({
            'date': pd.to_datetime(dates),
            'value': values
        })
        df_values.set_index('date', inplace=True)
        
        # Group by month
        monthly_groups = df_values.groupby(pd.Grouper(freq='M'))
        
        monthly_performance = []
        prev_end_value = self.initial_capital
        
        for month_end, group in monthly_groups:
            if len(group) == 0:
                continue
            
            start_value = prev_end_value
            end_value = group['value'].iloc[-1]
            ret = end_value - start_value
            ret_pct = (ret / start_value) * 100 if start_value > 0 else 0
            
            monthly_performance.append({
                'month': month_end.strftime('%Y-%m'),
                'start_value': start_value,
                'end_value': end_value,
                'return': ret,
                'return_pct': ret_pct
            })
            
            prev_end_value = end_value
        
        return monthly_performance
    
    def export_trades(self, filename: str = "tqqq_trades.csv"):
        """Export trade history to CSV"""
        trades_data = []
        for trade in self.portfolio.trade_history:
            trades_data.append({
                'Date': trade.date,
                'Type': trade.trade_type,
                'Shares': trade.shares,
                'Price': trade.price,
                'Amount': trade.amount
            })
        
        df_trades = pd.DataFrame(trades_data)
        df_trades.to_csv(filename, index=False)
        print(f"✅ Trades exported to {filename}")


def main():
    """Main execution"""
    import sys
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Stock Trading Strategy Backtester',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Default: TQQQ with QQQ filter
  python tqqq_backtest.py
  
  # Custom ticker with default filter (QQQ)
  python tqqq_backtest.py --ticker SOXL
  
  # Custom ticker and custom filter
  python tqqq_backtest.py --ticker SOXL --filter SOX
  
  # Disable market filter
  python tqqq_backtest.py --ticker TQQQ --no-filter
        """
    )
    parser.add_argument(
        '--ticker', '-t',
        type=str,
        default='TQQQ',
        help='Stock ticker to backtest (default: TQQQ)'
    )
    parser.add_argument(
        '--filter', '-f',
        type=str,
        default='QQQ',
        dest='filter_ticker',
        help='Ticker to use for 50 DMA market filter (default: QQQ)'
    )
    parser.add_argument(
        '--no-filter',
        action='store_true',
        help='Disable the 50 DMA market filter'
    )
    parser.add_argument(
        '--start-date',
        type=str,
        default='2025-01-01',
        help='Start date for backtest (YYYY-MM-DD) (default: 2025-01-01)'
    )
    parser.add_argument(
        '--end-date',
        type=str,
        default=None,
        help='End date for backtest (YYYY-MM-DD) (default: today)'
    )
    parser.add_argument(
        '--capital',
        type=float,
        default=20000,
        help='Initial capital (default: 20000)'
    )
    parser.add_argument(
        '--investment',
        type=float,
        default=2000,
        help='Daily investment amount (default: 2000)'
    )
    
    args = parser.parse_args()
    
    # Determine appropriate interval based on date range
    start_date = args.start_date
    end_date = args.end_date
    
    # Calculate days from start to now/end
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.now()
    days_diff = (end_dt - start_dt).days
    
    # Choose best interval based on days
    if days_diff <= 60:
        interval = "5m"
        print("ℹ️  Using 5-minute intervals (within 60-day limit)")
    elif days_diff <= 730:
        interval = "1h"
        print("ℹ️  Using 1-hour intervals (date range exceeds 5-minute data limit)")
    else:
        interval = "1d"
        print("ℹ️  Using daily intervals (date range exceeds intraday data limits)")
    
    print()
    
    # Initialize backtester
    backtester = TQQQBacktester(
        initial_capital=args.capital,
        daily_investment=args.investment,
        data_interval=interval,
        use_nasdaq_filter=not args.no_filter,
        ticker=args.ticker,
        filter_ticker=args.filter_ticker
    )
    
    # Run backtest
    backtester.run_backtest(
        start_date=start_date,
        end_date=end_date
    )
    
    # Export trades
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ticker_safe = args.ticker.lower().replace('/', '_')
    export_path = os.path.join(script_dir, f"{ticker_safe}_trades.csv")
    backtester.export_trades(export_path)
    
    print()
    print("=" * 80)
    print("🎉 Backtesting Complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
