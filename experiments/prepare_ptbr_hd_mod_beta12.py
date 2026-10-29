#!/usr/bin/env python3
"""Prepare a local PT-BR HD texture mod without editing the Forge pack or launch profile.

The output is a separate texture-pack tree to be activated after review.
Only the author's local PNG ZIP is used. No redistributed image assets.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
import zipfile
from pathlib import Path

from install_ptbr_hd_vanilla_beta12 import ATLAS, parse_zip, png_dimensions

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def plan(zip_path: Path, vanilla: Path, mapping: dict[str, str]) -> tuple[list[dict], bytes]:
    pngs = parse_zip(zip_path)
    candidates: dict[str, list[Path]] = {}
    for path in vanilla.rglob("*.png"):
        if path.is_symlink():
            raise ValueError(f"Symlink in source texture pack: {path}")
        candidates.setdefault(path.name.casefold(), []).append(path)
    edits = []
    for name, data in sorted(pngs.items()):
        if name == "TopScreen/ui_atlas_hd.png":
            continue
        basename = Path(name).name
        matches = candidates.get(basename.casefold(), [])
        if not matches:
            raise ValueError(f"Missing Vanilla original: {basename}")
        if basename in mapping:
            dest = (vanilla / mapping[basename]).resolve()
            if not dest.is_relative_to(vanilla.resolve()) or dest not in matches:
                raise ValueError(f"Invalid mapping: {basename} -> {mapping[basename]}")
        elif len(matches) == 1:
            dest = matches[0]
        else:
            raise ValueError(f"Ambiguous Vanilla target for {basename}: "
                             + ", ".join(str(p.relative_to(vanilla)) for p in matches))
        original = dest.read_bytes()
        if png_dimensions(data) != png_dimensions(original):
            raise ValueError(f"Dimensions mismatch for {basename}")
        edits.append({"source": name, "destination": dest.relative_to(vanilla).as_posix(),
                      "sha256": sha(data)})
    if len(edits) != 20:
        raise ValueError(f"Expected 20 Vanilla edits, got {len(edits)}")
    return edits, pngs["TopScreen/ui_atlas_hd.png"]

def prepare(zip_path: Path, vanilla: Path, destination: Path, mapping: dict, dry_run: bool):
    vanilla, destination = vanilla.resolve(), destination.resolve()
    if not vanilla.is_dir() or not (vanilla / "source.json").is_file():
        raise ValueError("Expected Forge-prepared Vanilla UI/HUD 3.2 directory with source.json")
    if destination.exists() or destination.is_relative_to(vanilla):
        raise ValueError("Destination exists or is inside the Vanilla source")
    if vanilla.is_relative_to(destination):
        raise ValueError("Destination cannot contain the source directory")
    edits, atlas = plan(zip_path, vanilla, mapping)
    summary = {"format": "oot3d_ptbr_hd_local_mod_v1", "source_zip_sha256": sha(zip_path.read_bytes()),
               "edited_textures": edits, "atlas_sha256": sha(atlas),
               "mod_directory": str(destination), "status": "dry-run" if dry_run else "prepared",
               "profile_changed": False, "original_vanilla_changed": False}
    if dry_run:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".ptbr-hd-prep-", dir=destination.parent))
    try:
        shutil.copytree(vanilla, stage, dirs_exist_ok=True, symlinks=False)
        with zipfile.ZipFile(zip_path) as archive:
            for edit in edits:
                target = stage / edit["destination"]
                data = archive.read(edit["source"])
                if sha(data) != edit["sha256"]:
                    raise ValueError("PNG changed during staging")
                with target.open("wb") as stream:
                    stream.write(data)
                    stream.flush()
                    os.fsync(stream.fileno())
        # TopScreen atlas can reference the matching edited Vanilla texture directly.
        atlas_target = next((stage / e["destination"] for e in edits
                             if Path(e["source"]).name == ATLAS), None)
        if atlas_target is None or sha(atlas_target.read_bytes()) != sha(atlas):
            raise ValueError("TopScreen atlas mismatch after staging")
        # Keep Forge's source.json unmodified; this is a local experimental copy.
        summary["topscreen_atlas_relative"] = atlas_target.relative_to(stage).as_posix()
        (stage / "ptbr-local-mod.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False),
                                                   encoding="utf-8")
        stage.rename(destination)
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    finally:
        if stage.exists():
            shutil.rmtree(stage)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--textures-zip", required=True, type=Path)
    parser.add_argument("--vanilla", required=True, type=Path)
    parser.add_argument("--destination", required=True, type=Path)
    parser.add_argument("--mapping", type=Path, help="Optional JSON: PNG basename -> relative Vanilla path")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    mapping = json.loads(args.mapping.read_text(encoding="utf-8-sig")) if args.mapping else {}
    if not isinstance(mapping, dict) or not all(isinstance(k, str) and isinstance(v, str)
                                                for k, v in mapping.items()):
        raise ValueError("Mapping must be a JSON object of strings")
    prepare(args.textures_zip, args.vanilla, args.destination, mapping, args.dry_run)

if __name__ == "__main__":
    main()
