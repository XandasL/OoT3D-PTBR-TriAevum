#!/usr/bin/env python3
"""Converte um ZIP completo ja validado em ZIPs Linux (sem recompilar O3RO)."""
import argparse
import hashlib
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo

EXPECTED = "4b2dc3e7734518200f8bf5483f74f16353da939b3914ab3986f1e20968eed9e3"
OVERLAY = "data/mods/OoT3D-PTBR/OoT3D-PTBR.o3ro"
ROOT = Path(__file__).resolve().parent
COMMON = ("Ativar-PTBR-Linux.sh", "ativar_ptbr_linux.py")
MODES = {"AppImage": "Linux AppImage", "Flatpak": "Linux Flatpak"}

def build(input_zip: Path, destination: Path) -> list[Path]:
    destination.mkdir(parents=True, exist_ok=True)
    with ZipFile(input_zip) as source:
        if sorted(source.namelist()) != sorted(["Ativar-PTBR.cmd", "Ativar-PTBR.ps1",
                                                 "LEIA-ME.txt", OVERLAY]):
            raise ValueError("ZIP Windows de entrada com arquivos inesperados")
        if hashlib.sha256(source.read(OVERLAY)).hexdigest() != EXPECTED:
            raise ValueError("O3RO do ZIP de entrada nao corresponde ao validado")
        original = source.read(OVERLAY)
        credits = source.read("LEIA-ME.txt")
    results = []
    for mode, label in MODES.items():
        output = destination / f"OoT3D-PTBR-v2.0-Beta-Linux-{mode}.zip"
        if output.exists():
            raise FileExistsError(output)
        instruction = (f"OoT3D PT-BR v2.0 Beta - {label} (EXPERIMENTAL)\n\n"
                       "Requer TriAevum v0.8.0-beta.1.2 preparado pelo Forge e Python 3.11+.\n"
                       "Feche o jogo e o Forge antes de ativar.\n"
                       "Extraia este ZIP na pasta preparada pelo Forge que contem data/TriAevum.launch.json.\n"
                       "Abra um terminal nessa pasta e execute:\n"
                       "  bash Ativar-PTBR-Linux.sh\n\n"
                       "Se o perfil estiver em outra pasta, informe o caminho explicitamente:\n"
                       '  bash Ativar-PTBR-Linux.sh "/caminho/para/pasta-do-TriAevum"\n\n'
                       "O script nao modifica AppImage, Flatpak, RomFS, saves ou texturas HD.\n"
                       "Se o ambiente Flatpak usar um diretorio isolado, aponte para a pasta real\n"
                       "de dados preparada pelo Forge, nao para o executavel .flatpak/.AppImage.\n"
                       "O script precisa ter permissao de gravacao nessa pasta.\n"
                       "Instalacao Linux ainda nao validada funcionalmente no jogo.\n\n")
        with ZipFile(output, "x", ZIP_DEFLATED, compresslevel=6) as archive:
            for file in COMMON:
                info = ZipInfo(file)
                info.external_attr = (0o100755 if file.endswith(".sh") else 0o100644) << 16
                archive.writestr(info, (ROOT / file).read_bytes(), compress_type=ZIP_DEFLATED)
            archive.writestr("LEIA-ME-LINUX.txt", instruction.encode("utf-8"))
            archive.writestr("LEIA-ME.txt", credits)
            archive.writestr(OVERLAY, original)
        with ZipFile(output) as archive:
            assert archive.testzip() is None
            assert hashlib.sha256(archive.read(OVERLAY)).hexdigest() == EXPECTED
        results.append(output)
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, required=True)
    parser.add_argument("--saida", type=Path, required=True)
    args = parser.parse_args()
    for file in build(args.entrada, args.saida):
        print(file)
