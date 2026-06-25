from __future__ import annotations

from arka_governor_dispatcher import arka_governor_dispatch

# Each test can be:
# (prompt, expected_text)
# or later:
# (prompt, expected_text, notes)
TESTS = [
    ("who am I ?", "Identity / Owner"),
    ("status", "Arka Governor Status"),
    ("could run status on our website", "Astraa Website Status"),
    ("has anyone signed up for the estimator?", "Astraa Leads / Signups Status"),
    ("who is lux", "Self-Discovered Ecosystem Registry"),
    ("Name all the Ai inside our ecosystem", "Generated from local ecosystem self-discovery"),
    ("tell me about the new VW ID.4? how many packages are available and what is it priced at?", "Astraa Safe Web Access"),
    ("How to bring Likely Astraa website files found locally: 255 down ?", "Astraa Website File Hygiene"),
]

def main():
    failures = []

    for test in TESTS:
        prompt = test[0]
        expected = test[1]

        result = arka_governor_dispatch(prompt)
        ok = expected in result

        print("[OK]" if ok else "[FAIL]", prompt, "=>", expected)

        if not ok:
            print("---- RESULT ----")
            print(result[:1500])
            failures.append((prompt, expected))

    if failures:
        print("")
        print("[FAIL] Smoke test failures:", len(failures))
        for prompt, expected in failures:
            print("-", prompt, "expected:", expected)
        raise SystemExit(1)

    print("[OK] Smoke tests passed.")

if __name__ == "__main__":
    main()
