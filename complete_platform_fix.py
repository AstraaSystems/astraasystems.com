#!/usr/bin/env python3
from pathlib import Path
import re

repo_root = Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git")
root_html_path = repo_root / "index.html"
cname_path = repo_root / "CNAME"

# 1. Fix the Deployment Pipeline Block (Inject Custom Domain CNAME)
print("[+] Generating root CNAME tracking record...")
cname_path.write_text("astraasystems.com\n")

# 2. Fix the Layout Constraints inside index.html
if not root_html_path.exists():
    print("[-] Error: Cannot locate root index.html")
    exit(1)

html_content = root_html_path.read_text(errors='ignore')

# Premium responsive widescreen layout matrix
bulletproof_style = """
    <!-- Desktop Structural Layout Hotfix -->
    <style id="production-desktop-layout-fix">
        /* Global Reset & Typography */
        * {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
            -webkit-font-smoothing: antialiased !important;
            box-sizing: border-box !important;
        }

        body {
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
            overflow-x: hidden !important;
            background-color: #ffffff !important;
        }

        /* Full-Width Layout Restoration (Stops the page from shrinking into a narrow column) */
        body > div, main, .main-content, #root {
            width: 100% !important;
            max-width: 100% !important;
            margin: 0 auto !important;
            transform: none !important;
        }

        /* Centered Inner Component Containers */
        .hero, section, main > div, .content-wrapper, [class*="Card"] {
            max-width: 1200px !important;
            margin: 0 auto !important;
            width: 100% !important;
        }

        /* Header Navigation Grid Baseline Alignment */
        header, nav, .navbar, .header {
            display: flex !important;
            flex-direction: row !important;
            justify-content: space-between !important;
            align-items: center !important;
            width: 100% !important;
            max-width: 1200px !important;
            margin: 0 auto !important;
            padding: 24px 20px !important;
            background-color: #ffffff !important;
        }

        /* Prevent Brand Metadata Text from Stack-Wrapping Vulnerabilities */
        header > div:first-child, .brand-container {
            display: flex !important;
            flex-direction: column !important;
            align-items: flex-start !important;
            justify-content: center !important;
            gap: 2px !important;
            width: auto !important;
            min-width: 200px !important;
        }

        header img, [class*="logo"] img {
            height: 34px !important;
            width: auto !important;
            display: block !important;
            margin-bottom: 4px !important;
        }

        header span, header p, .brand-text {
            font-size: 12px !important;
            line-height: 1.3 !important;
            color: #64748b !important;
            font-weight: 400 !important;
            margin: 0 !important;
            white-space: nowrap !important;
            display: block !important;
        }

        /* Desktop Horizontal Navigation Links Layout */
        header a, nav a, .navbar a {
            text-decoration: none !important;
            color: #475569 !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            margin: 0 14px !important;
            display: inline-block !important;
            transition: color 0.15s ease !important;
        }
        
        header a:hover, nav a:hover {
            color: #2563eb !important;
        }

        /* Action Workspace CTA Layout */
        a[href*="workspace"] {
            background-color: #0f172a !important;
            color: #ffffff !important;
            padding: 8px 16px !important;
            border-radius: 6px !important;
            margin-left: 14px !important;
            font-weight: 500 !important;
        }
    </style>
"""

# Completely scrub any older desktop layout hotfixes out of the head block
html_content = re.sub(r'<style id="production-desktop-layout-fix">.*?</style>', '', html_content, flags=re.DOTALL)

# Inject the clean wide-screen layout specifications
if "</head>" in html_content:
    updated_html = html_content.replace("</head>", f"{bulletproof_style}\n</head>")
    root_html_path.write_text(updated_html)
    print("[+] SUCCESS: Layout engine optimized and written clean to index.html.")
else:
    print("[-] Error: Unable to locate closing </head> tag inside target file.")
