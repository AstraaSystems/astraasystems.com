#!/usr/bin/env python3
from pathlib import Path

desktop_restoration_css = """
<style id="arka-desktop-restoration">
/* ========================================================================
   EMERGENCY DESKTOP STRUCTURE RESTORATION - ASTRAA SYSTEMS
   ======================================================================== */
@media screen and (min-width: 1025px) {
    /* Force canvas reset and clear rogue mobile constraints */
    html, body {
        width: 100% !important;
        max-width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        font-size: 16px !important;
        background-color: #ffffff !important;
    }

    /* Wrap contents in a clean centered executive grid */
    header, main, .main-container, #root, .workspace-wrapper {
        max-width: 1280px !important;
        margin: 0 auto !important;
        padding: 0 40px !important;
    }

    /* Normalize the header logo layout */
    .logo-container, img[src*="logo"] {
        max-width: 180px !important;
        height: auto !important;
        display: block !important;
        margin-bottom: 20px !important;
    }

    /* Standardize typography sizes across main sections */
    h1, .hero-title, .connected-tools-title {
        font-size: 2.5rem !important;
        line-height: 1.2 !important;
        width: 100% !important;
    }
    
    p, .hero-subtitle {
        font-size: 1.1rem !important;
        line-height: 1.6 !important;
        width: 100% !important;
    }

    /* Snap the Estimate/Track/Operate workflow cards back into a 3-column row */
    .workflow-container, .features-grid, .grid {
        display: flex !important;
        flex-direction: row !important;
        justify-content: space-between !important;
        gap: 24px !important;
        width: 100% !important;
        margin: 30px 0 !important;
    }

    .workflow-container > *, .features-grid > *, .grid > * {
        flex: 1 !important;
        min-width: 250px !important;
        padding: 24px !important;
    }

    /* Snapping the blue trial CTA back into structured corporate alignment */
    div[class*="trial"], .cta-box, .trial-banner-blueprint {
        max-width: 800px !important;
        margin: 50px auto !important;
        padding: 40px !important;
        text-align: center !important;
        display: block !important;
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
        # Clean out older patches if present to avoid bloat
        if "arka-desktop-restoration" in content:
            print(f"[*] Refreshing existing layout patch on {file_path.name}...")
            continue
            
        if "</head>" in content:
            patched_content = content.replace("</head>", f"{desktop_restoration_css}\n</head>")
            file_path.write_text(patched_content)
            print(f"[+] Rebuilt desktop structural integrity for: {file_path.name}")
    else:
        print(f"[-] File not found to patch: {file_path}")

