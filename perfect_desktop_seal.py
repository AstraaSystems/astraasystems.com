#!/usr/bin/env python3
from pathlib import Path
import re

root_html_path = Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git/index.html")

if not root_html_path.exists():
    print("[-] Error: Cannot locate root index.html")
    exit(1)

html_content = root_html_path.read_text(errors='ignore')

# The definitive style override engine
ultimate_style = """
    <style id="production-desktop-layout-fix">
        /* 1. Global Typography & Reset Enforcer */
        * {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
            -webkit-font-smoothing: antialiased !important;
            -moz-osx-font-smoothing: grayscale !important;
        }

        /* 2. Radical Link Reset - Strips underlines and forces modern slate color */
        a, a *, li a, nav a, .navbar a, header a {
            text-decoration: none !important;
            text-decoration-line: none !important;
            color: #334155 !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            transition: color 0.15s ease-time !important;
        }
        
        a:hover, a:hover * {
            color: #2563eb !important; /* Premium Blue */
        }

        /* 3. Top-Level Main Navigation Wrapper */
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

        /* 4. Brand Grouping (Forces Logo and Subtext into a clean alignment block) */
        .brand, [class*="logo"], header > div:first-child, body > div:first-of-type > div:first-child {
            display: flex !important;
            flex-direction: column !important;
            align-items: flex-start !important;
            gap: 4px !important;
        }

        /* Clean up branding metadata text formatting */
        header div, .brand-text, body > div:first-of-type div {
            font-size: 12px !important;
            line-height: 1.4 !important;
            color: #64748b !important;
            font-weight: 400 !important;
        }

        /* 5. Navigation Links Group Container */
        header ul, nav ul, .nav-links, body > div:first-of-type div:last-child {
            display: flex !important;
            flex-direction: row !important;
            align-items: center !important;
            gap: 28px !important;
            list-style: none !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        /* Global Viewport Constraints */
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

# Clean up any past style tags from this process
if "production-desktop-layout-fix" in html_content:
    html_content = re.sub(r'<style id="production-desktop-layout-fix">.*?</style>', '', html_content, flags=re.DOTALL)

# Inject the new master style block
if "</head>" in html_content:
    updated_html = html_content.replace("</head>", f"{ultimate_style}\n</head>")
    root_html_path.write_text(updated_html)
    print("[+] SUCCESS: Master design tokens and layout overrides forced into root index.html")
else:
    print("[-] Error: Closing </head> tag missing.")
