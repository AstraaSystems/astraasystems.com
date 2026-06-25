from __future__ import annotations

import ast
import math
import operator
import re
from decimal import Decimal, ROUND_HALF_UP

MATH_OS_NAME = "Arka Math OS"
MATH_OS_VERSION = "1.0"

# ------------------------------------------------------------
# Formatting helpers
# ------------------------------------------------------------

def money(value):
    try:
        return f"${float(value):,.2f}"
    except Exception:
        return str(value)

def whole(value):
    try:
        return f"{math.ceil(float(value)):,}"
    except Exception:
        return str(value)

def number(value):
    try:
        v = float(value)
        if abs(v - round(v)) < 1e-9:
            return f"{int(round(v)):,}"
        return f"{v:,.4f}".rstrip("0").rstrip(".")
    except Exception:
        return str(value)

def parse_money_values(text):
    vals = []
    for m in re.finditer(r"\$?\s*([0-9][0-9,]*(?:\.[0-9]+)?)", text or ""):
        try:
            vals.append(float(m.group(1).replace(",", "")))
        except Exception:
            pass
    return vals

def parse_percent(text):
    m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*%", text or "")
    if m:
        return float(m.group(1)) / 100.0

    m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*(percent|percentage)", text or "", flags=re.I)
    if m:
        return float(m.group(1)) / 100.0

    return None

def extract_years(text, default=1):
    m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*(year|years|yr|yrs)", text or "", flags=re.I)
    if m:
        return float(m.group(1))
    if "one year" in (text or "").lower():
        return 1
    return default

# ------------------------------------------------------------
# Safe arithmetic evaluator
# ------------------------------------------------------------

_ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

_ALLOWED_FUNCS = {
    "sqrt": math.sqrt,
    "ceil": math.ceil,
    "floor": math.floor,
    "round": round,
    "abs": abs,
    "pow": pow,
    "min": min,
    "max": max,
}

def safe_eval_expr(expr):
    expr = expr.strip()
    expr = expr.replace("$", "").replace(",", "")
    expr = expr.replace("×", "*").replace("÷", "/")

    tree = ast.parse(expr, mode="eval")

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Only numeric constants are allowed.")

        if isinstance(node, ast.Num):
            return node.n

        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in _ALLOWED_OPS:
                raise ValueError("Operator not allowed.")
            return _ALLOWED_OPS_eval(node.left, _eval(node.right))

        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in _ALLOWED_OPS:
                raise ValueError("Unary operator not allowed.")
            return _ALLOWED_OPS_eval(node.operand)

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Function not allowed.")
            name = node.func.id
            if name not in _ALLOWED_FUNCS:
                raise ValueError("Function not allowed.")
            args = [_eval(a) for a in node.args]
            return _ALLOWED_FUNCS*args

        raise ValueError("Unsupported expression.")

    return _eval(tree)

def looks_like_arithmetic(text):
    t = (text or "").strip().lower()
    if t.startswith(("calculate ", "math ", "solve ")):
        return True
    # e.g. "50000 / 12", "$99.99 * 100"
    return bool(re.fullmatch(r"[0-9,\s\.\$\+\-\*\/\(\)%×÷]+", t))

def arithmetic_response(raw):
    expr = raw.strip()
    for prefix in ["calculate ", "math ", "solve "]:
        if expr.lower().startswith(prefix):
            expr = expr[len(prefix):].strip()

    try:
        result = safe_eval_expr(expr)
        return f"Math OS result:\n\n{expr} = {number(result)}"
    except Exception as e:
        return f"I tried to calculate that, but Math OS could not parse the expression cleanly: {e}"

# ------------------------------------------------------------
# Goal / income / savings math
# ------------------------------------------------------------

def goal_breakdown(raw):
    vals = parse_money_values(raw)
    if not vals:
        return ""

    target = vals[0]
    years = extract_years(raw, default=1)
    months = years * 12
    weeks = years * 52
    days = years * 365

    monthly = target / months
    weekly = target / weeks
    daily = target / days

    lines = [
        f"Math OS goal breakdown for {money(target)} over {number(years)} year(s):",
        "",
        f"- Monthly target: {money(monthly)}",
        f"- Weekly target: {money(weekly)}",
        f"- Daily target: {money(daily)}",
    ]

    return "\n".join(lines)

