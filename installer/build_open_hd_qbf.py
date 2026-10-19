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


def build_hd_qbf(native: bytes, font_path: str | Path, *, pixel_size: int = 48) -> bytes:
    """Gera cobertura A4 linear, nibble alto primeiro, preservando métricas.

    O QBF produzido é cobertura para o runtime TriAevum; não substitui
    diretamente a fonte lógica 16x16 na ROM.
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
    # Preserva os slots não mapeados como transparência; nunca copia arte original.
    bitmaps = [bytes(2048) for _ in range(glyph_count)]
    for code, index in entries:
        glyph = chr(code)
        image = Image.new("L", (64, 64), 0)
        draw = ImageDraw.Draw(image)
        if code == 0x25C6 and code not in cmap:
            # Unicode BLACK DIAMOND is a geometric shape, not game artwork.
            draw.polygon([(32, 11), (53, 32), (32, 53), (11, 32)], fill=255)
            bounds = (0, 0, 0, 0)
        else:
            bounds = draw.textbbox((0, 0), glyph, font=font, anchor="lt")
        w, h = bounds[2] - bounds[0], bounds[3] - bounds[1]
        if w > 64 or h > 64:
            raise ValueError(f"Glifo U+{code:04X} excede 64x64")
        if code != 0x25C6 or code in cmap:
            draw.text(((64 - w) // 2, (64 - h) // 2), glyph,
                      font=font, anchor="lt", fill=255)
        pixels = image.tobytes()
        bitmap = bytes(((pixels[i] >> 4) << 4) | (pixels[i + 1] >> 4)
                       for i in range(0, len(pixels), 2))
        if bitmaps[index] != bytes(2048) and bitmaps[index] != bitmap:
            raise ValueError("Índice QBF compartilhado por glifos incompatíveis")
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
