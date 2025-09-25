// Flipkart Debug Test Script
// Run this in browser console on a Flipkart product page

(function() {
    console.log('=== Flipkart Extension Debug Test ===');
    
    const url = window.location.href;
    console.log('Current URL:', url);
    
    // Test URL patterns
    const flipkartPatterns = [
        /\/p\/[a-zA-Z0-9\-]+/,
        /\/[^/]+\/p\/[a-zA-Z0-9\-]+/
    ];
    
    console.log('\n1. URL Pattern Matching:');
    flipkartPatterns.forEach((pattern, index) => {
        const match = pattern.test(url);
        console.log(`  Pattern ${index + 1} (${pattern}): ${match}`);
    });
    
    // Test element selectors
    console.log('\n2. Element Selector Tests:');
    
    const titleSelectors = ['.VU-ZEz', '.yhB1nd', '.B_NuCI', '._35KyD6', 'span.B_NuCI', '.Nx9bqj', '.x-item-title-label', 'h1'];
    const priceSelectors = ['._30jeq3', '._1_WHN1', '.CEmiEU', '.Nx9bqj', '._16Jk6d', '._3I9_wc', '._25b18c'];
    const insertionSelectors = ['._30jeq3', '._16Jk6d', '._1vC4OE', '._3LWZlK', '.CEmiEU', '.Nx9bqj', '._25b18c', '._3I9_wc', '.col.col-7-12', '.col.col-5-12'];
    
    console.log('  Title selectors:');
    titleSelectors.forEach(selector => {
        const element = document.querySelector(selector);
        const found = !!element;
        const text = element ? element.textContent.trim().substring(0, 50) : '';
        console.log(`    ${selector}: ${found} ${text ? `("${text}...")` : ''}`);
    });
    
    console.log('  Price selectors:');
    priceSelectors.forEach(selector => {
        const element = document.querySelector(selector);
        const found = !!element;
        const text = element ? element.textContent.trim() : '';
        console.log(`    ${selector}: ${found} ${text ? `("${text}")` : ''}`);
    });
    
    console.log('  Button insertion points:');
    insertionSelectors.forEach(selector => {
        const element = document.querySelector(selector);
        const found = !!element;
        console.log(`    ${selector}: ${found}`);
    });
    
    // Test site detection
    console.log('\n3. Site Detection:');
    const hostname = window.location.hostname.toLowerCase();
    const isFlipkart = hostname.includes('flipkart.com');
    console.log(`  Hostname: ${hostname}`);
    console.log(`  Is Flipkart: ${isFlipkart}`);
    
    // Check for existing extension elements
    console.log('\n4. Extension Elements:');
    const extensionButton = document.getElementById('shoppers-verdict-button');
    const extensionResults = document.getElementById('shoppers-verdict-results');
    console.log(`  Extension button: ${!!extensionButton}`);
    console.log(`  Extension results: ${!!extensionResults}`);
    
    // Test Chrome APIs
    console.log('\n5. Chrome APIs:');
    console.log(`  chrome object: ${!!window.chrome}`);
    console.log(`  chrome.runtime: ${!!(window.chrome && window.chrome.runtime)}`);
    console.log(`  chrome.storage: ${!!(window.chrome && window.chrome.storage)}`);
    
    // Look for any elements with class containing common patterns
    console.log('\n6. General Element Scan:');
    const allElements = document.querySelectorAll('[class*="_"]');
    const uniqueClasses = new Set();
    allElements.forEach(el => {
        const classes = el.className.split(' ');
        classes.forEach(cls => {
            if (cls.startsWith('_') && cls.length > 2) {
                uniqueClasses.add(cls);
            }
        });
    });
    
    const classArray = Array.from(uniqueClasses).slice(0, 20); // Show first 20
    console.log('  Found underscore classes:', classArray);
    
    // Manual test injection
    console.log('\n7. Manual Button Test:');
    const testButton = document.createElement('div');
    testButton.innerHTML = '<button style="background: red; color: white; padding: 10px; position: fixed; top: 10px; right: 10px; z-index: 999999;">🛒 TEST BUTTON</button>';
    document.body.appendChild(testButton);
    console.log('  Test button injected at top-right');
    
    console.log('\n=== Debug Complete ===');
    console.log('If you see the RED test button, injection works.');
    console.log('Check the selector results above to see which elements are found.');
})();