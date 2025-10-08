#!/usr/bin/env python3
"""
TQQQ Buy Time Optimization

Tests different times of day for placing buy orders to find optimal entry timing.
Uses 30-minute intervals for buy times, but 5-minute data for sell execution accuracy.
"""

import pandas as pd
import numpy as np
from datetime import datetime, time, timedelta
from tqqq_backtest import TQQQBacktester
import warnings
warnings.filterwarnings('ignore')


class BuyTimeOptimizer:
    """Optimizer to find the best time of day for placing buy orders"""
    
    def __init__(self, initial_capital: float = 20000, daily_investment: float = 2000):
        self.initial_capital = initial_capital
        self.daily_investment = daily_investment
        self.results = []
        
    def test_buy_time(self, buy_hour: int, buy_minute: int, start_date: str, end_date: str):
        """Test a specific buy time and return results"""
        print(f"\n{'='*80}")
        print(f"Testing Buy Time: {buy_hour:02d}:{buy_minute:02d}")
        print(f"{'='*80}")
        
        # Create custom backtester with specific buy time
        backtester = CustomTimeBuyBacktester(
            initial_capital=self.initial_capital,
            daily_investment=self.daily_investment,
            data_interval="5m",  # Use 5-minute data for sell execution accuracy
            use_nasdaq_filter=True,
            buy_hour=buy_hour,
            buy_minute=buy_minute
        )
        
        try:
            # Run backtest
            backtester.run_backtest(start_date=start_date, end_date=end_date)
            
            # Get results
            final_price = backtester.final_price if hasattr(backtester, 'final_price') else 100
            final_value = backtester.portfolio.total_value(final_price)
            total_return = final_value - self.initial_capital
            return_pct = (total_return / self.initial_capital) * 100
            
            buy_trades = len([t for t in backtester.portfolio.trade_history if t.trade_type == 'BUY'])
            sell_trades = len([t for t in backtester.portfolio.trade_history if t.trade_type == 'SELL'])
            
            result = {
                'buy_time': f"{buy_hour:02d}:{buy_minute:02d}",
                'buy_hour': buy_hour,
                'buy_minute': buy_minute,
                'final_value': final_value,
                'total_return': total_return,
                'return_pct': return_pct,
                'buy_trades': buy_trades,
                'sell_trades': sell_trades,
                'skipped_cash': backtester.portfolio.skipped_buys_no_cash,
                'skipped_market': backtester.portfolio.skipped_buys_market_condition,
                'win_rate': (sell_trades / max(sell_trades, 1)) * 100 if sell_trades > 0 else 0
            }
            
            self.results.append(result)
            
            print(f"\n✅ Results for {buy_hour:02d}:{buy_minute:02d}")
            print(f"   Final Value: ${final_value:,.2f}")
            print(f"   Return: ${total_return:,.2f} ({return_pct:+.2f}%)")
            print(f"   Buy Trades: {buy_trades}")
            print(f"   Sell Trades: {sell_trades}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error testing {buy_hour:02d}:{buy_minute:02d}: {e}")
            return None
    
    def run_optimization(self, start_date: str = "2025-01-01", end_date: str = None):
        """Test all buy times in 30-minute intervals"""
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        print("="*80)
        print("🚀 TQQQ BUY TIME OPTIMIZATION")
        print("="*80)
        print(f"Testing Period: {start_date} to {end_date}")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Daily Investment: ${self.daily_investment:,.2f}")
        print(f"Data Interval: 5-minute (for accurate sell execution)")
        print(f"Buy Time Intervals: 30 minutes")
        print("="*80)
        
        # Test times: 9:30 AM to 3:30 PM in 30-minute intervals
        test_times = [
            (9, 30),   # Market open
            (10, 0),   # Standard time
            (10, 30),  # Mid-morning
            (11, 0),   # Late morning
            (11, 30),  # Pre-lunch
            (12, 0),   # Lunch
            (12, 30),  # Post-lunch
            (13, 0),   # Early afternoon (1:00 PM)
            (13, 30),  # Mid-afternoon (1:30 PM)
            (14, 0),   # Late afternoon (2:00 PM)
            (14, 30),  # (2:30 PM)
            (15, 0),   # (3:00 PM)
            (15, 30),  # Near close (3:30 PM)
        ]
        
        for hour, minute in test_times:
            self.test_buy_time(hour, minute, start_date, end_date)
        
        # Analyze results
        self.analyze_results()
    
    def analyze_results(self):
        """Analyze and display optimization results"""
        if not self.results:
            print("No results to analyze")
            return
        
        # Sort by return percentage
        sorted_results = sorted(self.results, key=lambda x: x['return_pct'], reverse=True)
        
        print("\n" + "="*80)
        print("📊 BUY TIME OPTIMIZATION RESULTS")
        print("="*80)
        print(f"\n{'Rank':<6} {'Buy Time':<10} {'Return':<15} {'Return %':<12} {'Buys':<8} {'Sells':<8}")
        print("-"*80)
        
        for i, result in enumerate(sorted_results, 1):
            print(f"{i:<6} {result['buy_time']:<10} ${result['total_return']:>12,.2f} "
                  f"{result['return_pct']:>10.2f}% {result['buy_trades']:>6} {result['sell_trades']:>6}")
        
        print("-"*80)
        
        # Best and worst
        best = sorted_results[0]
        worst = sorted_results[-1]
        
        print(f"\n🏆 BEST TIME: {best['buy_time']}")
        print(f"   Return: ${best['total_return']:,.2f} ({best['return_pct']:+.2f}%)")
        print(f"   Trades: {best['buy_trades']} buys, {best['sell_trades']} sells")
        
        print(f"\n❌ WORST TIME: {worst['buy_time']}")
        print(f"   Return: ${worst['total_return']:,.2f} ({worst['return_pct']:+.2f}%)")
        print(f"   Trades: {worst['buy_trades']} buys, {worst['sell_trades']} sells")
        
        print(f"\n📈 DIFFERENCE: ${best['total_return'] - worst['total_return']:,.2f} "
              f"({best['return_pct'] - worst['return_pct']:.2f} percentage points)")
        
        # Time of day analysis
        print(f"\n⏰ TIME OF DAY ANALYSIS")
        print("-"*80)
        
        # Morning (9:30-11:30)
        morning = [r for r in sorted_results if r['buy_hour'] < 12]
        # Afternoon (12:00-15:30)
        afternoon = [r for r in sorted_results if r['buy_hour'] >= 12]
        
        if morning:
            avg_morning = np.mean([r['return_pct'] for r in morning])
            print(f"Morning Average (9:30-11:30):  {avg_morning:.2f}%")
        
        if afternoon:
            avg_afternoon = np.mean([r['return_pct'] for r in afternoon])
            print(f"Afternoon Average (12:00-15:30): {avg_afternoon:.2f}%")
        
        # Export results
        self.export_results()
    
    def export_results(self):
        """Export results to CSV"""
        df = pd.DataFrame(self.results)
        df = df.sort_values('return_pct', ascending=False)
        filename = 'buy_time_optimization_results.csv'
        df.to_csv(filename, index=False)
        print(f"\n✅ Results exported to {filename}")


