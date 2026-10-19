"""Gera QBF1 A4 HD 64x64 a partir de TTF/OTF e QBF nativo local.

Sem assets SingleScreen. Mantém diretório, índices, fallback e métricas
do QBF original; apenas substitui os bitmaps por glifos rasterizados.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import struct

MAX_QBF_BYTES = 32 * 1024 * 1024


def parse_native(data: bytes):
    if len(data) < 16 or data[:4] != b"QBF1":
        raise ValueError("Cabeçalho QBF1 inválido")
    count, glyphs, fallback = struct.unpack_from("<HHH", data, 4)
    if data[12:16] != bytes((4, 16, 16, 2)):
        raise ValueError("Somente QBF1 A4/16x16/encoding 2 é suportado")
    if not count or not glyphs or len(data) != 16 + count * 8 + glyphs * 128:
        raise ValueError("Tamanho ou tabela QBF inválida")
    entries = []
    last = -1
    for i in range(count):
        code, index = struct.unpack_from("<HH", data, 16 + i * 8)
        if code <= last or index >= glyphs:
            raise ValueError("Índice QBF inválido, duplicado ou fora de ordem")
        entries.append((code, index))
        last = code
    if fallback not in {code for code, _ in entries}:
        raise ValueError("Fallback QBF ausente")
    return entries, glyphs


def native_ink_bounds(native: bytes, glyph_index: int, glyph_count: int):
    """Infer visual ink placement from the *local user's* 16x16 A4 source.

    Only pixel extents are used; game artwork never enters the HD bitmap.
    Coordinates include accents, descenders, and native left side-bearing.
    """
    directory_end = 16 + (len(native) - 16 - glyph_count * 128) // 8 * 8
    start = directory_end + glyph_index * 128
    bitmap = native[start:start + 128]
    if len(bitmap) != 128:
        raise ValueError("Native QBF bitmap truncated")
    occupied = []
    for i, byte in enumerate(bitmap):
        if byte >> 4:
            occupied.append((2 * i % 16, 2 * i // 16))
        if byte & 15:
            occupied.append(((2 * i + 1) % 16, (2 * i + 1) // 16))
    if not occupied:
        return None
    return (min(x for x, _ in occupied), min(y for _, y in occupied),
            max(x for x, _ in occupied) + 1, max(y for _, y in occupied) + 1)


def build_hd_qbf(native: bytes, font_path: str | Path, *, pixel_size: int = 48) -> bytes:
    """Rasterize OFL outlines into the *original* ink positions, 4x.

    Native QBF layout and glyph metrics remain authoritative at runtime.
    Font bearings from a different typeface must not recenter the glyph in
    the 64px coverage cell; that visibly breaks game text spacing.
    """
    if not 8 <= pixel_size <= 60:
        raise ValueError("pixel_size fora do intervalo 8..60")
    entries, glyph_count = parse_native(native)
    try:
        from PIL import Image, ImageDraw, ImageFont
        from fontTools.ttLib import TTFont
    except ImportError as exc:
        raise RuntimeError("Instale pillow e fonttools para gerar o QBF HD") from exc
    tt = TTFont(str(font_path), lazy=True)
    try:
        cmap = tt.getBestCmap()
        if not cmap:
            raise ValueError("Fonte TTF/OTF sem cmap Unicode")
        missing = [f"U+{code:04X}" for code, _ in entries if code not in cmap and code != 0x25C6]
        if missing:
            raise ValueError("Fonte aberta não cobre os códigos QBF: " + ", ".join(missing))
    finally:
        tt.close()
    font = ImageFont.truetype(str(font_path), pixel_size)
    output = bytearray(native[:16 + len(entries) * 8])
    output[13:15] = bytes((64, 64))
    bitmaps = [bytes(2048) for _ in range(glyph_count)]
    filled = {}
    for code, index in entries:
        ink = native_ink_bounds(native, index, glyph_count)
        if ink is None:
            continue  # Native spaces and blank glyphs must stay blank.
        left, top, right, bottom = ink
        destination = (4 * left, 4 * top, 4 * right, 4 * bottom)
        target_w = destination[2] - destination[0]
        target_h = destination[3] - destination[1]
        if not (0 < target_w <= 64 and 0 < target_h <= 64):
            raise ValueError(f"Native ink extents invalid: U+{code:04X}")
        glyph = chr(code)
        # Draw at native font scale on a large temporary mask, then crop to
        # actual visible ink. Pillow's font bearings remain internal to mask.
        mask = Image.new("L", (256, 256), 0)
        draw = ImageDraw.Draw(mask)
        if code == 0x25C6 and code not in cmap:
            draw.polygon([(128, 25), (231, 128), (128, 231), (25, 128)], fill=255)
        else:
            draw.text((128, 128), glyph, font=font, anchor="mm", fill=255)
        cropped = mask.getbbox()
        if cropped is None:
            raise ValueError(f"Fonte vazia para glifo nativo U+{code:04X}")
        shape = mask.crop(cropped).resize((target_w, target_h), Image.Resampling.LANCZOS)
        image = Image.new("L", (64, 64), 0)
        image.paste(shape, destination[:2])
        pixels = image.tobytes()
        bitmap = bytes(((pixels[i] >> 4) << 4) | (pixels[i + 1] >> 4)
                       for i in range(0, len(pixels), 2))
        if index in filled and filled[index] != bitmap:
            raise ValueError("Índice QBF compartilhado por glifos incompatíveis")
        filled[index] = bitmap
        bitmaps[index] = bitmap
    output.extend(b"".join(bitmaps))
    if len(output) > MAX_QBF_BYTES:
        raise ValueError("Fonte QBF HD excede o limite")
    return bytes(output)


def main():
    parser = argparse.ArgumentParser(description="Gerador local QBF HD a partir de fonte aberta")
    parser.add_argument("--native", required=True, type=Path, help="QBF original do usuário")
    parser.add_argument("--font", required=True, type=Path, help="TTF/OTF com licença apropriada")
    parser.add_argument("--output", required=True, type=Path, help="Arquivo HD QBF local")
    args = parser.parse_args()
    result = build_hd_qbf(args.native.read_bytes(), args.font)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(result)
    print(f"QBF HD gerado localmente: {args.output} ({len(result)} bytes)")


if __name__ == "__main__":
    main()
