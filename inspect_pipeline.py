#!/usr/bin/env python3
import urllib.request
import ssl
from pathlib import Path

local_root_path = Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git/index.html")
local_frontend_path = Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git/frontend/index.html")

print("🔍 ANALYZING DEPLOYMENT PIPELINE...\n")

# Fetch live production source code
try:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    req = urllib.request.Request(
        "https://astraasystems.com/", 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    with urllib.request.urlopen(req, context=ctx) as response:
        live_html = response.read().decode('utf-8', errors='ignore')
    print("[+] Successfully fetched live HTML from astraasystems.com")
except Exception as e:
    print(f"[-] Failed to fetch live website: {e}")
    live_html = ""

# Run diagnostics
if live_html:
    local_root = local_root_path.read_text(errors='ignore') if local_root_path.exists() else ""
    local_frontend = local_frontend_path.read_text(errors='ignore') if local_frontend_path.exists() else ""
    
    # Check if live server is tracking the subfolder instead of the root
    if 'href="frontend/' in live_html or 'src="frontend/' in live_html:
        print("\n💡 DIAGNOSIS: The live server IS updating, but asset paths are mismatched.")
        print("-> Action: We need to normalize your layout references.")
    elif local_frontend and (local_frontend[:500] in live_html or "Astraa Workspace" in live_html and "frontend/" not in live_html):
        print("\n💡 DIAGNOSIS: Your host is deploying directly from the '/frontend' folder as its root!")
        print("-> Meaning: Modifying the root index.html does nothing. We must fix the assets inside the /frontend directory.")
    else:
        print("\n💡 DIAGNOSIS: The live web server is completely ignoring your local updates.")
        print("-> Likely cause: A stuck CDN edge cache or the build pipeline is frozen on an older commit/branch.")

print("\n--- GIT STATUS CHECK ---")
import subprocess
try:
    print(subprocess.check_output(["git", "status", "-s"], cwd="/mnt/d/ARKA_HQ/repos/ardhanarishvara_git").decode())
    print("Current Branch:")
    print(subprocess.check_output(["git", "branch", "--show-current"], cwd="/mnt/d/ARKA_HQ/repos/ardhanarishvara_git").decode())
except Exception as e:
    print(f"Could not run git status: {e}")
