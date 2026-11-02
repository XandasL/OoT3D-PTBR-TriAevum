#!/usr/bin/env python3
"""Gera ZIPs Linux com ativador Bash, a partir do ZIP Windows validado."""
import argparse
import hashlib
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo

EXPECTED = "4b2dc3e7734518200f8bf5483f74f16353da939b3914ab3986f1e20968eed9e3"
OVERLAY = "data/mods/OoT3D-PTBR/OoT3D-PTBR.o3ro"
ROOT = Path(__file__).resolve().parent

def build(source_path: Path, output_dir: Path):
    with ZipFile(source_path) as src:
        required = {"Ativar-PTBR.cmd", "Ativar-PTBR.ps1", "LEIA-ME.txt", OVERLAY}
        if set(src.namelist()) != required:
            raise ValueError("Pacote Windows com conteudo inesperado")
        data = src.read(OVERLAY)
        if hashlib.sha256(data).hexdigest() != EXPECTED:
            raise ValueError("Hash do O3RO diferente do validado")
        credits = src.read("LEIA-ME.txt")
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for variant in ("AppImage", "Flatpak"):
        out = output_dir / f"OoT3D-PTBR-v2.0-Beta-Linux-{variant}.zip"
        if out.exists():
            raise FileExistsError(out)
        with ZipFile(out, "x", ZIP_DEFLATED, compresslevel=6) as z:
            z.writestr(OVERLAY, data)
            z.writestr("LEIA-ME.txt", credits)
            for name in ("Ativar-PTBR-Linux.sh", "LEIA-ME-LINUX.txt"):
                inf = ZipInfo(name)
                inf.external_attr = (0o100755 if name.endswith(".sh") else 0o100644) << 16
                z.writestr(inf, (ROOT / name).read_bytes(), compress_type=ZIP_DEFLATED)
        with ZipFile(out) as z:
            assert z.testzip() is None
            assert hashlib.sha256(z.read(OVERLAY)).hexdigest() == EXPECTED
        outputs.append(out)
    return outputs

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--entrada", type=Path, required=True)
    ap.add_argument("--saida", type=Path, required=True)
    args = ap.parse_args()
    for artifact in build(args.entrada, args.saida):
        print(artifact)
