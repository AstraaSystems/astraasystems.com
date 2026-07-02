#!/usr/bin/env python3
from pathlib import Path
import re

root_html_path = Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git/index.html")

if not root_html_path.exists():
    print("[-] Error: Cannot locate root index.html")
    exit(1)

html_content = root_html_path.read_text(errors='ignore')

# Absolute layout enforcer targeting raw elements and positions
brilliant_style = """
    <!-- Desktop Structural Layout Hotfix -->
    <style id="production-desktop-layout-fix">
        /* 1. Global Typography Enforcer - Apply to everything */
        html, body, div, p, span, a, h1, h2, h3 {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
            -webkit-font-smoothing: antialiased !important;
            -moz-osx-font-smoothing: grayscale !important;
        }

        /* 2. Top-Level Layout Row (Logo/Branding left, Links right) */
        body > div:first-of-type, header, nav, .navbar, .header-container {
            display: flex !important;
            flex-direction: row !important;
            justify-content: space-between !important;
            align-items: center !important;
            max-width: 1200px !important;
            margin: 0 auto !important;
            padding: 20px !important;
            box-sizing: border-box !important;
        }

        /* 3. Strip Underlines and Style ALL Top-Level Navigation Links */
        a {
            text-decoration: none !important;
            transition: color 0.15s ease !important;
        }
        
        /* Focus specifically on the header link collection */
        body > div:first-of-type a, header a, nav a, .navbar a {
            color: #334155 !important; /* Modern slate grey */
            font-size: 14px !important;
            font-weight: 500 !important;
            display: inline-block !important;
            margin: 0 14px !important;
        }

        body > div:first-of-type a:hover, header a:hover, nav a:hover, .navbar a:hover {
            color: #2563eb !important; /* Premium corporate blue */
        }

        /* 4. Fix and Beautify the Stacked Branding Text under the Logo */
        body > div:first-of-type div, header div, .brand-text {
            font-size: 12px !important;
            color: #64748b !important;
            line-height: 1.4 !important;
            font-weight: 400 !important;
        }

        /* Enforce desktop width parameters globally */
        .container, .wrapper, main, section, [class*="hero"] {
            max-width: 1200px !important;
            margin: 0 auto !important;
            width: 100% !important;
            box-sizing: border-box !important;
        }
    </style>
"""

# Wipe out the previous iteration of the style block
if "production-desktop-layout-fix" in html_content:
    html_content = re.sub(r'<style id="production-desktop-layout-fix">.*?</style>', '', html_content, flags=re.DOTALL)

# Inject the comprehensive premium rules right into the head block
if "</head>" in html_content:
    updated_html = html_content.replace("</head>", f"{brilliant_style}\n</head>")
    root_html_path.write_text(updated_html)
    print("[+] SUCCESS: Broad-spectrum typography and link engine successfully injected.")
else:
    print("[-] Error: Could not locate closing </head> tag.")
