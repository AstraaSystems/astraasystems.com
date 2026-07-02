#!/usr/bin/env python3
from pathlib import Path
import re

root_html_path = Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git/index.html")

if not root_html_path.exists():
    print("[-] Error: Cannot locate root index.html")
    exit(1)

html_content = root_html_path.read_text(errors='ignore')

# Premium corporate navigation layout rules
refined_style = """
    <style id="production-desktop-layout-fix">
        /* Main Navigation Bar Alignment */
        header, nav, .header, .navbar, #header {
            display: flex !important;
            flex-direction: row !important;
            justify-content: space-between !important;
            align-items: center !important;
            width: 100% !important;
            max-width: 1200px !important;
            margin: 0 auto !important;
            padding: 24px !important;
            box-sizing: border-box !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
            -webkit-font-smoothing: antialiased !important;
        }
        
        /* Clean up the branding text under/around the logo */
        header div, header span, .brand-text {
            font-size: 13px !important;
            line-height: 1.4 !important;
            color: #64748b !important; /* Professional muted slate */
            margin: 0 !important;
        }
        
        /* Make the main brand name slightly prominent if it exists as text */
        header text, header strong {
            color: #0f172a !important;
            font-weight: 600 !important;
            font-size: 15px !important;
        }
        
        /* Horizontal Link Grouping & Spacing */
        header nav, .nav-links-container {
            display: flex !important;
            flex-direction: row !important;
            align-items: center !important;
            gap: 28px !important;
        }
        
        /* Modern Minimalist Navigation Links */
        header a, nav a, .header a, .navbar a {
            display: inline-block !important;
            text-decoration: none !important;
            color: #334155 !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            margin: 0 !important;
            white-space: nowrap !important;
            transition: color 0.15s ease !important;
        }
        
        /* Interactive Hover State */
        header a:hover, nav a:hover {
            color: #2563eb !important; /* Clean corporate blue */
        }
        
        /* Global Desktop View Constraint */
        body {
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
            overflow-x: hidden !important;
            background-color: #ffffff !important;
        }
        
        .container, .wrapper, main, #main-content, section {
            max-width: 1200px !important;
            margin: 0 auto !important;
            width: 100% !important;
            box-sizing: border-box !important;
        }
    </style>
"""

# Completely strip out the previous draft layout fix
if "production-desktop-layout-fix" in html_content:
    html_content = re.sub(r'<style id="production-desktop-layout-fix">.*?</style>', '', html_content, flags=re.DOTALL)

# Inject the polished design blocks into the head
if "</head>" in html_content:
    updated_html = html_content.replace("</head>", f"{refined_style}\n</head>")
    root_html_path.write_text(updated_html)
    print("[+] SUCCESS: Premium desktop navigation overrides successfully built into the root layout.")
else:
    print("[-] Error: Could not locate closing </head> tag.")
