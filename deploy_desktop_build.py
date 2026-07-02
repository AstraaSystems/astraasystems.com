#!/usr/bin/env python3
import re
from pathlib import Path

frontend_html = Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git/frontend/index.html")
root_html = Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git/index.html")

if frontend_html.exists():
    content = frontend_html.read_text()
    
    # Automatically strip out any parent directory traversal selectors (../)
    # so that links to css/, js/, and images/ map perfectly from the root folder
    clean_content = re.sub(r'(src|href)=["\']\.\./([^"\']+)["\']', r'\1="\2"', content)
    
    root_html.write_text(clean_content)
    print("[+] SUCCESS: Your original desktop build has been migrated to the root production layer.")
else:
    print("[-] ERROR: Could not locate the desktop build template at frontend/index.html")
