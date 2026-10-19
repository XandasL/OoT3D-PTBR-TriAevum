"""Switch optional Latin HD coverage without touching RomFS or O3TU.

Only the exact font_coverage.zip beside the validated O3TU is managed.
An existing user pack is backed up once, never discarded.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def paths(pack: Path):
    return (pack.with_name("font_coverage.ptbr-noto.json"),
            pack.with_name("font_coverage.ptbr-noto.backup.zip"),
            pack.with_name("font_coverage.ptbr-noto.disabled.zip"))


def read_state(pack: Path):
    receipt, backup, disabled = paths(pack)
    if not receipt.exists():
        if backup.exists() or disabled.exists():
            raise RuntimeError("Arquivos anteriores da fonte sem recibo; operação recusada.")
        return None
    state = json.loads(receipt.read_text(encoding="utf-8"))
    if state.get("format") != "ptbr-noto-font-v1":
        raise RuntimeError("Recibo da fonte incompatível.")
    mode = state.get("mode", "hd")
    if mode not in ("hd", "original") or not isinstance(state.get("had_original"), bool):
        raise RuntimeError("Estado da fonte desconhecido.")
    if state["had_original"] != backup.exists():
        raise RuntimeError("Backup do pacote anterior ausente ou inesperado.")
    expected = state.get("sha256")
    if mode == "hd":
        if not pack.exists() or not expected or digest(pack.read_bytes()) != expected or disabled.exists():
            raise RuntimeError("Fonte HD ativa ou arquivos de controle alterados.")
    else:
        if pack.exists():
            raise RuntimeError("Modo original exige ausência do pacote HD ativo.")
        if disabled.exists() and (not expected or digest(disabled.read_bytes()) != expected):
            raise RuntimeError("Pacote HD desativado foi alterado.")
    return state


def _write_receipt(receipt: Path, state: dict):
    temporary = receipt.with_name(receipt.name + ".tmp")
    try:
        temporary.write_text(json.dumps(state, indent=2), encoding="utf-8")
        os.replace(temporary, receipt)
    finally:
        temporary.unlink(missing_ok=True)


def choose(pack: Path, mode: str, make_hd=None):
    """Choose 'original' (disable replacement) or 'hd' (use generated QBF).

    make_hd is called only for HD mode and returns a validated local ZIP.
    The original game font is never overwritten by this module.
    """
    if mode not in ("original", "hd"):
        raise ValueError("Modo de fonte inválido.")
    pack = Path(pack)
    receipt, backup, disabled = paths(pack)
    state = read_state(pack)
    if state is not None and state.get("mode", "hd") == mode:
        if mode == "hd":
            if make_hd is None:
                return "unchanged"
            data = make_hd()
            if digest(data) == state["sha256"]:
                return "unchanged"
        else:
            return "unchanged"
    if mode == "original":
        if state is None:
            previous = pack.read_bytes() if pack.exists() else None
            if previous is not None:
                # Own backup is validated before removing the active pack.
                backup.write_bytes(previous)
                if backup.read_bytes() != previous:
                    raise RuntimeError("Falha ao preservar pacote HD anterior.")
            state = {"format": "ptbr-noto-font-v1",
                     "had_original": previous is not None, "sha256": None}
        else:
            # Preserve the currently installed Noto Sans so the user may reenable it.
            previous = pack.read_bytes()
            disabled.write_bytes(previous)
            if digest(disabled.read_bytes()) != state["sha256"]:
                raise RuntimeError("Falha ao preservar Noto Sans antes da desativação.")
        os.replace(pack, disabled) if state["sha256"] is not None else pack.unlink(missing_ok=True)
        _write_receipt(receipt, {**state, "mode": "original"})
        return "original"
    if make_hd is None:
        raise RuntimeError("Gerador Noto Sans indisponível.")
    data = make_hd()
    new_hash = digest(data)
    if state is None:
        original = pack.read_bytes() if pack.exists() else None
        if original is not None:
            backup.write_bytes(original)
            if backup.read_bytes() != original:
                raise RuntimeError("Falha ao preservar pacote HD anterior.")
        state = {"format": "ptbr-noto-font-v1",
                 "had_original": original is not None}
    temporary = pack.with_name(pack.name + ".tmp")
    try:
        temporary.write_bytes(data)
        if digest(temporary.read_bytes()) != new_hash:
            raise RuntimeError("Pacote Noto Sans temporário corrompido.")
        os.replace(temporary, pack)
        _write_receipt(receipt, {**state, "mode": "hd", "sha256": new_hash})
        disabled.unlink(missing_ok=True)
    finally:
        temporary.unlink(missing_ok=True)
    return "hd"


def restore_previous(pack: Path):
    """Restore the pre-installer pack (if any), after provenance verification."""
    pack = Path(pack)
    state = read_state(pack)
    if state is None:
        return
    receipt, backup, disabled = paths(pack)
    if state["had_original"]:
        data = backup.read_bytes()
        temporary = pack.with_name(pack.name + ".restore.tmp")
        try:
            temporary.write_bytes(data)
            if temporary.read_bytes() != data:
                raise RuntimeError("Falha ao restaurar pacote anterior.")
            os.replace(temporary, pack)
        finally:
            temporary.unlink(missing_ok=True)
        backup.unlink()
    else:
        pack.unlink(missing_ok=True)
    disabled.unlink(missing_ok=True)
    receipt.unlink()
