# 🔍 Extension Not Working on Amazon - Debug Checklist

## ❌ **Common Issues & Solutions**

### 1. **Check Extension Installation Status**

**Step 1:** Go to `chrome://extensions/`
- ✅ Extension should be **Enabled**
- ✅ Version should show **1.0.0**
- ✅ No red error messages
- ✅ All icons loaded (no broken image icons)

**If issues found:** Click **Remove** → **Load unpacked** → Select `browser-extension` folder

### 2. **Verify Amazon URL Compatibility**

**Current URL patterns the extension works on:**
- ✅ `https://www.amazon.in/dp/[product-id]`
- ✅ `https://www.amazon.in/gp/product/[product-id]`
- ✅ `https://www.amazon.com/dp/[product-id]`
- ✅ `https://www.amazon.com/gp/product/[product-id]`

**Test with these working Amazon URLs:**
```
https://www.amazon.in/dp/B08N5WRWNW
https://www.amazon.com/dp/B08N5WRWNW
https://www.amazon.in/gp/product/B08N5WRWNW
```

**❌ URLs that WON'T work:**
- Search pages: `amazon.in/s?k=phone`
- Category pages: `amazon.in/electronics`
- Homepage: `amazon.in`
- Cart: `amazon.in/cart`

### 3. **Check Flask Server Status**

**Test Flask API:**
1. Open new tab: `http://localhost:5000/api/extension/health`
2. Should show JSON: `{"status": "healthy"}`
3. If not working, start server:
   ```bash
   cd d:\PROJECTS\NLP\shoppers-verdict
   venv\Scripts\activate
   python app.py
   ```

### 4. **Debug Extension Console**

**Check Content Script Errors:**
1. Go to Amazon product page
2. Press `F12` → Console tab
3. Look for red errors
4. Common errors:
   - `chrome is not defined`
   - `Cannot read properties of undefined`
   - `Failed to fetch`

**Check Extension Background:**
1. Go to `chrome://extensions/`
2. Find "Shopper's Verdict"
3. Click **"service worker"** link
4. Check for errors in new console

### 5. **Test Step by Step**

**Test 1: Basic Detection**
1. Go to: `https://www.amazon.in/dp/B08N5WRWNW`
2. Press F12 → Console
3. Type: `window.location.href`
4. Should show the Amazon URL

**Test 2: Content Script Loading**
1. On same page, in console type:
   ```javascript
   console.log('Extension test:', document.querySelector('#shoppers-verdict-button'))
   ```
2. Should show either the button element or null

**Test 3: Extension Popup**
1. Click extension icon in toolbar
2. Should show either:
   - "Analyzing product..." (if on product page)
   - "Navigate to Amazon/Flipkart..." (if not on product page)

## 🔧 **Most Likely Fixes**

### Fix 1: Complete Extension Reload
```
1. chrome://extensions/
2. Find "Shopper's Verdict"
3. Toggle OFF → Toggle ON
4. Or click Remove → Load unpacked again
```

### Fix 2: Add Missing URL Patterns
The extension might not match all Amazon URL formats. Let me update the manifest.