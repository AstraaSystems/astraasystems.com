#!/usr/bin/env python3
from pathlib import Path
import re
import time

css_path = Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git/css/astraa-mobile-responsive-fix.css")
root_index = Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git/index.html")

# 1. Sandbox the CSS file completely
if css_path.exists():
    content = css_path.read_text()
    
    if "GLOBAL_MOBILE_SAFETY_SANDBOX" not in content:
        sandboxed_css = f"""/* GLOBAL_MOBILE_SAFETY_SANDBOX */
@media screen and (max-width: 1024px) {{
{content}
}}
"""
        css_path.write_text(sandboxed_css)
        print("[+] SUCCESS: Mobile stylesheet rules strictly sandboxed below 1024px.")
    else:
        print("[*] Mobile stylesheet is already sandboxed.")
else:
    print("[-] Error: Mobile CSS file not found.")

# 2. Force a fresh cache-buster into the root index.html file
if root_index.exists():
    index_content = root_index.read_text()
    timestamp = int(time.time())
    
    # Replace any existing stylesheet reference with a fresh, uncached timestamped version
    pattern = r'href="css/astraa-mobile-responsive-fix\.css(?:\?v=\d+)?"'
    replacement = f'href="css/astraa-mobile-responsive-fix.css?v={timestamp}"'
    
    updated_content = re.sub(pattern, replacement, index_content)
    root_index.write_text(updated_content)
    print(f"[+] SUCCESS: Injected fresh cache-buster (?v={timestamp}) into root index.html")
else:
    print("[-] Error: Root index.html file not found.")

