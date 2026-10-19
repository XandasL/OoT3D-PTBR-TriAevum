"""Validação prévia de fontes abertas para futura geração QBF HD.

Não distribui nem modifica arquivos de fontes; a conversão QBF e integração
com a ROM exigem implementação e validação adicionais.
"""
from __future__ import annotations

from pathlib import Path

PTBR_REQUIRED = "áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ"


def check_font_coverage(font_path: str | Path) -> dict:
    """Verifica cmap Unicode de uma fonte TTF/OTF via fontTools (opcional).

    Falha de modo seguro quando fontTools não está instalado ou a fonte
    não pode ser interpretada. Não garante qualidade visual ou licença.
    """
    try:
        from fontTools.ttLib import TTFont
    except ImportError as exc:
        raise RuntimeError(
            "Instale fonttools para inspecionar fontes TTF/OTF: pip install fonttools"
        ) from exc

    path = Path(font_path)
    if not path.is_file():
        raise FileNotFoundError(f"Fonte não encontrada: {path}")
    font = TTFont(str(path), lazy=True)
    try:
        cmap = font.getBestCmap()
        if not cmap:
            raise ValueError("Fonte sem tabela Unicode cmap utilizável")
        missing = [ch for ch in PTBR_REQUIRED if ord(ch) not in cmap]
        return {
            "filename": path.name,
            "glyphs_mapped": len(cmap),
            "missing_ptbr": missing,
            "covers_ptbr": not missing,
        }
    finally:
        font.close()


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Verifica acentos PT-BR em TTF/OTF")
    parser.add_argument("font", type=Path, help="Fonte local fornecida pelo usuário")
    args = parser.parse_args()
    result = check_font_coverage(args.font)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["covers_ptbr"]:
        raise SystemExit(1)
