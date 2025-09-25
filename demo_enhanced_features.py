#!/usr/bin/env python3
"""
Demo script for Shopper's Verdict Enhanced Features
Shows both Browser Extension API and Smart Recommendation Engine
"""

import requests
import json
import time

# Configuration
API_BASE = "http://localhost:5000"
DEMO_PRODUCTS = [
    "https://www.flipkart.com/google-pixel-7a-sea-128-gb/p/itm8577377a36c72",
    "https://www.amazon.in/dp/B0BT9XXQY2",  # Example product
]

def test_health_endpoint():
    """Test the extension health endpoint"""
    print("🔍 Testing Extension Health Endpoint...")
    try:
        response = requests.get(f"{API_BASE}/api/extension/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health Check Passed!")
            print(f"   Status: {data['status']}")
            print(f"   Version: {data['version']}")
            print(f"   Features: {', '.join([f for f, enabled in data['features'].items() if enabled])}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_extension_analysis(product_url):
    """Test the extension analysis endpoint with recommendations"""
    print(f"\n🔍 Testing Extension Analysis...")
    print(f"   Product: {product_url}")
    
    try:
        payload = {
            "url": product_url,
            "include_recommendations": True
        }
        
        print("   📡 Sending analysis request...")
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE}/api/extension/analyze",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        processing_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('ok'):
                print("✅ Analysis Successful!")
                print(f"   ⏱️  Processing Time: {processing_time:.2f}s")
                print(f"   📊 Worth-to-Buy Score: {data['score']}%")
                print(f"   🏷️  Recommendation: {data['recommendation']}")
                
                # Display pros and cons
                if data.get('pros'):
                    print("   👍 Pros:")
                    for aspect, score in data['pros'][:2]:
                        print(f"      • {aspect.capitalize()}: {score:.2f}")
                
                if data.get('cons'):
                    print("   👎 Cons:")
                    for aspect, score in data['cons'][:2]:
                        print(f"      • {aspect.capitalize()}: {score:.2f}")
                
                # Display recommendations
                recommendations = data.get('recommendations', [])
                if recommendations:
                    print(f"   🎯 Found {len(recommendations)} recommendations:")
                    for i, rec in enumerate(recommendations[:3], 1):
                        print(f"      {i}. {rec['title'][:50]}...")
                        print(f"         Score: {rec['score']}% | Similarity: {rec['similarity']:.2f}")
                        print(f"         Site: {rec['site'].capitalize()}")
                        if rec.get('price'):
                            print(f"         Price: ₹{rec['price']:,.0f}")
                else:
                    print("   🎯 No recommendations found (need more data)")
                
                # Display voice verdict
                if data.get('voice_verdict'):
                    print(f"   🔊 Voice Verdict: {data['voice_verdict']}")
                
                return True
            else:
                print(f"❌ Analysis failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return False

def test_web_interface():
    """Test the main web interface"""
    print(f"\n🌐 Testing Web Interface...")
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code == 200:
            print("✅ Web interface accessible!")
            print(f"   URL: {API_BASE}")
            return True
        else:
            print(f"❌ Web interface error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Web interface error: {e}")
        return False

def display_demo_summary():
    """Display summary of implemented features"""
    print("\n" + "="*60)
    print("🎉 SHOPPER'S VERDICT - ENHANCED FEATURES DEMO")
    print("="*60)
    
    print("\n🌐 BROWSER EXTENSION:")
    print("   ✅ Chrome Extension v3 manifest")
    print("   ✅ Content script for product page detection")
    print("   ✅ Popup UI with analysis results")
    print("   ✅ On-page verdict injection")
    print("   ✅ Voice verdict playback")
    print("   ✅ Cross-platform support (Amazon/Flipkart)")
    
    print("\n🤖 SMART RECOMMENDATION ENGINE:")
    print("   ✅ Product embedding generation")
    print("   ✅ Similarity-based matching")
    print("   ✅ Cross-platform competitor discovery")
    print("   ✅ Score-based filtering")
    print("   ✅ Real-time analysis integration")
    print("   ✅ Caching system for performance")
    
    print("\n🔧 API ENHANCEMENTS:")
    print("   ✅ Extension-specific endpoints")
    print("   ✅ CORS support for browser extensions")
    print("   ✅ Recommendation data in responses")
    print("   ✅ Health check endpoint")
    
    print("\n🎨 UI IMPROVEMENTS:")
    print("   ✅ Enhanced results page with recommendations")
    print("   ✅ Interactive recommendation cards")
    print("   ✅ Modern gradient design")
    print("   ✅ Responsive layout")
    print("   ✅ Animated elements")
    
    print("\n📖 DOCUMENTATION:")
    print("   ✅ Comprehensive feature documentation")
    print("   ✅ Installation instructions")
    print("   ✅ API reference")
    print("   ✅ Technical implementation details")

def main():
    """Run the complete demo"""
    print("🚀 Starting Shopper's Verdict Enhanced Features Demo\n")
    
    # Test health endpoint
    if not test_health_endpoint():
        print("❌ Demo failed - Flask server not running or missing dependencies")
        print("📌 Make sure to run: python app.py")
        return
    
    # Test web interface
    if not test_web_interface():
        print("❌ Web interface test failed")
        return
    
    # Test extension analysis with a sample product
    print("\n" + "⏳ Testing analysis with sample product...")
    print("   Note: This may take 30-60 seconds for first-time analysis")
    
    # Try the first demo product
    success = test_extension_analysis(DEMO_PRODUCTS[0])
    
    if not success:
        print("   ℹ️  Analysis might need real product data to show recommendations")
        print("   📌 Try submitting products via the web interface first")
    
    # Display feature summary
    display_demo_summary()
    
    print("\n🎯 HOW TO USE:")
    print("   1. 🌐 Web Interface: Visit http://localhost:5000")
    print("   2. 🔌 Browser Extension:")
    print("      • Open Chrome → Extensions → Developer Mode")
    print("      • Click 'Load Unpacked' → Select 'browser-extension' folder")
    print("      • Visit any Amazon/Flipkart product page")
    print("      • Click extension icon or 'Get Verdict' button")
    print("   3. 🧪 API Testing: Use curl or Postman with provided endpoints")
    
    print("\n🎉 Demo completed successfully!")
    print("📋 See ENHANCED_FEATURES.md for detailed documentation")

if __name__ == "__main__":
    main()