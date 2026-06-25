from pathlib import Path
import re
import json
import py_compile

app = Path("arka_v1.py")
if not app.exists():
    raise FileNotFoundError("arka_v1.py not found. Run this inside D:\\ARKA_HQ\\repos\\ardhanarishvara_git\\arka_v1")

code = app.read_text(encoding="utf-8-sig")

helpers = r'''
PRODUCTS = ["Commerce", "Data", "Inference", "Distribution", "Vault"]

DEFAULT_PRICING_MAP = {
    "Commerce": {
        "competitive_reference": "Shopify / BigCommerce / WooCommerce-style commerce platforms",
        "source_notes": [
            "Shopify-style market references commonly show tiered pricing around Basic, Grow, Advanced, and Plus.",
            "Use official provider pages before final pricing."
        ],
        "starter_direction": "Astraa Commerce should likely be priced as a business tool, not a cheap widget. Start with Basic/Professional/Custom."
    },
    "Data": {
        "competitive_reference": "Snowflake / data cloud / warehouse / workspace tools",
        "source_notes": [
            "Snowflake uses consumption-based pricing with compute credits and storage pricing.",
            "Astraa Data should avoid uncontrolled usage costs for small businesses."
        ],
        "starter_direction": "Astraa Data should use packaged tiers with usage caps, then custom pricing for larger data volumes."
    },
    "Inference": {
        "competitive_reference": "OpenAI API / inference API / agent pricing",
        "source_notes": [
            "OpenAI API pricing is token-based and model-dependent.",
            "Astraa Inference should price by included usage plus overage or custom contract."
        ],
        "starter_direction": "Astraa Inference should be gated carefully with included requests/tokens and strict overage controls."
    },
    "Distribution": {
        "competitive_reference": "Shippo / ShipStation / shipping and logistics software",
        "source_notes": [
            "Shippo has Starter/Pro/Premier-style pricing with label and shipment volume considerations.",
            "Astraa Distribution should be priced by shipment/location/operation complexity."
        ],
        "starter_direction": "Astraa Distribution should start as Professional/Custom for logistics-heavy businesses."
    },
    "Vault": {
        "competitive_reference": "Dropbox Business / Box / secure file vault and document storage",
        "source_notes": [
            "Dropbox Business pricing uses per-user tiers for team storage and security features.",
            "Astraa Vault should include secure document storage, audit, retention, and client access controls."
        ],
        "starter_direction": "Astraa Vault can be bundled with other tools or sold as secure document/audit storage."
    }
}


def extract_products_from_text(raw):
    text = raw or ""
    found = []

    for product in PRODUCTS:
        if re.search(rf"\b{re.escape(product)}\b", text, flags=re.I):
            found.append(product)

    # If user says "other tools" but no list, include all five currently open tools.
    if not found and any(x in text.lower() for x in ["other tools", "these products", "these product", "products up and running"]):
        found = PRODUCTS[:]

    # preserve order
    ordered = []
    for p in PRODUCTS:
        if p in found:
            ordered.append(p)

    return ordered


def is_product_ceo_directive(raw):
    w = (raw or "").lower()

    product_words = any(p.lower() in w for p in PRODUCTS)
    directive_words = any(x in w for x in [
        "get astraa",
        "get these product",
        "get these products",
        "up and running",
        "fully running",
        "competitive pricing",
        "find competitive pricing",
        "product up",
        "tools up",
        "start working",
        "get them working"
    ])

    return product_words and directive_words


def ensure_product_state():
    s = state()
    s.setdefault("product_work_queue", [])
    s.setdefault("competitive_pricing_queue", [])
    s.setdefault("competitive_pricing_map", DEFAULT_PRICING_MAP)
    save_state(s)
    return s


def add_product_work(product, directive):
    s = ensure_product_state()

    existing = [
        x for x in s.get("product_work_queue", [])
        if x.get("product") == product and x.get("status") in ["open", "in_progress"]
    ]

    if existing:
        return existing[0]

    item = {
        "id": uid(),
        "timestamp": now(),
        "product": product,
        "status": "open",
        "priority": "high",
        "directive": directive,
        "mission": f"Get Astraa {product} up and running fully: product page, feature scope, pricing, lead path, and readiness checks.",
        "next_actions": [
            f"Audit local Astraa {product} files/pages/modules.",
            f"Create or update public website positioning for {product}.",
            f"Find competitive pricing references for {product}.",
            f"Prepare Basic / Professional / Custom packaging recommendation for {product}.",
            f"Log readiness gaps and action queue items for {product}."
        ]
    }

    s["product_work_queue"].insert(0, item)
    save_state(s)

    try:
        business_event("product_tools", "product_work_assigned", json.dumps(item), "open")
    except Exception:
        log_event("product_work_assigned", item)

    return item


def add_competitive_pricing_work(product):
    s = ensure_product_state()

    existing = [
        x for x in s.get("competitive_pricing_queue", [])
        if x.get("product") == product and x.get("status") in ["open", "in_progress"]
    ]

    if existing:
        return existing[0]

    pricing = DEFAULT_PRICING_MAP.get(product, {})

    item = {
        "id": uid(),
        "timestamp": now(),
        "product": product,
        "status": "open",
        "priority": "high",
        "mission": f"Find competitive pricing and package recommendation for Astraa {product}.",
        "competitive_reference": pricing.get("competitive_reference", ""),
        "starter_direction": pricing.get("starter_direction", ""),
        "research_sources_needed": [
            f"Official pricing pages for top {product} competitors",
            "Current monthly pricing",
            "Usage limits",
            "Free trial model",
            "Feature differences",
            "Best Astraa Basic / Professional / Custom fit"
        ]
    }

    s["competitive_pricing_queue"].insert(0, item)
    save_state(s)

    try:
        business_event("pricing", "competitive_pricing_assigned", json.dumps(item), "open")
    except Exception:
        log_event("competitive_pricing_assigned", item)

    return item


def handle_product_ceo_directive(raw):
    products = extract_products_from_text(raw)

    if not products:
        return "Tell me which Astraa products you want me to assign."

    # Save this directive as active memory too because this is CEO-level product direction.
    try:
        save_active_memory("CEO directive: " + raw.strip())
    except Exception:
        pass

    work_items = []
    pricing_items = []

    for product in products:
        work_items.append(add_product_work(product, raw.strip()))
        pricing_items.append(add_competitive_pricing_work(product))

    lines = [
        "Got it. I created CEO/COO product work assignments for Astraa.",
        "",
        "Products assigned:"
    ]

    for product in products:
        lines.append(f"- {product}: open → product readiness + website page + competitive pricing")

    lines.append("")
    lines.append("Immediate operating plan:")
    lines.append("1. Audit each product’s local files/pages/modules.")
    lines.append("2. Build or update website positioning for each product.")
    lines.append("3. Find competitive pricing references.")
    lines.append("4. Recommend Astraa Basic / Professional / Custom packaging.")
    lines.append("5. Log readiness gaps and next actions.")
    lines.append("")
    lines.append("Use: show product work queue")
    lines.append("Use: show competitive pricing")

    return "\n".join(lines)


def render_product_work_queue_text():
    s = ensure_product_state()
    queue = s.get("product_work_queue", [])

    if not queue:
        return "No Astraa product work items are open yet."

    lines = ["Astraa product work queue:"]
    for item in queue[:20]:
        lines.append("")
        lines.append(f"- {item.get('product')} | {item.get('status')} | {item.get('priority')}")
        lines.append(f"  Mission: {item.get('mission')}")
        for action in item.get("next_actions", [])[:5]:
            lines.append(f"  - {action}")

    return "\n".join(lines)


def render_competitive_pricing_text(product_filter=""):
    s = ensure_product_state()
    queue = s.get("competitive_pricing_queue", [])
    pricing_map = s.get("competitive_pricing_map", DEFAULT_PRICING_MAP)

    product_filter = (product_filter or "").strip().lower()

    if product_filter:
        queue = [x for x in queue if product_filter in x.get("product", "").lower()]

    if not queue:
        return "No competitive pricing work items are open yet."

    lines = ["Competitive pricing work queue:"]

    for item in queue[:20]:
        product = item.get("product", "")
        pricing = pricing_map.get(product, {})

        lines.append("")
        lines.append(f"- {product} | {item.get('status')} | {item.get('priority')}")
        lines.append(f"  Reference market: {item.get('competitive_reference')}")
        lines.append(f"  Starter direction: {item.get('starter_direction')}")

        notes = pricing.get("source_notes", [])
        if notes:
            lines.append("  Source notes:")
            for note in notes:
                lines.append("  - " + note)

    return "\n".join(lines)


def product_dashboard_html():
    s = state()
    product_queue = s.get("product_work_queue", [])
    pricing_queue = s.get("competitive_pricing_queue", [])

    html = []
    html.append("<h3>Astraa Product Command</h3>")

    if not product_queue:
        html.append("<p>No product work assigned yet.</p>")
    else:
        html.append("<p><b>Product work queue</b></p>")
        for item in product_queue[:8]:
            html.append("<p>• " + esc(item.get("product", "")) + ": " + esc(item.get("status", "")) + " — " + esc(item.get("mission", "")) + "</p>")

    if pricing_queue:
        html.append("<p><b>Competitive pricing queue</b></p>")
        for item in pricing_queue[:8]:
            html.append("<p>• " + esc(item.get("product", "")) + ": " + esc(item.get("status", "")) + " — " + esc(item.get("competitive_reference", "")) + "</p>")

    return "".join(html)
'''

