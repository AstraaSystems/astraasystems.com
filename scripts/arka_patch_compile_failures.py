from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")

# -------------------------------------------------------------------
# 1) Fix reflection_prototype.py
# Problem:
#   @staticmethod was at top-level while def now() was indented.
# Fix:
#   Put @staticmethod inside ReflectionRecord class.
# -------------------------------------------------------------------
p = ROOT / "reflection_prototype.py"
text = p.read_text(encoding="utf-8")

text = text.replace(
    "\n@staticmethod\n    def now():",
    "\n    @staticmethod\n    def now():"
)

write(p, text)


# -------------------------------------------------------------------
# 2) Fix storage_engine_v14_omniversal.py
# Problem:
#   read() ended with an incomplete line: "        for"
# Fix:
#   Replace the unfinished loop with a conservative read stub.
#   This does not perform external actions.
# -------------------------------------------------------------------
p = ROOT / "ArdhanarishvaraOS" / "kernel" / "storage_engine_v14_omniversal.py"
text = p.read_text(encoding="utf-8")

bad = "\n        for\n"
good = """
        for shard_id in shard_ids:
            shard = None

            # Conservative compatibility path:
            # Some restored storage engines may use self.shards, self.storage,
            # or volume-local shard maps. Try safe lookups only.
            if hasattr(self, "shards") and isinstance(getattr(self, "shards"), dict):
                shard = self.shards.get(shard_id)

            if shard is None and hasattr(self, "storage") and isinstance(getattr(self, "storage"), dict):
                shard = self.storage.get(shard_id)

            if shard is None:
                missing.append(shard_id)
            else:
                shards.append(shard)

        self.telemetry["reads"] = self.telemetry.get("reads", 0) + 1

        if missing:
            return {
                "status": "partial",
                "volume_id": volume_id,
                "origin_reality": origin_reality,
                "shards": shards,
                "missing": missing,
            }

        return {
            "status": "read",
            "volume_id": volume_id,
            "origin_reality": origin_reality,
            "shards": shards,
            "missing": missing,
        }
"""

if bad in text:
    text = text.replace(bad, good)
else:
    raise SystemExit("Could not find unfinished 'for' line in storage_engine_v14_omniversal.py")

write(p, text)


# -------------------------------------------------------------------
# 3) Fix entities/arkastra_kernel.py
# Problem:
#   A try block reaches "# MANIFEST BUILD" without except/finally.
# Fix:
#   Complete the manifest build section and close with except.
#   This is conservative and does not call external systems.
# -------------------------------------------------------------------
p = ROOT / "entities" / "arkastra_kernel.py"
text = p.read_text(encoding="utf-8")

marker = "            # MANIFEST BUILD\n"

replacement = """            # MANIFEST BUILD
            manifest = {
                "designs_generated": meta.designs_generated,
                "skus_compiled": meta.skus_compiled,
                "designs": designs,
                "skus": skus,
                "validation": "delegated",
            }

            try:
                meta.state = ArkastraState.MANIFEST_BUILD
            except Exception:
                pass

            return {
                "status": "manifest_ready",
                "manifest": manifest,
                "meta": meta,
            }

        except Exception as exc:
            try:
                meta.state = ArkastraState.ERROR
            except Exception:
                pass

            return {
                "status": "error",
                "error": str(exc),
                "meta": meta,
            }
"""

if marker in text and "except Exception as exc" not in text[text.find(marker):]:
    text = text.replace(marker, replacement)
else:
    raise SystemExit("Could not safely patch arkastra_kernel.py; marker missing or except already present.")

write(p, text)

print("Compile-failure patches applied.")
