"""
Astraa RBAC — Phase 1: per-account users + roles data model.
Foundation only: data store + helpers + guard rules. No routes/UI yet.
"""
import os, json, uuid, time

RBAC_STORE = os.path.join("astraa_data", "astraa_account_users.json")

# Bundle -> included seats + max admins (tiered)
BUNDLE_CONFIG = {
    "astraa_the_one":        {"seats": 10, "max_admins": 4},
    "astraa_business_elite": {"seats": 7,  "max_admins": 3},
    "astraa_core":           {"seats": 6,  "max_admins": 2},
}
DEFAULT_CONFIG = {"seats": 1, "max_admins": 1}

VALID_ROLES = ("owner", "admin", "basic")


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _load():
    if not os.path.exists(RBAC_STORE):
        return {}
    try:
        with open(RBAC_STORE, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except Exception:
        return {}


def _save(db):
    os.makedirs(os.path.dirname(RBAC_STORE), exist_ok=True)
    with open(RBAC_STORE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2)


def _key(email):
    return str(email or "").strip().lower()


def get_account(account_key):
    return _load().get(_key(account_key))


def ensure_account(account_key, owner_email, bundle=""):
    """Create the account-users record if missing; first user = owner."""
    db = _load()
    k = _key(account_key)
    if k in db:
        return db[k]
    cfg = BUNDLE_CONFIG.get(bundle, DEFAULT_CONFIG)
    owner = _key(owner_email) or k
    db[k] = {
        "owner_email": owner,
        "bundle": bundle,
        "seats_total": cfg["seats"],
        "max_admins": cfg["max_admins"],
        "users": [{
            "user_id": uuid.uuid4().hex[:12],
            "email": owner,
            "name": "Account Owner",
            "role": "owner",
            "tools": ["*"],
            "status": "active",
            "added_by": "system",
            "added_at": _now(),
        }],
        "created_at": _now(),
    }
    _save(db)
    return db[k]


def _find_user(acct, email):
    em = _key(email)
    for u in acct.get("users", []):
        if u["email"] == em:
            return u
    return None


def count_admins(acct):
    return sum(1 for u in acct["users"]
               if u["role"] in ("owner", "admin")
               and u["status"] == "active")


def seats_used(acct):
    return sum(1 for u in acct["users"] if u["status"] == "active")


def add_user(account_key, email, name, role="basic", tools=None,
             added_by="admin"):
    db = _load()
    acct = db.get(_key(account_key))
    if not acct:
        return False, "ACCOUNT_NOT_FOUND"
    if role not in VALID_ROLES or role == "owner":
        return False, "INVALID_ROLE"
    if _find_user(acct, email):
        return False, "USER_EXISTS"
    if seats_used(acct) >= acct["seats_total"]:
        return False, "NO_SEATS_LEFT"
    if role == "admin" and count_admins(acct) >= acct["max_admins"]:
        return False, "MAX_ADMINS_REACHED"
    acct["users"].append({
        "user_id": uuid.uuid4().hex[:12],
        "email": _key(email),
        "name": name or "",
        "role": role,
        "tools": tools if tools is not None else [],
        "status": "active",
        "added_by": added_by,
        "added_at": _now(),
    })
    db[_key(account_key)] = acct
    _save(db)
    return True, "OK"


def remove_user(account_key, email):
    db = _load()
    acct = db.get(_key(account_key))
    if not acct:
        return False, "ACCOUNT_NOT_FOUND"
    u = _find_user(acct, email)
    if not u:
        return False, "USER_NOT_FOUND"
    if u["role"] == "owner":
        return False, "CANNOT_REMOVE_OWNER"
    acct["users"] = [x for x in acct["users"] if x["email"] != _key(email)]
    db[_key(account_key)] = acct
    _save(db)
    return True, "OK"


def set_role(account_key, email, new_role):
    db = _load()
    acct = db.get(_key(account_key))
    if not acct:
        return False, "ACCOUNT_NOT_FOUND"
    if new_role not in VALID_ROLES or new_role == "owner":
        return False, "INVALID_ROLE"
    u = _find_user(acct, email)
    if not u:
        return False, "USER_NOT_FOUND"
    if u["role"] == "owner":
        return False, "CANNOT_CHANGE_OWNER"
    # promoting to admin -> check cap
    if new_role == "admin" and u["role"] != "admin":
        if count_admins(acct) >= acct["max_admins"]:
            return False, "MAX_ADMINS_REACHED"
    # demoting an admin -> ensure >=1 admin remains
    if u["role"] in ("admin", "owner") and new_role == "basic":
        if count_admins(acct) <= 1:
            return False, "NEED_AT_LEAST_ONE_ADMIN"
    u["role"] = new_role
    db[_key(account_key)] = acct
    _save(db)
    return True, "OK"


def set_tools(account_key, email, tools):
    db = _load()
    acct = db.get(_key(account_key))
    if not acct:
        return False, "ACCOUNT_NOT_FOUND"
    u = _find_user(acct, email)
    if not u:
        return False, "USER_NOT_FOUND"
    u["tools"] = tools or []
    db[_key(account_key)] = acct
    _save(db)
    return True, "OK"


def user_can_access(account_key, email, tool):
    acct = get_account(account_key)
    if not acct:
        return False
    u = _find_user(acct, email)
    if not u or u["status"] != "active":
        return False
    if "*" in u.get("tools", []):
        return True
    return tool in u.get("tools", [])


# ============================================================
# Phase 3: Departments + record visibility (hybrid A+B model)
# ============================================================

DEFAULT_DEPARTMENTS = [
    "Logistics", "Finance", "Sales", "Operations", "HR", "General"
]

# visibility levels for a record:
#   "private"    -> only owner_email
#   "department" -> everyone in the record's department (DEFAULT)
#   "shared"     -> department + record["shared_departments"] list
#   "company"    -> everyone in the account
VALID_VISIBILITY = ("private", "department", "shared", "company")


def get_departments(account_key):
    acct = get_account(account_key)
    if not acct:
        return list(DEFAULT_DEPARTMENTS)
    return acct.get("departments", list(DEFAULT_DEPARTMENTS))


def ensure_departments(account_key):
    """Seed default departments onto an account if missing."""
    db = _load()
    acct = db.get(_key(account_key))
    if not acct:
        return False, "ACCOUNT_NOT_FOUND"
    if "departments" not in acct:
        acct["departments"] = list(DEFAULT_DEPARTMENTS)
        db[_key(account_key)] = acct
        _save(db)
    return True, acct["departments"]


def set_departments(account_key, departments):
    """Replace the account's department list (company-customizable)."""
    db = _load()
    acct = db.get(_key(account_key))
    if not acct:
        return False, "ACCOUNT_NOT_FOUND"
    clean = [str(d).strip() for d in (departments or []) if str(d).strip()]
    if not clean:
        return False, "NEED_AT_LEAST_ONE_DEPARTMENT"
    acct["departments"] = clean
    db[_key(account_key)] = acct
    _save(db)
    return True, clean


def set_user_departments(account_key, email, departments):
    """Assign a user to one or more departments."""
    db = _load()
    acct = db.get(_key(account_key))
    if not acct:
        return False, "ACCOUNT_NOT_FOUND"
    u = _find_user(acct, email)
    if not u:
        return False, "USER_NOT_FOUND"
    valid = acct.get("departments", list(DEFAULT_DEPARTMENTS))
    clean = [d for d in (departments or []) if d in valid]
    u["departments"] = clean
    db[_key(account_key)] = acct
    _save(db)
    return True, clean


def user_departments(account_key, email):
    acct = get_account(account_key)
    if not acct:
        return []
    u = _find_user(acct, email)
    return u.get("departments", []) if u else []


def make_record(department, owner_email, visibility="department",
                shared_departments=None):
    """Helper to stamp visibility metadata onto any tool record."""
    if visibility not in VALID_VISIBILITY:
        visibility = "department"
    return {
        "_dept": department,
        "_owner": _key(owner_email),
        "_vis": visibility,
        "_shared": shared_departments or [],
    }


def share_record_to(record, department):
    """Cross-department bridge: share a record with another department."""
    record["_vis"] = "shared"
    lst = record.get("_shared", [])
    if department not in lst:
        lst.append(department)
    record["_shared"] = lst
    return record


def can_user_see_record(account_key, email, record):
    """
    The heart of the hybrid model. Returns True if this user may see
    this record, based on department + visibility + role overlay.
    """
    acct = get_account(account_key)
    if not acct:
        return True  # legacy/no-RBAC = allow (preserves old behavior)
    u = _find_user(acct, email)
    if not u or u.get("status") != "active":
        return False

    # Role overlay: owner/admin see everything (management view)
    if u.get("role") in ("owner", "admin"):
        return True

    vis = record.get("_vis", "department")
    rec_dept = record.get("_dept")
    rec_owner = record.get("_owner")
    my_depts = u.get("departments", [])

    if vis == "company":
        return True
    if vis == "private":
        return rec_owner == u.get("email")
    if vis == "department":
        return rec_dept in my_depts
    if vis == "shared":
        if rec_dept in my_depts:
            return True
        shared = record.get("_shared", [])
        return any(d in my_depts for d in shared)
    return False


# ============================================================
# Security: tools a bundle actually entitles (entitlement check)
# ============================================================
BUNDLE_TOOLS = {
    "astraa_the_one": ["estimator","logistics","business","finance",
                       "research_analyst","reports","vault","expense"],
    "astraa_business_elite": ["logistics","business","finance",
                              "research_analyst","reports","vault","expense"],
    "astraa_core": ["business","finance","research_analyst",
                    "reports","vault","expense"],
}

def account_allowed_tools(account_key):
    acct = get_account(account_key)
    if not acct:
        return None  # no record = don't restrict (legacy)
    return BUNDLE_TOOLS.get(acct.get("bundle"), None)

def filter_tools_to_entitlement(account_key, tools):
    """Return (clean_tools, rejected) limited to what the bundle allows.
    '*' is only allowed if the account has a known bundle (owner/admin full)."""
    allowed = account_allowed_tools(account_key)
    if allowed is None:
        return tools, []  # legacy/unknown = pass through
    if tools and "*" in tools:
        return ["*"], []
    clean = [t for t in (tools or []) if t in allowed]
    rejected = [t for t in (tools or []) if t not in allowed and t != "*"]
    return clean, rejected