def revenue_customer_count(raw):
    """
    Examples:
    - how many $99.99 customers do we need to make $10,000/month
    - how many customers at $39.99 to make $5000
    """
    w = raw.lower()
    vals = parse_money_values(raw)

    if len(vals) < 2:
        return ""

    # Heuristic:
    # If text says "customers at $X to make $Y", first is price, second is target.
    # If text says "make $Y with $X customers/plan", still use smaller as price if clear.
    if "customer" not in w and "subscription" not in w and "plan" not in w:
        return ""

    price = min(vals)
    target = max(vals)

    if price <= 0:
        return ""

    customers = math.ceil(target / price)
    actual = customers * price

    lines = [
        "Math OS revenue/customer target:",
        "",
        f"- Target revenue: {money(target)}",
        f"- Price per customer/plan: {money(price)}",
        f"- Customers needed: {customers:,}",
        f"- Revenue at {customers:,} customers: {money(actual)}",
    ]

    return "\n".join(lines)

def doordash_scenario(raw):
    w = raw.lower()
    if not any(x in w for x in ["doordash", "door dash", "dasher", "delivery", "deliveries"]):
        return ""

    vals = parse_money_values(raw)
    if not vals:
        return ""

    target = vals[0]
    years = extract_years(raw, default=1)
    weeks = years * 52

    weekly = target / weeks
    monthly = target / (years * 12)

    avg_pays = [6, 8, 10, 12, 15]

    lines = [
        f"Math OS DoorDash / delivery scenario for {money(target)} over {number(years)} year(s):",
        "",
        f"- Monthly target: {money(monthly)}",
        f"- Weekly target: {money(weekly)}",
        "",
        "Gross delivery count estimate before expenses/tax:",
        "",
        "| Avg pay per delivery | Deliveries/day if working daily | Deliveries/workday if working 3 days/week |",
        "|---:|---:|---:|",
    ]

    for pay in avg_pays:
        per_day = (weekly / 7) / pay
        per_3 = (weekly / 3) / pay
        lines.append(f"| ${pay} | {math.ceil(per_day)}/day | {math.ceil(per_3)}/workday |")

    expense_rate = 0.25
    se_tax_rate = 0.153
    gross_needed = target / ((1 - expense_rate) * (1 - se_tax_rate))
    weekly_gross = gross_needed / weeks
    monthly_gross = gross_needed / (years * 12)

    lines.extend([
        "",
        "Conservative take-home scenario using 25% expenses and 15.3% self-employment tax:",
        "",
        f"- Estimated gross needed: {money(gross_needed)}",
        f"- Monthly gross needed: {money(monthly_gross)}",
        f"- Weekly gross needed: {money(weekly_gross)}",
        "",
        "| Avg pay per delivery | Deliveries/day if working daily | Deliveries/workday if working 3 days/week |",
        "|---:|---:|---:|",
    ])

    for pay in avg_pays:
        per_day = (weekly_gross / 7) / pay
        per_3 = (weekly_gross / 3) / pay
        lines.append(f"| ${pay} | {math.ceil(per_day)}/day | {math.ceil(per_3)}/workday |")

    lines.extend([
        "",
        "Math OS note: this is a planning estimate, not guaranteed earnings. Actual DoorDash earnings depend on market, hours, tips, distance, gas, vehicle costs, and taxes."
    ])

    return "\n".join(lines)

# ------------------------------------------------------------
# Business math
# ------------------------------------------------------------

def percent_math(raw):
    w = raw.lower()
    vals = parse_money_values(raw)
    pct = parse_percent(raw)

    if pct is None:
        return ""

    if "of" in w and vals:
        base = vals[-1]
        result = base * pct
        return f"Math OS percentage:\n\n{number(pct * 100)}% of {money(base)} = {money(result)}"

    if any(x in w for x in ["increase", "markup", "raise"]) and vals:
        base = vals[-1]
        result = base * (1 + pct)
        return f"Math OS percentage increase:\n\n{money(base)} increased by {number(pct * 100)}% = {money(result)}"

    if any(x in w for x in ["decrease", "discount", "off"]) and vals:
        base = vals[-1]
        result = base * (1 - pct)
        return f"Math OS percentage decrease:\n\n{money(base)} decreased by {number(pct * 100)}% = {money(result)}"

    return ""

def margin_profit(raw):
    w = raw.lower()
    if not any(x in w for x in ["margin", "profit", "markup"]):
        return ""

    vals = parse_money_values(raw)
    if len(vals) < 2:
        return ""

    cost = vals[0]
    price = vals[1]

    if price <= 0:
        return ""

    profit = price - cost
    margin = profit / price
    markup = profit / cost if cost else 0

    lines = [
        "Math OS profit/margin:",
        "",
        f"- Cost: {money(cost)}",
        f"- Price: {money(price)}",
        f"- Profit: {money(profit)}",
        f"- Margin: {number(margin * 100)}%",
        f"- Markup: {number(markup * 100)}%",
    ]

    return "\n".join(lines)

