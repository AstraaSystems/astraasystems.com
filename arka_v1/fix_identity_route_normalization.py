from pathlib import Path
import re
import py_compile

path = Path("arka_governor_dispatcher.py")
code = path.read_text(encoding="utf-8-sig")

old_func = r'''def _is_identity_question(raw: str) -> bool:
    w = (raw or "").strip().lower()
    return w in {
        "who am i",
        "who am i?",
        "whoami",
        "who is the owner",
        "who owns arka",
        "who is arka built for",
        "who is the founder",
        "who is keshanth"
    }
'''

new_func = r'''def _is_identity_question(raw: str) -> bool:
    """
    Identity / owner questions must resolve from local owner/profile/memory,
    not web search. Normalize spaces/punctuation so variants like
    'who am I ?' still match.
    """
    text = (raw or "").strip().lower()

    # Normalize punctuation spacing:
    # "who am i ?" -> "who am i?"
    text = re.sub(r"\s+([?.!])", r"\1", text)
    text = re.sub(r"[?.!]+$", "", text).strip()
    text = re.sub(r"\s+", " ", text)

    identity_forms = {
        "who am i",
        "whoami",
        "who is the owner",
        "who owns arka",
        "who is arka built for",
        "who is the founder",
        "who is keshanth",
        "who is keshanth sivayogampillai"
    }

    return text in identity_forms
'''

if old_func not in code:
    raise RuntimeError("Could not find old _is_identity_question function exactly.")

code = code.replace(old_func, new_func, 1)

path.write_text(code, encoding="utf-8")
py_compile.compile(str(path), doraise=True)

print("[OK] Identity normalization fixed.")
