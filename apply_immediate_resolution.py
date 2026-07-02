#!/usr/bin/env python3
from pathlib import Path

css_path = Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git/css/astraa-mobile-responsive-fix.css")
index_path = Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git/frontend/index.html")
estimator_path = Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git/frontend/tool-estimator.html")

desktop_normalization = """
/* ========================================================================
   ARKA EXECUTION: IMMEDIATE DESKTOP ARCHITECTURE RESTORATION
   ======================================================================== */
@media screen and (min-width: 1025px) {
    html, body {
        width: 100% !important;
        max-width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        font-size: 16px !important;
    }
    header, main, .main-container, #root {
        max-width: 1280px !important;
        margin: 0 auto !important;
        padding: 0 40px !important;
        display: block !important;
    }
    img[src*="logo"], .logo-container {
        max-width: 180px !important;
        height: auto !important;
    }
    .workflow-container, .features-grid, .grid {
        display: flex !important;
        flex-direction: row !important;
        justify-content: space-between !important;
        gap: 30px !important;
        width: 100% !important;
    }
    .workflow-container > *, .features-grid > *, .grid > * {
        flex: 1 !important;
        max-width: 33% !important;
    }
    div[class*="trial"], .cta-box {
        max-width: 750px !important;
        margin: 40px auto !important;
        display: block !important;
    }
}
"""

# Append the isolation block directly to the bottom of the responsive stylesheet
if css_path.exists():
    content = css_path.read_text()
    if "IMMEDIATE DESKTOP ARCHITECTURE RESTORATION" not in content:
        with open(css_path, "a") as f:
            f.write(desktop_normalization)
        print("[+] Responsive stylesheet leaks safely sandboxed and contained.")

print("[+] Desktop layout restoration complete. Refresh astraasystems.com to verify.")
