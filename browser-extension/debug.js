// Debug helper for Shopper's Verdict Extension
// Add this to any JS file to catch and log errors

(function() {
    'use strict';
    
    // Global error handler
    window.addEventListener('error', function(event) {
        console.error('Extension Error:', {
            message: event.message,
            filename: event.filename,
            lineno: event.lineno,
            colno: event.colno,
            stack: event.error?.stack
        });
    });
    
    // Unhandled promise rejection handler
    window.addEventListener('unhandledrejection', function(event) {
        console.error('Extension Promise Rejection:', {
            reason: event.reason,
            promise: event.promise
        });
    });
    
    // Chrome API availability check
    function checkChromeAPI() {
        const checks = {
            chrome: typeof chrome !== 'undefined',
            runtime: chrome?.runtime ? true : false,
            tabs: chrome?.tabs ? true : false,
            storage: chrome?.storage ? true : false,
            action: chrome?.action ? true : false
        };
        
        console.log('Chrome API Availability:', checks);
        return checks;
    }
    
    // Safe Chrome API wrapper
    window.safeChrome = {
        runtime: {
            onMessage: {
                addListener: function(callback) {
                    if (chrome?.runtime?.onMessage) {
                        chrome.runtime.onMessage.addListener(callback);
                    } else {
                        console.warn('chrome.runtime.onMessage not available');
                    }
                }
            }
        },
        
        tabs: {
            query: function(queryInfo) {
                return new Promise((resolve, reject) => {
                    if (chrome?.tabs?.query) {
                        chrome.tabs.query(queryInfo, (tabs) => {
                            if (chrome.runtime.lastError) {
                                reject(chrome.runtime.lastError);
                            } else {
                                resolve(tabs);
                            }
                        });
                    } else {
                        reject(new Error('chrome.tabs.query not available'));
                    }
                });
            },
            
            sendMessage: function(tabId, message) {
                return new Promise((resolve, reject) => {
                    if (chrome?.tabs?.sendMessage) {
                        chrome.tabs.sendMessage(tabId, message, (response) => {
                            if (chrome.runtime.lastError) {
                                reject(chrome.runtime.lastError);
                            } else {
                                resolve(response);
                            }
                        });
                    } else {
                        reject(new Error('chrome.tabs.sendMessage not available'));
                    }
                });
            }
        },
        
        storage: {
            local: {
                get: function(keys) {
                    return new Promise((resolve, reject) => {
                        if (chrome?.storage?.local?.get) {
                            chrome.storage.local.get(keys, (result) => {
                                if (chrome.runtime.lastError) {
                                    reject(chrome.runtime.lastError);
                                } else {
                                    resolve(result);
                                }
                            });
                        } else {
                            reject(new Error('chrome.storage.local.get not available'));
                        }
                    });
                },
                
                set: function(items) {
                    return new Promise((resolve, reject) => {
                        if (chrome?.storage?.local?.set) {
                            chrome.storage.local.set(items, () => {
                                if (chrome.runtime.lastError) {
                                    reject(chrome.runtime.lastError);
                                } else {
                                    resolve();
                                }
                            });
                        } else {
                            reject(new Error('chrome.storage.local.set not available'));
                        }
                    });
                },
                
                remove: function(keys) {
                    return new Promise((resolve, reject) => {
                        if (chrome?.storage?.local?.remove) {
                            chrome.storage.local.remove(keys, () => {
                                if (chrome.runtime.lastError) {
                                    reject(chrome.runtime.lastError);
                                } else {
                                    resolve();
                                }
                            });
                        } else {
                            reject(new Error('chrome.storage.local.remove not available'));
                        }
                    });
                }
            }
        }
    };
    
    // Run API check on load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', checkChromeAPI);
    } else {
        checkChromeAPI();
    }
    
    console.log('Debug helper loaded for Shopper\'s Verdict Extension');
})();