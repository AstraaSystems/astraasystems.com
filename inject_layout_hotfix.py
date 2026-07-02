#!/usr/bin/env python3
from pathlib import Path

root_html_path = Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git/index.html")

if not root_html_path.exists():
    print("[-] Error: Cannot locate root index.html")
    exit(1)

html_content = root_html_path.read_text(errors='ignore')

# Definitive structural desktop layout rules to override broken or missing container blocks
hotfix_style = """
    <style id="production-desktop-layout-fix">
        /* Force unstyled header elements into a clean, horizontal desktop row */
        header, nav, .header, .navbar, #header {
            display: flex !important;
            flex-direction: row !important;
            justify-content: space-between !important;
            align-items: center !important;
            width: 100% !important;
            max-width: 1200px !important;
            margin: 0 auto !important;
            padding: 20px !important;
            box-sizing: border-box !important;
        }
        
        /* Force navigation links or list elements to sit side-by-side instead of stacking vertical */
        header a, nav a, .header a, .navbar a, header li, nav li {
            display: inline-block !important;
            margin: 0 15px !important;
            white-space: nowrap !important;
        }
        
        /* Restrain the global blown-out view from expanding endlessly edge-to-edge */
        body {
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
            overflow-x: hidden !important;
        }
        
        .container, .wrapper, main, #main-content, section {
            max-width: 1200px !important;
            margin: 0 auto !important;
            width: 100% !important;
            box-sizing: border-box !important;
        }
    </style>
"""

# Clean out any older versions of our style fix to prevent duplicate tags
if "production-desktop-layout-fix" in html_content:
    import re
    html_content = re.sub(r'<style id="production-desktop-layout-fix">.*?</style>', '', html_content, flags=re.DOTALL)

# Inject the rules right before the closing tag of the HTML head block
if "</head>" in html_content:
    updated_html = html_content.replace("</head>", f"{hotfix_style}\n</head>")
    root_html_path.write_text(updated_html)
    print("[+] SUCCESS: Inline structural desktop hotfix has been compiled directly into the root header.")
else:
    print("[-] Error: Could not locate closing </head> tag in index.html")
