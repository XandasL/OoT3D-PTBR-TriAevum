#!/usr/bin/env python3
"""Generate the locally tested classic-only bundle; NOT a redistribution license."""
import argparse
import hashlib
import zipfile
from pathlib import Path

EXPECTED = "4b2dc3e7734518200f8bf5483f74f16353da939b3914ab3986f1e20968eed9e3"
ROOT = Path(__file__).resolve().parent
MEMBERS = ("Ativar-PTBR.cmd", "Ativar-PTBR.ps1", "LEIA-ME.txt", "CREDITOS.txt",
           "data/mods/OoT3D-PTBR/classico.o3ro")

def generate(classico: Path, output: Path) -> None:
    if not classico.is_file():
        raise ValueError("O3RO classico nao encontrado")
    digest = hashlib.sha256()
    with classico.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    if digest.hexdigest() != EXPECTED:
        raise ValueError("Hash do O3RO diferente do validado para beta.1.2")
    output = output.resolve()
    if output.exists():
        raise ValueError("A saida ja existe; operacao cancelada")
    if output == classico.resolve():
        raise ValueError("Saida nao pode ser o O3RO de entrada")
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            for name in MEMBERS[:-1]:
                z.write(ROOT / name, name)
            z.write(classico, MEMBERS[-1])
        with zipfile.ZipFile(output) as z:
            if tuple(z.namelist()) != MEMBERS:
                raise ValueError("Conteudo inesperado no ZIP")
            if any(name.lower().endswith((".png", ".jpg", ".webp", ".ctxb")) for name in z.namelist()):
                raise ValueError("Arte grafica proibida neste pacote")
            if hashlib.sha256(z.read(MEMBERS[-1])).hexdigest() != EXPECTED:
                raise ValueError("O3RO alterado durante o empacotamento")
    except BaseException:
        output.unlink(missing_ok=True)
        raise

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--classico", required=True, type=Path)
    parser.add_argument("--saida", required=True, type=Path)
    args = parser.parse_args()
    try:
        generate(args.classico, args.saida)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print("Pacote LOCAL preparado:", args.saida)
    print("NAO PUBLICAR sem revisar direitos dos arquivos derivados do jogo.")

if __name__ == "__main__":
    main()
