# 🚀 Shopper's Verdict - Installation & Setup Guide

## 📋 Prerequisites

### System Requirements:
- Python 3.8 or higher
- Chrome/Edge browser (for extension)
- Internet connection
- 2GB RAM minimum
- 1GB free disk space

### Required Python Packages:
```
Flask==2.0.1
Flask-CORS==3.0.10
scikit-learn>=1.3.0
playwright>=1.55.0
beautifulsoup4>=4.13.5
vaderSentiment>=3.3.2
spacy>=3.0.9
numpy>=1.26.4
requests>=2.32.5
```

## 🛠️ Installation Steps

### 1. Setup Python Environment

```bash
# Clone or download the project
cd shoppers-verdict

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Install Playwright (for scraping)

```bash
# Install Playwright browsers
playwright install chromium
```

### 3. Download spaCy Model

```bash
# Download English language model
python -m spacy download en_core_web_sm
```

### 4. Verify Installation

```bash
# Test basic functionality
python test_imports.py

# Should show:
# ✓ Python version: 3.x.x
# ✓ Flask version: 2.0.1
# ✓ SQLite available
# ✓ Requests available
# ✓ VADER Sentiment working
```

## 🌐 Web Application Setup

### 1. Start the Flask Server

```bash
# Make sure virtual environment is activated
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Start the application
python app.py
```

### 2. Access the Application

- **Web Interface**: Open `http://localhost:5000` in your browser
- **API Health Check**: Visit `http://localhost:5000/api/extension/health`

### 3. Test Basic Functionality

1. Navigate to the web interface
2. Paste a product URL (Amazon/Flipkart)
3. Click "Analyze Product"
4. Wait for analysis results
5. Check for recommendations section

## 🔌 Browser Extension Setup

### 1. Prepare Extension Files

```bash
# Navigate to extension directory
cd browser-extension

# Create placeholder icons (required)
# Create 16x16, 48x48, 128x128 PNG files in icons/ folder
# Or use any placeholder images with these names:
# - icons/icon16.png
# - icons/icon48.png  
# - icons/icon128.png
```

### 2. Load Extension in Chrome

1. Open Chrome browser
2. Navigate to `chrome://extensions/`
3. Enable "Developer mode" (top-right toggle)
4. Click "Load unpacked"
5. Select the `browser-extension` folder
6. Extension should appear in your toolbar

### 3. Test Extension

1. Navigate to any Amazon or Flipkart product page
2. Look for the "🛒 Get Verdict" button on the page
3. Click the extension icon in the toolbar
4. Extension popup should show analysis options

## 📊 Database Setup

### 1. Automatic Database Creation

The application automatically creates required databases:
- `reviews_cache.db` - Caches scraped reviews
- `recommendations.db` - Stores analyzed products for recommendations

### 2. Manual Database Reset (if needed)

```bash
# Delete existing databases
rm reviews_cache.db recommendations.db

# Restart application - databases will be recreated
python app.py
```

## 🧪 Testing & Verification

### 1. Run Demo Script

```bash
# Run comprehensive feature demo
python demo_enhanced_features.py
```

### 2. Test Individual Components

```bash
# Test scraper
python scraper.py

# Test analyzer
python -c "from analyzer import perform_analysis; print(perform_analysis(['Good product', 'Bad quality']))"

# Test recommendation engine
python -c "from recommendation_engine import get_product_recommendations; print('Engine loaded')"
```

### 3. API Testing with curl

```bash
# Health check
curl -X GET http://localhost:5000/api/extension/health

# Analysis request
curl -X POST http://localhost:5000/api/extension/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.flipkart.com/product-url", "include_recommendations": true}'
```

## 🔧 Troubleshooting

### Common Issues:

#### 1. Import Errors
```bash
# Solution: Install missing packages
pip install -r requirements.txt

# Or install individually:
pip install flask flask-cors scikit-learn
```

#### 2. Playwright Installation Issues
```bash
# Reinstall Playwright
pip uninstall playwright
pip install playwright
playwright install chromium
```

#### 3. spaCy Model Not Found
```bash
# Download English model
python -m spacy download en_core_web_sm

# Alternative: Download manually
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.0.0/en_core_web_sm-3.0.0.tar.gz
```

#### 4. Extension Not Loading
- Check that all files are in `browser-extension` folder
- Verify `manifest.json` is valid JSON
- Create placeholder icon files in `icons/` folder
- Reload extension after changes

#### 5. CORS Errors
- Ensure Flask-CORS is installed: `pip install flask-cors`
- Check that Flask server is running on `localhost:5000`
- Try restarting the Flask application

#### 6. Scraping Timeouts
- Check internet connection
- Verify product URLs are valid and accessible
- Increase timeout in scraper settings if needed

### Performance Optimization:

#### 1. Database Cleanup
```bash
# Run periodic cleanup (optional)
python -c "
from recommendation_engine import recommendation_engine
# Cleanup old cache entries
print('Database cleanup completed')
"
```

#### 2. Cache Management
- Reviews cache: 7-day expiry
- Recommendations cache: 3-day expiry  
- Automatic cleanup on restart

## 📱 Browser Compatibility

### Supported Browsers:
- ✅ Chrome 88+
- ✅ Edge 88+
- ✅ Chromium-based browsers
- ❌ Firefox (different extension format)
- ❌ Safari (different extension format)

### Extension Permissions:
- `activeTab` - Access current tab
- `storage` - Store preferences
- Host permissions for Amazon/Flipkart domains

## 🌍 Platform Support

### Supported E-commerce Sites:
- ✅ Amazon.in
- ✅ Amazon.com  
- ✅ Flipkart.com
- 🔄 Extensible for additional platforms

### URL Pattern Recognition:
- Amazon: `/dp/[product-id]`
- Flipkart: `/p/[product-id]`

## 📈 Performance Metrics

### Expected Response Times:
- **Health Check**: < 100ms
- **Cached Analysis**: < 500ms
- **Fresh Analysis**: 5-30 seconds
- **With Recommendations**: 10-60 seconds

### Resource Usage:
- **Memory**: 50-200MB (during analysis)
- **Storage**: 10-100MB (cache files)
- **Network**: Variable (depends on scraping)

## 🎯 Next Steps

After successful installation:

1. **Test Basic Features**: Analyze a few products via web interface
2. **Try Browser Extension**: Install and test on product pages
3. **Explore Recommendations**: Look for alternatives suggestions
4. **Voice Features**: Test text-to-speech verdict
5. **API Integration**: Build custom integrations using the API

## 📞 Support

If you encounter issues:

1. Check this troubleshooting guide
2. Verify all dependencies are installed
3. Test with simple product URLs first
4. Check console/terminal for error messages
5. Refer to `ENHANCED_FEATURES.md` for detailed documentation

## 🎉 Success Indicators

Installation is successful when:
- ✅ Web interface loads at `http://localhost:5000`
- ✅ Extension appears in Chrome toolbar
- ✅ Health endpoint returns `{"status": "healthy"}`
- ✅ Product analysis completes without errors
- ✅ Recommendations appear in results
- ✅ Voice verdict plays correctly

Happy shopping with enhanced decision-making! 🛒✨