#!/usr/bin/env python3
from pathlib import Path
import re

repo_root = Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git")

# Enhanced navbar component using absolute root asset references and strict structural flex spacing
clean_navbar_html = """<header style="background: #ffffff; border-bottom: 1px solid #e2e8f0; padding: 16px 24px; box-sizing: border-box; width: 100%; font-family: system-ui, -apple-system, sans-serif;">
    <div style="max-width: 1200px; margin: 0 auto; display: flex; flex-direction: row; justify-content: space-between; align-items: center; width: 100%;">
        
        <a href="index.html" style="display: flex; flex-direction: row; align-items: center; gap: 12px; text-decoration: none; color: inherit; cursor: pointer;">
            <img src="/logo.png" alt="Astraa Systems Logo" style="height: 38px; width: auto; display: block;" onerror="this.src='logo.png';">
            <div style="display: flex; flex-direction: column; align-items: flex-start; justify-content: center;">
                <span style="font-weight: 700; font-size: 16px; letter-spacing: -0.3px; color: #0f172a;">Astraa Systems</span>
                <span style="font-size: 11px; color: #64748b; margin-top: 1px; white-space: nowrap;">Connected business tools</span>
            </div>
        </a>

        <nav style="display: flex; flex-direction: row; align-items: center; gap: 24px;">
            <a href="index.html" style="text-decoration: none; font-size: 14px; font-weight: 500; color: #475569;">Home</a>
            <a href="tools.html" style="text-decoration: none; font-size: 14px; font-weight: 500; color: #475569;">Tools</a>
            <a href="pricing.html" style="text-decoration: none; font-size: 14px; font-weight: 500; color: #475569;">Pricing</a>
            <a href="support.html" style="text-decoration: none; font-size: 14px; font-weight: 500; color: #475569;">FAQ / Support</a>
            <a href="contact.html" style="text-decoration: none; font-size: 14px; font-weight: 500; color: #475569;">Contact</a>
            <a href="workspace-test-login.html" style="text-decoration: none; font-size: 14px; font-weight: 600; color: #0284c7; margin-left: 8px;">Open Workspace</a>
        </nav>

    </div>
</header>"""

for html_file in repo_root.glob("*.html"):
    content = html_file.read_text(errors='ignore')
    
    # Clean out older structural markup instances
    if "<header" in content and "</header>" in content:
        content = re.sub(r'<header[\s\S]*?</header>', clean_navbar_html, content)
    
    # Strip any floating stray residual brand text duplicates
    content = re.sub(r'(Astraa Systems\s*Connected business tools\s*)+', '', content, flags=re.IGNORECASE)
    
    html_file.write_text(content)

print("[+] Clean asset navigation structures deployed locally.")
