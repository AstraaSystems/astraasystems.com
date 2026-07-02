#!/usr/bin/env python3
import re
from pathlib import Path
import time

base_dir = Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git")
frontend_dir = base_dir / "frontend"
root_index = base_dir / "index.html"
frontend_index = frontend_dir / "index.html"

if not frontend_index.exists():
    print("[-] Error: Can't find the desktop build template at frontend/index.html")
    exit(1)

html_content = frontend_index.read_text(errors='ignore')

def resolve_production_path(match):
    attr = match.group(1)  # href or src
    quote = match.group(2) # single or double quote
    orig_path = match.group(3)

    # Leave external CDNs, anchors, and root paths untouched
    if orig_path.startswith(("http://", "https://", "/", "#")):
        return match.group(0)

    # Check where the file actually lives on your hard drive
    path_obj = Path(orig_path)
    
    # Check 1: Is it inside the frontend subfolder?
    abs_path = (frontend_dir / path_obj).resolve()
    if abs_path.exists() and abs_path.is_relative_to(base_dir):
        rel_to_root = abs_path.relative_to(base_dir)
        return f'{attr}={quote}{str(rel_to_root).replace("\\", "/")}{quote}'
        
    # Check 2: Is it already relative to the root?
    abs_path_root = (base_dir / path_obj).resolve()
    if abs_path_root.exists() and abs_path_root.is_relative_to(base_dir):
        rel_to_root = abs_path_root.relative_to(base_dir)
        return f'{attr}={quote}{str(rel_to_root).replace("\\", "/")}{quote}'

    # Fallback if file isn't found locally yet
    return match.group(0)

# Match all asset links
pattern = r'(href|src)=(["\'])([^"\']+)\2'
fixed_html = re.sub(pattern, resolve_production_path, html_content)

# Force an aggressive edge-cache bust for stylesheets and javascript files
timestamp = int(time.time())
fixed_html = re.sub(r'\.cssTarget(?:\?v=\d+)?', '.css', fixed_html) # Normalize
fixed_html = re.sub(r'\.css(?:\?v=\d+)?', f'.css?v={timestamp}', fixed_html)
fixed_html = re.sub(r'\.js(?:\?v=\d+)?', f'.js?v={timestamp}', fixed_html)

root_index.write_text(fixed_html)
print("[+] SUCCESS: Calculated perfect asset mappings and compiled production root index.html")
