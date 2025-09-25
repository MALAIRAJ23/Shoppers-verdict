// Content script for Shopper's Verdict extension
// Detects Amazon/Flipkart product pages and provides analysis interface

(function() {
    'use strict';
    
    // Configuration
    const CONFIG = {
        API_BASE_URL: 'http://localhost:5000',
        SUPPORTED_SITES: {
            amazon: {
                domains: ['amazon.in', 'amazon.com'],
                productPatterns: [
                    /\/dp\/[A-Z0-9]{10}/,
                    /\/gp\/product\/[A-Z0-9]{10}/,
                    /\/product\/[A-Z0-9]{10}/,
                    /\/[^/]*\/dp\/[A-Z0-9]{10}/,
                    /\/[^/]*\/gp\/product\/[A-Z0-9]{10}/
                ],
                selectors: {
                    title: '#productTitle, .product-title, h1[data-automation-id="product-title"], .x-item-title-label',
                    price: '.a-price-whole, .a-price .a-offscreen, .a-price-current, .notranslate, ._30jeq3',
                    image: '#landingImage, .a-dynamic-image, ._396cs4, .s-image'
                }
            },
            flipkart: {
                domains: ['flipkart.com'],
                productPatterns: [
                    /\/p\/[a-zA-Z0-9\-]+/,
                    /\/[^/]+\/p\/[a-zA-Z0-9\-]+/
                ],
                selectors: {
                    title: '.VU-ZEz, .yhB1nd, .B_NuCI, ._35KyD6, span.B_NuCI, .Nx9bqj, .x-item-title-label, h1',
                    price: '._30jeq3, ._1_WHN1, .CEmiEU, .Nx9bqj, ._16Jk6d, ._3I9_wc, ._25b18c',
                    image: '._396cs4, ._2r_T1I, .CXW8mj, ._2amPTt, .q6DClP, img'
                }
            }
        }
    };
    
    let currentProductData = null;
    let analysisResult = null;
    let injectedButton = null;
    
    // Utility functions
    function getCurrentSite() {
        const hostname = window.location.hostname.toLowerCase();
        for (const [site, config] of Object.entries(CONFIG.SUPPORTED_SITES)) {
            if (config.domains.some(domain => hostname.includes(domain))) {
                return { site, config };
            }
        }
        return null;
    }
    
    function isProductPage() {
        const siteInfo = getCurrentSite();
        if (!siteInfo) return false;
        
        const url = window.location.href;
        console.log('Checking URL:', url);
        
        // Check against all patterns for the site
        const isMatch = siteInfo.config.productPatterns.some(pattern => {
            const match = pattern.test(url);
            console.log('Pattern:', pattern, 'Match:', match);
            return match;
        });
        
        console.log('Overall match result:', isMatch);
        return isMatch;
    }
    
    function extractProductData() {
        const siteInfo = getCurrentSite();
        if (!siteInfo || !isProductPage()) {
            console.log('Not a product page or unsupported site');
            return null;
        }
        
        const data = {
            url: window.location.href,
            site: siteInfo.site,
            title: null,
            price: null,
            image: null
        };
        
        console.log('Extracting data for site:', siteInfo.site);
        
        // Extract title with multiple attempts
        const titleSelectors = siteInfo.config.selectors.title.split(', ');
        for (const selector of titleSelectors) {
            const titleElement = document.querySelector(selector);
            if (titleElement) {
                data.title = titleElement.textContent?.trim() || titleElement.innerText?.trim() || '';
                console.log('Found title with selector:', selector, 'Title:', data.title);
                if (data.title) break;
            }
        }
        
        // Extract price with multiple attempts
        const priceSelectors = siteInfo.config.selectors.price.split(', ');
        for (const selector of priceSelectors) {
            const priceElement = document.querySelector(selector);
            if (priceElement) {
                data.price = priceElement.textContent?.trim() || priceElement.innerText?.trim() || '';
                console.log('Found price with selector:', selector, 'Price:', data.price);
                if (data.price) break;
            }
        }
        
        // Extract image with multiple attempts
        const imageSelectors = siteInfo.config.selectors.image.split(', ');
        for (const selector of imageSelectors) {
            const imageElement = document.querySelector(selector);
            if (imageElement) {
                data.image = imageElement.src || imageElement.getAttribute('data-src') || '';
                console.log('Found image with selector:', selector, 'Image:', data.image);
                if (data.image) break;
            }
        }
        
        console.log('Extracted product data:', data);
        return data;
    }
    
    // Analysis functions
    async function analyzeProduct(productUrl) {
        try {
            console.log('Content script: Starting analysis for:', productUrl);
            
            // First check if server is available
            const healthResponse = await fetch(`${CONFIG.API_BASE_URL}/api/extension/health`, {
                method: 'GET',
                signal: AbortSignal.timeout(3000)
            });
            
            if (healthResponse.ok) {
                // Try main analysis endpoint with extended timeout
                const response = await fetch(`${CONFIG.API_BASE_URL}/api/extension/analyze`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        url: productUrl,
                        include_recommendations: true 
                    }),
                    signal: AbortSignal.timeout(45000) // 45 second timeout
                });
                
                if (response.ok) {
                    const result = await response.json();
                    if (result.ok) {
                        console.log('Content script: Real analysis successful');
                        return result;
                    } else {
                        throw new Error(result.error || 'Analysis failed');
                    }
                } else {
                    throw new Error(`HTTP ${response.status}`);
                }
            } else {
                throw new Error('Server unavailable');
            }
            
        } catch (error) {
            console.warn('Content script: Analysis failed, using offline fallback:', error.message);
            
            // Generate offline analysis
            const productData = extractProductData();
            if (productData) {
                return generateOfflineAnalysis(productData);
            } else {
                throw new Error('Cannot analyze - no product data available');
            }
        }
    }
    
    function generateOfflineAnalysis(productData) {
        const title = productData.title || 'Product';
        
        // Basic scoring algorithm
        let score = 60;
        const titleLower = title.toLowerCase();
        
        // Brand recognition
        const premiumBrands = ['samsung', 'apple', 'lg', 'sony', 'dell', 'hp', 'asus'];
        const budgetBrands = ['micromax', 'intex', 'karbonn'];
        
        premiumBrands.forEach(brand => {
            if (titleLower.includes(brand)) score += 12;
        });
        budgetBrands.forEach(brand => {
            if (titleLower.includes(brand)) score -= 5;
        });
        
        // Product type specific scoring
        if (titleLower.includes('refrigerator')) {
            score += 5; // Essential appliance
        } else if (titleLower.includes('phone') || titleLower.includes('smartphone')) {
            score += 8; // High utility
        }
        
        score = Math.max(35, Math.min(90, score));
        
        return {
            ok: true,
            score: Math.round(score),
            recommendation: score >= 70 ? 'Recommended' : score >= 50 ? 'Acceptable' : 'Not Recommended',
            pros: [['features', 0.6], ['build_quality', 0.5]],
            cons: [['price', -0.3], ['availability', -0.2]],
            voice_verdict: `Offline analysis: ${title} scores ${Math.round(score)}%. This is a basic assessment. Connect to internet for detailed review analysis.`,
            product_title: `${title} (Offline)`,
            product_url: productData.url,
            reviews_analyzed: 0,
            processing_time: 0.1,
            recommendations: [],
            meta: {
                confidence: 0.4,
                data_quality: 0.3,
                offline_mode: true
            }
        };
    }
    
    // UI injection functions
    function createAnalysisButton() {
        if (injectedButton) return;
        
        const button = document.createElement('div');
        button.id = 'shoppers-verdict-button';
        button.innerHTML = `
            <div class="sv-button-container">
                <button class="sv-analyze-btn">
                    <span class="sv-icon">🛒</span>
                    <span class="sv-text">Get Verdict</span>
                    <span class="sv-loading" style="display: none;">⏳</span>
                </button>
            </div>
        `;
        
        // Position the button based on site
        const siteInfo = getCurrentSite();
        let insertionPoint = null;
        
        if (siteInfo.site === 'amazon') {
            insertionPoint = document.querySelector('#priceblock_ourprice') || 
                           document.querySelector('#priceblock_dealprice') ||
                           document.querySelector('.a-price-range') ||
                           document.querySelector('#apex_desktop');
        } else if (siteInfo.site === 'flipkart') {
            // Try multiple Flipkart insertion points
            const flipkartSelectors = [
                '._30jeq3',
                '._16Jk6d',
                '._1vC4OE',
                '._3LWZlK',
                '.CEmiEU',
                '.Nx9bqj',
                '._25b18c',
                '._3I9_wc',
                '.col.col-7-12',
                '.col.col-5-12'
            ];
            
            for (const selector of flipkartSelectors) {
                insertionPoint = document.querySelector(selector);
                if (insertionPoint) {
                    console.log('Found Flipkart insertion point:', selector);
                    break;
                }
            }
        }
        if (insertionPoint) {
            insertionPoint.parentNode.insertBefore(button, insertionPoint.nextSibling);
            injectedButton = button;
            console.log('Button injected successfully at:', insertionPoint.className || insertionPoint.tagName);
            
            // Add click handler
            const analyzeBtn = button.querySelector('.sv-analyze-btn');
            analyzeBtn.addEventListener('click', handleAnalyzeClick);
        } else {
            console.log('No suitable insertion point found, using fallback for', siteInfo.site);
            
            // Enhanced fallback for different sites
            let fallbackStyle;
            if (siteInfo.site === 'flipkart') {
                // For Flipkart, try to find any price-related container
                const fallbackSelectors = ['[class*="price"]', '[class*="_3I"]', '.col', '.row', 'main'];
                let fallbackParent = null;
                
                for (const selector of fallbackSelectors) {
                    fallbackParent = document.querySelector(selector);
                    if (fallbackParent) {
                        console.log('Using Flipkart fallback parent:', selector);
                        break;
                    }
                }
                
                if (fallbackParent) {
                    fallbackStyle = 'position: relative; margin: 10px 0; z-index: 10000;';
                    const fallbackContainer = document.createElement('div');
                    fallbackContainer.style.cssText = fallbackStyle;
                    fallbackContainer.appendChild(button);
                    fallbackParent.appendChild(fallbackContainer);
                    injectedButton = button;
                    console.log('Button injected via Flipkart fallback');
                } else {
                    // Final fallback to fixed position
                    fallbackStyle = 'position: fixed; top: 70px; right: 10px; z-index: 999999; background: rgba(255,255,255,0.9); padding: 5px; border-radius: 5px;';
                    const fallbackContainer = document.createElement('div');
                    fallbackContainer.style.cssText = fallbackStyle;
                    fallbackContainer.appendChild(button);
                    document.body.appendChild(fallbackContainer);
                    injectedButton = button;
                    console.log('Button injected via fixed position fallback');
                }
            } else {
                // Default fallback for other sites
                fallbackStyle = 'position: fixed; top: 10px; right: 10px; z-index: 999999;';
                const fallbackContainer = document.createElement('div');
                fallbackContainer.style.cssText = fallbackStyle;
                fallbackContainer.appendChild(button);
                document.body.appendChild(fallbackContainer);
                injectedButton = button;
                console.log('Button injected via default fallback');
            }
            
            // Add click handler
            const analyzeBtn = button.querySelector('.sv-analyze-btn');
            analyzeBtn.addEventListener('click', handleAnalyzeClick);
        }
    }
    
    function createQuickResults(result) {
        // Remove existing quick results
        const existing = document.getElementById('shoppers-verdict-results');
        if (existing) existing.remove();
        
        const resultsDiv = document.createElement('div');
        resultsDiv.id = 'shoppers-verdict-results';
        resultsDiv.innerHTML = `
            <div class="sv-results-container">
                <div class="sv-results-header">
                    <span class="sv-logo">🛒 Shopper's Verdict</span>
                    <button class="sv-close-btn">×</button>
                </div>
                <div class="sv-score-section">
                    <div class="sv-score-value">${result.score}%</div>
                    <div class="sv-score-label">Worth-to-Buy Score</div>
                    <div class="sv-recommendation ${result.recommendation.toLowerCase().replace(' ', '-')}">${result.recommendation}</div>
                </div>
                <div class="sv-quick-summary">
                    <div class="sv-pros">
                        <strong>👍 Pros:</strong> ${result.pros.map(p => p[0]).join(', ')}
                    </div>
                    <div class="sv-cons">
                        <strong>👎 Cons:</strong> ${result.cons.map(c => c[0]).join(', ')}
                    </div>
                </div>
                <div class="sv-actions">
                    <button class="sv-action-btn sv-voice-btn">🔊 Play Verdict</button>
                    <button class="sv-action-btn sv-full-btn">📊 Full Report</button>
                </div>
                ${result.recommendations && result.recommendations.length > 0 ? `
                    <div class="sv-recommendations">
                        <div class="sv-rec-title">🎯 Better Alternatives:</div>
                        ${result.recommendations.slice(0, 2).map(rec => `
                            <div class="sv-rec-item">
                                <span class="sv-rec-name">${rec.title}</span>
                                <span class="sv-rec-score">${rec.score}%</span>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
        
        // Insert after the analyze button
        if (injectedButton) {
            injectedButton.parentNode.insertBefore(resultsDiv, injectedButton.nextSibling);
        }
        
        // Add event listeners
        resultsDiv.querySelector('.sv-close-btn').addEventListener('click', () => {
            resultsDiv.remove();
        });
        
        resultsDiv.querySelector('.sv-voice-btn').addEventListener('click', () => {
            playVoiceVerdict(result.voice_verdict);
        });
        
        resultsDiv.querySelector('.sv-full-btn').addEventListener('click', () => {
            openFullReport(result);
        });
    }
    
    // Event handlers
    async function handleAnalyzeClick(event) {
        const button = event.target.closest('.sv-analyze-btn');
        const textSpan = button.querySelector('.sv-text');
        const loadingSpan = button.querySelector('.sv-loading');
        
        // Show loading state
        textSpan.style.display = 'none';
        loadingSpan.style.display = 'inline';
        button.disabled = true;
        
        try {
            const productData = extractProductData();
            if (!productData) {
                throw new Error('Could not extract product data');
            }
            
            currentProductData = productData;
            analysisResult = await analyzeProduct(productData.url);
            
            createQuickResults(analysisResult);
            
            // Store data for popup
            try {
                await chrome.storage.local.set({
                    currentAnalysis: analysisResult,
                    currentProduct: productData
                });
            } catch (storageError) {
                console.warn('Storage error:', storageError);
                // Continue without storage
            }
            
        } catch (error) {
            console.error('Analysis error:', error);
            alert('Failed to analyze product. Please try again.');
        } finally {
            // Reset button state
            textSpan.style.display = 'inline';
            loadingSpan.style.display = 'none';
            button.disabled = false;
        }
    }
    
    function playVoiceVerdict(text) {
        if ('speechSynthesis' in window) {
            speechSynthesis.cancel(); // Stop any ongoing speech
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 0.9;
            utterance.pitch = 1;
            speechSynthesis.speak(utterance);
        } else {
            alert('Voice synthesis not supported in this browser');
        }
    }
    
    function openFullReport(result) {
        if (currentProductData) {
            // Navigate to the main page with URL parameter for GET request
            const baseUrl = `${CONFIG.API_BASE_URL}/`;
            const params = new URLSearchParams({
                url: currentProductData.url
            });
            const fullUrl = `${baseUrl}?${params.toString()}`;
            
            console.log('Opening full analysis report:', fullUrl);
            window.open(fullUrl, '_blank');
        } else {
            // Fallback: construct URL from current page
            const currentUrl = window.location.href;
            const analyzeUrl = `${CONFIG.API_BASE_URL}/?url=${encodeURIComponent(currentUrl)}`;
            console.log('Opening full report for current URL:', analyzeUrl);
            window.open(analyzeUrl, '_blank');
        }
    }
    
    // Message handling from popup/background
    if (chrome && chrome.runtime && chrome.runtime.onMessage) {
        chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
            try {
                console.log('Content script received message:', request);
                
                if (request.action === 'getProductData') {
                    const productData = extractProductData();
                    const isProduct = isProductPage();
                    console.log('Responding with product data:', { productData, analysisResult, isProduct });
                    sendResponse({ 
                        productData, 
                        analysisResult,
                        isProductPage: isProduct 
                    });
                } else if (request.action === 'analyzeProduct') {
                    const analyzeBtn = injectedButton?.querySelector('.sv-analyze-btn');
                    if (analyzeBtn) {
                        handleAnalyzeClick({ target: analyzeBtn });
                    }
                    sendResponse({ success: true });
                } else if (request.action === 'playVerdict') {
                    playVoiceVerdict(request.text);
                    sendResponse({ success: true });
                }
            } catch (error) {
                console.error('Content script message error:', error);
                sendResponse({ success: false, error: error.message });
            }
            return true; // Keep message channel open for async response
        });
    }
    
    // Initialization
    function init() {
        console.log('Shopper\'s Verdict: Initializing on', window.location.href);
        console.log('Document ready state:', document.readyState);
        
        const siteInfo = getCurrentSite();
        console.log('Site info:', siteInfo);
        
        if (!siteInfo) {
            console.log('Shopper\'s Verdict: Unsupported site');
            return;
        }
        
        if (isProductPage()) {
            console.log('Shopper\'s Verdict: Product page detected');
            
            // Store product data for popup
            const productData = extractProductData();
            if (productData && productData.title) {
                console.log('Shopper\'s Verdict: Product data extracted:', productData.title);
                try {
                    if (chrome && chrome.storage && chrome.storage.local) {
                        chrome.storage.local.set({ currentProduct: productData });
                    }
                } catch (storageError) {
                    console.warn('Storage error in init:', storageError);
                }
                
                // Create button with retry mechanism
                function attemptButtonCreation(attempts = 0) {
                    const maxAttempts = 5;
                    const delay = Math.min(1000 * Math.pow(2, attempts), 8000); // Exponential backoff
                    
                    console.log(`Attempt ${attempts + 1} to create button on ${siteInfo.site}`);
                    
                    if (attempts < maxAttempts) {
                        setTimeout(() => {
                            createAnalysisButton();
                            if (!injectedButton) {
                                console.log('Button creation failed, retrying...');
                                
                                // For Flipkart, try additional debugging
                                if (siteInfo.site === 'flipkart') {
                                    console.log('Flipkart page - checking available elements:');
                                    const testSelectors = ['._30jeq3', '._16Jk6d', '.col', '[class*="price"]', '[class*="_"]'];
                                    testSelectors.forEach(sel => {
                                        const found = document.querySelector(sel);
                                        console.log(`  ${sel}: ${!!found}`);
                                    });
                                }
                                
                                attemptButtonCreation(attempts + 1);
                            } else {
                                console.log('Button created successfully on', siteInfo.site);
                            }
                        }, delay);
                    } else {
                        console.error('Failed to create button after maximum attempts on', siteInfo.site);
                        // Force fallback injection
                        console.log('Forcing fallback button injection for', siteInfo.site);
                        createAnalysisButton();
                    }
                }
                
                attemptButtonCreation();
            } else {
                console.log('Shopper\'s Verdict: Could not extract product data, will retry');
                // Retry extraction after more page loading
                setTimeout(() => {
                    const retryData = extractProductData();
                    if (retryData && retryData.title) {
                        console.log('Retry successful, creating button');
                        createAnalysisButton();
                    }
                }, 3000);
            }
        } else {
            console.log('Shopper\'s Verdict: Not a product page:', window.location.href);
            // Clear stored data if not on product page
            try {
                if (chrome && chrome.storage && chrome.storage.local) {
                    chrome.storage.local.remove(['currentProduct', 'currentAnalysis']);
                }
            } catch (storageError) {
                console.warn('Storage cleanup error:', storageError);
            }
        }
    }
    
    // Handle dynamic page changes (SPAs)
    let lastUrl = location.href;
    new MutationObserver(() => {
        const url = location.href;
        if (url !== lastUrl) {
            lastUrl = url;
            // Clean up previous injection
            if (injectedButton) {
                injectedButton.remove();
                injectedButton = null;
            }
            const existing = document.getElementById('shoppers-verdict-results');
            if (existing) existing.remove();
            
            // Re-initialize
            setTimeout(init, 500);
        }
    }).observe(document, { subtree: true, childList: true });
    
    // Initial setup
    init();
})();