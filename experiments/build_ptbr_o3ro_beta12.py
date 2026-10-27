#!/usr/bin/env python3
"""Experimental O3RO generator for TriAevum v0.8.0-beta.1.2.

Only writes a new overlay to an explicit output path OUTSIDE the installed game.
Does not change the ROM, the Forge configuration, launch profiles or any saves.
Requires local TriAevum SOURCE at the exact release tag.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "installer" / "payload-manifest.json"
TAG = "v0.8.0-beta.1.2"
EU_MIRRORS = (
    "hud_all00.ctxb", "hud_menu_title00.ctxb", "menu_equip_parts00.ctxb",
    "menu_file_select_parts00.ctxb", "menu_file_select_parts01.ctxb",
    "menu_hint_movie_parts00.ctxb", "menu_item_parts00.ctxb",
    "menu_map_parts00.ctxb", "menu_map_parts01.ctxb",
    "menu_okarina_parts00.ctxb", "menu_option_parts00.ctxb",
    "menu_top_parts00.ctxb", "name_entry00_parts00.ctxb",
    "name_entry00_parts01.ctxb",
)


def file_hash(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def source_targets(name: str) -> str:
    if name == "message/us/us.qm":
        return "message/eu/eu.qm"
    if name.startswith("message/us/"):
        return "message/eu/" + name[len("message/us/"):]
    if name.startswith("misc/us/"):
        return "misc/eu/" + name[len("misc/us/"):]
    return name


def verified_files(payload: Path) -> dict[str, Path]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if len(manifest) != 112:
        raise ValueError(f"Unexpected source manifest length: {len(manifest)}; expected 112")
    replacements: dict[str, Path] = {}
    for name, expected in sorted(manifest.items()):
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts or "\\" in name:
            raise ValueError(f"Unsafe translation path: {name}")
        source = (payload / relative).resolve()
        if not source.is_relative_to(payload) or not source.is_file():
            raise ValueError(f"Missing or escaping translation file: {name}")
        if file_hash(source) != expected.lower():
            raise ValueError(f"Translation file integrity mismatch: {name}")
        target = source_targets(name)
        if target in replacements:
            raise ValueError(f"Duplicate target path: {target}")
        replacements[target] = source
    for name in EU_MIRRORS:
        source = replacements[f"menu/01_US_ENGLISH/{name}"]
        target = f"menu/02_EU_ENGLISH/{name}"
        if target in replacements:
            raise ValueError(f"Duplicate EU mirror: {target}")
        replacements[target] = source
    if len(replacements) != 126:
        raise ValueError("126 operations expected")
    return replacements


def import_upstream(source_root: Path):
    # Require the exact upstream release tag; do not silently run newer code.
    try:
        head = subprocess.check_output(
            ["git", "-C", str(source_root), "rev-parse", "HEAD"], text=True).strip()
        release = subprocess.check_output(
            ["git", "-C", str(source_root), "rev-parse", f"refs/tags/{TAG}^{{commit}}"],
            text=True).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError("A git checkout of TriAevum with its beta.1.2 tag is required") from exc
    if head != release:
        raise ValueError(f"TriAevum source checkout is not at {TAG}: {head}")
    package_root = source_root / "tools" / "triaevum_release"
    if not (package_root / "romfs_mods.py").is_file():
        raise ValueError("Upstream O3RO implementation unavailable")
    sys.path.insert(0, str(package_root))
    return importlib.import_module("romfs_mods")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--triaevum-source", type=Path, required=True,
                        help="Local Git checkout at v0.8.0-beta.1.2")
    parser.add_argument("--payload", type=Path, required=True,
                        help="Root containing translation's actor/, menu/, message/, etc.")
    parser.add_argument("--romfs-image", type=Path, required=True,
                        help="Prepared user's own ORIGINAL RomFS image")
    parser.add_argument("--process-manifest", type=Path, required=True,
                        help="TriAevum original process-manifest.json")
    parser.add_argument("--output", type=Path, required=True,
                        help="NEW test O3RO file outside installed game directory")
    args = parser.parse_args()

    source_root = args.triaevum_source.expanduser().resolve()
    payload = args.payload.expanduser().resolve()
    romfs = args.romfs_image.expanduser().resolve()
    process_manifest = args.process_manifest.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if output.exists():
        raise ValueError("Refusing to overwrite any existing O3RO")
    if output == romfs or output.is_relative_to(romfs.parent):
        raise ValueError("Overlay output must be outside RomFS image directory")
    if output.is_relative_to(source_root) or output.is_relative_to(payload):
        raise ValueError("Overlay output must be outside source/payload directories")

    upstream = import_upstream(source_root)
    replacements = verified_files(payload)
    offset, size = upstream.romfs_service_view(process_manifest)
    # Reject targets missing from this exact game ROMFS before creating output.
    with romfs.open("rb") as stream:
        _header, records = upstream.romfs_file_records(stream, offset, size)
    missing = sorted(set(replacements) - set(records))
    if missing:
        raise ValueError(f"Unsupported ROM revision, {len(missing)} missing target files: {missing[:12]}")
    summary = upstream.build_romfs_overlay(
        romfs, service_offset=offset, service_size=size,
        replacements=replacements, output=output)
    digest = file_hash(output)
    print(json.dumps({
        "target": TAG, "experimental_only": True, "automatically_installed": False,
        "source_files": 112, "replacement_records": 126,
        "overlay_path": str(output), "overlay_sha256": digest, "summary": summary,
        "limitations": [
            "NOT yet integrated with Forge's catalogued mods",
            "HD64 font and TopScreen's O3TU hash-gate NOT validated",
            "Overlay conflicts with other mods NOT validated",
            "Requires isolated in-game testing before distribution",
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
