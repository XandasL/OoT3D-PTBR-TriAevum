#!/usr/bin/env python3
"""Read-only structural checks for the user-distributed v3.0 ZIP."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import PurePosixPath
from zipfile import ZipFile

ROOT = "data/mods/custom-romfs/"
EXPECTED_COUNTS = {".zar": 88, ".ctxb": 35, ".qm": 1, ".qbf": 1, ".bcsar": 1}
EXPECTED_QM = "2c01f578280f331befa6683eb2c18e27c8538b80df9536344c4c9cacc7c8866d"
KNOWN_V3_ZIP = "5db68dd5ce2d4633028ccbe63e0487446c5dccfe39bd4f27081e450796aece23"


def verify(path, *, check_release_hash=False):
    if check_release_hash:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != KNOWN_V3_ZIP:
            raise ValueError(f"ZIP hash does not match tested v3.0: {digest}")
    with ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError("Corrupted archive")
        members = [i for i in archive.infolist() if not i.is_dir()]
        names = [i.filename for i in members]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate ZIP entry")
        if any(n.startswith("/") or "\\" in n or ".." in PurePosixPath(n).parts
               for n in names):
            raise ValueError("Unsafe ZIP path")
        expected_meta = {ROOT + "triaevum-custom-romfs.json", "LEIA-ME.txt"}
        if not expected_meta <= set(names):
            raise ValueError("Missing manifest or LEIA-ME")
        payload = [n for n in names if n not in expected_meta]
        if len(payload) != 126 or not all(n.startswith(ROOT) for n in payload):
            raise ValueError("Unexpected files or missing translation resources")
        count = Counter(PurePosixPath(n).suffix.lower() for n in payload)
        if dict(count) != EXPECTED_COUNTS:
            raise ValueError(f"Unexpected resource types: {dict(count)}")
        manifest = json.loads(archive.read(ROOT + "triaevum-custom-romfs.json"))
        if manifest.get("format") != "triaevum_custom_romfs_v1":
            raise ValueError("Unexpected Custom RomFS format")
        if hashlib.sha256(archive.read(ROOT + "message/eu/eu.qm")).hexdigest() != EXPECTED_QM:
            raise ValueError("QM differs from in-game-tested universal USA/EUR version")
        if any(i.file_size == 0 for i in members):
            raise ValueError("Empty ZIP entry")
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip_file", type=__import__("pathlib").Path)
    parser.add_argument("--exact-release", action="store_true",
                        help="Require SHA-256 of the specific tested release ZIP")
    args = parser.parse_args()
    counts = verify(args.zip_file, check_release_hash=args.exact_release)
    print(f"OK: 126 translated resources; {dict(counts)}")


if __name__ == "__main__":
    main()
