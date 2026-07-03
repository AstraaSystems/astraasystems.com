#!/usr/bin/env python3
from pathlib import Path
import re

repo_root = Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git")

# Unified semantic header brand snippet
linked_brand_html = """<a href="index.html" style="text-decoration: none; color: inherit; display: flex; align-items: center; gap: 15px;">
    <img src="logo.png" alt="Astraa Systems Logo" style="height: 50px; width: auto; display: block;">
    <div style="display: flex; flex-direction: column; align-items: flex-start; line-height: 1.3;">
        <span style="font-weight: 700; font-size: 16px; color: #0d1b2a;">Astraa Systems</span>
        <span style="font-size: 12px; color: #666;">Connected business tools</span>
    </div>
</a>"""

for html_file in repo_root.glob("*.html"):
    content = html_file.read_text(errors='ignore')
    
    # Check if there is an unlinked header brand pattern or raw text matches
    if "Connected business tools" in content:
        print(f"[+] Re-structuring header branding block in: {html_file.name}")
        
        # Regex pattern to sweep away the unlinked image tag and the stray text tags if present together
        # Adjust if your actual img tag has a different name (e.g., logo_triangle.png)
        content = re.sub(
            r'<img[^>]*logo[^>]*>[\s\S]*?Astraa Systems[\s\S]*?Connected business tools',
            linked_brand_html,
            content,
            flags=re.IGNORECASE
        )
        
        # Clean up any leftover duplicate text blocks outside the main structural flow
        content = content.replace("Astraa Systems\nConnected business tools", "")
        content = content.replace("Astraa Systems Connected business tools", "")
        
        html_file.write_text(content)

