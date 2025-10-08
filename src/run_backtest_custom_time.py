#!/usr/bin/env python3
"""
Run stock backtest with custom buy time, date range, price increment, ticker, and filter

Usage:
    # Basic usage (Jan 1, 2025 to today, $1 increment, TQQQ/QQQ)
    python run_backtest_custom_time.py 14 0
    
    # With custom ticker and filter
    python run_backtest_custom_time.py 14 0 --ticker SOXL --filter SOX
    
    # With custom date range
    python run_backtest_custom_time.py 14 0 2025-01-01 2025-10-05
    
    # With custom price increment ($0.50)
    python run_backtest_custom_time.py 14 0 2025-01-01 2025-10-05 0.5
    
    # Complete example with all options
    python run_backtest_custom_time.py 14 0 2025-01-01 2025-10-05 0.5 --ticker SOXL --filter SOX
"""

import sys
import argparse
from datetime import datetime, time, timedelta
from tqqq_backtest import TQQQBacktester
import warnings
warnings.filterwarnings('ignore')


class CustomTimeTQQQBacktester(TQQQBacktester):
    """Backtester with customizable buy time"""
    
    def __init__(self, initial_capital: float = 20000, daily_investment: float = 2000,
                 data_interval: str = "1h", use_nasdaq_filter: bool = True,
                 buy_hour: int = 10, buy_minute: int = 0, price_increment: float = 1.0,
                 ticker: str = "TQQQ", filter_ticker: str = "QQQ"):
        super().__init__(initial_capital, daily_investment, data_interval, use_nasdaq_filter, 
                         price_increment, ticker, filter_ticker)
        self.buy_hour = buy_hour
        self.buy_minute = buy_minute
        
    def should_buy(self, dt: datetime) -> bool:
        """Check if we should execute buy at this timestamp (custom time)"""
        date_key = dt.date()
        
        # If already bought today, skip
        if date_key in self.buy_executed_today:
            return False
        
        # For daily data, buy at market open
        if self.data_interval == "1d":
            return True
        
        # For intraday data, check if it's the specified buy time
        market_time = dt.time()
        
        # Create a window around the buy time (±30 minutes for hourly data)
        if self.data_interval == "1h":
            # For hourly data, accept if within 1 hour window
            buy_time_start = time(max(self.buy_hour - 1, 9), 30)  # Start 1 hour before or market open
            buy_time_end = time(min(self.buy_hour + 1, 16), 0)   # End 1 hour after or market close
        else:
            # For 5-minute data, use tighter window
            buy_time_start = time(self.buy_hour, self.buy_minute)
            minute_end = self.buy_minute + 30
            hour_end = self.buy_hour
            if minute_end >= 60:
                hour_end += 1
                minute_end -= 60
            buy_time_end = time(hour_end, minute_end)
        
        if buy_time_start <= market_time < buy_time_end:
            return True
        
        return False


