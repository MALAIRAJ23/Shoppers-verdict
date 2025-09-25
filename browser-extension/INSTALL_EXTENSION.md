# 🔌 How to Install Shopper's Verdict Browser Extension

## ✅ Prerequisites Completed
- ✅ All icon files created (16x16, 48x48, 128x128)
- ✅ Manifest.json validated
- ✅ All extension files ready

## 📋 Installation Steps

### 1. Open Chrome Extension Management
1. Open Google Chrome browser
2. Click the three dots menu (⋮) in the top-right corner
3. Go to **More tools** → **Extensions**
4. Or directly navigate to: `chrome://extensions/`

### 2. Enable Developer Mode
1. In the Extensions page, look for "Developer mode" toggle in the top-right
2. **Turn ON** the "Developer mode" toggle
3. You should see additional buttons appear: "Load unpacked", "Pack extension", "Update"

### 3. Load the Extension
1. Click the **"Load unpacked"** button
2. Navigate to your project folder: `D:\PROJECTS\NLP\shoppers-verdict\browser-extension`
3. Select the `browser-extension` folder (not any subfolder)
4. Click **"Select Folder"**

### 4. Verify Installation
After loading, you should see:
- ✅ Extension card with "Shopper's Verdict" name
- ✅ Version 1.0.0
- ✅ Blue shopping cart icon
- ✅ Status: "Enabled"
- ✅ Extension icon appears in Chrome toolbar

### 5. Pin Extension to Toolbar (Recommended)
1. Click the puzzle piece icon (🧩) in Chrome toolbar
2. Find "Shopper's Verdict" in the list
3. Click the pin icon (📌) next to it
4. Extension icon will now always be visible in toolbar

## 🧪 Testing the Extension

### Test 1: Visit a Product Page
1. Navigate to any Amazon or Flipkart product page, for example:
   - `https://www.amazon.in/dp/B0BT9XXQY2`
   - `https://www.flipkart.com/google-pixel-7a-sea-128-gb/p/itm8577377a36c72`

2. Look for the "🛒 Get Verdict" button injected on the page
3. The extension icon should show a badge (!) indicating product page detected

### Test 2: Extension Popup
1. Click the Shopper's Verdict icon in the toolbar
2. Extension popup should open showing:
   - "Analyzing product..." (if on product page)
   - "Navigate to Amazon/Flipkart..." (if not on product page)

### Test 3: Full Analysis
1. On a product page, click either:
   - The "Get Verdict" button on the page, OR
   - The extension icon in toolbar
2. Wait for analysis to complete (may take 30-60 seconds)
3. Results should appear both:
   - In the extension popup
   - On the product page itself

## 🔧 Troubleshooting

### Issue: "Could not load manifest"
- **Solution**: Make sure you selected the `browser-extension` folder, not any subfolder
- **Check**: Manifest.json should be directly in the selected folder

### Issue: "Could not load icon"  
- **Solution**: Icons have been created! If still seeing this, try:
  1. Remove the extension
  2. Reload the extension
  3. Hard refresh Chrome (Ctrl+Shift+R)

### Issue: Extension doesn't appear on product pages
- **Check**: Make sure you're on a supported product page:
  - Amazon: URLs containing `/dp/[product-id]`
  - Flipkart: URLs containing `/p/[product-id]`
- **Solution**: Try refreshing the page after installing extension

### Issue: "Network error" in extension
- **Check**: Make sure Flask server is running at `http://localhost:5000`
- **Test**: Visit `http://localhost:5000/api/extension/health` in browser
- **Solution**: Start Flask server with `python app.py`

### Issue: CORS errors in console
- **Check**: Flask-CORS is installed and imported in app.py
- **Solution**: Restart Flask server after installing flask-cors

## 🎯 Usage Tips

### Best Practices:
1. **Keep Flask server running** while using the extension
2. **Wait for analysis** - first-time analysis takes longer
3. **Check popup** for detailed results and recommendations
4. **Use voice verdict** for hands-free insights

### Supported URLs:
- ✅ `https://www.amazon.in/*/dp/*`
- ✅ `https://amazon.in/*/dp/*`  
- ✅ `https://www.amazon.com/*/dp/*`
- ✅ `https://amazon.com/*/dp/*`
- ✅ `https://www.flipkart.com/*/p/*`
- ✅ `https://flipkart.com/*/p/*`

## 🚀 Next Steps

After successful installation:
1. **Test on multiple products** to see recommendations
2. **Try voice verdict** feature in popup
3. **Explore web interface** at `http://localhost:5000`
4. **Check recommendations** for better alternatives

## 🛡️ Privacy & Security

The extension:
- ✅ **Only accesses** Amazon/Flipkart product pages
- ✅ **No data collection** - analysis stays local
- ✅ **Minimal permissions** - only what's needed
- ✅ **Open source** - all code visible

## 📞 Support

If you encounter issues:
1. Check this troubleshooting guide
2. Verify Flask server is running
3. Test with simple product URLs first
4. Check browser console for error messages

---

**🎉 Congratulations!** Your browser extension is now ready to help you make better shopping decisions! 🛒✨