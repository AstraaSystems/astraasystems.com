/**
 * Astraa Systems - Post-Payment Verification Hook (Production Core)
 * Extracts transaction ticket and activates client SaaS access state
 */
(function () {
    window.addEventListener("DOMContentLoaded", function() {
        console.log("[Astraa Verification] Initializing landing token audit...");

        const urlParams = new URLSearchParams(window.location.search);
        const ticketToken = urlParams.get('ticket');

        if (!ticketToken) {
            console.error("[Astraa Verification] Missing token parameter context.");
            return;
        }

        fetch('/api/checkout/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ticket: ticketToken })
        })
        .then(function(response) { return response.json(); })
        .then(function(data) {
            if (data.success === "true") {
                console.log("[Astraa Verification] Payment captured confirmed by Java Gateway.");
                
                // CRITICAL: Elevate the client session permission token to activate the 3+1 services matrix
                sessionStorage.setItem("astraa_saas_active", "true");
                
                // Clean up transient transaction tracking records
                sessionStorage.removeItem("astraa_moneris_ticket");
                
                // Automatically redirect to the dashboard center now that account status is verified
                window.location.href = "../astraaspace/index.html";
            } else {
                console.error("[Astraa Verification] Security audit failed: " + data.error);
            }
        })
        .catch(function(err) {
            console.error("[Astraa Verification] Security pipeline breakdown error:", err);
        });
    });
})();
