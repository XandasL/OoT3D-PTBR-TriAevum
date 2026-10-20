"""Durable local transaction markers for the v1.3 installer.

Does not delete an unknown/user-owned file; refuses ambiguous recovery.
This is infrastructure, not a complete crash-safe installer by itself.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


class PendingTransaction(RuntimeError):
    pass


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def sync_directory(directory: Path) -> None:
    """Best effort on Windows; fsync directory metadata on POSIX."""
    if os.name == "nt":
        return
    fd = os.open(str(directory), os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def durable_replace(target: Path, content: bytes) -> None:
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(target.name + ".ptbr-write.tmp")
    if temp.exists():
        raise PendingTransaction("Arquivo temporário anterior encontrado: " + str(temp))
    try:
        with temp.open("xb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, target)
        sync_directory(target.parent)
    finally:
        # Do not delete unexpected existing temporary files after an error.
        pass


def write_journal(root: Path, record: dict) -> Path:
    target = Path(root) / "traducao_ptbr_v130.pending.json"
    if target.exists():
        raise PendingTransaction("Instalação anterior interrompida: " + str(target))
    durable_replace(target, (json.dumps(record, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    return target


def update_journal(path: Path, record: dict) -> None:
    if not path.is_file():
        raise PendingTransaction("Jornal ausente; recuperação manual necessária.")
    durable_replace(path, (json.dumps(record, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))


def pending(root: Path) -> dict | None:
    target = Path(root) / "traducao_ptbr_v130.pending.json"
    if not target.exists():
        return None
    try:
        record = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise PendingTransaction("Jornal de recuperação ilegível; não modificar a instalação.") from exc
    if record.get("format") != "oot3d_ptbr_v130_transaction_v1":
        raise PendingTransaction("Jornal de recuperação desconhecido; não modificar a instalação.")
    return record


def refuse_pending(root: Path) -> None:
    root = Path(root)
    # A power loss can happen before the initial journal rename.
    # Never overlook its partially written temporary file.
    unfinished = root / "traducao_ptbr_v130.pending.json.ptbr-write.tmp"
    profile_temp = root / "TriAevum.launch.json.ptbr-write.tmp"
    if unfinished.exists() or profile_temp.exists():
        raise PendingTransaction(
            "Arquivos temporários de uma operação interrompida foram encontrados. "
            "Nenhuma alteração será feita até revisão segura."
        )
    if pending(root) is not None:
        raise PendingTransaction(
            "Foi detectada uma operação PT-BR interrompida. "
            "Nenhuma instalação ou restauração será iniciada; "
            "preserve backups e verifique o perfil antes da recuperação."
        )


def complete_journal(path: Path) -> None:
    path.unlink()
    sync_directory(path.parent)


def recover_original_launch(root: Path) -> str:
    """Restore only the verified original launch profile after an interrupted operation.

    Never deletes translated data, game data, font packs, or the journal.
    Leaves the journal in place until remaining files have been reviewed.
    """
    root = Path(root)
    record = pending(root)
    if record is None:
        raise PendingTransaction("Nenhuma transação anterior registrada.")
    if record.get("operation") not in ("install", "restore"):
        raise PendingTransaction("Troca de fonte interrompida; reparo do perfil não aplicável.")
    original_hash = record.get("original_launch_sha256")
    if not isinstance(original_hash, str) or len(original_hash) != 64:
        raise PendingTransaction("SHA do perfil original ausente ou inválido.")

    launch = root / "TriAevum.launch.json"
    backup = root / "TriAevum.launch.json.antes_ptbr_textos"
    if not launch.is_file():
        raise PendingTransaction("Perfil ativo ausente; não é possível reparar automaticamente.")
    current = sha256(launch)
    if current == original_hash:
        return "already-original"
    expected_translated = record.get("expected_launch_sha256")
    if record.get("operation") == "restore":
        receipt = root / "traducao_ptbr_textos.json"
        if not receipt.is_file():
            raise PendingTransaction("Recibo anterior ausente; perfil desconhecido.")
        try:
            expected_translated = json.loads(receipt.read_text(encoding="utf-8"))["launch_sha256"]
        except (KeyError, ValueError, OSError) as exc:
            raise PendingTransaction("Recibo da tradução ilegível.") from exc
    if not expected_translated or current != expected_translated:
        raise PendingTransaction("Perfil ativo alterado por terceiros; recuperação recusada.")
    if not backup.is_file() or sha256(backup) != original_hash:
        raise PendingTransaction("Backup original ausente ou hash divergente; recuperação recusada.")

    durable_replace(launch, backup.read_bytes())
    if sha256(launch) != original_hash:
        raise PendingTransaction("Falha ao confirmar restauração do perfil original.")
    record["phase"] = "original_profile_recovered"
    update_journal(root / "traducao_ptbr_v130.pending.json", record)
    return "recovered-original"
