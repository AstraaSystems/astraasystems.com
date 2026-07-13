from pathlib import Path

# ---------- 1. Backend: append baseline rates + single-work logic to api.py ----------
api = Path("api.py")
s = api.read_text(encoding="utf-8")

if "ASTRAA_BASELINE_RATES" not in s:
    block = '''

# ASTRAA_SINGLEWORK_V2
ASTRAA_BASELINE_RATES = {
    "Interior Paint": {"material": 1.50, "labour": 2.50},
    "Flooring": {"material": 6.00, "labour": 4.00},
    "Drywall": {"material": 1.50, "labour": 1.50},
    "Tile": {"material": 6.00, "labour": 6.00},
    "Roofing": {"material": 4.00, "labour": 3.00},
    "Framing": {"material": 9.00, "labour": 9.00},
    "Concrete": {"material": 5.00, "labour": 4.00},
    "Electrical": {"material": 4.00, "labour": 5.00},
    "Plumbing": {"material": 4.00, "labour": 5.00},
    "Insulation": {"material": 1.50, "labour": 1.50},
    "HVAC": {"material": 6.00, "labour": 4.00},
    "General / Other": {"material": 3.00, "labour": 3.00},
}

@app.route("/api/estimate/baseline", methods=["GET"])
def astraa_baseline_rates_v2():
    return astraa_json_response({"success": True, "rates": ASTRAA_BASELINE_RATES})

def astraa_single_work_calc(payload):
    sqft = float(payload.get("sqft") or 0)
    cat = payload.get("category") or "General / Other"
    base = ASTRAA_BASELINE_RATES.get(cat, ASTRAA_BASELINE_RATES["General / Other"])
    mc = payload.get("material_cost")
    lc = payload.get("labour_cost")
    mat_rate = float(mc) if mc not in [None, ""] else base["material"]
    lab_rate = float(lc) if lc not in [None, ""] else base["labour"]
    loc = astraa_bc_location_multiplier(payload.get("location_market") or "BC / Vancouver")
    q = (payload.get("quality_level") or "Standard").lower()
    qm = 1.15 if q == "premium" else (0.9 if q == "economy" else 1.0)
    materials = round(sqft * mat_rate * loc * qm, 2)
    labour = round(sqft * lab_rate * loc * qm, 2)
    return {
        "mode": "single_work", "category": cat, "sqft": sqft,
        "location_market": payload.get("location_market"),
        "quality_level": payload.get("quality_level"),
        "material_rate": round(mat_rate * loc * qm, 2),
        "labour_rate": round(lab_rate * loc * qm, 2),
        "materials_cost": materials, "labour_cost": labour,
        "total": round(materials + labour, 2)
    }
# END ASTRAA_SINGLEWORK_V2
'''
    s += block
    api.write_text(s, encoding="utf-8")
    print("api.py: single-work backend appended")
else:
    print("api.py: single-work already present")

# ---------- 2. Patch the preview route to branch on mode ----------
s = api.read_text(encoding="utf-8")
needle = 'def astraa_estimate_preview():'
if needle in s and "SINGLEWORK_BRANCH" not in s:
    # find the line after email check inside preview and inject
    marker = 'def astraa_estimate_preview():\n    payload = astraa_get_request_json()\n    email = astraa_normalize_email(payload.get("email"))\n    if not email:\n        return astraa_json_response({"success": False, "error": "Missing email."}, 400)\n'
    if marker in s:
        inject = marker + '''    # SINGLEWORK_BRANCH
    if (payload.get("mode") or "") == "single_work":
        if float(payload.get("sqft") or 0) < 1:
            return astraa_json_response({"success": False, "error": "Enter square footage."}, 400)
        _r = astraa_single_work_calc(payload)
        import uuid as _u
        _tok = _u.uuid4().hex
        _pv = _astraa_load_previews(); _pv[_tok] = {"email": email, "created_at": astraa_now_iso(), "result": _r, "mode": "single_work"}; _astraa_save_previews(_pv)
        return astraa_json_response({"success": True, "preview": True, "preview_token": _tok, "mode": "single_work", "total": _r["total"], "category": _r["category"], "materials_cost": _r["materials_cost"], "labour_cost": _r["labour_cost"]})
'''
        s = s.replace(marker, inject, 1)
        api.write_text(s, encoding="utf-8")
        print("api.py: preview route branched for single_work")
    else:
        print("api.py: WARNING preview marker not found - preview route may differ")
else:
    print("api.py: preview branch already present or route missing")

import ast
ast.parse(Path("api.py").read_text(encoding="utf-8"))
print("api.py: SYNTAX OK after build")
