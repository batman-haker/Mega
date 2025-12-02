"""Simple cache test with verbose output"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / 'stockanalyzer'))

from collectors.stock_collector import get_stock_data

print("=== TEST 1: First load ===")
data1 = get_stock_data('AAPL', period='3mo', use_cache=True)
print(f"From cache: {data1['from_cache']}")
print(f"Score: {data1['overall_score']}")

print("\n=== TEST 2: Second load (should be cached) ===")
data2 = get_stock_data('AAPL', period='3mo', use_cache=True)
print(f"From cache: {data2['from_cache']}")
print(f"Score: {data2['overall_score']}")
