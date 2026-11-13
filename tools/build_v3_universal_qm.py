#!/usr/bin/env python3
"""Rebuild the v3.0 USA/EUR QM from the validated v2 text and an EUR RomFS.

No ROM or translated game data is committed. The operator supplies both ZIPs.
This tool reads inputs only and refuses to overwrite an existing output.
"""
from __future__ import annotations

import argparse
import hashlib
import struct
from pathlib import Path
from zipfile import ZipFile

RECORD_COUNT = 2510
RECORD_BYTES = 96
TABLE_END = 16 + RECORD_COUNT * RECORD_BYTES
QM_IN_PACK = "data/mods/custom-romfs/message/eu/eu.qm"
QM_IN_EUR_ROMFS = "RomFS_Extraida_EUR/message/eu/eu.qm"
V2_QM_SHA256 = "f2c97990c771dc883554b6007fce1a5b034ba227e56485fde3e5a1797eb19829"
EUR_QM_SHA256 = "5b5addf728b3462ed9bdf375aa9c1a6c7f3a4e4f541a1845c1e3d3f8cb60488e"
V3_QM_SHA256 = "2c01f578280f331befa6683eb2c18e27c8538b80df9536344c4c9cacc7c8866d"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_qm(data: bytes, expected_digest: str) -> None:
    if sha256(data) != expected_digest:
        raise ValueError("Unexpected QM SHA-256; verify that both inputs match the validated versions")
    if len(data) < TABLE_END or data[:4] != b"QM\0\0":
        raise ValueError("Invalid/truncated QM header")
    version, count = struct.unpack_from("<II", data, 4)
    if (version, count) != (4, RECORD_COUNT):
        raise ValueError("Unsupported QM revision")


def build_universal_qm(eur: bytes, ptbr_v2: bytes) -> bytes:
    """Append only PT-BR spans to EUR QM, redirecting English slots 1 and 2.

    Preserves all other EUR language slots and reuses identical source spans.
    """
    validate_qm(eur, EUR_QM_SHA256)
    validate_qm(ptbr_v2, V2_QM_SHA256)
    out = bytearray(eur)
    reused: dict[tuple[int, int], int] = {}
    for index in range(RECORD_COUNT):
        entry = 16 + index * RECORD_BYTES
        if eur[entry:entry + 16] != ptbr_v2[entry:entry + 16]:
            raise ValueError(f"QM record IDs differ at entry {index}")
        source_offset, length = struct.unpack_from("<II", ptbr_v2, entry + 24)
        if length:
            if source_offset < TABLE_END or source_offset + length > len(ptbr_v2):
                raise ValueError(f"Invalid translated text range in entry {index}")
            source_span = (source_offset, length)
            if source_span not in reused:
                out.extend(b"\0" * (-len(out) % 4))
                reused[source_span] = len(out)
                out.extend(ptbr_v2[source_offset:source_offset + length])
            target_offset = reused[source_span]
        else:
            target_offset = 0
        for slot in (1, 2):
            struct.pack_into("<II", out, entry + 16 + slot * 8, target_offset, length)
    result = bytes(out)
    if sha256(result) != V3_QM_SHA256:
        raise ValueError("Result differs from in-game-tested v3.0 QM")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eur-romfs-zip", type=Path, required=True)
    parser.add_argument("--ptbr-v2-zip", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Refusing to overwrite an existing output")
    with ZipFile(args.eur_romfs_zip) as archive:
        eur = archive.read(QM_IN_EUR_ROMFS)
    with ZipFile(args.ptbr_v2_zip) as archive:
        ptbr = archive.read(QM_IN_PACK)
    output = build_universal_qm(eur, ptbr)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as stream:
        stream.write(output)
    print(f"OK: {len(output)} bytes, SHA-256 {sha256(output)}")


if __name__ == "__main__":
    main()
