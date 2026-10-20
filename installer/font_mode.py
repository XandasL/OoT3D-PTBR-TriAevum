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
    if state.get("backup_sha256") and digest(backup.read_bytes()) != state["backup_sha256"]:
        raise RuntimeError("Backup da fonte foi alterado.")
    expected = state.get("sha256")
    if mode == "hd":
        if not pack.exists() or not expected or digest(pack.read_bytes()) != expected or disabled.exists():
            raise RuntimeError("Fonte HD ativa ou arquivos de controle alterados.")
    else:
        if state["had_original"]:
            if not pack.exists() or digest(pack.read_bytes()) != digest(backup.read_bytes()):
                raise RuntimeError("Pacote de fonte original do usuário foi alterado.")
        elif pack.exists():
            raise RuntimeError("Modo original sem backup não deve manter fonte substituta.")
        if disabled.exists() and (not expected or digest(disabled.read_bytes()) != expected):
            raise RuntimeError("Pacote HD desativado foi alterado.")
    return state


def _load_transaction_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location('ptbr_font_transactions', Path(__file__).with_name('transaction_guard.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tx = _load_transaction_module()
_read_state = read_state


def transaction_paths(pack):
    return (pack.with_name('font_coverage.ptbr-pending.json'),
            pack.with_name('font_coverage.ptbr-staging'))


def read_state(pack):
    pending, staging = transaction_paths(Path(pack))
    if pending.exists() or pending.with_name(pending.name + '.ptbr-write.tmp').exists():
        raise tx.PendingTransaction('Troca de fonte interrompida; use a recuperação antes de continuar.')
    if staging.exists() and any(staging.iterdir()):
        raise tx.PendingTransaction('Preparação de fonte anterior encontrada; preserve os arquivos para recuperação.')
    return _read_state(Path(pack))


def file_hash(path):
    return tx.sha256(path) if path.is_file() else None


def _checkpoint(name):
    """Fault-injection boundary; no effect outside tests."""


def _apply(pack, targets):
    pending, staging = transaction_paths(pack)
    if pending.exists() or (staging.exists() and any(staging.iterdir())):
        raise tx.PendingTransaction('Transação de fonte anterior encontrada.')
    staging.mkdir(exist_ok=True)
    tx.sync_directory(staging.parent)
    plan = {'format': 'ptbr_font_transaction_v1', 'phase': 'PREPARING', 'files': []}
    # Write intent before staging, and never modify active files in this phase.
    for i, (path, data) in enumerate(targets.items()):
        plan['files'].append({'name': path.name, 'before': file_hash(path),
                              'after': digest(data) if data is not None else None,
                              'payload': str(i) if data is not None else None})
    tx.durable_replace(pending, json.dumps(plan).encode())
    _checkpoint('font_intent')
    for entry, data in zip(plan['files'], targets.values()):
        if data is not None:
            tx.durable_replace(staging/entry['payload'], data)
        _checkpoint('font_payload_' + entry['name'])
    plan['phase'] = 'PREPARED'
    tx.durable_replace(pending, json.dumps(plan).encode())
    _checkpoint('font_prepared')
    return recover(pack)


def recover(pack):
    """Finish a verified font plan; refuse unrelated edits before any mutation."""
    pack = Path(pack); pending, staging = transaction_paths(pack)
    if not pending.exists():
        if pending.with_name(pending.name+'.ptbr-write.tmp').exists():
            raise tx.PendingTransaction('Jornal inicial de fonte incompleto; preserve os arquivos.')
        if staging.exists() and any(staging.iterdir()):
            raise tx.PendingTransaction('Staging sem recibo; revisão manual necessária.')
        return 'unchanged'
    plan = json.loads(pending.read_text(encoding='utf-8'))
    allowed = {p.name for p in (pack, *paths(pack))}
    if (plan.get('format') != 'ptbr_font_transaction_v1'
            or plan.get('phase') not in ('PREPARING', 'PREPARED', 'COMMITTED')
            or len({e.get('name') for e in plan.get('files',[])}) != len(plan.get('files',[]))):
        raise tx.PendingTransaction('Jornal da fonte incompatível.')
    entries = plan['files']
    for entry in entries:
        if entry['name'] not in allowed or (entry['payload'] is not None and not entry['payload'].isdigit()):
            raise tx.PendingTransaction('Caminho desconhecido no jornal da fonte.')
        target = pack.parent/entry['name']
        if target.exists() and not target.is_file():
            raise tx.PendingTransaction('Objeto desconhecido no destino da fonte.')
        current = file_hash(target)
        permitted = {entry['before']} if plan['phase']=='PREPARING' else {entry['before'],entry['after']}
        if current not in permitted:
            raise tx.PendingTransaction('Fonte alterada por terceiros; recuperação recusada.')
        if plan['phase'] != 'PREPARING' and current != entry['after'] and entry['after'] is not None:
            if file_hash(staging/entry['payload']) != entry['after']:
                raise tx.PendingTransaction('Payload da fonte ausente ou alterado.')
    # An interrupted temporary write is retained unless its bytes are a prefix
    # of this exact planned payload; no unrelated file is overwritten.
    for entry in entries:
        target = pack.parent/entry['name']; temporary = target.with_name(target.name+'.ptbr-write.tmp')
        if temporary.exists():
            payload = staging/str(entry['payload'])
            if not payload.is_file() or not payload.read_bytes().startswith(temporary.read_bytes()):
                raise tx.PendingTransaction('Temporário da fonte alterado; recuperação recusada.')
            temporary.unlink(); tx.sync_directory(temporary.parent)
    if plan['phase'] != 'PREPARING':
        for entry in entries:
            target = pack.parent/entry['name']
            if file_hash(target) != entry['after']:
                if entry['after'] is None:
                    target.unlink(); tx.sync_directory(target.parent)
                else:
                    tx.durable_replace(target,(staging/entry['payload']).read_bytes())
            _checkpoint('font_apply_' + entry['name'])
        plan['phase'] = 'COMMITTED'
        tx.durable_replace(pending,json.dumps(plan).encode())
        _checkpoint('font_committed')
    # Cleanup only our verified staged payloads. PREPARING never touched active files.
    if not staging.exists():
        if plan['phase']!='COMMITTED':raise tx.PendingTransaction('Staging da fonte ausente.')
        pending.unlink();tx.sync_directory(pending.parent);return 'recovered'
    for child in staging.iterdir():
        entry = next((e for e in entries if child.name == e['payload']),None)
        if entry is None or file_hash(child) != entry['after']:
            raise tx.PendingTransaction('Staging de fonte desconhecido; arquivos preservados.')
    for child in list(staging.iterdir()): child.unlink()
    staging.rmdir(); tx.sync_directory(staging.parent)
    pending.unlink(); tx.sync_directory(pending.parent)
    return 'recovered'


def choose(pack: Path, mode: str, make_hd=None):
    if mode not in ('original','hd'): raise ValueError('Modo de fonte inválido.')
    pack = Path(pack); state = read_state(pack)
    receipt, backup, disabled = paths(pack)
    if mode == 'original' and state is None: return 'unchanged'
    if state and state['mode']==mode:
        if mode=='original' or make_hd is None: return 'unchanged'
        data = make_hd()
        if digest(data)==state['sha256']: return 'unchanged'
    else: data = None
    if mode=='original':
        hd = pack.read_bytes()
        target = backup.read_bytes() if state['had_original'] else None
        updated = {**state,'mode':'original'}
        _apply(pack,{disabled:hd, pack:target,receipt:json.dumps(updated).encode()})
        return 'original'
    if make_hd is None: raise RuntimeError('Gerador de cobertura HD indisponível.')
    data = data if data is not None else make_hd()
    targets = {}
    if state is None:
        previous = pack.read_bytes() if pack.exists() else None
        if previous is not None: targets[backup]=previous
        state = {'format':'ptbr-noto-font-v1','had_original':previous is not None,
                 'backup_sha256':digest(previous) if previous is not None else None}
    targets[pack]=data
    targets[receipt]=json.dumps({**state,'mode':'hd','sha256':digest(data)}).encode()
    targets[disabled]=None
    _apply(pack,targets)
    return 'hd'


def restore_previous(pack):
    pack=Path(pack); state=read_state(pack)
    if state is None:return
    receipt,backup,disabled=paths(pack)
    data=backup.read_bytes() if state['had_original'] else None
    _apply(pack,{pack:data,disabled:None,receipt:None,backup:None})