def main():
    """Main execution"""
    # Create argument parser
    parser = argparse.ArgumentParser(
        description='Run stock backtest with custom buy time',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Positional Arguments:
  hour                  Buy time hour (9-15, Eastern)
  minute                Buy time minute (0-59)
  start_date            Start date (YYYY-MM-DD) - optional, default: 2025-01-01
  end_date              End date (YYYY-MM-DD) - optional, default: today
  price_increment       Sell order increment ($) - optional, default: 1.0

Optional Arguments:
  --ticker, -t          Stock ticker (default: TQQQ)
  --filter, -f          Filter ticker for 50 DMA (default: QQQ)
  --no-filter           Disable 50 DMA filter

Examples:
  # Basic: TQQQ at 2:00 PM
  python run_backtest_custom_time.py 14 0

  # SOXL with SOX filter at 2:00 PM
  python run_backtest_custom_time.py 14 0 --ticker SOXL --filter SOX

  # With price increment
  python run_backtest_custom_time.py 14 0 0.5 --ticker SOXL --filter SOX

  # With date range and price increment
  python run_backtest_custom_time.py 14 0 2025-01-01 2025-10-05 0.5 --ticker UPRO --filter SPY

  # Without market filter
  python run_backtest_custom_time.py 10 0 --no-filter

Common optimal times:
  14 0   - Best performer (2:00 PM)
  12 0   - Second best (12:00 PM)
  11 30  - Third best (11:30 AM)
        """,
        usage='%(prog)s hour minute [start_date] [end_date] [price_increment] [--ticker TICKER] [--filter FILTER]'
    )
    
    parser.add_argument('hour', type=int, help='Buy time hour (9-15)')
    parser.add_argument('minute', type=int, help='Buy time minute (0-59)')
    parser.add_argument('positional_args', nargs='*', help='Optional: start_date, end_date, price_increment')
    parser.add_argument('--ticker', '-t', type=str, default='TQQQ', help='Stock ticker (default: TQQQ)')
    parser.add_argument('--filter', '-f', type=str, dest='filter_ticker', default='QQQ', 
                        help='Filter ticker for 50 DMA (default: QQQ)')
    parser.add_argument('--no-filter', action='store_true', help='Disable 50 DMA filter')
    
    args = parser.parse_args()
    
    buy_hour = args.hour
    buy_minute = args.minute
    
    if not (9 <= buy_hour <= 15):
        print("❌ Error: Hour must be between 9 (9 AM) and 15 (3 PM)")
        sys.exit(1)
    
    if not (0 <= buy_minute <= 59):
        print("❌ Error: Minute must be between 0 and 59")
        sys.exit(1)
    
    # Parse optional positional arguments (start_date, end_date, price_increment)
    start_date = "2025-01-01"  # Default
    end_date = None  # Default (today)
    price_increment = 1.0  # Default
    
    positional = args.positional_args
    
    # Parse positional arguments similar to old logic
    if len(positional) == 1:
        # One argument - could be price_increment or start_date
        arg = positional[0]
        try:
            price_increment = float(arg)
            if price_increment <= 0:
                print("❌ Error: Price increment must be a positive number")
                sys.exit(1)
        except ValueError:
            # Not a number, try as date
            start_date = arg
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                print(f"❌ Error: Invalid format: {arg}")
                print("   Expected: start_date (YYYY-MM-DD) or price_increment (number)")
                sys.exit(1)
    
    elif len(positional) >= 2:
        # Two or more arguments: start_date, end_date, [price_increment]
        start_date = positional[0]
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            print(f"❌ Error: Invalid start date format: {start_date}")
            print("   Use format: YYYY-MM-DD (e.g., 2025-01-01)")
            sys.exit(1)
        
        end_date = positional[1]
        try:
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            print(f"❌ Error: Invalid end date format: {end_date}")
            print("   Use format: YYYY-MM-DD (e.g., 2025-12-31)")
            sys.exit(1)
        
        if len(positional) >= 3:
            try:
                price_increment = float(positional[2])
                if price_increment <= 0:
                    print("❌ Error: Price increment must be a positive number")
                    sys.exit(1)
            except ValueError:
                print(f"❌ Error: Invalid price increment: {positional[2]}")
                print("   Must be a positive number (e.g., 0.5, 1.0, 2.0)")
                sys.exit(1)
    
    # Determine data interval based on date range
    
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.now()
    days_diff = (end_dt - start_dt).days
    
    if days_diff < 0:
        print("❌ Error: Start date must be before end date")
        sys.exit(1)
    
    if days_diff <= 60:
        interval = "5m"
        print(f"ℹ️  Using 5-minute intervals ({days_diff} days - within 60-day limit)")
    elif days_diff <= 730:
        interval = "1h"
        print(f"ℹ️  Using 1-hour intervals ({days_diff} days)")
    else:
        interval = "1d"
        print(f"ℹ️  Using daily intervals ({days_diff} days)")
    
    end_date_display = end_date if end_date else datetime.now().strftime("%Y-%m-%d")
    print(f"📊 Ticker: {args.ticker}")
    print(f"📅 Period: {start_date} to {end_date_display}")
    print(f"⏰ Buy Time: {buy_hour:02d}:{buy_minute:02d}")
    print(f"💵 Price Increment: ${price_increment:.2f}")
    if not args.no_filter:
        print(f"🔍 Market Filter: {args.filter_ticker} 50 DMA")
    else:
        print(f"🔍 Market Filter: DISABLED")
    print()
    
    # Create backtester with custom time
    backtester = CustomTimeTQQQBacktester(
        initial_capital=20000,
        daily_investment=2000,
        data_interval=interval,
        use_nasdaq_filter=not args.no_filter,
        buy_hour=buy_hour,
        buy_minute=buy_minute,
        price_increment=price_increment,
        ticker=args.ticker,
        filter_ticker=args.filter_ticker
    )
    
    # Run backtest
    backtester.run_backtest(
        start_date=start_date,
        end_date=end_date
    )
    
    # Export trades with custom filename
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ticker_safe = args.ticker.lower().replace('/', '_')
    export_path = os.path.join(script_dir, f"{ticker_safe}_trades_{buy_hour:02d}_{buy_minute:02d}.csv")
    backtester.export_trades(export_path)
    
    print()
    print("=" * 80)
    print("✅ Backtest Complete!")
    print(f"📊 Ticker: {args.ticker}")
    print(f"📅 Period: {start_date} to {end_date_display}")
    print(f"⏰ Buy Time Used: {buy_hour:02d}:{buy_minute:02d}")
    print(f"💵 Price Increment: ${price_increment:.2f}")
    if not args.no_filter:
        print(f"🔍 Market Filter: {args.filter_ticker} 50 DMA")
    else:
        print(f"🔍 Market Filter: DISABLED")
    print("=" * 80)


if __name__ == "__main__":
    main()
