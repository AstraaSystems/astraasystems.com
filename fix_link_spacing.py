#!/usr/bin/env python3
from pathlib import Path
import re

root_html_path = Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git/index.html")

if not root_html_path.exists():
    print("[-] Error: Cannot locate root index.html")
    exit(1)

html_content = root_html_path.read_text(errors='ignore')

# Premium spacing layout engine
spacing_style = """
    <style id="production-desktop-layout-fix">
        /* 1. Global Modern Sans-Serif Base */
        * {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
            -webkit-font-smoothing: antialiased !important;
            -moz-osx-font-smoothing: grayscale !important;
        }

        /* 2. Primary Navigation Header Wrapper */
        header, nav, .navbar, .header, body > div:first-of-type {
            display: flex !important;
            flex-direction: row !important;
            justify-content: space-between !important;
            align-items: center !important;
            max-width: 1200px !important;
            margin: 0 auto !important;
            padding: 24px 20px !important;
            box-sizing: border-box !important;
        }

        /* 3. Un-smash Links: Force individual margins directly on anchor tags */
        a, header a, nav a, .navbar a, body > div:first-of-type a {
            text-decoration: none !important;
            text-decoration-line: none !important;
            color: #334155 !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            display: inline-block !important;
            margin-left: 16px !important;
            margin-right: 16px !important;
            padding: 4px 2px !important;
            transition: color 0.15s ease !important;
        }
        
        a:hover {
            color: #2563eb !important;
        }

        /* 4. Format and align the corporate branding block under the logo */
        .brand, [class*="logo"], header > div:first-child, body > div:first-of-type > div:first-child {
            display: flex !important;
            flex-direction: column !important;
            align-items: flex-start !important;
            text-align: left !important;
        }

        /* Style the subtext explicitly so it doesn't look like raw markup */
        header div, .brand-text, body > div:first-of-type div {
            font-size: 12px !important;
            line-height: 1.5 !important;
            color: #64748b !important;
            font-weight: 400 !important;
            margin: 0 !important;
        }

        /* 5. Keep page layout bounded nicely */
        body {
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
            overflow-x: hidden !important;
            background-color: #ffffff !important;
        }
        
        .container, .wrapper, main, section {
            max-width: 1200px !important;
            margin: 0 auto !important;
            width: 100% !important;
            box-sizing: border-box !important;
        }
    </style>
"""

# Clean out old hotfix style tags
if "production-desktop-layout-fix" in html_content:
    html_content = re.sub(r'<style id="production-desktop-layout-fix">.*?</style>', '', html_content, flags=re.DOTALL)

# Inject the fixed styling rules
if "</head>" in html_content:
    updated_html = html_content.replace("</head>", f"{spacing_style}\n</head>")
    root_html_path.write_text(updated_html)
    print("[+] SUCCESS: Link isolation and text padding styles deployed locally.")
else:
    print("[-] Error: Could not locate closing </head> tag.")
