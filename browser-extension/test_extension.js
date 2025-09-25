// Test script to verify extension functionality
// Copy and paste this into browser console on Amazon product page

(function() {
    console.log('🔍 Testing Shopper\'s Verdict Extension...');
    
    // Test 1: Check URL
    console.log('Current URL:', window.location.href);
    
    // Test 2: Check if it matches product pattern
    const productPatterns = [
        /\/(dp|gp\/product)\/[A-Z0-9]{10}/,
        /\/p\/[a-zA-Z0-9]+/
    ];
    
    const isProductPage = productPatterns.some(pattern => pattern.test(window.location.href));
    console.log('Is product page:', isProductPage);
    
    // Test 3: Check Chrome APIs
    console.log('Chrome available:', typeof chrome !== 'undefined');
    console.log('Runtime available:', !!(chrome && chrome.runtime));
    console.log('Storage available:', !!(chrome && chrome.storage));
    
    // Test 4: Check for extension elements
    const extensionButton = document.querySelector('#shoppers-verdict-button');
    console.log('Extension button found:', !!extensionButton);
    
    const extensionResults = document.querySelector('#shoppers-verdict-results');
    console.log('Extension results found:', !!extensionResults);
    
    // Test 5: Check product data extraction
    const titleElement = document.querySelector('#productTitle, .product-title');
    console.log('Product title element:', !!titleElement);
    if (titleElement) {
        console.log('Product title:', titleElement.textContent?.trim());
    }
    
    const priceElement = document.querySelector('.a-price-whole, .a-price .a-offscreen');
    console.log('Price element:', !!priceElement);
    if (priceElement) {
        console.log('Price text:', priceElement.textContent?.trim());
    }
    
    // Test 6: Manual trigger
    if (isProductPage && !extensionButton) {
        console.log('❌ Extension should be working but button not found');
        console.log('Possible issues:');
        console.log('1. Extension not loaded/enabled');
        console.log('2. Content script not running');
        console.log('3. URL pattern not matching');
        console.log('4. Page loaded too fast');
    } else if (extensionButton) {
        console.log('✅ Extension appears to be working');
    }
    
    // Return useful info
    return {
        url: window.location.href,
        isProductPage,
        chromeAvailable: typeof chrome !== 'undefined',
        extensionButton: !!extensionButton,
        titleElement: !!titleElement,
        priceElement: !!priceElement
    };
})();