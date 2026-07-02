#!/usr/bin/env python3
import re
from pathlib import Path
import time

root_dir = Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git")
frontend_html = root_dir / "frontend" / "index.html"
root_html = root_dir / "index.html"

if frontend_html.exists():
    # Read the clean desktop layout source code
    desktop_code = frontend_html.read_text(errors='ignore')
    
    # Remove any broken backward navigation links (../) so paths resolve cleanly
    clean_code = re.sub(r'(src|href)=["\']\.\./([^"\']+)["\']', r'\1="\2"', desktop_code)
    
    # Inject a definitive cache buster to force browsers to reload styles
    ts = int(time.time())
    clean_code = re.sub(r'\.css(?:\?v=\d+)?', f'.css?v={ts}', clean_code)
    
    # Write to root layer
    root_html.write_text(clean_code)
    
    print("[+] Sync Complete: Desktop builds unified across production environments.")
else:
    print("[-] Error: Source desktop index file not found.")
