// Debug test script for Shopper's Verdict extension
// Run this in browser console on Amazon/Flipkart product pages

(function() {
    console.log('=== Shopper\'s Verdict Debug Test ===');
    
    // Test 1: Check URL patterns
    const url = window.location.href;
    console.log('Current URL:', url);
    
    const amazonPatterns = [
        /\/dp\/[A-Z0-9]{10}/,
        /\/gp\/product\/[A-Z0-9]{10}/,
        /\/product\/[A-Z0-9]{10}/,
        /\/[^/]*\/dp\/[A-Z0-9]{10}/,
        /\/[^/]*\/gp\/product\/[A-Z0-9]{10}/
    ];
    
    const flipkartPatterns = [
        /\/p\/[a-zA-Z0-9\-]+/,
        /\/[^/]+\/p\/[a-zA-Z0-9\-]+/
    ];
    
    console.log('Amazon pattern matches:');
    amazonPatterns.forEach((pattern, index) => {
        const match = pattern.test(url);
        console.log(`  Pattern ${index + 1} (${pattern}): ${match}`);
    });
    
    console.log('Flipkart pattern matches:');
    flipkartPatterns.forEach((pattern, index) => {
        const match = pattern.test(url);
        console.log(`  Pattern ${index + 1} (${pattern}): ${match}`);
    });
    
    // Test 2: Check element selectors
    console.log('\n=== Element Selector Tests ===');
    
    const amazonSelectors = {
        title: ['#productTitle', '.product-title', 'h1[data-automation-id="product-title"]', '.x-item-title-label'],
        price: ['.a-price-whole', '.a-price .a-offscreen', '.a-price-current', '.notranslate', '._30jeq3'],
        image: ['#landingImage', '.a-dynamic-image', '._396cs4', '.s-image']
    };
    
    const flipkartSelectors = {
        title: ['.B_NuCI', '.yhB1nd', '._35KyD6', 'span.B_NuCI'],
        price: ['._30jeq3', '._1_WHN1', '.CEmiEU'],
        image: ['._396cs4', '._2r_T1I', '.CXW8mj']
    };
    
    function testSelectors(selectors, siteName) {
        console.log(`\n${siteName} selectors:`);
        Object.entries(selectors).forEach(([type, selectorList]) => {
            console.log(`  ${type}:`);
            selectorList.forEach(selector => {
                const element = document.querySelector(selector);
                const found = !!element;
                const text = element ? (element.textContent || element.innerText || element.src || '').trim().substring(0, 50) : '';
                console.log(`    ${selector}: ${found} ${text ? `("${text}...")` : ''}`);
            });
        });
    }
    
    if (url.includes('amazon')) {
        testSelectors(amazonSelectors, 'Amazon');
    } else if (url.includes('flipkart')) {
        testSelectors(flipkartSelectors, 'Flipkart');
    }
    
    // Test 3: Check for existing extension elements
    console.log('\n=== Extension Element Tests ===');
    const extensionButton = document.getElementById('shoppers-verdict-button');
    const extensionResults = document.getElementById('shoppers-verdict-results');
    
    console.log('Extension button found:', !!extensionButton);
    console.log('Extension results found:', !!extensionResults);
    
    // Test 4: Check Chrome APIs
    console.log('\n=== Chrome API Tests ===');
    console.log('chrome object:', !!window.chrome);
    console.log('chrome.runtime:', !!(window.chrome && window.chrome.runtime));
    console.log('chrome.storage:', !!(window.chrome && window.chrome.storage));
    
    // Test 5: Manual button injection test
    console.log('\n=== Manual Button Injection Test ===');
    
    // Try to find insertion points
    const amazonInsertionSelectors = [
        '#priceblock_ourprice',
        '#priceblock_dealprice', 
        '.a-price-range',
        '#corePrice_feature_div',
        '#apex_desktop',
        '#rightCol',
        '#feature-bullets',
        '.a-section.a-spacing-none.aok-align-center'
    ];
    
    const flipkartInsertionSelectors = [
        '._30jeq3',
        '._16Jk6d',
        '._1vC4OE',
        '._3LWZlK',
        '.CEmiEU'
    ];
    
    let insertionSelectors = [];
    if (url.includes('amazon')) {
        insertionSelectors = amazonInsertionSelectors;
    } else if (url.includes('flipkart')) {
        insertionSelectors = flipkartInsertionSelectors;
    }
    
    console.log('Testing insertion points:');
    insertionSelectors.forEach(selector => {
        const element = document.querySelector(selector);
        console.log(`  ${selector}: ${!!element}`);
    });
    
    console.log('\n=== Debug Test Complete ===');
    console.log('If extension is not working:');
    console.log('1. Check if URL patterns match');
    console.log('2. Check if selectors find elements');
    console.log('3. Check if Chrome APIs are available');
    console.log('4. Check browser console for errors');
    console.log('5. Reload extension at chrome://extensions/');
})();