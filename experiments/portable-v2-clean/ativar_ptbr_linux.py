#!/usr/bin/env python3
"""Ativa o O3RO localmente no perfil TriAevum; sem rede nem alteracoes na RomFS."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

EXPECTED = "4b2dc3e7734518200f8bf5483f74f16353da939b3914ab3986f1e20968eed9e3"

def activate(runtime: Path) -> Path:
    runtime = runtime.resolve()
    profile = runtime / "data" / "TriAevum.launch.json"
    overlay = runtime / "data" / "mods" / "OoT3D-PTBR" / "OoT3D-PTBR.o3ro"
    if not profile.is_file():
        raise ValueError(f"Perfil nao encontrado: {profile}")
    if not overlay.is_file():
        raise ValueError(f"Mod O3RO nao encontrado: {overlay}")
    sha = hashlib.file_digest(overlay.open("rb"), "sha256").hexdigest()
    if sha != EXPECTED:
        raise ValueError("SHA-256 do O3RO diferente do mod beta.1.2 validado")
    document = json.loads(profile.read_text(encoding="utf-8-sig"))
    args = document.get("arguments")
    if not isinstance(args, list) or any(not isinstance(a, str) for a in args):
        raise ValueError("O perfil nao possui uma lista 'arguments' valida")
    indices = [i for i, a in enumerate(args) if a == "--romfs-overlay"]
    if len(indices) > 1:
        raise ValueError("Perfil com --romfs-overlay duplicado")
    if indices:
        i = indices[0]
        if i + 1 >= len(args) or args[i + 1].startswith("--"):
            raise ValueError("--romfs-overlay incompleto")
        args[i + 1] = str(overlay)
    else:
        args.extend(["--romfs-overlay", str(overlay)])
    document["arguments"] = args
    new_content = json.dumps(document, ensure_ascii=False, indent=2) + "\n"
    # Uma copia anterior nunca deve ser sobrescrita.
    backup = profile.with_name(profile.name + ".backup-antes-ptbr.json")
    if not backup.exists():
        # O exclusivo 'xb' evita sobrescrever backups concorrentes.
        with backup.open("xb") as stream, profile.open("rb") as source:
            shutil.copyfileobj(source, stream)
        print(f"Backup criado: {backup}")
    else:
        print(f"Backup existente preservado: {backup}")
    # Grava no mesmo diretorio e troca atomicamente o perfil.
    fd, tmp = tempfile.mkstemp(prefix=".TriAevum.launch.", suffix=".tmp", dir=profile.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(new_content)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(tmp, profile.stat().st_mode & 0o777)
        os.replace(tmp, profile)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return profile

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", type=Path, default=Path.cwd(),
                        help="Pasta preparada pelo Forge que contem data/TriAevum.launch.json")
    options = parser.parse_args()
    try:
        profile = activate(options.runtime)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1
    print(f"Traducao PT-BR ativada: {profile}")
    print("TriAevum.exe, RomFS, saves e texturas personalizados nao foram alterados.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
