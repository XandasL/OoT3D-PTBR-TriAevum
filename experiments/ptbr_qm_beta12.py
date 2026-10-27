"""Strict PT-BR QM conversion for TriAevum's canonical EUR RomFS.

A standalone, import-safe adaptation of the translation V4's validated mapping.
Only the exact approved us.qm can be converted; unrelated languages are untouched.
"""
from __future__ import annotations

import hashlib
import struct

EXPECTED_QM_SHA256 = "f28114b0d915f936ff7e1ff112a96ba43c81983a20739509ffb943ec8c2ab4d1"
EXPECTED_RECORDS = 2510
RECORD_SIZE = 96
HEADER_SIZE = 16
SLOT_MAP = ((2, 1), (4, 5), (6, 7))
TILDE_ALIASES = (("ä", "ã"), ("ö", "õ"), ("Ä", "Ã"), ("Ö", "Õ"))


def convert_usa_to_eur(original: bytes) -> bytes:
    """Rewrite EUR language slots and Portuguese UTF-8 aliases, without resizing."""
    if hashlib.sha256(original).hexdigest() != EXPECTED_QM_SHA256:
        raise ValueError("Unknown PT-BR us.qm (SHA-256 differs from vetted resource)")
    if len(original) < HEADER_SIZE or original[:4] != b"QM\x00\x00":
        raise ValueError("Invalid QM header")
    version, records = struct.unpack_from("<II", original, 4)
    if version != 4 or records != EXPECTED_RECORDS:
        raise ValueError("Unexpected QM revision or record count")
    table_end = HEADER_SIZE + records * RECORD_SIZE
    if len(original) < table_end:
        raise ValueError("Truncated QM record table")
    result = bytearray(original)
    portuguese_spans, other_spans = set(), set()
    for record in range(records):
        entry = HEADER_SIZE + record * RECORD_SIZE
        for destination_slot, source_slot in SLOT_MAP:
            source_offset = entry + 16 + source_slot * 8
            destination_offset = entry + 16 + destination_slot * 8
            result[destination_offset:destination_offset + 8] = original[source_offset:source_offset + 8]
        for slot in (1, 5, 7):
            off, size = struct.unpack_from("<II", original, entry + 16 + slot * 8)
            if size == 0:
                continue
            if off < table_end or off + size > len(original):
                raise ValueError("QM text points outside valid payload")
            (portuguese_spans if slot == 1 else other_spans).add((off, off + size))
    ordered = sorted(portuguese_spans)
    if any(left[1] > right[0] for left, right in zip(ordered, ordered[1:])):
        raise ValueError("Overlapping Portuguese text spans")
    for start, end in ordered:
        if any(start < other_end and other_start < end
               for other_start, other_end in other_spans):
            raise ValueError("Portuguese text overlaps another language")
        payload = original[start:end]
        for before, after in TILDE_ALIASES:
            payload = payload.replace(before.encode("utf-8"), after.encode("utf-8"))
        if len(payload) != end - start:
            raise ValueError("QM conversion resized text")
        result[start:end] = payload
    if len(result) != len(original):
        raise ValueError("QM conversion resized original")
    return bytes(result)
