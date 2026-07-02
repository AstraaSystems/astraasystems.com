#!/usr/bin/env python3
from pathlib import Path
import time

root_index = Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git/index.html")

# Using a standard multi-line string block so Python ignores the CSS braces
desktop_override_css = """
<style id="arka-root-desktop-enforcer">
/* ========================================================================
   ASTRAA SYSTEMS - GLOBAL DESKTOP GRID ENFORCER
   ======================================================================== */
@media screen and (min-width: 1025px) {
    body, .wrapper, main, .main-content {
        max-width: 1240px !important;
        width: 1240px !important;
        margin: 0 auto !important;
        padding: 40px 20px !important;
        display: block !important;
    }

    /* Snap workflow items (Estimate, Track, Operate) back into a 3-column row */
    div[class*="workflow"], .grid, .features-grid, .workflow-container {
        display: flex !important;
        flex-direction: row !important;
        justify-content: space-between !important;
        align-items: stretch !important;
        gap: 24px !important;
        width: 100% !important;
        margin: 40px 0 !important;
    }

    div[class*="workflow"] > *, .grid > *, .features-grid > *, .workflow-container > * {
        flex: 1 !important;
        max-width: 32% !important;
        margin: 0 !important;
        display: block !important;
    }

    /* Expand the layout hero panel */
    div[class*="hero"], .hero-banner, .connected-tools-title {
        text-align: left !important;
        width: 100% !important;
    }

    /* Properly expand and space out the blue trial CTA box */
    div[class*="trial"], .cta-box {
        max-width: 850px !important;
        width: 850px !important;
        margin: 60px auto !important;
        text-align: center !important;
        display: block !important;
    }
}
</style>
"""

if root_index.exists():
    content = root_index.read_text()
    
    if "arka-root-desktop-enforcer" in content:
        print("[*] Layout patch already present in file template.")
    else:
        # Append style directly using standard string joining
        patched_content = content.replace("</head>", desktop_override_css + "\n</head>")
        
        # Inject cache-busting logic for the stylesheet
        version_string = f"v={int(time.time())}"
        patched_content = patched_content.replace(
            'href="css/astraa-mobile-responsive-fix.css"', 
            f'href="css/astraa-mobile-responsive-fix.css?{version_string}"'
        )
        
        root_index.write_text(patched_content)
        print("[+] Root index.html desktop layout engine successfully injected.")
else:
    print("[-] Root index.html file not found!")
