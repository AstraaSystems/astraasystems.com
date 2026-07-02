#!/usr/bin/env python3
from pathlib import Path
import re

root_html_path = Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git/index.html")

if not root_html_path.exists():
    print("[-] Error: Cannot locate root index.html")
    exit(1)

html_content = root_html_path.read_text(errors='ignore')

# Premium CSS layout engine to isolate the header and let the main content breathe
full_width_style = """
    <style id="production-desktop-layout-fix">
        /* 1. Global Typography & Reset Engine */
        * {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
            -webkit-font-smoothing: antialiased !important;
            -moz-osx-font-smoothing: grayscale !important;
            box-sizing: border-box !important;
        }

        body {
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
            overflow-x: hidden !important;
            background-color: #ffffff !important;
        }

        /* 2. Isolated Header Navigation Bar (Will not restrict the main body wrapper) */
        header, nav, .navbar, .header {
            display: flex !important;
            flex-direction: row !important;
            justify-content: space-between !important;
            align-items: center !important;
            width: 100% !important;
            max-width: 1280px !important;
            margin: 0 auto !important;
            padding: 20px 40px !important;
            background-color: #ffffff !important;
        }

        /* Defensive styling if a top-level div is used as a header wrapper */
        body > div:first-of-type {
            width: 100% !important;
            max-width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            display: block !important; /* Forces it to act as a full-width layout container */
        }

        /* 3. High-Specificity Brand Lockup (Logo + Title Stacked) */
        .brand, [class*="logo"]-container, header > div:first-child {
            display: flex !important;
            flex-direction: row !important;
            align-items: center !important;
            gap: 12px !important;
            height: auto !important;
        }

        /* Tight vertical arrangement for branding text */
        header > div:first-child div, .brand-text-stack {
            display: flex !important;
            flex-direction: column !important;
            align-items: flex-start !important;
            gap: 2px !important;
        }

        header img, [class*="logo"] img {
            height: 38px !important;
            width: auto !important;
            display: block !important;
        }

        /* Fine-tuned Corporate Identity Text */
        .brand-title, header strong, header h1 {
            font-size: 15px !important;
            font-weight: 700 !important;
            color: #0f172a !important;
            line-height: 1.2 !important;
            margin: 0 !important;
        }

        .brand-subtitle, header span, header p {
            font-size: 11px !important;
            line-height: 1.2 !important;
            color: #64748b !important;
            font-weight: 400 !important;
            margin: 0 !important;
            white-space: nowrap !important;
        }

        /* 4. Elegant Navigation Menu Links */
        a, header a, nav a {
            text-decoration: none !important;
            color: #475569 !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            margin: 0 16px !important;
            padding: 6px 0 !important;
            transition: color 0.15s ease !important;
        }
        
        a:hover {
            color: #2563eb !important;
        }

        /* Premium Dark Action Call-to-Action */
        a[href*="workspace"], .cta-button {
            background-color: #0f172a !important;
            color: #ffffff !important;
            padding: 10px 20px !important;
            border-radius: 6px !important;
            margin-left: 16px !important;
            font-weight: 500 !important;
            display: inline-block !important;
        }

        a[href*="workspace"]:hover {
            background-color: #1e293b !important;
        }

        /* 5. Main Content Component Layout Safeties (Restores your beautiful wide cards) */
        main, .main-content, div[class*="hero"], div[class*="wrapper"] {
            width: 100% !important;
            max-width: 1280px !important;
            margin: 0 auto !important;
            padding: 40px 24px !important;
        }
    </style>
"""

# Completely strip out old desktop layout hotfixes
if "production-desktop-layout-fix" in html_content:
    html_content = re.sub(r'<style id="production-desktop-layout-fix">.*?</style>', '', html_content, flags=re.DOTALL)

# Inject the clean isolated full-width ruleset
if "</head>" in html_content:
    updated_html = html_content.replace("</head>", f"{full_width_style}\n</head>")
    root_html_path.write_text(updated_html)
    print("[+] SUCCESS: Isolated header engine built. Page structural widths restored.")
else:
    print("[-] Error: Unable to locate closing </head> block.")
