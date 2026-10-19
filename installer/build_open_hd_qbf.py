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


def build_hd_qbf(native: bytes, font_path: str | Path, *, pixel_size: int = 44) -> bytes:
    """Render Noto Sans at one common font scale and baseline.

    Native QBF provides *horizontal origin only*. The shared baseline and
    a single TTF pixel size preserve typographic proportions: scaling every
    glyph to its 16x16 native ink rectangle made "i", "m" and capitals
    wildly different in apparent size. Runtime retains native advance widths.
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
    baseline = 52  # Native 16px Latin font baseline around row 13, at 4x.
    for code, index in entries:
        ink = native_ink_bounds(native, index, glyph_count)
        if ink is None:
            continue  # Spaces remain transparent, never fabricate ink.
        left, _, _, _ = ink
        origin_x = 4 * left
        image = Image.new("L", (64, 64), 0)
        if code == 0x25C6 and code not in cmap:
            # Geometric fallback with one fixed em size (no native rectangle stretching).
            shape = Image.new("L", (28, 28), 0)
            ImageDraw.Draw(shape).polygon([(14, 0), (27, 14), (14, 27), (0, 14)], fill=255)
            x, y = origin_x, baseline - 28
        else:
            # Anchor 'ls' gives the font's real baseline. Cropping removes the
            # font-specific negative side bearing, not its typographic height.
            display_char = "-" if code == 0x00AD else chr(code)
            bounds = font.getbbox(display_char, anchor="ls")
            if bounds is None:
                raise ValueError(f"Glifo U+{code:04X} sem bbox da fonte")
            x0, y0, x1, y1 = bounds
            shape = Image.new("L", (max(1, x1 - x0), max(1, y1 - y0)), 0)
            ImageDraw.Draw(shape).text((-x0, -y0), display_char, font=font,
                                       anchor="ls", fill=255)
            bbox = shape.getbbox()
            if bbox is None:
                raise ValueError(f"Glifo não-vazio U+{code:04X} ficou vazio")
            # Keep actual ascent/descent, including punctuation and accents.
            x, y = origin_x + bbox[0], baseline + y0 + bbox[1]
            shape = shape.crop(bbox)
        if x < 0 or y < 0 or x + shape.width > 64 or y + shape.height > 64:
            raise ValueError(
                f"U+{code:04X} não cabe em 64x64 com a escala uniforme "
                f"{pixel_size}: origem=({x},{y}), tamanho={shape.size}")
        image.paste(shape, (x, y))
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
