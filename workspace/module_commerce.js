const CommerceModule = {
    render: () => `
        <div class="purchase-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px;">
            <div class="bundle-card" style="background: var(--bg-panel); border: var(--border); padding: 30px; border-radius: var(--radius); text-align: center;">
                <h3>Modular Access</h3>
                <p style="color: var(--text-secondary); font-size: 0.9rem;">Single tool deployment for targeted operations.</p>
                <h2 style="color: var(--brand-blue); margin: 20px 0;">$499<span style="font-size: 0.8rem; color: var(--text-secondary);">/mo</span></h2>
                <button class="cta-button" onclick="alert('Initializing Checkout: Modular Access Tier')">Select Module</button>
            </div>
            <div class="bundle-card" style="background: var(--bg-panel); border: 2px solid var(--brand-blue); padding: 30px; border-radius: var(--radius); text-align: center; box-shadow: 0 0 20px var(--brand-glow);">
                <span style="background: var(--brand-blue); color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: bold;">MOST POPULAR</span>
                <h3 style="margin-top: 15px;">Astraa Full Suite</h3>
                <p style="color: var(--text-secondary); font-size: 0.9rem;">Complete access to all 9 integrated modules.</p>
                <h2 style="color: var(--brand-blue); margin: 20px 0;">$2,499<span style="font-size: 0.8rem; color: var(--text-secondary);">/mo</span></h2>
                <button class="cta-button" onclick="alert('Initializing Checkout: Full Suite Bundle')">Deploy Suite</button>
            </div>
            <div class="bundle-card" style="background: var(--bg-panel); border: var(--border); padding: 30px; border-radius: var(--radius); text-align: center;">
                <h3>Custom Enterprise</h3>
                <p style="color: var(--text-secondary); font-size: 0.9rem;">Tailored sovereign infrastructure & local architecture.</p>
                <h2 style="color: var(--text-primary); margin: 20px 0;">Custom</h2>
                <button class="cta-button" style="background: transparent; border: 1px solid var(--brand-blue);" onclick="alert('Routing to Engineering Architecture Team...')">Inquire</button>
            </div>
        </div>
    `
};
