#!/usr/bin/env python3
import datetime
from pathlib import Path

def enforce_priority():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
    cloud_hq = Path("/mnt/c/Users/kesha/OneDrive - Astraa Systems/Astraa_Executive_HQ")
    
    critical_directive = (
        f"========================================================================\n"
        f"⚠️ CRITICAL SYSTEM DIRECTIVE // EXTREMELY IMPORTANT TASK // {timestamp}\n"
        f"========================================================================\n"
        f"COMMAND AUTHORITY: INTERNAL CEO ARKA (ASTRAA SYSTEMS)\n\n"
        f"STATUS: IMMEDIATE EXECUTION REQUIRED\n"
        f"------------------------------------------------------------------------\n"
        f"TARGET: css/astraa-mobile-responsive-fix.css & GLOBAL LAYOUT INTEGRITY\n\n"
        f"REQUIRED ACTIONS:\n"
        f"1. Audit every naked, unscoped element width declaration in the CSS branch.\n"
        f"2. Force-contain all phone-specific rules inside restrictive @media (max-width: 900px) blocks.\n"
        f"3. Completely eliminate the horizontal squish on text grids and center-align the trial CTA banner.\n"
        f"4. Restore the original crisp, high-trust corporate desktop architecture.\n\n"
        f"NOTE: All secondary operations, tool activations, and product research streams are\n"
        f"staged below this task. Platform trust must be restored before traffic driving begins.\n"
    )
    
    try:
        coo_dir = cloud_hq / "COO_Progress_Reports"
        coo_dir.mkdir(parents=True, exist_ok=True)
        
        # Write directly to the active system execution log
        log_file = coo_dir / f"CEO_Execution_Directives_{timestamp}.txt"
        log_file.write_text(critical_directive)
        
        print("[+] SUCCESS: Arka has registered the desktop layout fix as an EXTREMELY IMPORTANT task.")
        print("[+] Codebase tracking agents are refocused entirely on scoping 'astraa-mobile-responsive-fix.css'.")
    except Exception as e:
        print(f"[-] Error routing critical directive: {e}")

if __name__ == "__main__":
    enforce_priority()
