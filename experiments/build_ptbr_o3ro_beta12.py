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
import tempfile
import subprocess
import sys
from pathlib import Path

from ptbr_qm_beta12 import convert_usa_to_eur

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "installer" / "payload-manifest.json"
TAG = "v0.8.0-beta.1.2"
EXPECTED_BASE_SHA256 = "dae620379c805e96a6187c212dc2b177cf5fdb0c184d526a06ebaeeaa481aa56"
EXPECTED_BASE_BYTES = 473522176
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


# The original title artwork stays native, alongside the HD menu artwork.
# Do not exclude other misc CTXB files: they may contain untranslated content.
HD_EXCLUDED_LOGOS = (
    "misc/logo00.ctxb",
    "misc/us/english/menu_title_logo.ctxb",
    "misc/us/english/menu_title_logo_ura.ctxb",
)


def hd_exclusion_paths(replacements: dict[str, Path]) -> list[str]:
    expected_menu = {f"menu/{language}/{name}"
                     for language in ("01_US_ENGLISH", "02_EU_ENGLISH")
                     for name in EU_MIRRORS}
    expected = expected_menu | set(HD_EXCLUDED_LOGOS)
    if not expected <= replacements.keys():
        raise ValueError("Missing expected HD-menu or logo targets; refusing partial exclusion")
    actual_menu = {name for name in replacements
                   if name.startswith(("menu/01_US_ENGLISH/", "menu/02_EU_ENGLISH/"))
                   and name.endswith(".ctxb")}
    if actual_menu != expected_menu:
        raise ValueError("Unexpected menu CTXB set; refusing an unsafe O3RO variant")
    if len(expected) != 31:
        raise ValueError("Unexpected HD exclusion count")
    return sorted(expected)


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
    parser.add_argument("--preserve-hd-textures", action="store_true",
                        help="Exclude 28 menu CTXB targets and 3 logos while retaining other translated misc graphics")
    parser.add_argument("--check-only", action="store_true",
                        help="Validate all inputs and RomFS targets without generating an overlay")
    parser.add_argument("--output", type=Path,
                        help="NEW test O3RO file outside installed game directory")
    args = parser.parse_args()

    source_root = args.triaevum_source.expanduser().resolve()
    payload = args.payload.expanduser().resolve()
    romfs = args.romfs_image.expanduser().resolve()
    process_manifest = args.process_manifest.expanduser().resolve()
    output = args.output.expanduser().resolve() if args.output else None
    if not args.check_only and output is None:
        parser.error("--output is required when not using --check-only")
    if output is not None and output.exists():
        raise ValueError("Refusing to overwrite any existing O3RO")
    if output is not None and (output == romfs or output.is_relative_to(romfs.parent)):
        raise ValueError("Overlay output must be outside RomFS image directory")
    if output is not None and (output.is_relative_to(source_root) or output.is_relative_to(payload)):
        raise ValueError("Overlay output must be outside source/payload directories")

    if romfs.stat().st_size != EXPECTED_BASE_BYTES or file_hash(romfs) != EXPECTED_BASE_SHA256:
        raise ValueError("Refusing RomFS that differs from the verified beta.1.2 base")
    upstream = import_upstream(source_root)
    replacements = verified_files(payload)
    excluded_ctxb = []
    if args.preserve_hd_textures:
        excluded_ctxb = hd_exclusion_paths(replacements)
        # 28 menu CTXB destinations and 3 logo CTXB destinations only.
        for name in excluded_ctxb:
            del replacements[name]
    expected_targets = 95 if args.preserve_hd_textures else 126
    if len(replacements) != expected_targets:
        raise ValueError("Unexpected O3RO target count")
    offset, size = upstream.romfs_service_view(process_manifest)
    if offset != 0 or size != EXPECTED_BASE_BYTES:
        raise ValueError("Unexpected RomFS service view for the validated beta.1.2 base")
    with romfs.open("rb") as stream:
        header, records = upstream.romfs_file_records(stream, offset, size)
    missing = sorted(set(replacements) - set(records))
    if missing:
        raise ValueError(f"Unsupported RomFS, {len(missing)} missing target files: {missing[:12]}")
    # Keep the native EUR QBF, exactly as the approved original-font installer does.
    font_key = "message/eu/ltn16.qbf"
    _font_record, font_offset, font_length = records[font_key]
    with romfs.open("rb") as stream:
        stream.seek(offset + header[9] + font_offset)
        native_font = stream.read(font_length)
    translation_font = replacements[font_key].read_bytes()
    if len(native_font) != font_length or len(translation_font) != len(native_font):
        raise ValueError("Native versus translated QBF size mismatch")
    if native_font[:1608] != translation_font[:1608]:
        raise ValueError("Native versus translated QBF glyph metrics differ")
    # Convert into a temporary source used only for this offline overlay build.
    with tempfile.TemporaryDirectory(prefix="ptbr-o3ro-prep-") as temporary:
        staging = Path(temporary)
        converted_qm = convert_usa_to_eur((payload / "message/us/us.qm").read_bytes())
        qm_path = staging / "eu.qm"
        qm_path.write_bytes(converted_qm)
        font_path = staging / "ltn16.qbf"
        font_path.write_bytes(native_font)
        replacements["message/eu/eu.qm"] = qm_path
        replacements[font_key] = font_path
        if len(replacements) != expected_targets:
            raise ValueError(f"Expected exactly {expected_targets} translation overlay targets")
        if args.check_only:
            print(json.dumps({
                "target": TAG, "check_only": True, "base_sha256": EXPECTED_BASE_SHA256,
                "translation_files_verified": 112, "overlay_targets_found": expected_targets,
                "ctxb_excluded": excluded_ctxb, "preserve_hd_textures": args.preserve_hd_textures,
                "qm_record_count": 2510, "qm_converted_sha256": hashlib.sha256(converted_qm).hexdigest(),
                "native_font_preserved": True, "overlay_created": False,
                "topscreen_integration_verified": False
            }, indent=2))
            return
        summary = upstream.build_romfs_overlay(
            romfs, service_offset=offset, service_size=size,
            replacements=replacements, output=output)
    digest = file_hash(output)
    print(json.dumps({
        "target": TAG, "experimental_only": True, "automatically_installed": False,
        "source_files": 112, "replacement_records": expected_targets,
        "ctxb_excluded": excluded_ctxb, "preserve_hd_textures": args.preserve_hd_textures,
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
