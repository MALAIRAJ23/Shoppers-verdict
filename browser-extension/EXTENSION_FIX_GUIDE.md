# Extension Troubleshooting Guide

## Quick Fix Steps

### 1. Reload Extension
1. Go to `chrome://extensions/`
2. Find "Shopper's Verdict"
3. Click the refresh icon (⟳)
4. Test on a product page

### 2. Test URLs
Try these working URLs:
- **Amazon India**: https://www.amazon.in/dp/B08N5WRWNW
- **Amazon US**: https://www.amazon.com/dp/B08N5WRWNW  
- **Flipkart**: https://www.flipkart.com/apple-iphone-13-blue-128-gb/p/itm6c601e0a58b67

### 3. Debug Console Test
1. Open any Amazon/Flipkart product page
2. Press F12 → Console tab
3. Copy and paste the debug script from `debug_test.js`
4. Press Enter and check results

## Common Issues & Solutions

### Issue 1: Button Not Appearing
**Symptoms**: No "🛒 Get Verdict" button on product pages
**Solutions**:
1. Wait 3-5 seconds after page loads
2. Check console for errors (F12 → Console)
3. Verify URL matches patterns (use debug script)
4. Reload extension and refresh page

### Issue 2: Extension Not Detecting Product Pages
**Symptoms**: Popup shows "Navigate to a product page"
**Solutions**:
1. Ensure you're on a direct product URL (not search results)
2. Check URL contains `/dp/` for Amazon or `/p/` for Flipkart
3. Try the test URLs above
4. Clear browser cache and reload

### Issue 3: "Failed to analyze product"
**Symptoms**: Button appears but analysis fails
**Solutions**:
1. Check if Flask backend is running (`python app.py`)
2. Verify backend is accessible at http://localhost:5000
3. Check browser console for network errors
4. Disable ad blockers temporarily

### Issue 4: Popup Shows Error
**Symptoms**: Extension popup displays error message
**Solutions**:
1. Check Chrome permissions (should have activeTab, storage)
2. Reload extension completely
3. Test on different product pages
4. Check console errors in popup (right-click popup → Inspect)

## Advanced Debugging

### Console Commands
Run these in browser console (F12):

```javascript
// Check if content script loaded
console.log('Extension loaded:', !!document.getElementById('shoppers-verdict-button'));

// Test product detection
console.log('Is product page:', /\/(dp|gp\/product)\/[A-Z0-9]{10}/.test(location.href));

// Check element selectors
console.log('Title element:', document.querySelector('#productTitle'));
console.log('Price element:', document.querySelector('.a-price-whole'));

// Test Chrome APIs
console.log('Chrome runtime:', !!chrome?.runtime);
console.log('Chrome storage:', !!chrome?.storage);
```

### Backend Check
Verify Flask server is running:
1. Open http://localhost:5000 in browser
2. Should see the web interface
3. Check terminal for server logs

### Extension Permissions
Verify in `chrome://extensions/`:
- [x] Allow access to file URLs (if needed)
- [x] Active tab permission
- [x] Storage permission

## Still Not Working?

### Step 1: Complete Reset
1. Go to `chrome://extensions/`
2. Remove "Shopper's Verdict" extension
3. Restart Chrome completely
4. Re-install from folder
5. Test with provided URLs

### Step 2: Check Requirements
- Chrome/Edge browser (latest version)
- Flask backend running on localhost:5000
- No conflicting ad blockers
- Valid Amazon/Flipkart product URL

### Step 3: Error Reporting
If still failing, collect this info:
1. Browser and version
2. Exact URL tested
3. Console errors (F12)
4. Extension popup errors
5. Backend terminal logs

## Success Indicators

Extension is working when you see:
- ✅ "🛒 Get Verdict" button on product pages
- ✅ Badge (!) appears on extension icon
- ✅ Popup shows product analysis
- ✅ Console shows "Shopper's Verdict: Product page detected"

## Test Checklist

- [ ] Extension reloaded at chrome://extensions/
- [ ] Tested on provided working URLs  
- [ ] Backend server running (localhost:5000)
- [ ] No console errors in browser
- [ ] Chrome permissions granted
- [ ] Ad blockers disabled for testing

Follow these steps in order and the extension should work properly!