# 🔧 Browser Extension Troubleshooting Guide

## 🚨 Common "Uncaught TypeError: Cannot read properties of" Errors

### 1. **Chrome Extension API Not Available**

**Error Example:**
```
Uncaught TypeError: Cannot read properties of undefined (reading 'tabs')
```

**Cause:** Chrome extension APIs not loaded or extension not properly installed.

**Solutions:**
1. **Reload Extension:**
   - Go to `chrome://extensions/`
   - Find "Shopper's Verdict"
   - Click reload button (🔄)

2. **Check Extension Status:**
   - Ensure extension is "Enabled"
   - Look for any error messages in red

3. **Verify Installation:**
   - Extension should show version 1.0.0
   - All icons should be loaded
   - No "Could not load..." errors

### 2. **DOM Elements Not Found**

**Error Example:**
```
Uncaught TypeError: Cannot read properties of null (reading 'textContent')
```

**Cause:** Trying to access DOM elements that don't exist on the page.

**Solutions:**
1. **Check Page Type:**
   - Only works on Amazon/Flipkart product pages
   - URL must match patterns: `/dp/` or `/p/`

2. **Wait for Page Load:**
   - Refresh the page after installing extension
   - Wait for page to fully load before clicking extension

3. **Clear Cache:**
   - Hard refresh: `Ctrl + Shift + R`
   - Clear browser cache

### 3. **Storage API Issues**

**Error Example:**
```
Uncaught TypeError: Cannot read properties of undefined (reading 'get')
```

**Cause:** Chrome storage API not available or permission denied.

**Solutions:**
1. **Check Permissions:**
   - Extension should have "storage" permission in manifest
   - Reload extension after any changes

2. **Reset Storage:**
   ```javascript
   // In browser console on extension popup:
   chrome.storage.local.clear()
   ```

### 4. **Network/CORS Issues**

**Error Example:**
```
TypeError: Failed to fetch
```

**Cause:** Flask server not running or CORS issues.

**Solutions:**
1. **Start Flask Server:**
   ```bash
   cd shoppers-verdict
   venv\Scripts\activate
   python app.py
   ```

2. **Test API:**
   - Visit: `http://localhost:5000/api/extension/health`
   - Should return JSON with `"status": "healthy"`

3. **Check CORS:**
   - Ensure flask-cors is installed
   - Restart Flask server

## 🛠️ Step-by-Step Debugging

### Step 1: Check Browser Console
1. Right-click on webpage → "Inspect"
2. Go to "Console" tab
3. Look for red error messages
4. Note the exact error message and line number

### Step 2: Check Extension Console
1. Go to `chrome://extensions/`
2. Find "Shopper's Verdict"
3. Click "service worker" link (if present)
4. Check for errors in the new console window

### Step 3: Check Extension Popup Console
1. Click extension icon to open popup
2. Right-click inside popup → "Inspect"
3. Check console for errors

### Step 4: Test Individual Components

**Test Content Script:**
1. Navigate to Amazon/Flipkart product page
2. Open browser console
3. Type: `console.log('Content script test')`
4. Look for "Get Verdict" button on page

**Test Popup:**
1. Click extension icon
2. Should show either analysis or "Navigate to product page"
3. Check for error messages

**Test API:**
1. Open new tab: `http://localhost:5000/api/extension/health`
2. Should show JSON response
3. If error, check Flask server

## 🔧 Quick Fixes

### Fix 1: Complete Extension Reload
```bash
1. Go to chrome://extensions/
2. Find "Shopper's Verdict"
3. Click "Remove"
4. Click "Load unpacked" again
5. Select browser-extension folder
```

### Fix 2: Reset All Data
1. **Clear Extension Storage:**
   - Open extension popup
   - Press F12 → Console
   - Type: `chrome.storage.local.clear()`

2. **Clear Browser Cache:**
   - Press `Ctrl + Shift + Delete`
   - Select "All time"
   - Clear "Cached images and files"

### Fix 3: Verify File Structure
```
browser-extension/
├── manifest.json ✅
├── popup.html ✅
├── popup.js ✅
├── content.js ✅
├── content.css ✅
├── background.js ✅
└── icons/
    ├── icon16.png ✅
    ├── icon48.png ✅
    └── icon128.png ✅
```

## 🚀 Advanced Debugging

### Enable Debug Mode
1. Add debug.js to manifest.json:
```json
{
  "content_scripts": [
    {
      "matches": [...],
      "js": ["debug.js", "content.js"],
      "css": ["content.css"]
    }
  ]
}
```

2. Reload extension
3. Check console for detailed error info

### Check Specific APIs
Open browser console and test:
```javascript
// Test Chrome APIs
console.log('Chrome:', typeof chrome !== 'undefined');
console.log('Runtime:', !!chrome?.runtime);
console.log('Tabs:', !!chrome?.tabs);
console.log('Storage:', !!chrome?.storage);

// Test DOM
console.log('Document ready:', document.readyState);
console.log('Product page:', window.location.href);
```

## 📋 Common Solutions Summary

| Error Type | Quick Fix |
|------------|-----------|
| Chrome API undefined | Reload extension |
| DOM element null | Check page type / refresh |
| Storage errors | Clear storage / reload |
| Network errors | Start Flask server |
| Permission denied | Check manifest permissions |
| Script not loading | Verify file paths |

## 🆘 Still Having Issues?

1. **Check Flask Server:**
   ```bash
   curl http://localhost:5000/api/extension/health
   ```

2. **Test with Simple Product:**
   - Try: `https://www.amazon.in/dp/B08N5WRWNW`
   - Should work if everything is set up correctly

3. **Browser Compatibility:**
   - Chrome 88+ required
   - Manifest V3 support needed
   - Try in Incognito mode

4. **File Permissions:**
   - Ensure all extension files are readable
   - Check folder permissions

## 🎯 Success Indicators

Extension is working correctly when:
- ✅ No errors in any console
- ✅ Extension icon appears in toolbar
- ✅ "Get Verdict" button appears on product pages
- ✅ Popup shows analysis or "navigate to product page"
- ✅ Flask API responds to health check
- ✅ Analysis completes without errors

Remember: The most common cause of TypeErrors is trying to access Chrome extension APIs before they're fully loaded or on pages where they're not available.