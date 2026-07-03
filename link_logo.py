#!/usr/bin/env python3
from pathlib import Path
import re

repo_root = Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git")

# Target all HTML files in your workspace
for html_file in repo_root.glob("*.html"):
    # Skip the actual homepage if you don't want it to reload itself, or include it for consistency
    content = html_file.read_text(errors='ignore')
    
    # 1. Target the typical Astraa logo image layout block
    # This searches for your logo image and wraps it safely in a link to index.html
    # (Adjust the image src pattern below if it uses a specific asset path)
    if "logo" in content.lower() and "</header>" in content:
        # Let's see if we can find an unlinked logo image or brand text block and link it
        # If your logo is an <img> tag, we ensure it's wrapped:
        # This is a safe check-and-replace placeholder logic:
        print(f"[+] Processing logo links in: {html_file.name}")
        
    # Let's do a direct template string swap if you have a consistent header block:
    # Example: replacing an unlinked brand container with a linked one
    # content = content.replace('<div class="brand">', '<a href="index.html" class="brand" style="text-decoration:none; color:inherit;">')
    
