#!/usr/bin/env python3
"""
Visualization script for TQQQ backtesting results

This script creates charts and visualizations from the backtest results to help
analyze the trading strategy performance.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
from tqqq_backtest import TQQQBacktester
import warnings
warnings.filterwarnings('ignore')


def run_and_visualize():
    """Run backtest and create visualizations"""
    # Determine appropriate interval
    start_date = "2025-01-01"
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.now()
    days_diff = (end_dt - start_dt).days
    
    if days_diff <= 60:
        interval = "5m"
    elif days_diff <= 730:
        interval = "1h"
    else:
        interval = "1d"
    
    print(f"Running backtest with {interval} interval...")
    print()
    
    # Run backtest
    backtester = TQQQBacktester(
        initial_capital=20000,
        daily_investment=2000,
        data_interval=interval
    )
    
    backtester.run_backtest(start_date=start_date, end_date=None)
    
    # Create visualizations
    print("\n📊 Creating visualizations...")
    create_visualizations(backtester)
    print("✅ Visualizations created!")


def create_visualizations(backtester: TQQQBacktester):
    """Create all visualization charts"""
    # Set style
    plt.style.use('seaborn-v0_8-darkgrid')
    
    # Create figure with subplots
    fig = plt.figure(figsize=(16, 12))
    
    # 1. Portfolio Value Over Time
    ax1 = plt.subplot(3, 2, 1)
    plot_portfolio_value(backtester, ax1)
    
    # 2. Monthly Returns
    ax2 = plt.subplot(3, 2, 2)
    plot_monthly_returns(backtester, ax2)
    
    # 3. Trade Distribution
    ax3 = plt.subplot(3, 2, 3)
    plot_trade_distribution(backtester, ax3)
    
    # 4. Cumulative Profit
    ax4 = plt.subplot(3, 2, 4)
    plot_cumulative_profit(backtester, ax4)
    
    # 5. Cash vs Shares Value
    ax5 = plt.subplot(3, 2, 5)
    plot_cash_vs_shares(backtester, ax5)
    
    # 6. Profit per Trade
    ax6 = plt.subplot(3, 2, 6)
    plot_profit_histogram(backtester, ax6)
    
    plt.tight_layout()
    plt.savefig('tqqq_backtest_analysis.png', dpi=300, bbox_inches='tight')
    print(f"   Saved: tqqq_backtest_analysis.png")


def plot_portfolio_value(backtester: TQQQBacktester, ax):
    """Plot portfolio value over time"""
    dates = sorted(backtester.portfolio.daily_values.keys())
    values = [backtester.portfolio.daily_values[d] for d in dates]
    
    dates_dt = pd.to_datetime(dates)
    
    ax.plot(dates_dt, values, linewidth=2, color='#2E86AB', label='Portfolio Value')
    ax.axhline(y=backtester.initial_capital, color='red', linestyle='--', 
               linewidth=1.5, label='Initial Capital')
    
    ax.set_title('Portfolio Value Over Time', fontsize=14, fontweight='bold')
    ax.set_xlabel('Date')
    ax.set_ylabel('Portfolio Value ($)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Add value labels
    ax.text(dates_dt[0], values[0], f'${values[0]:,.0f}', 
            fontsize=9, ha='left', va='bottom')
    ax.text(dates_dt[-1], values[-1], f'${values[-1]:,.0f}', 
            fontsize=9, ha='right', va='bottom')


def plot_monthly_returns(backtester: TQQQBacktester, ax):
    """Plot monthly returns"""
    monthly_perf = backtester.calculate_monthly_performance(pd.DataFrame())
    
    if not monthly_perf:
        return
    
    months = [m['month'] for m in monthly_perf]
    returns = [m['return_pct'] for m in monthly_perf]
    
    colors = ['green' if r >= 0 else 'red' for r in returns]
    
    ax.bar(months, returns, color=colors, alpha=0.7, edgecolor='black')
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    
    ax.set_title('Monthly Returns (%)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Month')
    ax.set_ylabel('Return (%)')
    ax.grid(True, alpha=0.3, axis='y')
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')


def plot_trade_distribution(backtester: TQQQBacktester, ax):
    """Plot trade type distribution"""
    buy_trades = len([t for t in backtester.portfolio.trade_history if t.trade_type == 'BUY'])
    sell_trades = len([t for t in backtester.portfolio.trade_history if t.trade_type == 'SELL'])
    
    sizes = [buy_trades, sell_trades]
    labels = [f'Buy Trades\n({buy_trades})', f'Sell Trades\n({sell_trades})']
    colors = ['#A23B72', '#2E86AB']
    
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                        startangle=90, textprops={'fontsize': 11})
    
    ax.set_title('Trade Distribution', fontsize=14, fontweight='bold')


def plot_cumulative_profit(backtester: TQQQBacktester, ax):
    """Plot cumulative profit over time"""
    sell_trades = [t for t in backtester.portfolio.trade_history if t.trade_type == 'SELL']
    
    if not sell_trades:
        return
    
    dates = [t.date for t in sell_trades]
    
    # Calculate profit for each sell
    cumulative_profit = []
    total_profit = 0
    
    for trade in sell_trades:
        # Find corresponding buy price (simplified)
        buy_price = None
        for bt in reversed(backtester.portfolio.trade_history):
            if bt.trade_type == 'BUY' and bt.date <= trade.date:
                buy_price = bt.price
                break
        
        if buy_price:
            profit = (trade.price - buy_price) * trade.shares
            total_profit += profit
            cumulative_profit.append(total_profit)
        else:
            cumulative_profit.append(total_profit)
    
    ax.plot(dates, cumulative_profit, linewidth=2, color='#F18F01')
    ax.fill_between(dates, 0, cumulative_profit, alpha=0.3, color='#F18F01')
    
    ax.set_title('Cumulative Realized Profit', fontsize=14, fontweight='bold')
    ax.set_xlabel('Date')
    ax.set_ylabel('Cumulative Profit ($)')
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')


def plot_cash_vs_shares(backtester: TQQQBacktester, ax):
    """Plot cash vs shares value over time"""
    dates = sorted(backtester.portfolio.daily_values.keys())
    
    # We need to track cash and shares separately over time
    # For simplicity, we'll show final state
    final_cash = backtester.portfolio.cash
    final_shares_value = backtester.portfolio.total_value(100) - final_cash  # Approximate
    
    # Get stock price from last trade
    if backtester.portfolio.trade_history:
        last_price = backtester.portfolio.trade_history[-1].price
        final_shares_value = backtester.portfolio.shares_held * last_price
    
    sizes = [final_cash, final_shares_value]
    labels = [f'Cash\n${final_cash:,.0f}', f'Shares\n${final_shares_value:,.0f}']
    colors = ['#06A77D', '#2E86AB']
    
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                        startangle=90, textprops={'fontsize': 11})
    
    ax.set_title('Current Portfolio Allocation', fontsize=14, fontweight='bold')


def plot_profit_histogram(backtester: TQQQBacktester, ax):
    """Plot histogram of profit per trade"""
    sell_trades = [t for t in backtester.portfolio.trade_history if t.trade_type == 'SELL']
    
    if not sell_trades:
        return
    
    profits = []
    for trade in sell_trades:
        # Find corresponding buy price
        buy_price = None
        for bt in reversed(backtester.portfolio.trade_history):
            if bt.trade_type == 'BUY' and bt.date <= trade.date:
                buy_price = bt.price
                break
        
        if buy_price:
            profit = (trade.price - buy_price) * trade.shares
            profits.append(profit)
    
    ax.hist(profits, bins=30, color='#2E86AB', alpha=0.7, edgecolor='black')
    ax.axvline(x=np.mean(profits), color='red', linestyle='--', 
               linewidth=2, label=f'Mean: ${np.mean(profits):.2f}')
    
    ax.set_title('Profit Distribution per Sell Trade', fontsize=14, fontweight='bold')
    ax.set_xlabel('Profit per Trade ($)')
    ax.set_ylabel('Frequency')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')


def main():
    """Main execution"""
    run_and_visualize()


if __name__ == "__main__":
    main()
