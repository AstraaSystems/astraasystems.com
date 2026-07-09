/**
 * Astraa Systems - Moneris Core Object Framework
 * Preserved Baseline Configuration
 */
(function() {
    window.astraaEnsureMonerisCheckoutReady = function() {
        return new Promise(function(resolve, reject) {
            try {
                if (!window.monerisCheckout) {
                    console.log("[Astraa Core] Appending official Moneris global runtime script...");
                    const monerisScript = document.createElement("script");
                    
                    // Production Moneris Live Gateway Endpoint
                    monerisScript.src = "https://gateway.moneris.com/chkt/js/chkt_v1.00.js"; 
                    
                    monerisScript.onload = function() {
                        initializeAstraaWrapper(resolve);
                    };
                    monerisScript.onerror = function() {
                        reject(new Error("Failed to download official Moneris client library dependencies."));
                    };
                    document.head.appendChild(monerisScript);
                } else {
                    initializeAstraaWrapper(resolve);
                }
            } catch (err) {
                reject(err);
            }
        });
    };

    function initializeAstraaWrapper(resolve) {
        console.log("[Astraa Core] Configuring canvas orchestration wrapper targets...");
        const checkoutInstance = new monerisCheckout();
        checkoutInstance.setCheckoutDiv("monerisCheckout");
        
        checkoutInstance.setCallback("page_loaded", function(data) { console.log("Moneris Loaded:", data); });
        checkoutInstance.setCallback("cancel_transaction", function() { alert("Transaction Canceled"); });
        checkoutInstance.setCallback("error_event", function(data) { console.error("Moneris Error:", data); });

        resolve(checkoutInstance);
    }
})();
