#!/usr/bin/env python3
from pathlib import Path
import re

root_html_path = Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git/index.html")

if not root_html_path.exists():
    print("[-] Error: Cannot locate root index.html")
    exit(1)

html_content = root_html_path.read_text(errors='ignore')

# Precision CSS engine that preserves nested layout div structural mechanics
bulletproof_style = """
    <style id="production-desktop-layout-fix">
        /* 1. Global Modern Typeface Enforcer */
        * {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
            -webkit-font-smoothing: antialiased !important;
            -moz-osx-font-smoothing: grayscale !important;
        }

        /* 2. Top-Level Flex Row Matrix */
        header, nav, .navbar, .header, body > div:first-of-type {
            display: flex !important;
            flex-direction: row !important;
            justify-content: space-between !important;
            align-items: center !important;
            max-width: 1200px !important;
            margin: 0 auto !important;
            padding: 24px 20px !important;
            box-sizing: border-box !important;
            background-color: #ffffff !important;
        }

        /* 3. Safe Brand Stacking (Stops text from dropping or floating away) */
        .brand, [class*="logo"]-container, header > div:first-child, body > div:first-of-type > div:first-child {
            display: flex !important;
            flex-direction: column !important;
            align-items: flex-start !important;
            justify-content: center !important;
            gap: 2px !important;
            margin: 0 !important;
            padding: 0 !important;
            height: auto !important;
        }

        /* Force logo proportions and reset bounding box padding */
        header img, body > div:first-of-type img, [class*="logo"] img {
            height: 34px !important;
            width: auto !important;
            margin: 0 0 2px 0 !important;
            display: block !important;
        }

        /* Target text nodes explicitly instead of targeting generic wrapper divs */
        header span, header p, 
        body > div:first-of-type > div:first-child text,
        body > div:first-of-type > div:first-child p,
        body > div:first-of-type > div:first-child span {
            font-size: 12px !important;
            line-height: 1.4 !important;
            color: #64748b !important;
            font-weight: 400 !important;
            margin: 0 !important;
            padding: 0 !important;
            display: block !important;
        }

        /* 4. Link Spacing & Navigation Alignment */
        a, header a, nav a, .navbar a, body > div:first-of-type a {
            text-decoration: none !important;
            text-decoration-line: none !important;
            color: #334155 !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            display: inline-block !important;
            margin: 0 14px !important;
            padding: 4px 2px !important;
            transition: color 0.15s ease !important;
        }
        
        a:hover {
            color: #2563eb !important;
        }

        /* Separate and stylize the Workspace Action CTA Button */
        a[href*="workspace"], body > div:first-of-type a:last-of-type {
            background-color: #0f172a !important; /* Premium Dark Slate */
            color: #ffffff !important;
            padding: 8px 16px !important;
            border-radius: 6px !important;
            margin-left: 24px !important;
            font-weight: 500 !important;
        }

        a[href*="workspace"]:hover, body > div:first-of-type a:last-of-type:hover {
            background-color: #1e293b !important;
        }

        /* 5. Root Document Constants */
        body {
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
            overflow-x: hidden !important;
            background-color: #ffffff !important;
        }
    </style>
"""

# Strip out previous layout attempts
if "production-desktop-layout-fix" in html_content:
    html_content = re.sub(r'<style id="production-desktop-layout-fix">.*?</style>', '', html_content, flags=re.DOTALL)

# Inject the clean targeted code block
if "</head>" in html_content:
    updated_html = html_content.replace("</head>", f"{bulletproof_style}\n</head>")
    root_html_path.write_text(updated_html)
    print("[+] SUCCESS: High-specificity layout metrics injected cleanly.")
else:
    print("[-] Error: Could not locate closing </head> tag.")
