document.addEventListener('DOMContentLoaded', () => {
    // Target the specific form/button layout of the testing portal
    const loginBtn = document.querySelector('button, input[type="submit"]');
    const emailInput = document.querySelector('input[type="email"], input[placeholder="name@company.com"]');
    const accessCodeInput = document.querySelector('input[type="password"], input[placeholder="Enter access code"]');
    const productSelect = document.querySelector('select');

    // Handle session clearance if the user clicks "Clear Session"
    const buttons = document.querySelectorAll('button, input[type='button']');
    buttons.forEach(btn => {
        if (btn.textContent.includes('Clear Session')) {
            btn.onclick = () => {
                localStorage.removeItem('astraa_session');
                alert('Session Cleared.');
            };
        }
    });

    if (loginBtn && emailInput) {
        loginBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const email = emailInput.value.trim();
            const accessCode = accessCodeInput ? accessCodeInput.value.trim() : '';
            const simulatedProduct = productSelect ? productSelect.value : 'all';

            if (email) {
                // Save the session data including the product selected for evaluation
                const sessionData = {
                    user: email.split('@')[0],
                    email: email,
                    role: "Testing Operator",
                    simulatedModule: simulatedProduct,
                    token: "ASTRAA-TEST-SESSION-" + Date.now()
                };
                localStorage.setItem('astraa_session', JSON.stringify(sessionData));
                
                // Redirect directly into the motherboard workspace directory
                window.location.href = 'workspace/index.html';
            } else {
                alert('Please enter a valid Account Email to test.');
            }
        });
    }
});

function logoutAstraa() {
    localStorage.removeItem('astraa_session');
    // Bounce back out to the main test gateway route
    window.location.href = '../workspace-test-login.html';
}
