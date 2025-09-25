# 🔧 **Fix Amazon Extension - Step by Step Guide**

## 🚨 **Extension Not Working on Amazon? Follow These Steps:**

### **Step 1: Reload the Extension (MOST IMPORTANT)**
1. Open Chrome and go to: `chrome://extensions/`
2. Find **"Shopper's Verdict"**
3. Click the **🔄 Reload** button
4. **OR** Toggle it OFF then ON
5. **OR** Remove and re-add: Click **Remove** → **Load unpacked** → Select `browser-extension` folder

### **Step 2: Test with Correct Amazon URLs**
The extension only works on **product pages**, not search or category pages.

✅ **WORKING URLs (Test these):**
```
https://www.amazon.in/dp/B08N5WRWNW
https://www.amazon.com/dp/B08N5WRWNW  
https://www.amazon.in/gp/product/B08N5WRWNW
```

❌ **NON-WORKING URLs:**
```
https://www.amazon.in/s?k=phone          (Search page)
https://www.amazon.in/electronics        (Category page)
https://www.amazon.in                    (Homepage)
```

### **Step 3: Verify Extension Status**
1. Go to `chrome://extensions/`
2. Check **"Shopper's Verdict"**:
   - ✅ Should be **Enabled**
   - ✅ Version: **1.0.0**
   - ✅ No red error messages
   - ✅ Icons loaded (not broken)

### **Step 4: Test with Console**
1. Go to a working Amazon URL (from Step 2)
2. Press **F12** → **Console** tab
3. Copy and paste this test code:

```javascript
// Test Extension
console.log('🔍 Testing Extension...');
console.log('URL:', window.location.href);
console.log('Chrome API:', typeof chrome !== 'undefined');
console.log('Extension button:', !!document.querySelector('#shoppers-verdict-button'));

// Check if URL matches pattern
const isProduct = /\/(dp|gp\/product)\/[A-Z0-9]{10}/.test(window.location.href);
console.log('Is product page:', isProduct);
```

4. Press **Enter**
5. Should show results like:
   ```
   🔍 Testing Extension...
   URL: https://www.amazon.in/dp/B08N5WRWNW
   Chrome API: true
   Extension button: true (or false)
   Is product page: true
   ```

### **Step 5: Check Flask Server**
1. Open new tab: `http://localhost:5000/api/extension/health`
2. Should show: `{"status": "healthy", "ok": true}`
3. If not working:
   ```bash
   cd d:\PROJECTS\NLP\shoppers-verdict
   venv\Scripts\activate
   python app.py
   ```

### **Step 6: Manual Button Creation (Last Resort)**
If extension still not working, try this in console on Amazon product page:

```javascript
// Manually create button for testing
const button = document.createElement('div');
button.innerHTML = '<button style="background: #667eea; color: white; padding: 10px; border: none; border-radius: 5px; cursor: pointer;">🛒 Test Verdict</button>';
button.style.position = 'fixed';
button.style.top = '10px';
button.style.right = '10px';
button.style.zIndex = '10000';
document.body.appendChild(button);

button.onclick = () => {
  alert('Extension framework working! Check why auto-injection failed.');
};
```

## 🔍 **Common Issues & Solutions**

### Issue 1: "Extension button never appears"
**Solution:** 
- Reload extension
- Try different Amazon URL formats
- Check console for errors

### Issue 2: "Extension icon shows but nothing happens"
**Solution:**
- Check Flask server is running
- Test: `http://localhost:5000/api/extension/health`
- Look for CORS errors in console

### Issue 3: "Console shows Chrome API errors"
**Solution:**
- Extension not properly loaded
- Go to `chrome://extensions/` → Reload
- Check extension permissions

### Issue 4: "Works sometimes but not always"  
**Solution:**
- Amazon loads content dynamically
- Extension might load before page ready
- Try refreshing the page (F5)

## 🎯 **Success Indicators**

Extension is working when:
1. ✅ On Amazon product page, you see "🛒 Get Verdict" button
2. ✅ Extension icon shows badge (!) when on product page
3. ✅ Clicking extension icon shows analysis popup
4. ✅ No red errors in browser console
5. ✅ Flask health check returns `{"status": "healthy"}`

## 🚀 **Quick Test Sequence**

1. **Reload extension** at `chrome://extensions/`
2. **Go to**: `https://www.amazon.in/dp/B08N5WRWNW`
3. **Wait 3-5 seconds** for page to fully load
4. **Look for** "🛒 Get Verdict" button on page
5. **Click extension icon** in toolbar
6. **Should see** analysis popup or "analyzing..." message

If none of this works, the issue might be:
- Chrome version compatibility (need Chrome 88+)
- Browser permissions blocking the extension
- Antivirus/firewall blocking local connections

Try the extension in **Incognito mode** to rule out other extension conflicts.