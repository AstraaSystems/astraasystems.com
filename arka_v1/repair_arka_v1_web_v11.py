from pathlib import Path
import re
import py_compile

app = Path("arka_v1.py")
if not app.exists():
    raise FileNotFoundError("arka_v1.py not found. Run inside D:\\ARKA_HQ\\repos\\ardhanarishvara_git\\arka_v1")

code = app.read_text(encoding="utf-8-sig")

helpers = r'''
def arka_encode_query(q):
    return urllib.parse.quote_plus((q or "").strip())


def arka_source_link_fallback(query):
    """
    If live scraping is blocked, return useful source/search links.
    This is better than a dead-end response and does not fake facts.
    """
    q = (query or "").strip()
    enc = arka_encode_query(q)

    links = [
        ("Bing search", "https://www.bing.com/search?q=" + enc),
        ("DuckDuckGo search", "https://duckduckgo.com/?q=" + enc),
        ("Google search", "https://www.google.com/search?q=" + enc)
    ]

    lines = [
        "I could not pull reliable live snippets from the local web connector.",
        "I won't make anything up, but here are source links you can open/check:",
        ""
    ]

    for name, url in links:
        lines.append("- " + name + ": " + url)

    log_event("web_source_fallback", q)
    return "\\n".join(lines)


def arka_search_or_sources(query):
    """
    Try Arka's live web search function if available.
    If it returns nothing, provide useful source links.
    """
    q = (query or "").strip()
    if not q:
        return "Tell me what you want me to search."

    results = []

    # Prefer strongest local search helper available.
    try:
        if "arka_web_search_v2" in globals():
            results = arka_web_search_v2(q, limit=8)
        elif "web_search_sources" in globals():
            results = web_search_sources(q, limit=8)
    except Exception as e:
        log_event("web_search_runtime_error", str(e))
        results = []

    if results:
        try:
            if "format_web_results_v2" in globals():
                return format_web_results_v2(q, results)
            return format_web_results(q, results)
        except Exception:
            lines = ["Here is what I found for: " + q, ""]
            for i, r in enumerate(results, 1):
                lines.append(str(i) + ". " + r.get("title", "Result"))
                if r.get("snippet"):
                    lines.append("   " + r.get("snippet"))
                lines.append("   Source: " + r.get("url", ""))
                lines.append("")
            return "\\n".join(lines).strip()

    return arka_source_link_fallback(q)


def arka_flight_source_fallback(raw):
    """
    Travel source mode. No fake prices. No ticket holds.
    Special handling for Vancouver/YVR to Hyderabad/HYD.
    """
    q = (raw or "").strip()
    low = q.lower()

    # Normalize likely route.
    from_yvr = any(x in low for x in ["vancouver", "yvr"])
    to_hyd = any(x in low for x in ["hyderabad", "hyd"])

    lines = [
        "I could not pull verified live fare snippets from the local connector.",
        "I won't invent prices and I won't claim ticket holds.",
        ""
    ]

    if from_yvr and to_hyd:
        lines.append("Best source pages for Vancouver/YVR to Hyderabad/HYD:")
        lines.append("- Google Flights route page: https://www.google.com/travel/flights/flights-from-vancouver-to-hyderabad.html")
        lines.append("- Skyscanner Canada route page: https://www.skyscanner.ca/routes/yvra/hyd/vancouver-to-hyderabad.html")
        lines.append("- Skyscanner YVR-HYD route page: https://www.skyscanner.com/routes/yvr/hyd/vancouver-international-to-hyderabad.html")
        lines.append("")
        lines.append("For December 2026, use the date grid / month view on those pages to verify live fares.")
    else:
        enc = arka_encode_query(q + " flight prices")
        lines.append("Flight search sources:")
        lines.append("- Google Flights: https://www.google.com/travel/flights")
        lines.append("- Bing travel search: https://www.bing.com/search?q=" + enc)
        lines.append("- DuckDuckGo travel search: https://duckduckgo.com/?q=" + enc)
        lines.append("- Skyscanner: https://www.skyscanner.ca/")
        lines.append("- Kayak: https://www.ca.kayak.com/flights")
        lines.append("- Expedia: https://www.expedia.ca/Flights")

    log_event("flight_source_fallback", q)
    return "\\n".join(lines)


def arka_is_general_question(raw):
    w = (raw or "").lower().strip()

    if not w:
        return False

    # Avoid routing personal memory or command phrases to web.
    blocked = [
        "what is my wife",
        "what's my wife",
        "what is my son",
        "what's my son",
        "what do you remember",
        "what did i say",
        "show memory",
        "show journal",
        "record this",
        "save this",
        "remember that",
        "check website",
        "how are sales",
        "marketing",
        "assign astraa"
    ]

    if any(b in w for b in blocked):
        return False

    starters = [
        "what ", "who ", "when ", "where ", "why ", "how ",
        "do ", "does ", "did ", "can ", "could ", "should ",
        "best ", "find ", "search ", "compare ", "price ", "prices ",
        "tell me about "
    ]

    return w.endswith("?") or any(w.startswith(s) for s in starters)


def arka_general_question_response(raw):
    """
    For unknown factual questions, do source mode rather than dead fallback.
    """
    q = (raw or "").strip()
    if not q:
        return "I'm here."

    # Flight/travel gets travel source handling.
    low = q.lower()
    if any(x in low for x in ["flight", "flights", "airfare", "ticket price", "ticket prices", "travel price"]):
        return arka_flight_source_fallback(q)

    return arka_search_or_sources(q)
'''

