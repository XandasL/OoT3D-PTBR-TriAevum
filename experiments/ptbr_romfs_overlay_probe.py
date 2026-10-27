#!/usr/bin/env python3
"""Read-only feasibility probe for PT-BR translation as an O3RO RomFS mod.

No TriAevum runtime changes, no ROM modification, no writes to installations.
Checks exact SHA-256 of all 112 translation source assets before any experiment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "installer" / "payload-manifest.json"
GROUPS = ("actor", "menu", "message", "misc", "scene", "sound")


def audit(manifest: dict[str, str], payload: Path | None) -> dict:
    invalid = [name for name, sha in manifest.items()
               if Path(name).is_absolute() or ".." in Path(name).parts
               or name.replace("\\", "/") != name
               or name.split("/")[0] not in GROUPS
               or len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha.lower())]
    if invalid:
        raise ValueError(f"Invalid paths/hashes in manifest: {invalid[:5]}")
    groups = dict(sorted(Counter(k.split("/")[0] for k in manifest).items()))
    result = {"translation_source_files": len(manifest), "groups": groups,
              "manifest": str(MANIFEST.relative_to(ROOT)),
              "romfs_overlay_format": "O3RO v1",
              "upstream_catalogue_status": "Not a general mod-folder importer; requires upstream integration",
              "supported_mode": "read-only feasibility audit"}
    if payload is not None:
        missing, mismatch, matched = [], [], 0
        for name, expected in sorted(manifest.items()):
            candidate = payload / name
            if not candidate.is_file() or candidate.is_symlink():
                missing.append(name)
                continue
            digest = hashlib.file_digest(candidate.open("rb"), "sha256").hexdigest()
            if digest != expected.lower():
                mismatch.append(name)
            else:
                matched += 1
        result.update({"matched": matched, "missing": missing, "sha256_mismatch": mismatch,
                       "payload_verified": not (missing or mismatch)})
    else:
        result["payload_verified"] = False
        result["reason"] = "No local original translation resource directory provided"
    result["ready_to_install_as_mod"] = False
    result["remaining_requirements"] = [
        "Validate all translation payload file hashes and target ROM revision",
        "Resolve EUR language mirrors and optional font HD64 as separate compatibility cases",
        "Check O3RO base-image identity, conflict with TopScreen and other overlays",
        "Add explicit opt-in mod support to TriAevum Forge upstream, or validate a supported launcher hook",
        "Run synthetic tests, then isolated in-game tests; preserve existing installer and saves",
    ]
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--payload", type=Path,
                        help="Root containing actor/, menu/, message/, misc/, scene/, sound/")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    result = audit(manifest, args.payload.expanduser().resolve() if args.payload else None)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("PT-BR / O3RO compatibility probe (READ ONLY)")
        print("Source files:", result["translation_source_files"], "groups:", result["groups"])
        print("Payload verified:", result["payload_verified"])
        if args.payload:
            print("Matched:", result["matched"], "missing:", len(result["missing"]),
                  "mismatched:", len(result["sha256_mismatch"]))
        print("Native mod directly supported:", result["ready_to_install_as_mod"])
        print("Next:", *result["remaining_requirements"], sep="\n- ")


if __name__ == "__main__":
    main()
