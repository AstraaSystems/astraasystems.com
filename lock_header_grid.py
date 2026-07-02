#!/usr/bin/env python3
from pathlib import Path
import re

root_html_path = Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git/index.html")

if not root_html_path.exists():
    print("[-] Error: Cannot locate root index.html")
    exit(1)

html_content = root_html_path.read_text(errors='ignore')

# Advanced CSS matrix to group brand elements and match navigation baselines perfectly
bulletproof_grid_style = """
    <style id="production-desktop-layout-fix">
        /* 1. Global Typography Enforcer */
        * {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
            -webkit-font-smoothing: antialiased !important;
            -moz-osx-font-smoothing: grayscale !important;
        }

        /* 2. Main Navigation Bar Grid Row Scaling */
        header, nav, .navbar, .header, body > div:first-of-type {
            display: flex !important;
            flex-direction: row !important;
            justify-content: space-between !important;
            align-items: center !important;
            width: 100% !important;
            max-width: 1200px !important;
            margin: 0 auto !important;
            padding: 18px 24px !important;
            box-sizing: border-box !important;
            background-color: #ffffff !important;
        }

        /* 3. Unified Brand Lockup Matrix (Logo + Text Side-by-Side/Row Layout) */
        header > div:first-child, 
        body > div:first-of-type > div:first-child, 
        .brand-container {
            display: flex !important;
            flex-direction: row !important; /* Lines up logo and text side-by-side */
            align-items: center !important;
            justify-content: flex-start !important;
            gap: 12px !important;
            margin: 0 !important;
            padding: 0 !important;
            height: auto !important;
        }

        /* Prevent intermediate layout elements inside the brand block from breaking lines */
        header > div:first-child div,
        body > div:first-of-type > div:first-child > div {
            display: flex !important;
            flex-direction: column !important; /* Stacks title and subtitle cleanly */
            align-items: flex-start !important;
            justify-content: center !important;
            gap: 1px !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        /* Force logo scaling boundaries */
        header img, body > div:first-of-type img, [class*="logo"] img {
            height: 36px !important;
            width: auto !important;
            margin: 0 !important;
            padding: 0 !important;
            display: block !important;
        }

        /* Core Typography for Brand Subtext */
        header span, header p, 
        body > div:first-of-type > div:first-child span,
        body > div:first-of-type > div:first-child p,
        body > div:first-of-type > div:first-child div {
            font-size: 12px !important;
            line-height: 1.3 !important;
            color: #64748b !important;
            font-weight: 400 !important;
            margin: 0 !important;
            padding: 0 !important;
            white-space: nowrap !important;
        }

        /* Explicitly style the main company title text to stand out next to logo */
        header strong, header h1, .brand-title,
        body > div:first-of-type > div:first-child b {
            font-size: 15px !important;
            font-weight: 700 !important;
            color: #0f172a !important;
            line-height: 1.2 !important;
        }

        /* 4. Navigation Links Base Alignment */
        a, header a, nav a, .navbar a, body > div:first-of-type a {
            text-decoration: none !important;
            color: #475569 !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            display: inline-block !important;
            margin: 0 16px !important;
            padding: 6px 0 !important;
            transition: color 0.15s ease !important;
            vertical-align: middle !important;
        }
        
        a:hover {
            color: #2563eb !important;
        }

        /* Premium Call-To-Action Workspace Button */
        a[href*="workspace"], body > div:first-of-type a:last-of-type {
            background-color: #0f172a !important;
            color: #ffffff !important;
            padding: 9px 18px !important;
            border-radius: 6px !important;
            margin-left: 20px !important;
            font-weight: 500 !important;
        }

        a[href*="workspace"]:hover, body > div:first-of-type a:last-of-type:hover {
            background-color: #1e293b !important;
        }

        /* 5. Content Layout Constraints */
        body {
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
            overflow-x: hidden !important;
            background-color: #ffffff !important;
        }
    </style>
"""

# Strip out older style injection filters
if "production-desktop-layout-fix" in html_content:
    html_content = re.sub(r'<style id="production-desktop-layout-fix">.*?</style>', '', html_content, flags=re.DOTALL)

# Inject the clean horizontal row configuration rules
if "</head>" in html_content:
    updated_html = html_content.replace("</head>", f"{bulletproof_grid_style}\n</head>")
    root_html_path.write_text(updated_html)
    print("[+] SUCCESS: Horizontal flex layout grid applied successfully.")
else:
    print("[-] Error: Unable to locate structural closing </head> block.")