if "def arka_source_link_fallback(query):" not in code:
    code = code.replace("def arka_reply(raw):", helpers + "\n\ndef arka_reply(raw):", 1)

router = r'''
    # V1.1 web search and question fallback.
    if (
        w.startswith("search the web for ")
        or w.startswith("web search ")
        or w.startswith("search ")
        or w.startswith("look up ")
        or w.startswith("google ")
    ):
        q = raw.strip()
        for prefix in [
            "search the web for ",
            "web search ",
            "search ",
            "look up ",
            "google "
        ]:
            if q.lower().startswith(prefix):
                q = q[len(prefix):].strip()
                break
        return arka_search_or_sources(q)

    if any(x in w for x in [
        "flight price",
        "flight prices",
        "find flight",
        "best flight",
        "airfare",
        "ticket price",
        "ticket prices"
    ]):
        return arka_flight_source_fallback(raw)

    if arka_is_general_question(raw):
        return arka_general_question_response(raw)
'''

if "V1.1 web search and question fallback." not in code:
    targets = ["    w = raw.lower()", "    w=raw.lower()"]
    patched = False
    for target in targets:
        if target in code:
            code = code.replace(target, target + "\n" + router, 1)
            patched = True
            break
    if not patched:
        raise RuntimeError("Could not find w = raw.lower() inside arka_reply.")

# Replace the dead-end generic fallback if present.
old_fallbacks = [
    'return "Yeah, I got you. Tell me what you want me to do next."',
    'return "Yeah, I got you. Tell me what you want me to do next."'
]

new_fallback = '''
    if arka_is_general_question(raw):
        return arka_general_question_response(raw)

    return "I’m with you. Tell me if you want me to record it, research it, check Astraa, or turn it into an action."
'''

for old in old_fallbacks:
    if old in code:
        code = code.replace(old, new_fallback, 1)

app.write_text(code, encoding="utf-8")
py_compile.compile(str(app), doraise=True)

print("[OK] Arka V1.1 web/question fallback repair applied.")
print("[OK] Test: search the web for Astraa Systems competitors")
print("[OK] Test: Do best flight prices for Hyderabad India leaving from vancouver on Dec 2026")
print("[OK] Test: what is Moneris?")
