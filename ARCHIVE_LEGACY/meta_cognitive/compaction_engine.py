# File: /home/keshanth/ARKA/ardhanarishvara/meta_cognitive/compaction_engine.py
#!/usr/bin/env python3
"""
Compaction Engine
-----------------
Compresses memory by removing noise and redundancy.
"""

class CompactionEngine:

    def compact(self, text: str) -> str:
        words = text.split()
        if len(words) <= 20:
            return text

        return " ".join(words[:20]) + " ..."
