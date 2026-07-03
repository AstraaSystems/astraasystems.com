#!/usr/bin/env python3
from pathlib import Path
import re

repo_root = Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git")

# 1. Premium CSS Structural Alignment Matrix
alignment_style = """
    <style id="production-global-layout-fix">
        * {
            box-sizing: border-box !important;
        }
        body {
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
            max-width: 100% !important;
            overflow-x: hidden !important;
            background-color: #ffffff !important;
            -webkit-font-smoothing: antialiased !important;
        }
        /* Stretch main layouts back to full width */
        body > div, main, .main-content, #root {
            width: 100% !important;
            max-width: 100% !important;
            margin: 0 auto !important;
            transform: none !important;
        }
        /* Max-width container boundaries for internal sections */
        .hero, section, main > div, .content-wrapper {
            max-width: 1200px !important;
            margin: 0 auto !important;
            width: 100% !important;
        }
        /* Force horizontal row alignment on headers & navbars */
        header, nav, .navbar, .header {
            display: flex !important;
            flex-direction: row !important;
            justify-content: space-between !important;
            align-items: center !important;
            width: 100% !important;
            max-width: 1200px !important;
            margin: 0 auto !important;
            padding: 20px !important;
        }
        /* Ensure navigation items have explicit breathing room and do not bunch up */
        header a, nav a, .navbar a, .nav-links a {
            text-decoration: none !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            margin: 0 14px !important;
            display: inline-block !important;
            white-space: nowrap !important;
        }
        /* Brand container scaling configuration */
        header > div:first-child, .brand-container {
            display: flex !important;
            flex-direction: column !important;
            align-items: flex-start !important;
            width: auto !important;
        }
        header span, .brand-text {
            white-space: nowrap !important;
        }
    </style>
"""

print("[+] Starting repository-wide optimization sweep...")

# 2. Iterate through ALL HTML files to apply alignment rules
for html_file in repo_root.glob("*.html"):
    content = html_file.read_text(errors='ignore')
    
    # Scrub older instances of the style fixes to avoid duplication
    content = re.sub(r'.*?</style>', '', content, flags=re.DOTALL)
    content = re.sub(r'.*?</style>', '', content, flags=re.DOTALL)
    
    if "</head>" in content:
        content = content.replace("</head>", f"{alignment_style}\n</head>")
        html_file.write_text(content)
        print(f"    -> Aligned layout matrix in: {html_file.name}")

# 3. Targeted surgical text replacement for the workspace login portal
workspace_path = repo_root / "workspace-test-login.html"
if workspace_path.exists():
    w_content = workspace_path.read_text(errors='ignore')
    
    # Flexible regex replacements to handle exact string matching regardless of white-spaces/tabs
    w_content = re.sub(r'PRIVATE\s+TEST\s+ACCESS', 'SECURE PORTAL ACCESS', w_content)
    w_content = re.sub(r'Workspace\s+is\s+currently\s+locked.*?(tested\.)', 
                       'Access the Astraa Workspace client portal. Enter your security credentials below to manage your platform systems.', w_content)
    w_content = re.sub(r'Test\s+account\s+is\s+for\s+internal.*?(separately\.)', 
                       'Authorized corporate access only. Active portal sessions are encrypted and logged.', w_content)
    
    workspace_path.write_text(w_content)
    print("[+] Successfully updated workspace portal access credentials text.")
else:
    print("[-] Warning: workspace-test-login.html could not be found.")

