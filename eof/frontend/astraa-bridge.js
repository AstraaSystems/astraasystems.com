/**
 * Astraa Systems - Moneris Bridge Link
 * Coordinates server-side ticket generation with the June 19 Canvas Layout Wrapper
 */
(function () {
    window.launchSecureAstraaCheckout = function() {
        console.log("[Astraa UI] Initiating contact with secure Java ticket generator endpoint...");

        // 1. Contact your new backend controller to get a single-use token safely
        fetch('/api/checkout/initiate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(function(response) {
            if (!response.ok) {
                throw new Error("Network transaction registration failed: Server responded with status " + response.status);
            }
            return response.json();
        })
        .then(function(data) {
            if (data.success === "true" && data.ticket) {
                console.log("[Astraa UI] Server ticket grabbed successfully: " + data.ticket);

                // 2. Cache it securely inside sessionStorage to satisfy the June 19 wrapper state checks
                sessionStorage.setItem("astraa_moneris_ticket", data.ticket);

                // 3. Mount the payment frame layout directly using your original framework listeners
                return window.astraaEnsureMonerisCheckoutReady()
                    .then(function(checkout) {
                        console.log("[Astraa UI] Mounting standalone checkout canvas window wrapper frame.");
                        checkout.startCheckout(data.ticket);
                    });
            } else {
                throw new Error(data.error || "Unknown validation problem reported by payment gateway.");
            }
        })
        .catch(function(error) {
            console.error("[Astraa UI] Critical payment initialization breakdown:", error);
            alert("Unable to establish secure payment channel: " + error.message);
        });
    };
})();
