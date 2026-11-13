#!/usr/bin/env python3
"""Assemble a v3.0 Custom RomFS ZIP using validated earlier assets.

Inputs are supplied locally. No ROM, executable or translation payload is
downloaded or embedded in this source tree.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from build_v3_universal_qm import (
    QM_IN_PACK, QM_IN_EUR_ROMFS, build_universal_qm,
    V2_QM_SHA256,
)
from verify_v3_package import verify

ROOT = "data/mods/custom-romfs/"
MANIFEST = ROOT + "triaevum-custom-romfs.json"


def assemble(v2_zip: Path, eur_romfs_zip: Path, readme: Path, output: Path):
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite: {output}")
    instructions = readme.read_bytes()
    if not instructions or b"Custom RomFS" not in instructions:
        raise ValueError("Expected a nonempty, current v3.0 LEIA-ME")
    with ZipFile(v2_zip) as old, ZipFile(eur_romfs_zip) as european:
        names = [i.filename for i in old.infolist() if not i.is_dir()]
        if len(names) != 128 or len(names) != len(set(names)):
            raise ValueError("Expected exactly 128 unique files in previous Custom RomFS ZIP")
        if "LEIA-ME.txt" not in names or MANIFEST not in names or QM_IN_PACK not in names:
            raise ValueError("Incomplete Custom RomFS baseline")
        if any(not (name.startswith(ROOT) or name == "LEIA-ME.txt") for name in names):
            raise ValueError("Unexpected path in baseline package")
        original_qm = old.read(QM_IN_PACK)
        if hashlib.sha256(original_qm).hexdigest() != V2_QM_SHA256:
            raise ValueError("Incorrect previous translated QM")
        universal_qm = build_universal_qm(european.read(QM_IN_EUR_ROMFS), original_qm)
        with output.open("xb") as handle:
            with ZipFile(handle, "w", compression=ZIP_DEFLATED, compresslevel=9) as dst:
                for name in names:
                    if name == QM_IN_PACK:
                        data = universal_qm
                    elif name == "LEIA-ME.txt":
                        data = instructions
                    else:
                        data = old.read(name)
                    dst.writestr(name, data)
    verify(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ptbr-v2-zip", type=Path, required=True)
    parser.add_argument("--eur-romfs-zip", type=Path, required=True)
    parser.add_argument("--readme", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assemble(args.ptbr_v2_zip, args.eur_romfs_zip, args.readme, args.output)
    print("OK: v3.0 package assembled and structurally validated.")
    print("Note: ZIP compression/metadata can change the full archive SHA-256.")


if __name__ == "__main__":
    main()