if "def handle_product_ceo_directive(raw):" not in code:
    code = code.replace("def arka_reply(raw):", helpers + "\n\ndef arka_reply(raw):", 1)

router = r'''
    # Product CEO/COO directive router.
    if is_product_ceo_directive(raw):
        return handle_product_ceo_directive(raw)

    if w.startswith("show product work queue") or w.startswith("show astraa product work"):
        return render_product_work_queue_text()

    if w.startswith("show competitive pricing") or w.startswith("show pricing queue"):
        return render_competitive_pricing_text()

    if w.startswith("competitive pricing for "):
        product = raw[len("competitive pricing for "):].strip()
        return render_competitive_pricing_text(product)
'''

if "Product CEO/COO directive router." not in code:
    targets = ["    w = raw.lower()", "    w=raw.lower()"]
    patched = False
    for target in targets:
        if target in code:
            code = code.replace(target, target + "\n" + router, 1)
            patched = True
            break
    if not patched:
        raise RuntimeError("Could not find w = raw.lower() inside arka_reply.")

# Patch executive panel to include product dashboard if possible.
if "product_dashboard_html()" not in code:
    code = code.replace(
        'html.append("<h3>Astraa Revenue Command</h3>")',
        'html.append("<h3>Astraa Revenue Command</h3>")\n    html.append(product_dashboard_html())',
        1
    )

app.write_text(code, encoding="utf-8")
py_compile.compile(str(app), doraise=True)

print("[OK] Arka V1 product CEO/COO router applied.")
print("[OK] Test your original product directive again.")
print("[OK] Then test: show product work queue")
print("[OK] Then test: show competitive pricing")
