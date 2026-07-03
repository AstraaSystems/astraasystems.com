#!/usr/bin/env python3
from pathlib import Path
import re

repo_root = Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git")

# 1. Precision text swap for workspace-test-login.html
workspace_path = repo_root / "workspace-test-login.html"
if workspace_path.exists():
    content = workspace_path.read_text(errors='ignore')
    
    # Exact literal replacements matching your grep results
    content = content.replace("<title>Astraa Workspace Test Access</title>", "<title>Astraa Workspace Secure Access</title>")
    content = content.replace('<div class="badge">Private Test Access</div>', '<div class="badge">Secure Portal Access</div>')
    content = content.replace('<label for="email">Test account email</label>', '<label for="email">Account Email</label>')
    content = content.replace('Clear Test Access', 'Clear Session')
    
    # Clean multiline paragraph swap
    content = re.sub(
        r'Workspace is currently locked from public access while Astraa Finance, Expense, Operations, Estimator, and additional tools are tested\.',
        'Access the Astraa Workspace client portal. Enter your security credentials below to manage your platform systems.',
        content, flags=re.DOTALL
    )
    # Secondary check for variations of the layout block layout split
    content = re.sub(
        r'Workspace is currently locked.*?tools are tested\.',
        'Access the Astraa Workspace client portal. Enter your security credentials below to manage your platform systems.',
        content, flags=re.DOTALL
    )
    
    workspace_path.write_text(content)
    print("[+] Successfully updated workspace login text fields.")

# 2. Safe, isolated alignment injection for all subpages
css_matrix = """<style id="astraa-alignment-matrix">
        * { box-sizing: border-box !important; }
        body { margin: 0 !important; padding: 0 !important; width: 100% !important; max-width: 100% !important; overflow-x: hidden !important; }
        body > div, main, .main-content, #root { width: 100% !important; max-width: 100% !important; margin: 0 auto !important; transform: none !important; }
        .hero, section, main > div, .content-wrapper { max-width: 1200px !important; margin: 0 auto !important; width: 100% !important; }
        header, nav, .navbar, .header { display: flex !important; flex-direction: row !important; justify-content: space-between !important; align-items: center !important; width: 100% !important; max-width: 1200px !important; margin: 0 auto !important; padding: 20px !important; }
        header a, nav a, .navbar a, .nav-links a { text-decoration: none !important; font-size: 14px !important; font-weight: 500 !important; margin: 0 14px !important; display: inline-block !important; white-space: nowrap !important; }
        header > div:first-child, .brand-container { display: flex !important; flex-direction: column !important; align-items: flex-start !important; width: auto !important; }
        header span, .brand-text { white-space: nowrap !important; }
    </style>"""

for html_file in repo_root.glob("*.html"):
    file_text = html_file.read_text(errors='ignore')
    
    # Only insert if it hasn't been added yet
    if 'id="astraa-alignment-matrix"' not in file_text:
        if "</head>" in file_text:
            file_text = file_text.replace("</head>", f"{css_matrix}\n</head>")
            html_file.write_text(file_text)
            print(f"    -> Injected safe alignment layout matrix into: {html_file.name}")

