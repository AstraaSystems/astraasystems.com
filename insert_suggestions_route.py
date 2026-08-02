import shutil
from pathlib import Path
from datetime import datetime

p = Path("api.py")
s = p.read_text(encoding="utf-8")
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copyfile("api.py", f"api.py.before_suggestions_{stamp}")

anchor = "# ===== ASTRAA REPORTS (read-only analytics over Finance + Expense) ====="
if s.count(anchor) != 1:
    print("ABORT: anchor not found exactly once:", s.count(anchor)); raise SystemExit

block = '''# ===== ASTRAA SMART SUGGESTIONS (read-only tips over Finance + Expense + Quotes) =====
@app.route("/api/suggestions/list", methods=["GET"])
def astraa_suggestions_list():
    identity = astraa_resolve_session_identity(request)
    if not identity:
        return astraa_json_response({"success": False, "error": "Not authenticated."}, 401)
    email = identity.get("account_email"); key = astraa_account_key(email)

    # --- gather data (read-only) ---
    fdb, fkey = _astraa_fin_bucket(email); b = fdb[fkey]
    invoices = b.get("invoices", [])
    fin_income = b.get("income", [])
    fin_expenses = b.get("expenses", [])

    exp_entries = []
    try:
        edb = _astraa_load_expenses()
        exp_entries = edb.get(key, []) or []
    except Exception:
        exp_entries = []

    rec = astraa_storage_load_usage_db().get(key) or {}
    quotes = rec.get("saved_estimates") or []

    def month_key(dstr):
        return str(dstr or "")[:7]

    from datetime import datetime as _dt
    this_m = _dt.now().strftime("%Y-%m")
    ly, lm = _dt.now().year, _dt.now().month - 1
    if lm == 0: lm = 12; ly -= 1
    last_m = "%04d-%02d" % (ly, lm)

    # totals
    inv_income = sum(float(i.get("amount",0) or 0) for i in invoices if i.get("status")=="Paid")
    manual_income = sum(float(x.get("amount",0) or 0) for x in fin_income)
    total_income = inv_income + manual_income
    manual_expense = sum(float(x.get("amount",0) or 0) for x in fin_expenses)
    tool_expense = sum(float(x.get("amount",0) or 0) for x in exp_entries)
    total_expense = manual_expense + tool_expense
    net = total_income - total_expense

    # overdue / pending
    pending = [i for i in invoices if i.get("status") in ("Pending","Overdue")]
    pending_total = sum(float(i.get("amount",0) or 0) for i in pending)

    # monthly expense compare
    def exp_for(m):
        t = sum(float(x.get("amount",0) or 0) for x in fin_expenses if month_key(x.get("date"))==m)
        t += sum(float(x.get("amount",0) or 0) for x in exp_entries if month_key(x.get("date"))==m)
        return t
    this_exp = exp_for(this_m); last_exp = exp_for(last_m)

    # expense category concentration
    by_cat = {}
    for x in exp_entries:
        c = (x.get("category") or "Other")
        by_cat[c] = by_cat.get(c,0) + float(x.get("amount",0) or 0)
    for x in fin_expenses:
        c = (x.get("category") or "Other")
        by_cat[c] = by_cat.get(c,0) + float(x.get("amount",0) or 0)

    tips = []
    def money(n): return "$" + format(round(float(n or 0),2), ",.2f")

    # 1) overdue / unpaid invoices
    if pending:
        tips.append({"severity":"warning","icon":"\\U0001F4B0",
            "title":"Money waiting to be collected",
            "detail":"You have " + money(pending_total) + " across " + str(len(pending)) + " unpaid invoice(s).",
            "action":"Open Finance and send a friendly follow-up to these clients."})

    # 2) spending spike
    if last_exp > 0 and this_exp > last_exp * 1.2:
        pct = round((this_exp/last_exp - 1) * 100)
        tips.append({"severity":"warning","icon":"\\U0001F4C8",
            "title":"Expenses are up this month",
            "detail":"This month's expenses (" + money(this_exp) + ") are about " + str(pct) + "% higher than last month (" + money(last_exp) + ").",
            "action":"Review recent expenses to make sure nothing is off."})

    # 3) unconverted quotes
    n_unconv = max(0, len(quotes) - len(invoices))
    if len(quotes) > 0 and n_unconv > 0:
        tips.append({"severity":"info","icon":"\\U0001F4CB",
            "title":"Quotes ready to become invoices",
            "detail":"You have " + str(n_unconv) + " saved quote(s) that may not be invoiced yet.",
            "action":"In Estimator, turn accepted quotes into invoices so you get paid."})

    # 4) thin margin
    if total_income > 0:
        margin = net / total_income * 100
        if margin < 10:
            tips.append({"severity":"warning","icon":"\\u26A0\\uFE0F",
                "title":"Your profit margin is thin",
                "detail":"Overall margin is about " + str(round(margin)) + "%. Income " + money(total_income) + ", expenses " + money(total_expense) + ".",
                "action":"Consider reviewing pricing or trimming costs where you can."})

    # 5) category concentration
    if total_expense > 0 and by_cat:
        top_cat = max(by_cat.items(), key=lambda kv: kv[1])
        share = top_cat[1] / total_expense * 100
        if share >= 40:
            tips.append({"severity":"info","icon":"\\U0001F5C2\\uFE0F",
                "title":"Most spending is in one area",
                "detail":"\\"" + str(top_cat[0]) + "\\" is about " + str(round(share)) + "% of your expenses (" + money(top_cat[1]) + ").",
                "action":"Worth checking if this category can be reduced or negotiated."})

    # 6) healthy cash (positive note)
    if total_income > 0 and net > 0 and not pending:
        tips.append({"severity":"good","icon":"\\u2705",
            "title":"You're in good shape",
            "detail":"You're cash-positive (" + money(net) + " profit) with no unpaid invoices. Nice work.",
            "action":"Keep it up \\u2014 maybe set aside some profit for taxes and slow months."})

    # empty-state
    if not tips:
        tips.append({"severity":"info","icon":"\\U0001F44B",
            "title":"Nothing needs your attention yet",
            "detail":"As you add invoices and expenses, helpful suggestions will show up here.",
            "action":"Start by adding an invoice in Finance or an expense in Expense."})

    order = {"warning":0,"info":1,"good":2}
    tips.sort(key=lambda t: order.get(t.get("severity"),1))
    return astraa_json_response({"success": True, "count": len(tips), "tips": tips})
# ===== END ASTRAA SMART SUGGESTIONS =====

'''

s = s.replace(anchor, block + anchor, 1)
p.write_text(s, encoding="utf-8")
print("Suggestions route inserted. Backup: api.py.before_suggestions_" + stamp)
