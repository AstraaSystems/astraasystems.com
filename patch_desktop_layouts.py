#!/usr/bin/env python3
from pathlib import Path

desktop_css_patch = """
<style>
/* ==========================================
   ARKA AUTOMATED DESKTOP INJECTION PATCH
   ========================================== */
@media screen and (min-width: 1151px) {
    body, .main-content, main, .container {
        max-width: 1200px !important;
        margin: 0 auto !important;
        font-size: 16px !important;
    }
    .grid, .form-container, .tool-layout {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 40px !important;
    }
    input, button, .cta-box {
        max-width: 450px !important;
    }
}
</style>
"""

target_files = [
    Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git/frontend/index.html"),
    Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git/frontend/tool-estimator.html")
]

for file_path in target_files:
    if file_path.exists():
        content = file_path.read_text()
        if "</head>" in content and "ARKA AUTOMATED DESKTOP INJECTION PATCH" not in content:
            patched_content = content.replace("</head>", f"{desktop_css_patch}\n</head>")
            file_path.write_text(patched_content)
            print(f"[+] Successfully patched layout grid for: {file_path.name}")
        else:
            print(f"[-] {file_path.name} already patched or missing structural tags.")
    else:
        print(f"[-] File path not found: {file_path}")

