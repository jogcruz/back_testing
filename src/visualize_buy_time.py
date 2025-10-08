#!/usr/bin/env python3
"""
Visualize buy time optimization results
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read results
df = pd.read_csv('buy_time_optimization_results.csv')

# Create figure with multiple subplots
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('TQQQ Buy Time Optimization Analysis', fontsize=16, fontweight='bold')

# 1. Returns by Buy Time (Bar Chart)
ax1 = axes[0, 0]
colors = ['green' if x >= df['return_pct'].median() else 'red' for x in df['return_pct']]
colors[df['return_pct'].idxmax()] = 'darkgreen'  # Highlight best
bars = ax1.bar(df['buy_time'], df['return_pct'], color=colors, alpha=0.7, edgecolor='black')

# Add value labels on bars
for i, (bar, val) in enumerate(zip(bars, df['return_pct'])):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
            f'{val:.2f}%', ha='center', va='bottom', fontsize=8)

ax1.set_xlabel('Buy Time', fontweight='bold')
ax1.set_ylabel('Return (%)', fontweight='bold')
ax1.set_title('Returns by Buy Time', fontsize=12, fontweight='bold')
ax1.axhline(y=df['return_pct'].mean(), color='blue', linestyle='--', 
           linewidth=2, label=f'Average: {df["return_pct"].mean():.2f}%')
ax1.legend()
ax1.grid(True, alpha=0.3, axis='y')
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')

# 2. Number of Trades by Time
ax2 = axes[0, 1]
x = np.arange(len(df))
width = 0.35
bars1 = ax2.bar(x - width/2, df['buy_trades'], width, label='Buy Trades', 
               color='#2E86AB', alpha=0.8)
bars2 = ax2.bar(x + width/2, df['sell_trades'], width, label='Sell Trades', 
               color='#F18F01', alpha=0.8)

ax2.set_xlabel('Buy Time', fontweight='bold')
ax2.set_ylabel('Number of Trades', fontweight='bold')
ax2.set_title('Trade Volume by Buy Time', fontsize=12, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(df['buy_time'])
ax2.legend()
ax2.grid(True, alpha=0.3, axis='y')
plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')

# 3. Return Distribution (Line Plot)
ax3 = axes[1, 0]
ax3.plot(df['buy_time'], df['return_pct'], marker='o', linewidth=2, 
        markersize=8, color='#2E86AB')

# Highlight best and worst
best_idx = df['return_pct'].idxmax()
worst_idx = df['return_pct'].idxmin()
ax3.scatter(df.loc[best_idx, 'buy_time'], df.loc[best_idx, 'return_pct'], 
           color='green', s=200, zorder=5, marker='*', label='Best')
ax3.scatter(df.loc[worst_idx, 'buy_time'], df.loc[worst_idx, 'return_pct'], 
           color='red', s=200, zorder=5, marker='v', label='Worst')

ax3.set_xlabel('Buy Time', fontweight='bold')
ax3.set_ylabel('Return (%)', fontweight='bold')
ax3.set_title('Return Progression Throughout Day', fontsize=12, fontweight='bold')
ax3.axhline(y=13.26, color='orange', linestyle='--', linewidth=2, 
           label='Original (10:00 AM): 13.26%')
ax3.legend()
ax3.grid(True, alpha=0.3)
plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')

# 4. Time Periods Comparison
ax4 = axes[1, 1]

# Define time periods
morning = df[df['buy_hour'] < 12]
afternoon = df[df['buy_hour'] >= 12]

# Create comparison
periods = ['Morning\n(9:30-11:30)', 'Afternoon\n(12:00-15:30)']
avg_returns = [morning['return_pct'].mean(), afternoon['return_pct'].mean()]
colors_period = ['#A23B72', '#06A77D']

bars = ax4.bar(periods, avg_returns, color=colors_period, alpha=0.7, edgecolor='black')

# Add value labels
for bar, val in zip(bars, avg_returns):
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height,
            f'{val:.2f}%', ha='center', va='bottom', fontsize=12, fontweight='bold')

ax4.set_ylabel('Average Return (%)', fontweight='bold')
ax4.set_title('Morning vs Afternoon Performance', fontsize=12, fontweight='bold')
ax4.set_ylim([13, 14])
ax4.grid(True, alpha=0.3, axis='y')

# Add statistics text
best_time = df.loc[df['return_pct'].idxmax(), 'buy_time']
best_return = df['return_pct'].max()
worst_time = df.loc[df['return_pct'].idxmin(), 'buy_time']
worst_return = df['return_pct'].min()
original_return = df[df['buy_time'] == '10:00']['return_pct'].values[0]

stats_text = f"""
Key Findings:
• Best: {best_time} ({best_return:.2f}%)
• Worst: {worst_time} ({worst_return:.2f}%)
• Original 10:00 AM: {original_return:.2f}%
• Improvement: +{best_return - original_return:.2f}%
"""

fig.text(0.02, 0.02, stats_text, fontsize=10, family='monospace',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig('buy_time_optimization_chart.png', dpi=300, bbox_inches='tight')
print("✅ Chart saved to: buy_time_optimization_chart.png")

plt.show()
