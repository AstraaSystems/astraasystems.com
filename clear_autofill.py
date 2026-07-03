#!/usr/bin/env python3
from pathlib import Path

workspace_path = Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git/workspace-test-login.html")

if workspace_path.exists():
    content = workspace_path.read_text(errors='ignore')
    
    # 1. Swap the specific testing placeholder with a generic corporate one
    content = content.replace(
        'placeholder="astraa.live.test@astraasystems.com"', 
        'placeholder="name@company.com"'
    )
    
    # 2. Comment out or remove the JavaScript line forcing the input value on load
    content = content.replace(
        'document.getElementById("email").value = TEST_EMsoftwareL;',
        '// document.getElementById("email").value = TEST_EMsoftwareL; // Cleared for production'
    )
    
    workspace_path.write_text(content)
    print("[+] Successfully cleared email auto-fill and updated placeholder.")
else:
    print("[-] File not found.")
