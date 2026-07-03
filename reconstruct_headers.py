#!/usr/bin/env python3
from pathlib import Path
import re

repo_root = Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git")

# Define a clean, production-grade navbar component
# Uses inline CSS flexboxes to guarantee perfect widescreen alignment and clickability
clean_navbar_html = """<header style="background: #ffffff; border-bottom: 1px solid #f0f4f8; padding: 15px 24px; box-sizing: border-box; width: 100%;">
    <div style="max-width: 1200px; margin: 0 auto; display: flex; flex-direction: row; justify-content: space-between; align-items: center; width: 100%;">
        
        <a href="index.html" style="display: flex; flex-direction: row; align-items: center; gap: 14px; text-decoration: none; color: inherit; cursor: pointer;">
            <img src="logo.png" alt="Astraa Systems Logo" style="height: 40px; width: auto; display: block;" onerror="this.src='assets/logo.png';">
            <div style="display: flex; flex-direction: column; align-items: flex-start; justify-content: center;">
                <span style="font-weight: 700; font-size: 16px; letter-spacing: -0.3px; color: #0f172a; font-family: system-ui, -apple-system, sans-serif;">Astraa Systems</span>
                <span style="font-size: 11px; color: #64748b; margin-top: -1px; font-family: system-ui, -apple-system, sans-serif;">Connected business tools</span>
            </div>
        </a>

        <nav style="display: flex; flex-direction: row; align-items: center; gap: 24px;">
            <a href="index.html" style="text-decoration: none; font-size: 14px; font-weight: 500; color: #475569; font-family: system-ui, -apple-system, sans-serif;">Home</a>
            <a href="tools.html" style="text-decoration: none; font-size: 14px; font-weight: 500; color: #475569; font-family: system-ui, -apple-system, sans-serif;">Tools</a>
            <a href="pricing.html" style="text-decoration: none; font-size: 14px; font-weight: 500; color: #475569; font-family: system-ui, -apple-system, sans-serif;">Pricing</a>
            <a href="support.html" style="text-decoration: none; font-size: 14px; font-weight: 500; color: #475569; font-family: system-ui, -apple-system, sans-serif;">FAQ / Support</a>
            <a href="contact.html" style="text-decoration: none; font-size: 14px; font-weight: 500; color: #475569; font-family: system-ui, -apple-system, sans-serif;">Contact</a>
            <a href="workspace-test-login.html" style="text-decoration: none; font-size: 14px; font-weight: 600; color: #0284c7; margin-left: 10px; font-family: system-ui, -apple-system, sans-serif;">Open Workspace</a>
        </nav>

    </div>
</header>"""

for html_file in repo_root.glob("*.html"):
    content = html_file.read_text(errors='ignore')
    
    # 1. Strip out the old variable <header> segments or stray layout elements down to the body opening tag
    if "<header" in content and "</header>" in content:
        content = re.sub(r'<header[\s\S]*?</header>', clean_navbar_html, content)
        print(f"[+] Reconstructed semantic header container for: {html_file.name}")
    else:
        # Fallback for pages without standard semantic headers: insert cleanly below the opening <body> tag
        if "<body>" in content:
            content = content.replace("<body>", f"<body>\n{clean_navbar_html}")
            print(f"[+] Injected clean navbar layout block into: {html_file.name}")

    # 2. Complete clean-up of duplicated text fragments floating around raw template segments
    content = re.sub(r'(Astraa Systems\s*Connected business tools\s*)+', '', content, flags=re.IGNORECASE)
    
    # Restore the brand identity string strictly back into our freshly laid navbar block code
    content = content.replace('alt=" Logo"', 'alt="Astraa Systems Logo"')
    
    html_file.write_text(content)

print("[+] Global navigation architecture refactoring complete.")
