#!/usr/bin/env python3
"""Read-only integrity check of the first experimental TriAevum beta.1.2 O3RO."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

BASE_SHA256 = "dae620379c805e96a6187c212dc2b177cf5fdb0c184d526a06ebaeeaa481aa56"
OVERLAY_SHA256 = "4b2dc3e7734518200f8bf5483f74f16353da939b3914ab3986f1e20968eed9e3"
BASE_SIZE = 473522176
PATCH_COUNT = 126
HEADER = struct.Struct("<4sIQQIIQ24x")
PATCH = struct.Struct("<QIIQQ")


def digest(path):
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def validate(romfs: Path, overlay: Path):
    if romfs.stat().st_size != BASE_SIZE or digest(romfs) != BASE_SHA256:
        raise ValueError("Base RomFS is not the validated beta.1.2 image")
    if digest(overlay) != OVERLAY_SHA256:
        raise ValueError("O3RO digest differs from the reported first generated file")
    with romfs.open("rb") as base, overlay.open("rb") as mod:
        header = mod.read(HEADER.size)
        if len(header) != HEADER.size:
            raise ValueError("Truncated O3RO header")
        magic, version, base_size, view_size, count, reserved, tail_start = HEADER.unpack(header)
        if (magic, version, base_size, count, reserved) != (b"O3RO", 1, BASE_SIZE, PATCH_COUNT, 0):
            raise ValueError("Unexpected O3RO identity, version, or record count")
        if view_size <= base_size or tail_start != 64 + 64 * count:
            raise ValueError("Invalid virtual RomFS geometry")
        if overlay.stat().st_size != tail_start + (view_size - base_size):
            raise ValueError("Truncated O3RO appended file data")
        patches = []
        for index in range(count):
            raw = mod.read(PATCH.size)
            if len(raw) != PATCH.size:
                raise ValueError("Truncated patch table")
            pos, length, flags, before, after = PATCH.unpack(raw)
            if (length != 16 or flags != 0 or pos + 16 > base_size
                    or before != 64 + 32 * count + 32 * index or after != before + 16):
                raise ValueError(f"Invalid patch entry {index}")
            patches.append((pos, before, after))
        if len({p[0] for p in patches}) != count:
            raise ValueError("Duplicate patch destinations")
        for pos, before, after in patches:
            base.seek(pos)
            expected = base.read(16)
            mod.seek(before)
            if len(expected) != 16 or mod.read(16) != expected:
                raise ValueError(f"Original RomFS bytes mismatch at patch position {pos}")
            mod.seek(after)
            new = mod.read(16)
            if len(new) != 16:
                raise ValueError(f"Truncated new RomFS record at {pos}")
            data_offset, data_len = struct.unpack("<QQ", new)
            if not data_len or data_offset + data_len > view_size:
                raise ValueError(f"Replacement out of virtual RomFS bounds at {pos}")
    return {
        "status": "OK",
        "read_only": True,
        "version": "v0.8.0-beta.1.2",
        "expected_overlay_sha256": OVERLAY_SHA256,
        "checked_patch_records": len(patches),
        "base_bytes": base_size,
        "appended_bytes": view_size - base_size,
        "overlay_bytes": overlay.stat().st_size,
        "note": "Header, all 126 before/after patch records, and file SHA-256 checked. In-game rendering and individual translated contents are not validated.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--romfs-image", type=Path, required=True)
    parser.add_argument("--overlay", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(validate(args.romfs_image.resolve(), args.overlay.resolve()), indent=2))