def break_even(raw):
    w = raw.lower()
    if "break even" not in w and "breakeven" not in w:
        return ""

    vals = parse_money_values(raw)
    if len(vals) < 2:
        return ""

    fixed = vals[0]
    profit_per_unit = vals[1]

    if profit_per_unit <= 0:
        return "Math OS break-even needs positive profit per unit."

    units = math.ceil(fixed / profit_per_unit)

    return (
        "Math OS break-even:\n\n"
        f"- Fixed cost / target recovery: {money(fixed)}\n"
        f"- Profit per unit/customer: {money(profit_per_unit)}\n"
        f"- Break-even units/customers needed: {units:,}"
    )

def compound_growth(raw):
    w = raw.lower()
    if not any(x in w for x in ["compound", "cagr", "growth"]):
        return ""

    vals = parse_money_values(raw)
    pct = parse_percent(raw)
    years = extract_years(raw, default=1)

    if len(vals) >= 2 and "cagr" in w:
        start, end = vals[0], vals[1]
        if start <= 0 or years <= 0:
            return ""
        cagr = (end / start) ** (1 / years) - 1
        return (
            "Math OS CAGR:\n\n"
            f"- Start: {money(start)}\n"
            f"- End: {money(end)}\n"
            f"- Years: {number(years)}\n"
            f"- CAGR: {number(cagr * 100)}%"
        )

    if vals and pct is not None:
        principal = vals[0]
        future = principal * ((1 + pct) ** years)
        return (
            "Math OS compound growth:\n\n"
            f"- Starting amount: {money(principal)}\n"
            f"- Growth rate: {number(pct * 100)}%\n"
            f"- Years: {number(years)}\n"
            f"- Future value: {money(future)}"
        )

    return ""

def loan_payment(raw):
    w = raw.lower()
    if not any(x in w for x in ["loan", "mortgage", "payment"]):
        return ""

    vals = parse_money_values(raw)
    pct = parse_percent(raw)
    years = extract_years(raw, default=1)

    if not vals or pct is None:
        return ""

    principal = vals[0]
    monthly_rate = pct / 12
    n = years * 12

    if monthly_rate == 0:
        payment = principal / n
    else:
        payment = principal * (monthly_rate * (1 + monthly_rate) ** n) / ((1 + monthly_rate) ** n - 1)

    total = payment * n
    interest = total - principal

    return (
        "Math OS loan/payment estimate:\n\n"
        f"- Principal: {money(principal)}\n"
        f"- Annual rate: {number(pct * 100)}%\n"
        f"- Term: {number(years)} year(s)\n"
        f"- Monthly payment: {money(payment)}\n"
        f"- Total paid: {money(total)}\n"
        f"- Estimated interest: {money(interest)}"
    )

# ------------------------------------------------------------
# Router
# ------------------------------------------------------------

def is_math_intent(raw):
    w = (raw or "").lower().strip()

    if looks_like_arithmetic(raw):
        return True

    triggers = [
        "calculate", "math", "solve",
        "how much monthly", "how much per month", "per month",
        "how many customers", "customers do we need",
        "monthly target", "weekly target", "daily target",
        "make $", "save $", "one year", "1 year",
        "doordash", "door dash", "delivery", "deliveries",
        "margin", "profit", "markup", "break even", "breakeven",
        "compound", "cagr", "loan", "mortgage", "payment",
        "percentage", "% of", "discount", "increase", "decrease"
    ]

    if any(t in w for t in triggers) and parse_money_values(raw):
        return True

    if any(t in w for t in ["how many", "how much"]) and any(ch.isdigit() for ch in w):
        return True

    return False

def arka_math_os_router(raw):
    raw = raw or ""

    if not is_math_intent(raw):
        return ""

    # Order matters: specific before general.
    handlers = [
        doordash_scenario,
        revenue_customer_count,
        loan_payment,
        break_even,
        margin_profit,
        compound_growth,
        percent_math,
        goal_breakdown,
    ]

    for handler in handlers:
        try:
            result = handler(raw)
            if result:
                return result
        except Exception as e:
            return f"Math OS hit an error in {handler.__name__}: {e}"

    if looks_like_arithmetic(raw):
        return arithmetic_response(raw)

    # fallback: if it has money + year/month, still do goal breakdown
    result = goal_breakdown(raw)
    if result:
        return result

    return "Math OS detected a calculation request, but I need clearer numbers to solve it."