class CustomTimeBuyBacktester(TQQQBacktester):
    """Custom backtester that allows specifying exact buy time"""
    
    def __init__(self, initial_capital: float = 20000, daily_investment: float = 2000,
                 data_interval: str = "5m", use_nasdaq_filter: bool = True,
                 buy_hour: int = 10, buy_minute: int = 0):
        super().__init__(initial_capital, daily_investment, data_interval, use_nasdaq_filter)
        self.buy_hour = buy_hour
        self.buy_minute = buy_minute
        self.final_price = None
        
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
        
        # Allow a 5-minute window for the buy time
        buy_time_start = time(self.buy_hour, self.buy_minute)
        buy_time_end = time(self.buy_hour, self.buy_minute + 5) if self.buy_minute <= 55 else time(self.buy_hour + 1, 0)
        
        if buy_time_start <= market_time < buy_time_end:
            return True
        
        return False
    
    def run_backtest(self, start_date: str = "2025-01-01", end_date: str = None):
        """Run backtest with minimal output"""
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        # Download Nasdaq data for market filter
        if self.use_nasdaq_filter:
            self.nasdaq_data = self.download_nasdaq_data(start_date, end_date)
        
        # Download TQQQ data
        df = self.download_data(start_date, end_date)
        
        # Run simulation
        for idx, (timestamp, row) in enumerate(df.iterrows()):
            current_price = row['Close']
            high_price = row['High']
            
            # Skip if not market hours
            if not self.is_market_open_time(timestamp):
                continue
            
            # Check and execute buy orders
            if self.should_buy(timestamp):
                self.execute_buy(timestamp, current_price)
            
            # Check and execute sell orders
            self.check_sell_orders(timestamp, high_price)
            
            # Record daily portfolio value
            should_record = False
            if self.data_interval == "1d":
                should_record = True
            elif timestamp.time() >= time(15, 30):
                should_record = True
            
            if should_record:
                date_key = timestamp.date().strftime("%Y-%m-%d")
                if date_key not in self.portfolio.daily_values:
                    portfolio_value = self.portfolio.total_value(current_price)
                    self.portfolio.daily_values[date_key] = portfolio_value
        
        # Store final price for result calculation
        self.final_price = df['Close'].iloc[-1]


def main():
    """Main execution"""
    print("\n⏰ TQQQ Buy Time Optimization")
    print("Testing different times of day to find optimal entry point")
    print()
    
    # Check if we can use 5-minute data
    start_date = "2025-01-01"
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.now()
    days_diff = (end_dt - start_dt).days
    
    if days_diff > 60:
        print("⚠️  WARNING: Date range exceeds 5-minute data limit (60 days)")
        print("   Using most recent 60 days of data for optimization")
        print()
        start_date = (end_dt - timedelta(days=59)).strftime("%Y-%m-%d")
    
    # Create optimizer
    optimizer = BuyTimeOptimizer(
        initial_capital=20000,
        daily_investment=2000
    )
    
    # Run optimization
    optimizer.run_optimization(start_date=start_date, end_date=None)


if __name__ == "__main__":
    main()
