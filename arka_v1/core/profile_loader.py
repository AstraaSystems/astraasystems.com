"""
profile_loader.py

Phase 4 trusted profile loader for Arka V1.

This module loads read-only trusted local profile facts for Arka's context builder.

It does not:
- answer prompts
- dispatch tools
- call web/search/server/GitHub/Moneris/Netlify
- mutate memory
- write runtime state
- load secrets

It only loads safe local identity/profile facts for context construction.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Optional


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROFILE_PATH = ROOT / "config" / "owner_profile.json"


DEFAULT_PROFILE: Dict[str, Any] = {
    "owner": {
        "name": "Keshanth Sivayogampillai",
        "role": "owner",
        "authority": "owner",
    },
    "family": {
        "wife_name": "Thrilochana",
        "first_born_son_name": "Bhirav Aditya",
    },
    "system": {
        "name": "Arka V1",
        "mode": "local",
        "version": "1.0",
    },
    "ecosystem": {
        "arka": {
            "role": "personal local-first AI governor",
            "cloud_local_ratio": "10_cloud_90_local",
        },
        "astraa": {
            "role": "public cloud-first business platform and safe access gateway",
            "cloud_local_ratio": "90_cloud_10_local",
        },
        "aruhan": {
            "role": "internal intelligence and security mind",
        },
        "ardhanarishvara_os": {
            "role": "core internal governance, math, and kernel infrastructure",
        },
    },
    "metadata": {
        "profile_version": "phase4",
        "source": "default_fallback",
        "mutable_by_ai": False,
        "contains_secrets": False,
    },
}


class ProfileLoaderError(RuntimeError):
    """
    Raised only for explicit strict-mode profile loader failures.
    """


def _deep_merge_defaults(
    loaded: Dict[str, Any],
    defaults: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Merge loaded profile over defaults while preserving required default keys.

    The loaded profile wins for existing values.
    Defaults fill missing required structure.
    """

    merged = deepcopy(defaults)

    for key, value in loaded.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge_defaults(value, merged[key])
        else:
            merged[key] = value

    return merged


def _normalize_profile_metadata(
    profile: Dict[str, Any],
    *,
    profile_loaded: bool,
    profile_path: Optional[Path],
    fallback_reason: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Add loader metadata without mutating the caller's original profile object.
    """

    normalized = deepcopy(profile)
    metadata = dict(normalized.get("metadata", {}))

    metadata.update(
        {
            "profile_version": metadata.get("profile_version", "phase4"),
            "profile_loaded": profile_loaded,
            "profile_path": str(profile_path) if profile_path else None,
            "fallback_reason": fallback_reason,
            "loader": "arka_v1.core.profile_loader",
            "external_calls": False,
            "memory_mutation": False,
            "contains_secrets": bool(metadata.get("contains_secrets", False)),
        }
    )

    normalized["metadata"] = metadata
    return normalized


def _validate_minimum_profile(profile: Dict[str, Any]) -> None:
    """
    Validate minimum expected profile structure.

    This is intentionally conservative and does not perform heavy schema validation.
    """

    required_paths = [
        ("owner", "name"),
        ("owner", "authority"),
        ("family", "wife_name"),
        ("family", "first_born_son_name"),
        ("system", "name"),
        ("system", "mode"),
    ]

    missing = []

    for section, field in required_paths:
        if not isinstance(profile.get(section), dict):
            missing.append(f"{section}.{field}")
            continue

        value = profile[section].get(field)

        if value is None or value == "":
            missing.append(f"{section}.{field}")

    if missing:
        raise ProfileLoaderError(
            "Profile missing required fields: " + ", ".join(missing)
        )


def load_profile(
    profile_path: Optional[str | Path] = None,
    *,
    strict: bool = False,
) -> Dict[str, Any]:
    """
    Load Arka's trusted local profile.

    If the file is missing or invalid and strict=False, return safe defaults.
    If strict=True, raise ProfileLoaderError on missing/invalid profile.
    """

    path = Path(profile_path) if profile_path else DEFAULT_PROFILE_PATH

    if not path.exists():
        if strict:
            raise ProfileLoaderError(f"Profile file not found: {path}")

        return _normalize_profile_metadata(
            DEFAULT_PROFILE,
            profile_loaded=False,
            profile_path=path,
            fallback_reason="profile_file_missing",
        )

    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        if strict:
            raise ProfileLoaderError(f"Could not read profile file: {path}") from exc

        return _normalize_profile_metadata(
            DEFAULT_PROFILE,
            profile_loaded=False,
            profile_path=path,
            fallback_reason="profile_file_unreadable",
        )

    if not isinstance(loaded, dict):
        if strict:
            raise ProfileLoaderError(f"Profile file did not contain a JSON object: {path}")

        return _normalize_profile_metadata(
            DEFAULT_PROFILE,
            profile_loaded=False,
            profile_path=path,
            fallback_reason="profile_not_object",
        )

    merged = _deep_merge_defaults(loaded, DEFAULT_PROFILE)

    try:
        _validate_minimum_profile(merged)
    except ProfileLoaderError:
        if strict:
            raise

        return _normalize_profile_metadata(
            DEFAULT_PROFILE,
            profile_loaded=False,
            profile_path=path,
            fallback_reason="profile_failed_minimum_validation",
        )

    return _normalize_profile_metadata(
        merged,
        profile_loaded=True,
        profile_path=path,
        fallback_reason=None,
    )


def get_owner_name(profile: Optional[Dict[str, Any]] = None) -> str:
    """
    Convenience accessor for owner name.
    """

    data = profile or load_profile()
    return str(data["owner"]["name"])


def get_family_profile(profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Convenience accessor for family profile.
    """

    data = profile or load_profile()
    return dict(data.get("family", {}))


def get_system_profile(profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Convenience accessor for system profile.
    """

    data = profile or load_profile()
    return dict(data.get("system", {}))


def get_ecosystem_profile(profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Convenience accessor for ecosystem profile.
    """

    data = profile or load_profile()
    return dict(data.get("ecosystem", {}))
