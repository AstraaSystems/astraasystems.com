/**
 * Astraa Systems - Post-Payment Verification Hook
 * Extracts transaction ticket from url context and requests server validation
 */
(function () {
    window.addEventListener("DOMContentLoaded", function() {
        console.log("[Astraa Verification] Initializing landing token audit...");

        // 1. Grab the ticket parameter from the current browser URL bar
        const urlParams = new URLSearchParams(window.location.search);
        const ticketToken = urlParams.get('ticket');

        if (!ticketToken) {
            console.error("[Astraa Verification] Missing token parameter context.");
            document.getElementById("statusText").textContent = "Error: No transaction identity token found.";
            return;
        }

        // 2. Transmit token securely up to your new validation servlet handler
        fetch('/api/checkout/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ticket: ticketToken })
        })
        .then(function(response) { return response.json(); })
        .then(function(data) {
            const statusDisplay = document.getElementById("statusText") || document.body;
            
            if (data.success === "true") {
                console.log("[Astraa Verification] Payment captured! Clearing session states.");
                statusDisplay.textContent = "Payment Verified Successfully! Activating your subscription bundle...";
                
                // Clear out local session caches now that processing is final
                sessionStorage.removeItem("astraa_moneris_ticket");
            } else {
                statusDisplay.textContent = "Payment Verification Warning: " + data.error;
            }
        })
        .catch(function(err) {
            console.error("[Astraa Verification] Security pipeline error:", err);
        });
    });
})();
