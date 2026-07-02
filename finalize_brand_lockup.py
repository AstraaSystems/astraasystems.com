#!/usr/bin/env python3
from pathlib import Path
import re

root_html_path = Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git/index.html")

if not root_html_path.exists():
    print("[-] Error: Cannot locate root index.html")
    exit(1)

html_content = root_html_path.read_text(errors='ignore')

# Precision layout overrides to lock logo, text, and navigation links into place
premium_header_style = """
    <style id="production-desktop-layout-fix">
        /* 1. Global Core Reset & Modern Typography */
        * {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
            -webkit-font-smoothing: antialiased !important;
            -moz-osx-font-smoothing: grayscale !important;
        }

        /* 2. Main Navigation Bar Flex Grid Baseline */
        header, nav, .navbar, .header, body > div:first-of-type {
            display: flex !important;
            flex-direction: row !important;
            justify-content: space-between !important;
            align-items: center !important;
            max-width: 1200px !important;
            margin: 0 auto !important;
            padding: 20px 24px !important;
            box-sizing: border-box !important;
            background-color: #ffffff !important;
        }

        /* 3. Tight Brand Lockup (Logo + Text Container Fix) */
        header > div:first-child, body > div:first-of-type > div:first-child, .brand-container {
            display: flex !important;
            flex-direction: column !important;
            align-items: flex-start !important;
            justify-content: flex-start !important;
            gap: 2px !important; /* Closes the giant vertical gap completely */
            margin: 0 !important;
            padding: 0 !important;
        }

        /* Force logo image proportions */
        header img, body > div:first-of-type img, [class*="logo"] img {
            height: 32px !important;
            width: auto !important;
            margin: 0 0 4px 0 !important;
            display: block !important;
        }

        /* Format branding copy precisely without letting it affect sibling wrappers */
        .brand-text, 
        header > div:first-child span, 
        header > div:first-child p,
        body > div:first-of-type > div:first-child div {
            font-size: 12px !important;
            line-height: 1.4 !important;
            color: #64748b !important; /* Modern slate grey */
            font-weight: 400 !important;
            margin: 0 !important;
            padding: 0 !important;
            display: block !important;
        }

        /* 4. Navigation Links Structure & Dynamic Spacing */
        a, header a, nav a, .navbar a, body > div:first-of-type a {
            text-decoration: none !important;
            text-decoration-line: none !important;
            color: #334155 !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            display: inline-block !important;
            margin: 0 14px !important;
            padding: 6px 2px !important;
            transition: color 0.15s ease !important;
        }
        
        a:hover {
            color: #2563eb !important; /* Clean corporate blue hover state */
        }

        /* Highlight the 'Open Workspace' anchor link as a professional action button */
        a[href*="workspace"], body > div:first-of-type a:last-of-type {
            background-color: #0f172a !important; /* Slate 900 */
            color: #ffffff !important;
            padding: 8px 16px !important;
            border-radius: 6px !important;
            margin-left: 20px !important;
        }

        a[href*="workspace"]:hover, body > div:first-of-type a:last-of-type:hover {
            background-color: #1e293b !important;
            color: #ffffff !important;
        }

        /* 5. Production Content Constancy Layout */
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

# Completely strip any remnants of the older hotfix tags
if "production-desktop-layout-fix" in html_content:
    html_content = re.sub(r'<style id="production-desktop-layout-fix">.*?</style>', '', html_content, flags=re.DOTALL)

# Insert the clean layout rules directly into the head block
if "</head>" in html_content:
    updated_html = html_content.replace("</head>", f"{premium_header_style}\n</head>")
    root_html_path.write_text(updated_html)
    print("[+] SUCCESS: Structural brand alignment matrix successfully written to index.html.")
else:
    print("[-] Error: Unable to locate closing </head> tag.")
