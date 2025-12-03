"""
Mystic Pulse V2.0 Strategy Package

Python implementation of the Mystic Pulse V2.0 trading strategy
based on the Pine Script indicator by chervolino.

Author: Converted from Pine Script
License: Mozilla Public License 2.0
"""

from .strategy import MysticPulseV2Strategy, get_strategy_signals

__version__ = '2.0.0'
__author__ = 'chervolino (Pine Script), Python conversion'
__license__ = 'Mozilla Public License 2.0'

__all__ = [
    'MysticPulseV2Strategy',
    'get_strategy_signals',
]

