#!/usr/bin/env python3
"""
Test script to verify Shopper's Verdict application components
"""

def test_basic_imports():
    print("Testing basic imports...")
    try:
        import sys
        print(f"✓ Python version: {sys.version}")
        
        import flask
        print(f"✓ Flask version: {flask.__version__}")
        
        import sqlite3
        print("✓ SQLite available")
        
        import requests
        print("✓ Requests available")
        
        return True
    except Exception as e:
        print(f"✗ Basic imports failed: {e}")
        return False

def test_nlp_imports():
    print("\nTesting NLP imports...")
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        analyzer = SentimentIntensityAnalyzer()
        score = analyzer.polarity_scores("This is a great product!")
        print(f"✓ VADER Sentiment working: {score['compound']}")
        
        try:
            import spacy
            print("✓ spaCy available")
            try:
                nlp = spacy.load('en_core_web_sm')
                print("✓ spaCy English model loaded")
            except:
                print("⚠ spaCy English model not available, will use fallback")
        except:
            print("⚠ spaCy not available, will use fallback")
        
        import nltk
        print("✓ NLTK available")
        
        return True
    except Exception as e:
        print(f"✗ NLP imports failed: {e}")
        return False

def test_scraping_imports():
    print("\nTesting scraping imports...")
    try:
        from playwright.sync_api import sync_playwright
        print("✓ Playwright available")
        
        from bs4 import BeautifulSoup
        print("✓ BeautifulSoup available")
        
        return True
    except Exception as e:
        print(f"✗ Scraping imports failed: {e}")
        return False

def test_app_modules():
    print("\nTesting application modules...")
    try:
        from scraper import scrape_data, init_db
        print("✓ Scraper module imported")
        
        from analyzer import perform_analysis, get_nlp
        print("✓ Analyzer module imported")
        
        from app import app
        print("✓ Flask app imported")
        
        # Test routes
        with app.app_context():
            routes = []
            for rule in app.url_map.iter_rules():
                routes.append(f"{list(rule.methods)} {rule.rule}")
            print(f"✓ App has {len(routes)} routes:")
            for route in routes:
                print(f"   - {route}")
        
        return True
    except Exception as e:
        print(f"✗ App modules failed: {e}")
        return False

def test_database():
    print("\nTesting database functionality...")
    try:
        from scraper import init_db
        init_db()
        print("✓ Database initialized successfully")
        
        import sqlite3
        conn = sqlite3.connect('reviews_cache.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"✓ Database tables: {[table[0] for table in tables]}")
        conn.close()
        
        return True
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def test_sample_analysis():
    print("\nTesting sample analysis...")
    try:
        from analyzer import perform_analysis
        
        sample_reviews = [
            "Great product with excellent battery life and amazing camera quality!",
            "The build quality is poor and the screen is too dim",
            "Love the fast charging feature but the price is too high",
            "Battery drains quickly but overall performance is good"
        ]
        
        results = perform_analysis(sample_reviews)
        print(f"✓ Sample analysis completed")
        print(f"   Overall sentiment: {results.get('overall_sentiment', {})}")
        print(f"   Aspects found: {len(results.get('aspect_sentiments', {}))}")
        print(f"   Reviews processed: {results.get('meta', {}).get('reviews_used', 0)}")
        
        return True
    except Exception as e:
        print(f"✗ Sample analysis failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Shopper's Verdict - Component Test Suite")
    print("=" * 50)
    
    tests = [
        test_basic_imports,
        test_nlp_imports,
        test_scraping_imports,
        test_app_modules,
        test_database,
        test_sample_analysis
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Application is ready to use.")
    else:
        print(f"⚠ {total - passed} tests failed. Check the errors above.")
    
    print("\nTo run the application:")
    print("1. Use: run_app.bat (Windows)")
    print("2. Or: python app.py")
    print("3. Then open: http://localhost:5000")
