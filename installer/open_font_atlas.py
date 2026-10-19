"""Rasterização experimental de fonte OFL para inspeção visual, SEM gerar QBF.

Nunca incorpora bitmaps SingleScreen ou extrai glifos de jogos. O atlas
PNG é um artefato intermediário; ainda não é compatível com o jogo.
"""
from __future__ import annotations

from pathlib import Path
import json

from open_font_probe import PTBR_REQUIRED, check_font_coverage


def render_ptbr_atlas(font_path: str | Path, output_dir: str | Path,
                      *, cell_size: int = 64, font_size: int = 42) -> dict:
    """Renderiza os acentos PT-BR em células RGBA transparentes.

    Exige cobertura Unicode completa; falha antes de gravar arquivos.
    Não altera ROM, QBF, O3TU nem o instalador.
    """
    if cell_size < 16 or cell_size > 256 or font_size < 8 or font_size > cell_size:
        raise ValueError("Tamanho de célula ou fonte fora dos limites")
    coverage = check_font_coverage(font_path)
    if not coverage["covers_ptbr"]:
        raise ValueError("Fonte sem glifos PT-BR: " + "".join(coverage["missing_ptbr"]))
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:
        raise RuntimeError("Instale pillow para rasterizar: pip install pillow") from exc

    glyphs = list(dict.fromkeys(PTBR_REQUIRED))
    cols = 8
    rows = (len(glyphs) + cols - 1) // cols
    atlas = Image.new("RGBA", (cols * cell_size, rows * cell_size), (0, 0, 0, 0))
    font = ImageFont.truetype(str(font_path), font_size)
    draw = ImageDraw.Draw(atlas)
    entries = []
    for i, char in enumerate(glyphs):
        x, y = (i % cols) * cell_size, (i // cols) * cell_size
        bounds = draw.textbbox((0, 0), char, font=font, anchor="lt")
        width, height = bounds[2] - bounds[0], bounds[3] - bounds[1]
        if width > cell_size or height > cell_size:
            raise ValueError(f"Glifo U+{ord(char):04X} excede a célula")
        draw.text((x + (cell_size - width) // 2, y + (cell_size - height) // 2),
                  char, font=font, anchor="lt", fill=(255, 255, 255, 255))
        entries.append({"character": char, "codepoint": ord(char),
                        "cell_x": x, "cell_y": y, "width": width, "height": height})
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    atlas.save(output / "ptbr-glyph-preview.png")
    manifest = {"format": "ptbr_open_font_preview_v1", "source": Path(font_path).name,
                "cell_size": cell_size, "font_size": font_size, "glyphs": entries,
                "not_qbf": True}
    (output / "ptbr-glyph-preview.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Gera atlas PNG experimental de acentos PT-BR")
    parser.add_argument("font", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    render_ptbr_atlas(args.font, args.output)
