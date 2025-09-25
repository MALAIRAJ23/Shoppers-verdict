// Popup script for Shopper's Verdict extension

(function() {
    'use strict';
    
    const CONFIG = {
        API_BASE_URL: 'http://localhost:5000'
    };
    
    // DOM elements
    const elements = {
        loading: document.getElementById('loading'),
        notProductPage: document.getElementById('notProductPage'),
        content: document.getElementById('content'),
        error: document.getElementById('error'),
        scoreValue: document.getElementById('scoreValue'),
        recommendation: document.getElementById('recommendation'),
        prosList: document.getElementById('prosList'),
        consList: document.getElementById('consList'),
        playVerdictBtn: document.getElementById('playVerdictBtn'),
        viewFullBtn: document.getElementById('viewFullBtn'),
        retryBtn: document.getElementById('retryBtn'),
        errorMessage: document.getElementById('errorMessage'),
        recommendationsSection: document.getElementById('recommendationsSection'),
        recommendationsList: document.getElementById('recommendationsList')
    };
    
    let currentProductData = null;
    let currentAnalysis = null;
    
    // Utility functions
    function showView(viewName) {
        // Hide all views
        Object.values(elements).forEach(el => {
            if (el && ['loading', 'notProductPage', 'content', 'error'].includes(el.id)) {
                el.style.display = 'none';
            }
        });
        
        // Show requested view
        if (elements[viewName]) {
            elements[viewName].style.display = 'block';
        }
    }
    
    function formatAspect(aspect) {
        // Capitalize first letter and clean up the aspect name
        return aspect.charAt(0).toUpperCase() + aspect.slice(1).replace(/_/g, ' ');
    }
    
    function getRecommendationClass(score) {
        if (score >= 70) return 'recommended';
        if (score >= 50) return 'acceptable';
        return 'not-recommended';
    }
    
    function getRecommendationText(score) {
        if (score >= 70) return 'Recommended';
        if (score >= 50) return 'Acceptable';
        return 'Not Recommended';
    }
    
    // Analysis functions
    async function analyzeCurrentProduct() {
        if (!currentProductData) {
            throw new Error('No product data available');
        }
        
        // First check if server is available
        try {
            console.log('Popup: Checking server health...');
            const healthResponse = await fetch(`${CONFIG.API_BASE_URL}/api/extension/health`, {
                method: 'GET',
                signal: AbortSignal.timeout(3000) // 3 second timeout for health check
            });
            
            if (healthResponse.ok) {
                console.log('Popup: Server is healthy, attempting main analysis...');
                // Try main analysis endpoint with longer timeout
                const response = await fetch(`${CONFIG.API_BASE_URL}/api/extension/analyze`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        url: currentProductData.url,
                        include_recommendations: true 
                    }),
                    signal: AbortSignal.timeout(45000) // 45 second timeout for analysis
                });
                
                if (response.ok) {
                    const result = await response.json();
                    if (result.ok) {
                        console.log('Popup: Real analysis successful!');
                        return result;
                    } else {
                        throw new Error(result.error || 'Analysis failed');
                    }
                } else {
                    throw new Error(`HTTP ${response.status}`);
                }
            } else {
                throw new Error('Server health check failed');
            }
            
        } catch (serverError) {
            console.warn('Server or analysis failed, using local fallback:', serverError.message);
            
            // Return local analysis when server is down or analysis fails
            return generateLocalAnalysis();
        }
    }
    
    function generateLocalAnalysis() {
        console.log('Generating local fallback analysis...');
        
        // Generate analysis based on product title and basic heuristics
        const title = currentProductData.title || 'Product';
        const site = currentProductData.site || 'unknown';
        
        // Simple scoring based on title keywords
        let score = 65; // Base score
        const positiveKeywords = ['samsung', 'apple', 'lg', 'sony', 'best', 'premium', 'pro', 'plus', 'ultra'];
        const negativeKeywords = ['cheap', 'basic', 'old', 'refurbished'];
        
        const titleLower = title.toLowerCase();
        positiveKeywords.forEach(keyword => {
            if (titleLower.includes(keyword)) score += 8;
        });
        negativeKeywords.forEach(keyword => {
            if (titleLower.includes(keyword)) score -= 10;
        });
        
        // Keep score in valid range
        score = Math.max(30, Math.min(95, score));
        
        // Generate basic pros/cons based on product category
        let pros = [['quality', 0.6], ['features', 0.5]];
        let cons = [['price', -0.3], ['availability', -0.2]];
        
        if (titleLower.includes('refrigerator') || titleLower.includes('fridge')) {
            pros = [['cooling', 0.7], ['capacity', 0.6]];
            cons = [['power_consumption', -0.3], ['noise', -0.2]];
        } else if (titleLower.includes('phone') || titleLower.includes('mobile')) {
            pros = [['camera', 0.6], ['battery', 0.5]];
            cons = [['price', -0.4], ['heating', -0.2]];
        } else if (titleLower.includes('laptop') || titleLower.includes('computer')) {
            pros = [['performance', 0.7], ['display', 0.6]];
            cons = [['battery_life', -0.3], ['weight', -0.2]];
        }
        
        const recommendation = score >= 70 ? 'Recommended' : score >= 50 ? 'Acceptable' : 'Not Recommended';
        
        return {
            ok: true,
            score: Math.round(score),
            recommendation: recommendation,
            pros: pros,
            cons: cons,
            voice_verdict: `Local analysis for ${title}: This product scores ${Math.round(score)}% based on basic assessment. Note: This is offline analysis - connect to internet for detailed review analysis.`,
            product_title: `${title} (Offline Analysis)`,
            product_url: currentProductData.url,
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
    
    // UI update functions
    function displayAnalysis(analysis) {
        // Update score
        elements.scoreValue.textContent = `${analysis.score}%`;
        
        // Update recommendation
        const recommendationText = getRecommendationText(analysis.score);
        const recommendationClass = getRecommendationClass(analysis.score);
        elements.recommendation.textContent = recommendationText;
        elements.recommendation.className = `recommendation ${recommendationClass}`;
        
        // Add offline indicator if in offline mode
        if (analysis.meta && analysis.meta.offline_mode) {
            const offlineIndicator = document.createElement('div');
            offlineIndicator.style.cssText = 'background: #ff9800; color: white; padding: 5px; border-radius: 3px; margin: 5px 0; font-size: 12px; text-align: center;';
            offlineIndicator.textContent = '📴 Offline Mode - Basic Analysis Only';
            elements.content.insertBefore(offlineIndicator, elements.content.firstChild);
        }
        
        // Update pros
        elements.prosList.innerHTML = '';
        if (analysis.pros && analysis.pros.length > 0) {
            analysis.pros.forEach(([aspect, score]) => {
                const li = document.createElement('li');
                li.textContent = formatAspect(aspect);
                li.title = `Sentiment score: ${score}`;
                elements.prosList.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.textContent = 'No specific pros found';
            li.style.opacity = '0.6';
            elements.prosList.appendChild(li);
        }
        
        // Update cons
        elements.consList.innerHTML = '';
        if (analysis.cons && analysis.cons.length > 0) {
            analysis.cons.forEach(([aspect, score]) => {
                const li = document.createElement('li');
                li.textContent = formatAspect(aspect);
                li.title = `Sentiment score: ${score}`;
                elements.consList.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.textContent = 'No major cons found';
            li.style.opacity = '0.6';
            elements.consList.appendChild(li);
        }
        
        // Update recommendations
        if (analysis.recommendations && analysis.recommendations.length > 0) {
            elements.recommendationsList.innerHTML = '';
            analysis.recommendations.slice(0, 3).forEach(rec => {
                const div = document.createElement('div');
                div.className = 'recommendation-item';
                div.innerHTML = `
                    <div class="recommendation-title">${rec.title}</div>
                    <div class="recommendation-price">${rec.price || 'Price not available'}</div>
                    <div class="recommendation-score">${rec.score}%</div>
                `;
                div.addEventListener('click', () => {
                    chrome.tabs.create({ url: rec.url });
                });
                div.style.cursor = 'pointer';
                elements.recommendationsList.appendChild(div);
            });
            elements.recommendationsSection.style.display = 'block';
        } else {
            elements.recommendationsSection.style.display = 'none';
        }
        
        showView('content');
    }
    
    function displayError(message) {
        elements.errorMessage.textContent = message;
        showView('error');
    }
    
    // Event handlers
    async function handleAnalyze() {
        showView('loading');
        
        try {
            currentAnalysis = await analyzeCurrentProduct();
            
            // Store analysis for later use
            try {
                await chrome.storage.local.set({
                    currentAnalysis: currentAnalysis,
                    timestamp: Date.now()
                });
            } catch (storageError) {
                console.warn('Storage error:', storageError);
                // Continue without storage
            }
            
            displayAnalysis(currentAnalysis);
            
        } catch (error) {
            console.error('Analysis error:', error);
            displayError(error.message || 'Failed to analyze product');
        }
    }
    
    function handlePlayVerdict() {
        if (currentAnalysis && currentAnalysis.voice_verdict) {
            // Try to send message to content script first
            if (chrome && chrome.tabs) {
                chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
                    if (tabs && tabs[0]) {
                        chrome.tabs.sendMessage(tabs[0].id, {
                            action: 'playVerdict',
                            text: currentAnalysis.voice_verdict
                        }).catch(() => {
                            // Fallback: use popup's speech synthesis
                            playVerdictFallback();
                        });
                    } else {
                        playVerdictFallback();
                    }
                });
            } else {
                playVerdictFallback();
            }
        }
    }
    
    function playVerdictFallback() {
        if ('speechSynthesis' in window && currentAnalysis && currentAnalysis.voice_verdict) {
            speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(currentAnalysis.voice_verdict);
            utterance.rate = 0.9;
            utterance.pitch = 1;
            speechSynthesis.speak(utterance);
        } else {
            alert('Voice synthesis not available');
        }
    }
    
    function handleViewFull() {
        if (currentProductData) {
            // Navigate to the main page with URL parameter for GET request
            const baseUrl = `${CONFIG.API_BASE_URL}/`;
            const params = new URLSearchParams({
                url: currentProductData.url
            });
            const fullUrl = `${baseUrl}?${params.toString()}`;
            
            console.log('Popup: Opening full analysis report:', fullUrl);
            chrome.tabs.create({ url: fullUrl });
        } else {
            // Fallback: get current tab URL and analyze it
            chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
                if (tabs && tabs[0]) {
                    const analyzeUrl = `${CONFIG.API_BASE_URL}/?url=${encodeURIComponent(tabs[0].url)}`;
                    console.log('Popup: Opening full report for current URL:', analyzeUrl);
                    chrome.tabs.create({ url: analyzeUrl });
                }
            });
        }
    }
    
    // Initialization
    async function initialize() {
        showView('loading');
        
        try {
            // Check if Chrome APIs are available
            if (!chrome || !chrome.tabs) {
                displayError('Chrome extension APIs not available');
                return;
            }
            
            // Get current tab info
            const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
            const currentTab = tabs?.[0];
            
            if (!currentTab) {
                displayError('Unable to access current tab');
                return;
            }
            
            console.log('Popup: Current tab URL:', currentTab.url);
            
            // Check if current URL is supported
            const supportedPatterns = [
                /amazon\.(in|com)/,
                /flipkart\.com/
            ];
            
            const isSupportedSite = supportedPatterns.some(pattern => pattern.test(currentTab.url));
            
            // Additional check for product pages
            const isProductPage = (
                (/amazon\.(in|com).*\/(dp|gp\/product)\/[A-Z0-9]{10}/.test(currentTab.url)) ||
                (/flipkart\.com.*\/p\/[a-zA-Z0-9\-]+/.test(currentTab.url))
            );
            
            console.log('Popup: Is supported site:', isSupportedSite);
            console.log('Popup: Is product page:', isProductPage);
            
            if (!isSupportedSite) {
                console.log('Popup: Not a supported site');
                showView('notProductPage');
                return;
            }
            
            // Try to get product data from content script
            let response = null;
            try {
                response = await chrome.tabs.sendMessage(currentTab.id, {
                    action: 'getProductData'
                });
                console.log('Popup: Content script response:', response);
            } catch (messageError) {
                console.warn('Popup: Content script communication error:', messageError);
                // Wait a bit and try again
                await new Promise(resolve => setTimeout(resolve, 2000));
                try {
                    response = await chrome.tabs.sendMessage(currentTab.id, {
                        action: 'getProductData'
                    });
                    console.log('Popup: Retry response:', response);
                } catch (retryError) {
                    console.warn('Popup: Retry failed:', retryError);
                }
            }
            
            if (response && response.isProductPage && response.productData) {
                currentProductData = response.productData;
                console.log('Popup: Product data received:', currentProductData);
                
                // Check if we have cached analysis
                const stored = await chrome.storage.local.get(['currentAnalysis', 'timestamp']).catch(() => ({}));
                const cacheAge = Date.now() - (stored.timestamp || 0);
                const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes
                
                if (stored.currentAnalysis && cacheAge < CACHE_DURATION) {
                    currentAnalysis = stored.currentAnalysis;
                    displayAnalysis(currentAnalysis);
                } else if (response.analysisResult) {
                    // Use analysis from content script
                    currentAnalysis = response.analysisResult;
                    displayAnalysis(currentAnalysis);
                } else {
                    // Start new analysis
                    await handleAnalyze();
                }
            } else {
                // Not a product page or couldn't get data
                console.log('Popup: Not a product page or no data available');
                showView('notProductPage');
            }
            
        } catch (error) {
            console.error('Popup: Initialization error:', error);
            displayError('Failed to initialize extension: ' + error.message);
        }
    }
    
    // Event listeners
    elements.playVerdictBtn.addEventListener('click', handlePlayVerdict);
    elements.viewFullBtn.addEventListener('click', handleViewFull);
    elements.retryBtn.addEventListener('click', handleAnalyze);
    
    // Message handling
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
        if (request.action === 'updateAnalysis') {
            currentAnalysis = request.analysis;
            displayAnalysis(currentAnalysis);
            sendResponse({ success: true });
        }
    });
    
    // Start the popup
    document.addEventListener('DOMContentLoaded', initialize);
})();