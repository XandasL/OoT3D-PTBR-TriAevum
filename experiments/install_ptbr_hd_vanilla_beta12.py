#!/usr/bin/env python3
"""Experimental, local-only HD PT-BR integration for TriAevum beta.1.2.

No modified third-party textures are stored in this repository.
Use the author's own locally edited texture ZIP, after licensing review.
Never edits the O3RO, game executable, original Vanilla pack or saves.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import struct
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

ATLAS = "tex1_512x256_1FAF9B5B2ADF6038_13_mip0.png"
PACK_REL = Path("data/mods/ui-textures/vanilla_ui_hud-3.2")
CUSTOM_REL = Path("data/mods/ui-textures/ptbr-hd-beta12")
PROFILE_REL = Path("data/TriAevum.launch.json")
BACKUP_REL = Path("data/mods/ptbr-hd-beta12-launch-original.json")
RECEIPT_REL = Path("data/mods/ptbr-hd-beta12-receipt.json")
EXPECTED_FLAG = "--ui-texture-pack"
ATLAS_FLAG = "--topscreen-ui-atlas-hd"
MAX_ARCHIVE_BYTES = 1024 * 1024 * 1024
MAX_IMAGE_BYTES = 96 * 1024 * 1024


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def png_dimensions(data: bytes) -> tuple[int, int]:
    if len(data) < 33 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise ValueError("Invalid PNG signature or IHDR")
    width, height = struct.unpack(">II", data[16:24])
    if not (0 < width <= 16384 and 0 < height <= 16384):
        raise ValueError("Invalid PNG dimensions")
    return width, height


def parse_zip(path: Path) -> dict[str, bytes]:
    content = {}
    size = 0
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError("ZIP CRC mismatch")
        for member in archive.infolist():
            if member.is_dir():
                continue
            name = member.filename.replace("\\", "/")
            parts = PurePosixPath(name).parts
            if (name.startswith("/") or any(p in ("..", ".") for p in parts)
                    or "\x00" in name or ":" in name or len(parts) > 15):
                raise ValueError(f"Unsafe ZIP member: {name!r}")
            if not name.lower().endswith(".png"):
                continue
            if (member.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError(f"Symbolic links forbidden: {name}")
            if member.file_size > MAX_IMAGE_BYTES:
                raise ValueError(f"Oversized PNG: {name}")
            size += member.file_size
            if size > MAX_ARCHIVE_BYTES:
                raise ValueError("PNG extraction limit exceeded")
            data = archive.read(member)
            png_dimensions(data)
            if name in content:
                raise ValueError(f"Duplicated ZIP entry: {name}")
            content[name] = data
    if not content:
        raise ValueError("No PNG files found in supplied ZIP")
    if any(not (n.startswith("VanillaUI/") or n == "TopScreen/ui_atlas_hd.png") for n in content):
        raise ValueError("Unexpected ZIP layout: expected VanillaUI/ and TopScreen/ui_atlas_hd.png")
    if len([n for n in content if n.startswith("VanillaUI/")]) != 20:
        raise ValueError("Expected the 20 verified VanillaUI images from the author ZIP")
    atlas = content.get("TopScreen/ui_atlas_hd.png")
    if atlas is None or png_dimensions(atlas) != (4096, 2048):
        raise ValueError("Required 4096x2048 TopScreen atlas missing")
    vanilla_atlas = content.get("VanillaUI/" + ATLAS)
    if vanilla_atlas != atlas:
        raise ValueError("TopScreen atlas and VanillaUI atlas differ; refuse implicit substitution")
    return content


def find_targets(base: Path, name: str, candidates: list[Path]) -> list[Path]:
    norm = name.casefold().replace("\\", "/")
    parts = norm.split("/")
    # Prefer normalized path suffixes, then an unambiguous texture basename.
    for count in range(min(len(parts), 5), 1, -1):
        suffix = "/".join(parts[-count:])
        found = [p for p in candidates if p.relative_to(base).as_posix().casefold().endswith(suffix)]
        if len(found) == 1:
            return found
    found = [p for p in candidates if p.name.casefold() == parts[-1]]
    if len(found) == 1:
        return found
    if len(found) > 1 and parts[-1] == ATLAS.casefold():
        # Only the common atlas is a safe special case.
        common = [p for p in found if "/common/ui/" in ("/" + p.relative_to(base).as_posix().casefold())]
        if len(common) == 1:
            return common
    if not found:
        raise ValueError(f"Texture not present in Vanilla 3.2: {name}")
    raise ValueError(f"Ambiguous texture filename, include language folder in ZIP: {name}")


def load_profile(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("arguments"), list):
        raise ValueError("Unexpected TriAevum.launch.json schema")
    if not all(isinstance(a, str) for a in data["arguments"]):
        raise ValueError("Non-string launch argument")
    return data


def replace_flag(args: list[str], flag: str, path: str) -> None:
    indices = [i for i, a in enumerate(args) if a == flag]
    if len(indices) != 1 or indices[0] + 1 >= len(args):
        raise ValueError(f"Expected exactly one {flag} with a value")
    args[indices[0] + 1] = path


def fsync_file(path: Path, data: bytes) -> None:
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".ptbr-temp")
    if temp.exists():
        raise ValueError(f"Interrupted prior transaction requires inspection: {temp}")
    try:
        fsync_file(temp, data)
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def run_install(runtime: Path, zip_path: Path, dry_run: bool) -> None:
    base, custom = runtime / PACK_REL, runtime / CUSTOM_REL
    profile_path, backup = runtime / PROFILE_REL, runtime / BACKUP_REL
    receipt = runtime / RECEIPT_REL
    if not base.is_dir() or not profile_path.is_file():
        raise ValueError("TriAevum beta.1.2 Vanilla pack/profile not found")
    if any(p.exists() for p in (custom, backup, receipt)):
        raise ValueError("Previous integration detected; uninstall/review before retrying")
    pngs = parse_zip(zip_path)
    candidates = [p for p in base.rglob("*.png") if p.is_file()]
    if not candidates:
        raise ValueError("No original Vanilla textures found")
    modified: dict[Path, bytes] = {}
    source_names: dict[str, str] = {}
    for name, data in pngs.items():
        if name == "TopScreen/ui_atlas_hd.png":
            continue  # Same verified bytes as the VanillaUI atlas; not a second texture-pack target.
        target = find_targets(base, name, candidates)[0]
        if target in modified:
            raise ValueError(f"Multiple source files target {target.relative_to(base)}")
        original = target.read_bytes()
        if png_dimensions(original) != png_dimensions(data):
            raise ValueError(f"PNG dimensions changed: {name}: {png_dimensions(original)} -> {png_dimensions(data)}")
        modified[target] = data
        source_names[target.relative_to(base).as_posix()] = name
    if len(modified) != 20:
        raise ValueError(f"Expected 20 unique Vanilla destinations, found {len(modified)}")
    original_profile = profile_path.read_bytes()
    profile = load_profile(profile_path)
    args = profile["arguments"]
    replace_flag(args, EXPECTED_FLAG, "${runtime_dir}/" + CUSTOM_REL.as_posix())
    atlas_target = next((p for p in modified if p.name == ATLAS), None)
    if atlas_target is not None:
        replace_flag(args, ATLAS_FLAG, "${runtime_dir}/" + (CUSTOM_REL / atlas_target.relative_to(base)).as_posix())
    changed_profile = (json.dumps(profile, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    audit = {
        "tool": "ptbr_hd_vanilla_beta12",
        "original_profile_sha256": digest(original_profile),
        "installed_profile_sha256": digest(changed_profile),
        "source_zip_sha256": digest(zip_path.read_bytes()),
        "edited_png_count": len(modified),
        "edits": [{"path": p.relative_to(base).as_posix(),
                   "source": source_names[p.relative_to(base).as_posix()],
                   "sha256": digest(data)}
                  for p, data in sorted(modified.items())],
    }
    print(json.dumps({"mode": "dry-run" if dry_run else "install", **audit}, ensure_ascii=False, indent=2))
    if dry_run:
        return
    custom.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="ptbr-hd-stage-", dir=custom.parent))
    try:
        shutil.copytree(base, stage, dirs_exist_ok=True)
        for path, data in modified.items():
            target = stage / path.relative_to(base)
            target.unlink()
            fsync_file(target, data)
        # Stage becomes the installed pack before the launch profile points to it.
        stage.rename(custom)
        try:
            fsync_file(backup, original_profile)
            atomic_write(receipt, (json.dumps(audit, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
            atomic_write(profile_path, changed_profile)
        except BaseException:
            # Recover profile before dropping temporary pack.
            if backup.is_file() and digest(profile_path.read_bytes()) == digest(changed_profile):
                atomic_write(profile_path, original_profile)
            raise
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def run_uninstall(runtime: Path) -> None:
    profile_path, backup, receipt = runtime / PROFILE_REL, runtime / BACKUP_REL, runtime / RECEIPT_REL
    custom = runtime / CUSTOM_REL
    if not (backup.is_file() and receipt.is_file() and profile_path.is_file()):
        raise ValueError("Missing original profile backup or receipt; refuse unsafe uninstall")
    audit = json.loads(receipt.read_text(encoding="utf-8"))
    current = profile_path.read_bytes()
    if digest(current) != audit["installed_profile_sha256"]:
        raise ValueError("Launch profile changed since integration; refusing to overwrite user's edits")
    original = backup.read_bytes()
    if digest(original) != audit["original_profile_sha256"]:
        raise ValueError("Original profile backup hash mismatch")
    atomic_write(profile_path, original)
    # The translated pack remains on disk as a safe backup; never delete user assets.
    print("Original launch profile restored. Generated HD pack intentionally kept at:", custom)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", type=Path, required=True, help="TriAevum Windows-x64 folder")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--textures-zip", type=Path, help="Locally edited PNG ZIP")
    group.add_argument("--uninstall", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    runtime = args.runtime.expanduser().resolve()
    if args.uninstall:
        if args.dry_run:
            raise ValueError("--dry-run applies only to installation")
        run_uninstall(runtime)
    else:
        run_install(runtime, args.textures_zip.expanduser().resolve(), args.dry_run)


if __name__ == "__main__":
    main()
