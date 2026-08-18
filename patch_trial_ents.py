import shutil
from pathlib import Path
from datetime import datetime
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
ap = Path("api.py"); s = ap.read_text(encoding="utf-8")
shutil.copyfile("api.py", f"api.py.before_trialents_{stamp}")
b = 0

# 1) Trial branch: full ecosystem access
anchor = '    exp = "Expense (full)" if plan_l in ("professional","pro","custom") else "Expense (limited)"'
trial_block = (anchor + '\n\n'
    '    # TRIAL: full ecosystem preview \u2014 all tools unlocked (Estimator usage capped separately at 30 approvals)\n'
    '    if plan_l == "trial" or "professional suite" in t or t == "professional_suite" or "all" in t or "eco" in t:\n'
    '        if plan_l == "trial" or "all" in t or "eco" in t or "professional suite" in t or t == "professional_suite":\n'
    '            return ["Astraa Estimator", "Astraa Business", "Astraa Finance", "Astraa Expense (full)",\n'
    '                    "Astraa Vault", "Astraa Logistics", "Astraa Reports", "Astraa Research Analyst", exp]')
if anchor in s and "full ecosystem preview" not in s:
    s = s.replace(anchor, trial_block, 1); b += 1

ap.write_text(s, encoding="utf-8")
print(f"trial entitlements changes: {b} (expected 1)")
