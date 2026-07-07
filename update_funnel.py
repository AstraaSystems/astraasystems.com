import os
import re

# Core marketing files to update navigation items on
files = ["index.html", "tools.html", "pricing.html", "support.html", "contact.html", "register.html"]

for filename in files:
    if os.path.exists(filename):
        with open(filename, "r") as f:
            content = f.read()
        
        # 1. Update the visible CTA text and target paths to Buy Now
        content = content.replace('href="/register.html">Register', 'href="/buynow.html">Buy Now')
        content = content.replace('Login / Register', 'Buy Now')
        content = content.replace('href="/login.html"', 'href="/buynow.html"')
        content = content.replace('href="/register.html"', 'href="/buynow.html"')
        
        with open(filename, "w") as f:
            f.write(content)
        print(f"Updated funnel paths on: {filename}")

# 2. Create the brand new optimized buynow.html with proper asset scaling links
buy_now_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Astraa Systems — Secure Checkout</title>
  <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>

<nav class="nav">
  <div class="container nav-inner">
    <a class="brand" href="/index.html">
      <img src="/assets/images/astraa_logo.png" alt="Astraa Systems logo" />
      Astraa Systems
    </a>
    <div class="nav-links">
      <a href="/index.html">Home</a>
      <a href="/tools.html">Tools</a>
      <a href="/pricing.html">Pricing</a>
      <a href="/faq.html">FAQ / Support</a>
      <a href="/astraaspace/login.html">Astraa Space</a>
      <a href="/contact.html">Custom Packages</a>
      <a class="nav-cta" href="/buynow.html">Buy Now</a>
    </div>
  </div>
</nav>

<main class="page">
  <div class="container layout" style="max-width: 1100px; margin: 40px auto; padding: 0 24px; display: grid; grid-template-columns: 1fr 1fr; gap: 48px; align-items: start;">
    
    <section class="card" style="padding: 32px;">
      <h2 style="font-size: 28px; font-weight: 700; margin-bottom: 12px; color: #0f172a;">Complete your Astraa Setup</h2>
      <p style="color: #64748b; font-size: 16px; line-height: 1.6; margin-bottom: 24px;">
        Deploy precision automation, analytics engine tools, and optimized workspace management environments directly onto your operations workflow.
      </p>
      
      <div style="background: #f8fafc; border-radius: 8px; padding: 20px; border: 1px solid #e2e8f0;">
        <h4 style="font-weight: 600; margin-bottom: 8px; color: #334155;">Included with Deployment:</h4>
        <ul style="padding-left: 20px; color: #475569; font-size: 14px; display: flex; flex-direction: column; gap: 8px;">
          <li>Full production workspace environment access</li>
          <li>Astraa Estimator toolkit integration</li>
          <li>Encrypted data vault & resource logging telemetry</li>
        </ul>
      </div>
    </section>

    <section class="card" style="padding: 32px;">
      <h3 style="font-size: 20px; font-weight: 600; margin-bottom: 20px; color: #0f172a;">Account Registration</h3>
      <form style="display: flex; flex-direction: column; gap: 16px;">
        <div style="display: flex; flex-direction: column; gap: 6px;">
          <label style="font-size: 14px; font-weight: 600; color: #334155;">Full Name</label>
          <input type="text" placeholder="Your Name" style="padding: 10px 14px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px;">
        </div>
        <div style="display: flex; flex-direction: column; gap: 6px;">
          <label style="font-size: 14px; font-weight: 600; color: #334155;">Email Address</label>
          <input type="email" placeholder="you@example.com" style="padding: 10px 14px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px;">
        </div>
        <button type="submit" style="background: #6366f1; color: white; border: none; padding: 14px; border-radius: 6px; font-weight: 600; cursor: pointer; margin-top: 12px; font-size: 15px;">Continue to Payment</button>
      </form>
    </section>

  </div>
</main>

</body>
</html>
"""

with open("buynow.html", "w") as f:
    f.write(buy_now_content)
print("Created layout-optimized buynow.html.")
