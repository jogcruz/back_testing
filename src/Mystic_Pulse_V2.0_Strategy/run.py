#!/usr/bin/env python3
"""
Quick Start Script for Mystic Pulse V2.0 Strategy

This script provides an easy way to run the backtest with different configurations.
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from backtest import run_backtest
except ImportError:
    print("\n❌ Error: Required packages not installed!")
    print("\nPlease install dependencies first:")
    print("  1. Create virtual environment: python3 -m venv venv")
    print("  2. Activate it: source venv/bin/activate")
    print("  3. Install packages: pip install -r ../../requirements.txt")
    print("\nSee INSTALL.md for detailed instructions.")
    sys.exit(1)


def main():
    """Main function to run backtest scenarios."""
    print("\n" + "="*80)
    print(" Mystic Pulse V2.0 Strategy - Quick Start")
    print("="*80)
    print("\nSelect a backtest to run:")
    print("\n  Leveraged ETFs:")
    print("    1. TQQQ (3x Nasdaq)")
    print("    2. SOXL (3x Semiconductors)")
    print("\n  Major Indices:")
    print("    3. QQQ (Nasdaq)")
    print("    4. SPY (S&P 500)")
    print("\n  Cryptocurrencies:")
    print("    5. BTC-USD (Bitcoin)")
    print("    6. ETH-USD (Ethereum)")
    print("    7. SOL-USD (Solana)")
    print("\n  Other:")
    print("    8. Custom ticker")
    print("    0. Exit")
    print("="*80)
    
    try:
        choice = input("\nEnter your choice (0-8): ").strip()
        
        if choice == '0':
            print("Exiting...")
            return
        
        # Common parameters
        start_date = '2020-01-01'
        initial_cash = 10000.0
        commission = 0.01  # 1%
        slippage = 0.0001  # 0.01%
        
        # Select ticker based on choice
        if choice == '1':
            ticker = 'TQQQ'
        elif choice == '2':
            ticker = 'SOXL'
        elif choice == '3':
            ticker = 'QQQ'
        elif choice == '4':
            ticker = 'SPY'
        elif choice == '5':
            ticker = 'BTC-USD'
            print("\n💡 Tip: Crypto markets are 24/7, data available from ~2014")
        elif choice == '6':
            ticker = 'ETH-USD'
            print("\n💡 Tip: Ethereum data available from ~2017")
        elif choice == '7':
            ticker = 'SOL-USD'
            print("\n💡 Tip: Solana data available from ~2020")
        elif choice == '8':
            ticker = input("Enter ticker symbol (e.g., AAPL, BTC-USD): ").strip().upper()
            if not ticker:
                print("Invalid ticker!")
                return
            # Check if it's crypto format
            if '-USD' in ticker or '-BTC' in ticker or '-ETH' in ticker:
                print("\n💡 Detected cryptocurrency ticker")
        else:
            print("Invalid choice!")
            return
        
        # Optional: customize parameters
        print(f"\nSelected ticker: {ticker}")
        customize = input("Customize parameters? (y/n): ").strip().lower()
        
        if customize == 'y':
            start_input = input(f"Start date (default: {start_date}): ").strip()
            if start_input:
                start_date = start_input
            
            cash_input = input(f"Initial cash (default: ${initial_cash:,.2f}): ").strip()
            if cash_input:
                try:
                    initial_cash = float(cash_input)
                except ValueError:
                    print("Invalid cash amount, using default.")
        
        # Run backtest
        print("\n" + "="*80)
        cerebro = run_backtest(
            ticker=ticker,
            start_date=start_date,
            initial_cash=initial_cash,
            commission=commission,
            slippage_perc=slippage
        )
        
        if cerebro:
            print("\n✅ Backtest completed successfully!")
            
            # Ask if user wants to plot results
            plot_choice = input("\nWould you like to plot the results? (y/n): ").strip().lower()
            if plot_choice == 'y':
                try:
                    print("\nGenerating plot...")
                    cerebro.plot(style='candlestick')
                    print("Plot window opened!")
                except Exception as e:
                    print(f"Could not generate plot: {str(e)}")
        else:
            print("\n❌ Backtest failed!")
            
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

