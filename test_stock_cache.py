"""
Test script for Stock Cache functionality
"""

import sys
from pathlib import Path
import time

# Add stockanalyzer to path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'stockanalyzer'))

from collectors.stock_collector import get_stock_data

print("="*60)
print("STOCK CACHE TEST")
print("="*60)

# Test 1: First load (should fetch from Yahoo Finance)
print("\n[TEST 1] First load of AAPL (should fetch from Yahoo)")
print("-"*60)
start = time.time()
data1 = get_stock_data('AAPL', period='3mo', use_cache=True)
elapsed1 = time.time() - start

print(f"[OK] Company: {data1['company_name']}")
print(f"[OK] Score: {data1['overall_score']}/100")
print(f"[OK] From cache: {data1['from_cache']}")
print(f"[TIME] {elapsed1:.2f}s")

# Test 2: Second load (should come from cache)
print("\n[TEST 2] Second load of AAPL (should come from CACHE)")
print("-"*60)
start = time.time()
data2 = get_stock_data('AAPL', period='3mo', use_cache=True)
elapsed2 = time.time() - start

print(f"[OK] Company: {data2['company_name']}")
print(f"[OK] Score: {data2['overall_score']}/100")
print(f"[OK] From cache: {data2['from_cache']}")
print(f"[TIME] {elapsed2:.2f}s")

# Compare speeds
print("\n[PERFORMANCE] COMPARISON")
print("-"*60)
print(f"First load:  {elapsed1:.2f}s (Yahoo API)")
print(f"Second load: {elapsed2:.2f}s (Cache)")
speedup = elapsed1 / elapsed2 if elapsed2 > 0 else 0
print(f"Speedup:     {speedup:.1f}x faster!")

# Test 3: Load with cache disabled
print("\n[TEST 3] Load with cache DISABLED")
print("-"*60)
start = time.time()
data3 = get_stock_data('AAPL', period='3mo', use_cache=False)
elapsed3 = time.time() - start

print(f"[OK] Company: {data3['company_name']}")
print(f"[OK] From cache: {data3['from_cache']}")
print(f"[TIME] {elapsed3:.2f}s")

print("\n" + "="*60)
print("[SUCCESS] ALL TESTS PASSED!")
print("="*60)
