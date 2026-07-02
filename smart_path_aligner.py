#!/usr/bin/env python3
import re
from pathlib import Path
import time

root_dir = Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git")
frontend_html_path = root_dir / "frontend" / "index.html"
root_html_path = root_dir / "index.html"
css_path = root_dir / "css" / "astraa-mobile-responsive-fix.css"

# 1. Clear out the previous mobile media-query sandbox so desktop styles can breathe
if css_path.exists():
    css_content = css_path.read_text()
    if "GLOBAL_MOBILE_SAFETY_SANDBOX" in css_content:
        lines = css_content.splitlines()
        if len(lines) >= 4:
            body_lines = lines[2:-1] if lines[-1].strip() == "}" else lines[2:]
            css_path.write_text("\n".join(body_lines))
            print("[+] Successfully removed mobile constraints from the root stylesheet.")

# 2. Map HTML asset links from the frontend folder to the production root
if frontend_html_path.exists():
    html_content = frontend_html_path.read_text()
    
    def adjust_path(match):
        attr = match.group(1)  # href or src
        sep = match.group(2)   # single or double quote
        path = match.group(3)  # the file path
        
        # Ignore external CDNs or paths that are already explicitly mapped
        if path.startswith(("http://", "https://", "/", "frontend/")):
            return f'{attr}={sep}{path}{sep}'
        
        # If a path was looking backward out of the folder (../css/...)
        if path.startswith("../"):
            clean_path = path.replace("../", "")
            return f'{attr}={sep}{clean_path}{sep}'
        
        # Redirect relative paths to look inside the active frontend directory
        return f'{attr}={sep}frontend/{path}{sep}'

    pattern = r'(href|src)=(["\'])([^"\']+)\2'
    updated_html = re.sub(pattern, adjust_path, html_content)
    
    # Inject a fresh cache-buster timestamp
    timestamp = int(time.time())
    updated_html = re.sub(r'\.css(?:\?v=\d+)?', f'.css?v={timestamp}', updated_html)
    
    root_html_path.write_text(updated_html)
    print("[+] Successfully migrated desktop build with fully aligned asset pathways.")
else:
    print("[-] Error: Cannot locate the source template at frontend/index.html")
