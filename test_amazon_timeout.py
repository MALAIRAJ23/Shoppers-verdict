#!/usr/bin/env python3
"""
Quick Amazon test with timeout protection
"""

import subprocess
import sys
import signal
import os

def test_amazon_with_timeout():
    print("🧪 Testing Amazon scraping with timeout protection...")
    
    # Create a simple test script
    test_script = '''
import sys
sys.path.append(".")
from scraper import scrape_data
import time

start = time.time()
try:
    result = scrape_data("https://www.amazon.in/dp/B0DGTTPPT2")
    elapsed = time.time() - start
    
    if result:
        print(f"SUCCESS in {elapsed:.1f}s:")
        print(f"  Title: {result.get('title', 'No title')[:50]}...")
        print(f"  Reviews: {len(result.get('reviews', []))}")
        print(f"  Has price history: {bool(result.get('price_history'))}")
    else:
        print(f"FAILED after {elapsed:.1f}s: No result returned")
        
except Exception as e:
    elapsed = time.time() - start
    print(f"ERROR after {elapsed:.1f}s: {e}")
'''
    
    # Write test script to file
    with open('temp_amazon_test.py', 'w') as f:
        f.write(test_script)
    
    try:
        # Run with 30 second timeout
        print("Running test (30s timeout)...")
        result = subprocess.run([
            sys.executable, 'temp_amazon_test.py'
        ], timeout=30, capture_output=True, text=True, cwd='.')
        
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("❌ Test timed out after 30 seconds - Amazon scraping is hanging")
        print("This suggests Amazon is blocking or the page is very slow to load")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        
    finally:
        # Clean up
        try:
            os.remove('temp_amazon_test.py')
        except:
            pass

if __name__ == '__main__':
    test_amazon_with_timeout()