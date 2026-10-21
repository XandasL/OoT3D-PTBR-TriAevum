"""Convert the project's validated linear A4 glyph atlas from 128 to 64 pixels.

No game-native QBF, ROM or external font is included. The logical metrics are
copied by the caller; only 2x2 pixel coverage is area-filtered.
"""
from __future__ import annotations


def half_a4_atlas(atlas: bytes, glyph_count: int, *, source_cell: int = 128) -> bytes:
    if source_cell != 128 or not 0 < glyph_count <= 4096:
        raise ValueError("Unsupported A4 atlas geometry")
    source_bytes_per_glyph = source_cell * source_cell // 2
    if len(atlas) != glyph_count * source_bytes_per_glyph:
        raise ValueError("A4 atlas length does not match glyph count")
    output = bytearray(glyph_count * 64 * 64 // 2)
    for glyph in range(glyph_count):
        start = glyph * source_bytes_per_glyph
        dest = glyph * (64 * 64 // 2)
        for y in range(64):
            row1 = start + (y * 2) * 64
            row2 = row1 + 64
            for x in range(64):
                # Each source byte contains two adjacent A4 coverage pixels.
                b1 = atlas[row1 + x]
                b2 = atlas[row2 + x]
                total = (b1 >> 4) + (b1 & 15) + (b2 >> 4) + (b2 & 15)
                alpha = (total + 2) // 4  # Round half up, retaining A4 coverage.
                offset = dest + y * 32 + x // 2
                if x & 1:
                    output[offset] |= alpha
                else:
                    output[offset] = alpha << 4
    return bytes(output)
