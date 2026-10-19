# -*- coding: utf-8 -*-
"""
Instalador V4 - Tradução PT-BR completa + TopScreen para Ocarina of Time 3D / TriAevum

- Porta os 112 recursos reais da tradução.
- Espelha os 14 CTXB PT-BR para menu/02_EU_ENGLISH.
- Ignora scene/fazer (arquivos-base/backup da equipe de tradução).
- Converte message/us/us.qm para message/eu/eu.qm (slots USA -> EUR).
- Mapeia message/us -> message/eu e misc/us -> misc/eu.
- Substitui payloads de mesmo tamanho no lugar.
- Realoca payloads de tamanho diferente para o fim do RomFS.
- Atualiza process-manifest.json.
- Ajusta somente o OriginalHash do menu_top no TopScreen O3TU, preservando o replacement Single Screen.
- Cria backups próprios da V4.
- Valida todos os payloads antes de concluir.
- Permite restaurar o original.

Execute este arquivo a partir da pasta Windows do TriAevum.
"""

from pathlib import Path
import hashlib
import json
import os
import shutil
import struct
import sys
import time

INVALID = 0xFFFFFFFF

APP_NAME = "Instalador V4 - Tradução PT-BR OoT3D"
MARKER_FORMAT = "oot3d_ptbr_full_translation_install_v4"

EXPECTED_CLEAN_ROMFS_SIZE = 473_522_176
EXPECTED_CLEAN_ROMFS_SHA256 = (
    "011c0b6933f3932c704ff1c6ab562023f407c2929661a6d54ecea1ca81072f99"
)

EXPECTED_TRANSLATION_FILES = 112
EXPECTED_QM_RECORDS = 2510
EXPECTED_US_QM_SHA256 = (
    "f28114b0d915f936ff7e1ff112a96ba43c81983a20739509ffb943ec8c2ab4d1"
)

# V4: os 14 CTXB de menu também são espelhados para o slot EUR realmente
# consumido pelo runtime. menu_top precisa, além disso, ser reconhecido pelo
# hash-gate do TopScreen.
MENU_SLOT_EU_FILES = (
    "hud_all00.ctxb",
    "hud_menu_title00.ctxb",
    "menu_equip_parts00.ctxb",
    "menu_file_select_parts00.ctxb",
    "menu_file_select_parts01.ctxb",
    "menu_hint_movie_parts00.ctxb",
    "menu_item_parts00.ctxb",
    "menu_map_parts00.ctxb",
    "menu_map_parts01.ctxb",
    "menu_okarina_parts00.ctxb",
    "menu_option_parts00.ctxb",
    "menu_top_parts00.ctxb",
    "name_entry00_parts00.ctxb",
    "name_entry00_parts01.ctxb",
)
EXPECTED_V4_PATCH_OPERATIONS = 126

O3TU_OLD_ORIGINAL_HASH = 0xB216011E1F24749C
O3TU_PTBR_ORIGINAL_HASH = 0xAC72735EF08ABEAB
O3TU_ENGLISH_REPLACEMENT_HASH = 0xF7DE7A380F490FF1

if getattr(sys, "frozen", False):
    BASE = Path(sys.executable).resolve().parent
else:
    BASE = Path(__file__).resolve().parent

LAUNCH = BASE / "TriAevum.launch.json"
TRAD_ROOT = BASE / "TraducaoCompleta" / "citra" / "romfs"
MARKER = BASE / "traducao_ptbr_v4_instalada.json"


# ============================================================
# Utilidades
# ============================================================

def pause():
    input("\nPressione ENTER para continuar...")


def sha256_file(path, chunk=4 * 1024 * 1024):
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def sha256_region(f, offset, size, chunk=4 * 1024 * 1024):
    h = hashlib.sha256()
    f.seek(offset)
    remaining = size
    while remaining:
        b = f.read(min(chunk, remaining))
        if not b:
            raise RuntimeError("Fim inesperado ao validar payload do RomFS.")
        h.update(b)
        remaining -= len(b)
    return h.hexdigest()


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save_json(path, obj):
    path.write_text(
        json.dumps(obj, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def align_up(value, alignment=16):
    return (value + alignment - 1) // alignment * alignment


def human(n):
    return f"{n:,}".replace(",", ".")


# ============================================================
# Localização do manifesto / RomFS
# ============================================================

def resolve_profile_path(text):
    if not isinstance(text, str) or not text or '\0' in text:
        raise RuntimeError('Caminho inválido no launch profile.')
    text = text.replace('\\', '/')
    for variable in ('${profile_dir}/', '${runtime_dir}/'):
        if text.startswith(variable):
            text = text[len(variable):]
            break
    if '${' in text:
        raise RuntimeError('Variável de caminho desconhecida no launch profile.')
    return contained(BASE / text)


def locate_runtime():
    if not LAUNCH.exists():
        raise RuntimeError(
            f"TriAevum.launch.json não encontrado:\n{LAUNCH}\n\n"
            "Coloque este instalador na pasta Windows do TriAevum."
        )

    launch = load_json(LAUNCH)
    args = launch.get("arguments", [])

    try:
        i = args.index("--a32-process-manifest")
        manifest_text = args[i + 1]
    except (ValueError, IndexError):
        raise RuntimeError("--a32-process-manifest não encontrado no launch profile.")

    manifest = resolve_profile_path(manifest_text)
    if not manifest.exists():
        raise RuntimeError(f"Manifesto não encontrado:\n{manifest}")

    manifest_data = load_json(manifest)
    source = manifest_data.get("source", {})
    rel = source.get("romfs_image_path")
    if not rel:
        raise RuntimeError("romfs_image_path não encontrado no manifesto.")

    romfs = (manifest.parent / rel).resolve()
    if not romfs.exists():
        raise RuntimeError(f"RomFS não encontrado:\n{romfs}")

    return manifest, manifest_data, romfs


# ============================================================
# Parser RomFS Level-3
# ============================================================

def index_romfs(path):
    """
    Retorna:
      header: offsets principais
      files_by_path: caminho lowercase -> metadata
    Lê apenas header/tabelas de metadata, não carrega ~473 MB em RAM.
    """
    with path.open("rb") as f:
        header_raw = f.read(40)
        if len(header_raw) != 40:
            raise RuntimeError("RomFS pequeno/inválido.")

        (
            header_size,
            dir_hash_offset,
            dir_hash_size,
            dir_meta_offset,
            dir_meta_size,
            file_hash_offset,
            file_hash_size,
            file_meta_offset,
            file_meta_size,
            file_data_offset,
        ) = struct.unpack("<10I", header_raw)

        if header_size != 40:
            raise RuntimeError(f"Header Level-3 inesperado: {header_size}")

        ranges = [(dir_hash_offset, dir_hash_size), (dir_meta_offset, dir_meta_size),
                  (file_hash_offset, file_hash_size), (file_meta_offset, file_meta_size)]
        end = 40
        for start, length in ranges:
            if start < end or start + length > file_data_offset:
                raise RuntimeError("Tabelas RomFS sobrepostas ou fora dos limites.")
            end = start + length
        if file_data_offset > path.stat().st_size:
            raise RuntimeError("Dados RomFS fora dos limites.")
        f.seek(dir_meta_offset)
        dirs = f.read(dir_meta_size)

        f.seek(file_meta_offset)
        files = f.read(file_meta_size)

    dir_paths = {}
    visited_dirs = set()

    def visit_dir(offset, parent_path, parent_offset=0):
        if offset == INVALID:
            return
        if offset in visited_dirs:
            raise RuntimeError("Ciclo ou diretório compartilhado no RomFS.")
        if offset + 24 > len(dirs):
            raise RuntimeError("Metadata de diretório fora dos limites.")

        visited_dirs.add(offset)
        parent, sibling, child_dir, child_file, hash_next, name_size = \
            struct.unpack_from("<6I", dirs, offset)

        if parent != parent_offset or name_size % 2:
            raise RuntimeError("Pai ou nome de diretório inválido.")
        ns = offset + 24
        ne = ns + name_size
        if ne > len(dirs):
            raise RuntimeError("Nome de diretório fora dos limites.")

        name = dirs[ns:ne].decode("utf-16-le")
        if parent_path and name:
            current = parent_path + "/" + name
        elif name:
            current = name
        else:
            current = parent_path

        dir_paths[offset] = current

        if child_dir != INVALID:
            visit_dir(child_dir, current, offset)
        if sibling != INVALID:
            visit_dir(sibling, parent_path, parent_offset)

    visit_dir(0, "")

    result = {}

    for dir_offset, directory in dir_paths.items():
        if dir_offset + 24 > len(dirs):
            continue

        child_file = struct.unpack_from("<I", dirs, dir_offset + 12)[0]
        current = child_file
        seen = set()

        while current != INVALID:
            if current in seen:
                raise RuntimeError("Loop na metadata de arquivos.")
            seen.add(current)

            if current + 32 > len(files):
                raise RuntimeError("Metadata de arquivo fora dos limites.")

            parent, sibling, payload_rel, size, hash_next, name_size = \
                struct.unpack_from("<IIQQII", files, current)

            if name_size % 2 or not name_size:
                raise RuntimeError("Nome de arquivo inválido.")
            ns = current + 32
            ne = ns + name_size
            if ne > len(files):
                raise RuntimeError("Nome de arquivo fora dos limites.")

            name = files[ns:ne].decode("utf-16-le")
            full = f"{directory}/{name}" if directory else name

            if parent != dir_offset or full.lower() in result:
                raise RuntimeError("Pai inválido ou caminho duplicado no RomFS.")
            if file_data_offset + payload_rel + size > path.stat().st_size:
                raise RuntimeError("Payload fora dos limites do RomFS.")
            result[full.lower()] = {
                "path": full,
                "name": name,
                "meta_rel": current,
                "meta_abs": file_meta_offset + current,
                "payload_rel": payload_rel,
                "absolute": file_data_offset + payload_rel,
                "size": size,
            }

            current = sibling

    header = {
        "file_meta_offset": file_meta_offset,
        "file_data_offset": file_data_offset,
    }
    return header, result


# ============================================================
# Conversão QM USA -> EUR
# ============================================================

def convert_qm_us_to_eu(data):
    if len(data) < 16:
        raise RuntimeError("us.qm pequeno demais.")

    if data[:4] != b"QM\x00\x00":
        raise RuntimeError("Magic do us.qm inválido.")

    version = struct.unpack_from("<I", data, 4)[0]
    records = struct.unpack_from("<I", data, 8)[0]

    if version != 4:
        raise RuntimeError(f"Versão QM inesperada: {version}")

    if records != EXPECTED_QM_RECORDS:
        raise RuntimeError(
            f"Quantidade de registros QM inesperada: {records} "
            f"(esperado {EXPECTED_QM_RECORDS})"
        )

    record_size = 96
    minimum = 16 + records * record_size
    if len(data) < minimum:
        raise RuntimeError("Estrutura do us.qm está truncada.")

    out = bytearray(data)

    # Conversão já validada no teste anterior:
    # slot EUR destino <- slot USA origem
    slot_map = (
        (2, 1),  # EUR English <- USA English
        (4, 5),  # EUR French  <- USA French
        (6, 7),  # EUR Spanish <- USA Spanish
    )

    for index in range(records):
        entry = 16 + index * record_size
        for dest, origin in slot_map:
            src = entry + 16 + origin * 8
            dst = entry + 16 + dest * 8
            out[dst:dst + 8] = data[src:src + 8]

    if EXPECTED_CLEAN_ROMFS_SHA256 == BETA_ROMFS_SHA256:
        out = normalize_ptbr_tildes(data, out)
    return bytes(out)


# ============================================================
# Tradução: coleta e mapeamento
# ============================================================

def map_translation_path(rel):
    p = rel.as_posix()

    if p == "message/us/us.qm":
        return "message/eu/eu.qm", "qm"

    if p.startswith("message/us/"):
        return "message/eu/" + p[len("message/us/"):], "raw"

    if p.startswith("misc/us/"):
        return "misc/eu/" + p[len("misc/us/"):], "raw"

    return p, "raw"


def collect_translation():
    if not TRAD_ROOT.exists():
        raise RuntimeError(
            "Pasta da tradução completa não encontrada:\n"
            f"{TRAD_ROOT}"
        )

    items = []

    for p in sorted(TRAD_ROOT.rglob("*"), key=lambda x: x.as_posix().lower()):
        if not p.is_file():
            continue

        rel = p.relative_to(TRAD_ROOT)
        posix = rel.as_posix()

        # scene/fazer contém cópias dos recursos originais/base.
        if posix.startswith("scene/fazer/"):
            continue

        target, kind = map_translation_path(rel)
        items.append({
            "source": p,
            "source_rel": posix,
            "target": target,
            "kind": kind,
        })

    if len(items) != EXPECTED_TRANSLATION_FILES:
        raise RuntimeError(
            f"Foram encontrados {len(items)} arquivos reais da tradução, "
            f"mas esta V4 espera exatamente {EXPECTED_TRANSLATION_FILES}.\n\n"
            "A instalação foi cancelada para evitar aplicar um pacote incompleto "
            "ou diferente do que analisamos."
        )

    qm_items = [x for x in items if x["kind"] == "qm"]
    if len(qm_items) != 1:
        raise RuntimeError(f"Esperava exatamente 1 us.qm; encontrados: {len(qm_items)}")

    qm_hash = sha256_file(qm_items[0]["source"])
    if qm_hash.lower() != EXPECTED_US_QM_SHA256:
        raise RuntimeError(
            "O us.qm não corresponde ao arquivo da tradução v1.2 que testamos.\n"
            f"SHA encontrado: {qm_hash}\n"
            f"SHA esperado  : {EXPECTED_US_QM_SHA256}"
        )

    return items


def collect_v4_items():
    """112 recursos base + cópia dos 14 CTXB para menu/02_EU_ENGLISH."""
    items = collect_translation()
    extra = []
    for name in MENU_SLOT_EU_FILES:
        source = TRAD_ROOT / "menu" / "01_US_ENGLISH" / name
        if not source.exists():
            raise RuntimeError(f"CTXB PT-BR ausente para o slot EUR: {source}")
        extra.append({
            "source": source,
            "source_rel": f"menu/01_US_ENGLISH/{name} [espelho slot 02_EU_ENGLISH]",
            "target": f"menu/02_EU_ENGLISH/{name}",
            "kind": "raw",
        })
    result = items + extra
    if len(result) != EXPECTED_V4_PATCH_OPERATIONS:
        raise RuntimeError(
            f"Quantidade interna de operações V4 inesperada: {len(result)} "
            f"(esperado {EXPECTED_V4_PATCH_OPERATIONS})."
        )
    return result


def fnv1a64(data):
    h = 0xCBF29CE484222325
    for b in data:
        h ^= b
        h = (h * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return h


def locate_o3tu():
    root = BASE / "data" / "mods" / "topscreen"
    found = list(root.rglob("atlas_overrides.o3tu")) if root.exists() else []
    if len(found) != 1:
        raise RuntimeError(
            "A V4 precisa do TopScreen compatível instalado.\n"
            f"Esperava exatamente 1 atlas_overrides.o3tu em {root}; "
            f"encontrei {len(found)}."
        )
    return found[0]


def parse_o3tu_entries(raw):
    if len(raw) < 16 or raw[:4] != b"O3TU":
        raise RuntimeError("atlas_overrides.o3tu inválido.")
    version, count, profiles = struct.unpack_from("<III", raw, 4)
    if version != 2:
        raise RuntimeError(f"Versão O3TU não suportada pela V4: {version}")
    off = 16
    entries = []
    for i in range(count):
        if off + 20 > len(raw):
            raise RuntimeError("O3TU truncado na tabela de overrides.")
        original, replacement, size = struct.unpack_from("<QQI", raw, off)
        header_off = off
        off += 20
        if off + size > len(raw):
            raise RuntimeError("O3TU truncado em payload de override.")
        payload = raw[off:off + size]
        entries.append({
            "index": i,
            "original": original,
            "replacement": replacement,
            "size": size,
            "header_off": header_off,
            "payload_off": off,
            "payload": payload,
        })
        off += size
    return version, count, profiles, entries


# Confirmed empty override index in TriAevum v0.8.0-beta.1.1 on 2026-10-19.
# Its profile payload remains verified structurally; never treat other empty packs
# as safe without a verified exact file identity.
KNOWN_EMPTY_TOPSCREEN_O3TU_SHA256 = frozenset({
    '13ace413af089274e7fa3907f2b5adda73ab199d0624572a260127cb545d7c22',
})


def inspect_topscreen(pack):
    raw = pack.read_bytes()
    version, count, profiles, entries = parse_o3tu_entries(raw)
    validate_o3tu_complete(raw, entries, profiles)
    if count == 0 and hashlib.sha256(raw).hexdigest() in KNOWN_EMPTY_TOPSCREEN_O3TU_SHA256:
        # There is no menu_top override and consequently no O3TU hash gate
        # to change. This pack must be preserved bit-for-bit.
        return raw, None
    candidates = [
        e for e in entries
        if e["original"] in (O3TU_OLD_ORIGINAL_HASH, O3TU_PTBR_ORIGINAL_HASH)
    ]
    if len(candidates) != 1:
        # No mutation: provide a compact, deterministic fingerprint so that a
        # newer/different Forge texture pack can be classified safely.
        # Do not infer identity from payload size or entry ordering.
        fingerprint = hashlib.sha256(raw).hexdigest()
        known_replacements = [e for e in entries
                              if e["replacement"] == O3TU_ENGLISH_REPLACEMENT_HASH]
        entry_preview = ", ".join(
            f"#{e['index']}:original={e['original']:016x}/replacement={e['replacement']:016x}"
            for e in entries[:12]
        ) or "(nenhuma entrada)"
        raise RuntimeError(
            "TopScreen O3TU diferente da variante validada; "
            "nenhuma entrada menu_top identificada unicamente. "
            "A instalação foi cancelada sem alterar arquivos.\\n"
            f"Arquivo: {pack}\\n"
            f"SHA-256: {fingerprint}\\n"
            f"Overrides: {count}; candidatos por original: {len(candidates)}; "
            f"candidatos pelo replacement inglês: {len(known_replacements)}\\n"
            f"Primeiras entradas: {entry_preview}\\n"
            "Envie apenas este trecho do log para identificar a variante. "
            "Não substitua o O3TU manualmente nem ignore a validação."
        )
    e = candidates[0]
    calculated = fnv1a64(e["payload"])
    if e["replacement"] != O3TU_ENGLISH_REPLACEMENT_HASH:
        raise RuntimeError(
            "O ReplacementHash da entrada menu_top foi modificado por algum "
            "teste/versão diferente.\n"
            f"Encontrado: {e['replacement']:016x}\n"
            f"Esperado  : {O3TU_ENGLISH_REPLACEMENT_HASH:016x}\n\n"
            "Restaure o atlas_overrides.o3tu original antes da instalação V4."
        )
    if calculated != O3TU_ENGLISH_REPLACEMENT_HASH:
        raise RuntimeError(
            "O payload replacement inglês do TopScreen foi modificado.\n"
            f"FNV calculado: {calculated:016x}\n"
            f"Esperado     : {O3TU_ENGLISH_REPLACEMENT_HASH:016x}\n\n"
            "Restaure o atlas_overrides.o3tu original antes da instalação V4."
        )
    return raw, e


def patch_topscreen_to_ptbr(pack, backup):
    raw, e = inspect_topscreen(pack)
    if e["original"] == O3TU_PTBR_ORIGINAL_HASH:
        return "already_ptbr", e["index"]

    if backup.exists():
        raise RuntimeError(
            f"Backup TopScreen V4 já existe e não será sobrescrito:\n{backup}"
        )
    shutil.copy2(pack, backup)
    validate_copy(pack, backup)

    out = bytearray(raw)
    struct.pack_into("<Q", out, e["header_off"], O3TU_PTBR_ORIGINAL_HASH)
    temp = pack.with_name(pack.name + ".v4.tmp")
    temp.write_bytes(out)

    _, ve = inspect_topscreen(temp)
    if ve["original"] != O3TU_PTBR_ORIGINAL_HASH:
        temp.unlink(missing_ok=True)
        raise RuntimeError("Falha ao validar hash-gate PT-BR no O3TU temporário.")

    os.replace(temp, pack)
    return "patched", e["index"]


def prepare_payload(item):
    data = item["source"].read_bytes()
    if item["kind"] == "qm":
        data = convert_qm_us_to_eu(data)
    return data


# ============================================================
# Backups / estado
# ============================================================

def backup_paths(romfs, manifest):
    return (
        romfs.with_name(romfs.name + ".antes_traducao_ptbr_v4"),
        manifest.with_name(manifest.name + ".antes_traducao_ptbr_v4"),
    )


def read_marker():
    if not MARKER.exists():
        return None
    try:
        return load_json(MARKER)
    except Exception:
        return None


def is_v4_installed():
    m = read_marker()
    return bool(m and m.get("format") == MARKER_FORMAT)


# ============================================================
# Instalação
# ============================================================

def install():
    preflight(require_payload=True)
    print("\n[1/9] Localizando TriAevum...")
    manifest, manifest_data, romfs = locate_runtime()
    romfs_backup, manifest_backup = backup_paths(romfs, manifest)

    if is_v4_installed():
        raise RuntimeError(
            "A tradução completa V4 já está marcada como instalada.\n"
            "Restaure o original antes de instalar novamente."
        )

    print(f"RomFS: {romfs}")
    print(f"Manifesto: {manifest}")

    o3tu = locate_o3tu()
    o3tu_backup = o3tu.with_name(o3tu.name + ".antes_traducao_ptbr_v4")
    _, o3tu_entry = inspect_topscreen(o3tu)
    if o3tu_entry is not None and o3tu_entry["original"] != O3TU_OLD_ORIGINAL_HASH:
        raise RuntimeError(
            "O TopScreen já está com o hash-gate PT-BR de um teste anterior.\n"
            "Para o primeiro teste oficial da V4, restaure o O3TU original "
            "(OriginalHash b216011e1f24749c) e rode novamente.\n\n"
            "Isso garante que a V4 consiga criar um backup original e também "
            "desinstalar tudo de forma totalmente reversível."
        )
    print(f"TopScreen: {o3tu}")
    if o3tu_entry is None:
        print('[OK] O3TU beta.1.1 sem overrides; manteremos esse arquivo intocado.')
    else:
        print(
            f"[OK] O3TU v2 / entrada #{o3tu_entry['index']} / "
            f"OriginalHash={o3tu_entry['original']:016x}"
        )

    print("\n[2/9] Verificando base limpa...")
    size = romfs.stat().st_size
    if size != EXPECTED_CLEAN_ROMFS_SIZE:
        raise RuntimeError(
            f"O RomFS atual tem {human(size)} bytes.\n"
            f"A base limpa esperada tem {human(EXPECTED_CLEAN_ROMFS_SIZE)} bytes.\n\n"
            "Use a restauração do instalador anterior ou desta V4 antes de continuar."
        )

    print("Calculando SHA-256 do RomFS original...")
    clean_hash = sha256_file(romfs)
    if clean_hash.lower() != EXPECTED_CLEAN_ROMFS_SHA256:
        raise RuntimeError(
            "O RomFS tem o tamanho esperado, mas o SHA-256 é diferente da base "
            "que analisamos.\n\n"
            f"Encontrado: {clean_hash}\n"
            f"Esperado  : {EXPECTED_CLEAN_ROMFS_SHA256}\n\n"
            "A instalação foi cancelada por segurança."
        )
    print("[OK] RomFS original confirmado.")

    print("\n[3/9] Analisando tradução completa...")
    items = collect_v4_items()
    print(f"[OK] 112 recursos reais + 14 espelhos de menu EUR = {len(items)} operações.")

    print("\n[4/9] Indexando RomFS e validando destinos...")
    header, index = index_romfs(romfs)
    print(f"Arquivos indexados: {len(index)}")

    missing = []
    for item in items:
        if item["target"].lower() not in index:
            missing.append((item["source_rel"], item["target"]))

    if missing:
        text = "\n".join(f"  {a} -> {b}" for a, b in missing[:30])
        raise RuntimeError(
            f"{len(missing)} destino(s) não existem no RomFS:\n{text}\n\n"
            "Nada foi modificado."
        )

    print(f"[OK] Todos os {len(items)} destinos existem.")

    print("\n[5/9] Preparando backups V4...")
    if romfs_backup.exists() or manifest_backup.exists():
        raise RuntimeError(
            "Já existem backups V4:\n"
            f"{romfs_backup}\n{manifest_backup}\n\n"
            "Não vou sobrescrevê-los automaticamente. "
            "Verifique/remova backups antigos somente se tiver certeza de que não são necessários."
        )

    if o3tu_backup.exists():
        raise RuntimeError("Backup O3TU existente; não será sobrescrito.")
    shutil.copy2(romfs, romfs_backup)
    shutil.copy2(manifest, manifest_backup)
    validate_copy(romfs, romfs_backup)
    validate_copy(manifest, manifest_backup)
    print("[OK] Backups criados e validados.")

    temp_romfs = romfs.with_name(romfs.name + ".v4.tmp")

    try:
        print("\n[6/9] Construindo RomFS traduzido...")
        if temp_romfs.exists():
            temp_romfs.unlink()

        shutil.copy2(romfs_backup, temp_romfs)

        patch_records = []
        same_size_count = 0
        relocated_count = 0

        with temp_romfs.open("r+b") as f:
            for n, item in enumerate(items, 1):
                info = index[item["target"].lower()]
                payload = prepare_payload(item)
                payload_hash = hashlib.sha256(payload).hexdigest()

                if len(payload) == info["size"]:
                    # Mesmo tamanho: substituição direta.
                    f.seek(info["absolute"])
                    f.write(payload)
                    final_abs = info["absolute"]
                    final_rel = info["payload_rel"]
                    same_size_count += 1
                    mode = "in-place"
                else:
                    # Tamanho diferente: anexa no fim, alinhado a 16 bytes,
                    # e atualiza payload_relative + size na metadata.
                    f.seek(0, os.SEEK_END)
                    eof = f.tell()
                    aligned = align_up(eof, 16)

                    if aligned > eof:
                        f.write(b"\x00" * (aligned - eof))

                    final_abs = aligned
                    final_rel = final_abs - header["file_data_offset"]

                    f.write(payload)

                    # File record <IIQQII>
                    # +8  = payload_relative (Q)
                    # +16 = size (Q)
                    f.seek(info["meta_abs"] + 8)
                    f.write(struct.pack("<Q", final_rel))
                    f.seek(info["meta_abs"] + 16)
                    f.write(struct.pack("<Q", len(payload)))

                    relocated_count += 1
                    mode = "relocated"

                patch_records.append({
                    "source": item["source_rel"],
                    "target": item["target"],
                    "kind": item["kind"],
                    "mode": mode,
                    "size": len(payload),
                    "sha256": payload_hash,
                    "absolute": final_abs,
                    "relative": final_rel,
                    "meta_abs": info["meta_abs"],
                })

                print(
                    f"[{n:03d}/{len(items)}] {item['source_rel']} "
                    f"-> {item['target']} [{mode}]"
                )

            f.flush()
            os.fsync(f.fileno())

        final_size = temp_romfs.stat().st_size

        print(f"\n[7/9] Validando os {len(items)} payloads...")
        # Reindexa o arquivo final para conferir metadata e payloads.
        final_header, final_index = index_romfs(temp_romfs)

        with temp_romfs.open("rb") as f:
            for n, rec in enumerate(patch_records, 1):
                info = final_index.get(rec["target"].lower())
                if not info:
                    raise RuntimeError(
                        f"Falha de validação: destino desapareceu: {rec['target']}"
                    )

                if info["size"] != rec["size"]:
                    raise RuntimeError(
                        f"Falha de validação em {rec['target']}: "
                        f"metadata size={info['size']}, esperado={rec['size']}"
                    )

                if info["absolute"] + info["size"] > final_size:
                    raise RuntimeError(
                        f"Falha de validação: payload fora do RomFS: {rec['target']}"
                    )

                actual_hash = sha256_region(f, info["absolute"], info["size"])
                if actual_hash != rec["sha256"]:
                    raise RuntimeError(
                        f"Falha de validação SHA-256: {rec['target']}\n"
                        f"Encontrado: {actual_hash}\n"
                        f"Esperado  : {rec['sha256']}"
                    )

                if n % 10 == 0 or n == len(patch_records):
                    print(f"Validado: {n}/{len(patch_records)}")

        print("[OK] Todos os payloads foram validados.")

        # Atualiza manifesto em memória.
        new_manifest = load_json(manifest_backup)
        source = new_manifest.setdefault("source", {})
        source["romfs_image_file_size"] = final_size
        source["romfs_service_size"] = final_size

        temp_manifest = manifest.with_name(manifest.name + ".v4.tmp")
        save_json(temp_manifest, new_manifest)

        print("\n[8/9] Ativando RomFS traduzido...")
        os.replace(temp_romfs, romfs)
        os.replace(temp_manifest, manifest)

        print("\n[9/9] Aplicando compatibilidade TopScreen PT-BR...")
        if o3tu_entry is None:
            o3tu_mode, o3tu_index = 'no_overrides', None
            # Validate identity again to guard replacement between preflight
            # and commit. Zero-entry packs are not modified or backed up.
            _, final_o3tu_entry = inspect_topscreen(o3tu)
            if final_o3tu_entry is not None:
                raise RuntimeError('O3TU alterado durante instalação; operação cancelada.')
            print('[OK] O3TU sem overrides preservado sem alterações.')
        else:
            o3tu_mode, o3tu_index = patch_topscreen_to_ptbr(o3tu, o3tu_backup)
            print(
                f"[OK] TopScreen entrada #{o3tu_index}: "
                + ("hash-gate PT-BR aplicado." if o3tu_mode == "patched"
                   else "hash-gate PT-BR já estava aplicado.")
            )

        final_romfs_hash = sha256_file(romfs)

        marker = {
            "format": MARKER_FORMAT,
            "installed_at_local": time.strftime("%Y-%m-%d %H:%M:%S"),
            "translation_files": 112,
            "font_policy": "preserve_native_hd_normalized_tildes" if EXPECTED_CLEAN_ROMFS_SHA256 == BETA_ROMFS_SHA256 else "legacy_translation",
            "menu_eu_mirrors": 14,
            "patch_operations": len(items),
            "ignored_scene_fazer": 85,
            "topscreen_o3tu": str(o3tu),
            "topscreen_backup": str(o3tu_backup) if o3tu_backup.exists() else None,
            "topscreen_original_hash_ptbr": f"{O3TU_PTBR_ORIGINAL_HASH:016x}" if o3tu_index is not None else None,
            "topscreen_entry": o3tu_index,
            "topscreen_mode": o3tu_mode,
            "same_size_replacements": same_size_count,
            "relocated_replacements": relocated_count,
            "original_romfs_size": EXPECTED_CLEAN_ROMFS_SIZE,
            "original_romfs_sha256": EXPECTED_CLEAN_ROMFS_SHA256,
            "installed_romfs_size": final_size,
            "installed_romfs_sha256": final_romfs_hash,
            "romfs_path": str(romfs),
            "manifest_path": str(manifest),
            "romfs_backup": str(romfs_backup),
            "manifest_backup": str(manifest_backup),
            "resources": [
                {
                    "source": r["source"],
                    "target": r["target"],
                    "kind": r["kind"],
                    "mode": r["mode"],
                    "size": r["size"],
                    "sha256": r["sha256"],
                }
                for r in patch_records
            ],
        }
        save_json(MARKER, marker)

        print("\n" + "=" * 72)
        print("TRADUÇÃO COMPLETA INSTALADA COM SUCESSO")
        print("=" * 72)
        print("Recursos base       : 112")
        print("Espelhos menu EUR   : 14")
        print(f"Operações RomFS     : {len(items)}")
        print("TopScreen hash-gate : " + (f"{O3TU_PTBR_ORIGINAL_HASH:016x}" if o3tu_index is not None else "não aplicável (zero overrides)"))
        print(f"Mesmo tamanho       : {same_size_count}")
        print(f"Realocados          : {relocated_count}")
        print(f"RomFS original      : {human(EXPECTED_CLEAN_ROMFS_SIZE)} bytes")
        print(f"RomFS traduzido     : {human(final_size)} bytes")
        print(f"SHA final           : {final_romfs_hash}")
        print("\nAgora inicie o jogo e teste menus, imagens, cenas, áudio e textos.")

    except Exception:
        # O RomFS ativo ainda deve ser original até os.replace final.
        # Se a troca final ocorreu mas algo posterior falhou, restaura backups.
        try:
            if romfs.exists() and sha256_file(romfs) != EXPECTED_CLEAN_ROMFS_SHA256:
                if romfs_backup.exists():
                    shutil.copy2(romfs_backup, romfs)
                if manifest_backup.exists():
                    shutil.copy2(manifest_backup, manifest)
        except Exception:
            pass

        try:
            if 'o3tu_backup' in locals() and o3tu_backup.exists() and 'o3tu' in locals():
                shutil.copy2(o3tu_backup, o3tu)
        except Exception:
            pass

        try:
            if temp_romfs.exists():
                temp_romfs.unlink()
        except Exception:
            pass

        temp_manifest = manifest.with_name(manifest.name + ".v4.tmp")
        try:
            if temp_manifest.exists():
                temp_manifest.unlink()
        except Exception:
            pass

        raise


# ============================================================
# Restauração
# ============================================================

def restore():
    manifest, manifest_data, romfs = locate_runtime()
    romfs_backup, manifest_backup = backup_paths(romfs, manifest)
    o3tu = locate_o3tu()
    o3tu_backup = o3tu.with_name(o3tu.name + ".antes_traducao_ptbr_v4")

    if not romfs_backup.exists() or not manifest_backup.exists():
        raise RuntimeError(
            "Backups V4 completos não foram encontrados.\n\n"
            f"RomFS backup: {romfs_backup}\n"
            f"Manifest backup: {manifest_backup}"
        )

    print("\nValidando backup do RomFS...")
    size = romfs_backup.stat().st_size
    digest = sha256_file(romfs_backup)

    if size != EXPECTED_CLEAN_ROMFS_SIZE or digest.lower() != EXPECTED_CLEAN_ROMFS_SHA256:
        raise RuntimeError(
            "O backup V4 do RomFS não corresponde à base original conhecida.\n"
            "Restauração cancelada."
        )

    print("[OK] Backup original confirmado.")
    print("Restaurando...")

    shutil.copy2(romfs_backup, romfs)
    shutil.copy2(manifest_backup, manifest)
    if o3tu_backup.exists():
        shutil.copy2(o3tu_backup, o3tu)

    restored_manifest = load_json(manifest)
    source = restored_manifest.get("source", {})

    if (
        source.get("romfs_image_file_size") != EXPECTED_CLEAN_ROMFS_SIZE
        or source.get("romfs_service_size") != EXPECTED_CLEAN_ROMFS_SIZE
    ):
        raise RuntimeError(
            "O manifesto restaurado não possui os tamanhos originais esperados."
        )

    if MARKER.exists():
        MARKER.unlink()

    # Remove os backups V4 somente depois de uma restauração validada.
    romfs_backup.unlink()
    manifest_backup.unlink()
    if o3tu_backup.exists():
        o3tu_backup.unlink()

    print("\n[OK] Arquivos originais restaurados.")
    print("Os backups V4 (RomFS/manifest/TopScreen) foram removidos após a restauração.")


# ============================================================
# Status
# ============================================================

def status():
    manifest, manifest_data, romfs = locate_runtime()
    size = romfs.stat().st_size
    marker = read_marker()

    print("\n" + "=" * 72)
    print("STATUS")
    print("=" * 72)
    print(f"RomFS: {romfs}")
    print(f"Tamanho atual: {human(size)} bytes")

    if marker and marker.get("format") == MARKER_FORMAT:
        print("\nEstado: TRADUÇÃO PT-BR V4 + TOPSCREEN INSTALADA")
        print(f"Recursos base: {marker.get('translation_files')}")
        print(f"Espelhos menu EUR: {marker.get('menu_eu_mirrors')}")
        print(f"Operações: {marker.get('patch_operations')}")
        print(f"Realocados: {marker.get('relocated_replacements')}")
        print(f"SHA registrado: {marker.get('installed_romfs_sha256')}")
    elif size == EXPECTED_CLEAN_ROMFS_SIZE:
        print("\nEstado aparente: ROMFS ORIGINAL / NÃO INSTALADO")
        print("Use a opção de instalação para validar também o SHA-256.")
    else:
        print("\nEstado: ROMFS MODIFICADO, mas sem marcador V4.")
        print("Não instale por cima deste estado.")


# ============================================================
# Menu
# ============================================================

def main():
    while True:
        print("\n" + "=" * 72)
        print(APP_NAME)
        print("=" * 72)
        print("1 - Instalar Tradução PT-BR OoT3D V4")
        print("2 - Desinstalar V4 / restaurar original")
        print("3 - Status")
        print("4 - Sair")

        choice = input("\nEscolha: ").strip()

        if choice == "1":
            try:
                install()
            except Exception as e:
                print("\n" + "=" * 72)
                print("INSTALAÇÃO CANCELADA / FALHOU")
                print("=" * 72)
                print(e)
            pause()

        elif choice == "2":
            try:
                restore()
            except Exception as e:
                print("\n" + "=" * 72)
                print("RESTAURAÇÃO CANCELADA / FALHOU")
                print("=" * 72)
                print(e)
            pause()

        elif choice == "3":
            try:
                status()
            except Exception as e:
                print("\nErro ao obter status:")
                print(e)
            pause()

        elif choice == "4":
            break

        else:
            print("\nOpção inválida.")



# Experimental compatibility checks. Public V4 and release v1.0.0 are unchanged.
KNOWN_BASES = {
    '011c0b6933f3932c704ff1c6ab562023f407c2929661a6d54ecea1ca81072f99': 'alpha.2c',
    'dae620379c805e96a6187c212dc2b177cf5fdb0c184d526a06ebaeeaa481aa56': 'beta.1 / beta.1c (base local validada)',
}


def contained(path):
    path = path.resolve()
    if not path.is_relative_to(BASE.resolve()):
        raise RuntimeError(f'Caminho fora da instalação: {path}')
    return path


_legacy_locate_runtime = locate_runtime


def locate_runtime():
    manifest, data, romfs = _legacy_locate_runtime()
    contained(manifest)
    contained(romfs)
    launch = load_json(LAUNCH)
    if launch.get('format') != 'oot3d_native_game_launch_profile_v1':
        raise RuntimeError('Formato launch desconhecido.')
    if data.get('format') != 'oot3d_native_process_manifest_v1':
        raise RuntimeError('Formato manifesto desconhecido.')
    source = data['source']
    if source.get('romfs_service_offset') != 0:
        raise RuntimeError('RomFS precisa ser Level-3 com service offset zero.')
    if any(source.get(k) != romfs.stat().st_size for k in
           ('romfs_image_file_size', 'romfs_service_size')):
        raise RuntimeError('Tamanhos do manifesto e RomFS divergentes.')
    return manifest, data, romfs


def locate_o3tu():
    args = load_json(LAUNCH).get('arguments', [])
    if args.count('--topscreen-texture-overrides') != 1:
        raise RuntimeError('Override TopScreen ausente ou ambíguo no launch.')
    try:
        pack = contained(resolve_profile_path(args[args.index('--topscreen-texture-overrides') + 1]))
    except IndexError:
        raise RuntimeError('Caminho TopScreen ausente.')
    if not pack.is_file():
        raise RuntimeError('O3TU ativo não encontrado.')
    return pack


def validate_copy(source, backup):
    if source.stat().st_size != backup.stat().st_size or sha256_file(source) != sha256_file(backup):
        raise RuntimeError(f'Backup não confere: {backup}')


def validate_o3tu_complete(raw, entries, profiles):
    originals = set()
    for e in entries:
        if e['original'] in originals or fnv1a64(e['payload']) != e['replacement']:
            raise RuntimeError('O3TU override duplicado ou ReplacementHash inválido.')
        originals.add(e['original'])
    off = entries[-1]['payload_off'] + entries[-1]['size'] if entries else 16
    names = set()
    for _ in range(profiles):
        if off + 24 > len(raw):
            raise RuntimeError('Perfil O3TU truncado.')
        ns, width, height, fmt, size, digest = struct.unpack_from('<IHHB3xIQ', raw, off)
        off += 24
        if not ns or not width or not height or off + ns + size > len(raw):
            raise RuntimeError('Perfil O3TU inválido.')
        name = raw[off:off+ns].decode('utf-8')
        off += ns
        if '\0' in name or name in names or fnv1a64(raw[off:off+size]) != digest:
            raise RuntimeError('Nome ou hash do perfil O3TU inválido.')
        names.add(name)
        off += size
    if off != len(raw):
        raise RuntimeError('Dados extras no O3TU.')


def menu_texture(data):
    # TriAevum v0.8 builder hashes native encoded payload after 0x48-byte CTXB header.
    if len(data) != 262216 or data[:4] != b'ctxb':
        raise RuntimeError('Estrutura menu_top CTXB inesperada.')
    if struct.unpack_from('<I', data, 4)[0] != len(data):
        raise RuntimeError('Tamanho declarado CTXB inválido.')
    return data[0x48:]


def normalize_ptbr_tildes(original, converted):
    # This exact translation uses German umlaut codepoints as Portuguese tilde
    # aliases. Only its USA-English message spans are changed, never QM tables
    # or the French/Spanish payloads. All UTF-8 substitutions keep byte length.
    if hashlib.sha256(original).hexdigest() != EXPECTED_US_QM_SHA256:
        raise RuntimeError('QM desconhecido para normalização dos aliases PT-BR.')
    out = bytearray(converted)
    table_end = 16 + EXPECTED_QM_RECORDS * 96
    spans = set()
    other_spans = set()
    for index in range(EXPECTED_QM_RECORDS):
        entry = 16 + index * 96 + 16
        for slot in (1, 5, 7):
            offset, size = struct.unpack_from('<II', original, entry + slot * 8)
            if not size:
                continue
            if offset < table_end or offset + size > len(original):
                raise RuntimeError('Texto QM fora dos limites.')
            (spans if slot == 1 else other_spans).add((offset, offset + size))
    ordered = sorted(spans)
    for previous, current in zip(ordered, ordered[1:]):
        if previous[1] > current[0]:
            raise RuntimeError('Textos PT-BR QM sobrepostos.')
    for start, end in ordered:
        if any(start < other_end and other_start < end for other_start, other_end in other_spans):
            raise RuntimeError('Texto PT-BR compartilha bytes com outro idioma.')
        payload = original[start:end]
        for before, after in (('ä', 'ã'), ('ö', 'õ'), ('Ä', 'Ã'), ('Ö', 'Õ')):
            payload = payload.replace(before.encode('utf-8'), after.encode('utf-8'))
        if len(payload) != end - start:
            raise RuntimeError('Normalização alterou tamanho QM.')
        out[start:end] = payload
    print('[OK] Aliases ä/ö/Ä/Ö dos textos PT-BR normalizados para ã/õ/Ã/Õ; fonte HD preservada.')
    return out


BETA_ROMFS_SHA256 = 'dae620379c805e96a6187c212dc2b177cf5fdb0c184d526a06ebaeeaa481aa56'
HD_FONT_PACK_SHA256 = '1c49f6d817e9e6a6aed3a47143ad7cba0f0b9cf4f7a5441c9cf99a4c7d8e588e'
PRESERVED_NATIVE_FONT = None
_legacy_prepare_payload = prepare_payload


def prepare_payload(item):
    if (EXPECTED_CLEAN_ROMFS_SHA256 == BETA_ROMFS_SHA256
            and item['target'].lower() == 'message/eu/ltn16.qbf'):
        if PRESERVED_NATIVE_FONT is None:
            raise RuntimeError('Fonte HD não validada; execute preflight antes de preparar payloads.')
        translated = _legacy_prepare_payload(item)
        if len(translated) != len(PRESERVED_NATIVE_FONT) or translated[:1608] != PRESERVED_NATIVE_FONT[:1608]:
            raise RuntimeError('Mapeamento ou métricas QBF PT-BR diferentes; preservação da fonte recusada.')
        return PRESERVED_NATIVE_FONT
    return _legacy_prepare_payload(item)


OPEN_FONT_PACK_TO_INSTALL = None
OPEN_FONT_PACK_SHA256 = None


def _bundled_noto_font():
    """Locate only a deliberately bundled OFL font; never fetch at runtime."""
    import sys
    resource_root = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))
    folder = resource_root / 'open-font'
    found = [p for p in folder.glob('*.ttf') if p.is_file()]
    if len(found) != 1 or not (folder / 'OFL.txt').is_file():
        return None
    return found[0]


def _local_noto_pack(native):
    """Build temporary archive, then retain bytes until install is committed."""
    import sys
    import tempfile
    folder = Path(__file__).resolve().parent
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))
    from prepare_open_font_pack import prepare_local_font_pack
    with tempfile.TemporaryDirectory(prefix='ptbr-noto-qbf-') as temporary:
        output = Path(temporary) / 'font_coverage.zip'
        prepare_local_font_pack(native, _bundled_noto_font(), output)
        return output.read_bytes()


def validate_hd_font(romfs, index):
    import io
    import zipfile
    global PRESERVED_NATIVE_FONT, OPEN_FONT_PACK_TO_INSTALL, OPEN_FONT_PACK_SHA256
    PRESERVED_NATIVE_FONT = None
    OPEN_FONT_PACK_TO_INSTALL = None
    OPEN_FONT_PACK_SHA256 = None
    if EXPECTED_CLEAN_ROMFS_SHA256 != BETA_ROMFS_SHA256:
        return
    info = index['message/eu/ltn16.qbf']
    with romfs.open('rb') as f:
        f.seek(info['absolute'])
        native = f.read(info['size'])
    if native[:4] != b'QBF1' or len(native) != 28232 or struct.unpack_from('<H', native, 4)[0] != 199:
        raise RuntimeError('QBF original inesperada.')
    pack = contained(locate_o3tu().parent / 'font_coverage.zip')
    noto = _bundled_noto_font()
    if noto is not None:
        # Prefer independently generated OFL coverage even when old SingleScreen
        # packs are present. Preflight is read-only: persist only after install.
        content = _local_noto_pack(native)
        OPEN_FONT_PACK_TO_INSTALL = content
        OPEN_FONT_PACK_SHA256 = hashlib.sha256(content).hexdigest()
    elif pack.is_file() and sha256_file(pack) == HD_FONT_PACK_SHA256:
        content = pack.read_bytes()
    elif not pack.is_file():
        raise RuntimeError(f'Pacote de fonte HD não encontrado: {pack}. Nenhum arquivo alterado.')
    else:
        raise RuntimeError(f'Pacote de fonte HD incompatível: {pack}. SHA-256 não corresponde à base validada. Nenhum arquivo alterado.')
    with zipfile.ZipFile(io.BytesIO(content)) as z:
        manifest = json.loads(z.read('manifest.json'))
        if manifest.get('format') != 'oot3d_qbf_coverage_v1':
            raise RuntimeError('Manifesto da fonte HD inválido.')
        fonts = [x for x in manifest['fonts'] if x['romfs_path'] == 'message/eu/ltn16.qbf']
        if len(fonts) != 1:
            raise RuntimeError('Fonte HD EUR ausente ou ambígua.')
        font = fonts[0]
        coverage = z.read(font['coverage_file'])
        if (z.read(font['native_file']) != native
                or hashlib.sha256(native).hexdigest() != font['native_sha256']
                or hashlib.sha256(coverage).hexdigest() != font['coverage_sha256']
                or coverage[:4] != b'QBF1' or coverage[13:15] != bytes((64, 64))):
            raise RuntimeError('Identidade ou cobertura da fonte HD inválida.')
        native_codes = {struct.unpack_from('<H', native, 16 + i * 8)[0] for i in range(199)}
        hd_codes = {struct.unpack_from('<H', coverage, 16 + i * 8)[0]
                    for i in range(struct.unpack_from('<H', coverage, 4)[0])}
        if not native_codes <= hd_codes:
            raise RuntimeError('Cobertura HD incompleta.')
        if not {ord(ch) for ch in 'áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ'} <= hd_codes:
            raise RuntimeError('Acentos PT-BR ausentes na fonte HD.')
    PRESERVED_NATIVE_FONT = native
    print('[OK] Fonte original EUR preservada; cobertura HD Noto Sans validada.' if noto
          else '[OK] Fonte original EUR preservada; pacote HD legado validado.')


def preflight(require_payload=False):
    global EXPECTED_CLEAN_ROMFS_SHA256
    manifest, md, romfs = locate_runtime()
    digest = sha256_file(romfs)
    if romfs.stat().st_size != EXPECTED_CLEAN_ROMFS_SIZE or digest not in KNOWN_BASES:
        raise RuntimeError(f'Base desconhecida: {digest}')
    EXPECTED_CLEAN_ROMFS_SHA256 = digest
    header, index = index_romfs(romfs)
    validate_hd_font(romfs, index)
    with romfs.open('rb') as f:
        info = index['menu/02_eu_english/menu_top_parts00.ctxb']
        f.seek(info['absolute'])
        menu = f.read(info['size'])
    original_hash = fnv1a64(menu_texture(menu))
    if original_hash != O3TU_OLD_ORIGINAL_HASH:
        raise RuntimeError(f'OriginalHash menu_top real não confere: {original_hash:016x}')
    raw, entry = inspect_topscreen(locate_o3tu())
    if entry is not None and (entry['original'] != original_hash or entry['size'] != len(menu_texture(menu))):
        raise RuntimeError('O3TU não corresponde à textura original do RomFS.')
    if entry is None:
        print('[OK] O3TU beta.1.1 sem entradas; compatibilidade menu_top via RomFS, sem alterar overrides.')
    missing = [name for name in MENU_SLOT_EU_FILES if ('menu/02_EU_ENGLISH/'+name).lower() not in index]
    if missing:
        raise RuntimeError(f'Menus EUR ausentes: {missing}')
    if require_payload:
        items = collect_v4_items()
        targets = set()
        for item in items:
            target = item['target'].lower()
            if target in targets or target not in index:
                raise RuntimeError(f'Destino ausente ou duplicado: {target}')
            targets.add(target)
            data = prepare_payload(item)  # Includes full QM validation before backup/writes.
            if target == 'menu/02_eu_english/menu_top_parts00.ctxb':
                if data[:0x48] != menu[:0x48] or fnv1a64(menu_texture(data)) != O3TU_PTBR_ORIGINAL_HASH:
                    raise RuntimeError('CTXB PT-BR não corresponde ao hash-gate V4.')
    print(f'[OK] Base {KNOWN_BASES[digest]}: {digest}; {len(index)} arquivos; O3TU integral validado.')
    return digest


def restore():
    global EXPECTED_CLEAN_ROMFS_SHA256
    manifest, md, romfs = locate_runtime()
    rb, mb = backup_paths(romfs, manifest)
    pack = locate_o3tu()
    pb = pack.with_name(pack.name + '.antes_traducao_ptbr_v4')
    if not rb.is_file() or not mb.is_file():
        raise RuntimeError('Backups RomFS/manifest obrigatórios para restauração.')
    _, current_o3tu_entry = inspect_topscreen(pack)
    if current_o3tu_entry is None:
        if pb.exists():
            raise RuntimeError('O3TU sem overrides possui backup inesperado; restauração recusada.')
    elif not pb.is_file():
        raise RuntimeError('Backup O3TU obrigatório para restauração da variante com overrides.')
    digest = sha256_file(rb)
    if digest not in KNOWN_BASES or rb.stat().st_size != EXPECTED_CLEAN_ROMFS_SIZE:
        raise RuntimeError('Backup RomFS desconhecido ou corrompido.')
    bm = load_json(mb)
    if bm.get('format') != md.get('format') or bm.get('source', {}).get('romfs_image_path') != md['source']['romfs_image_path']:
        raise RuntimeError('Manifesto backup não corresponde à instalação.')
    if any(bm['source'].get(k) != EXPECTED_CLEAN_ROMFS_SIZE for k in ('romfs_image_file_size','romfs_service_size')) or bm['source'].get('romfs_service_offset') != 0:
        raise RuntimeError('Manifesto backup inválido.')
    if current_o3tu_entry is not None:
        _, e = inspect_topscreen(pb)
        if e is None or e['original'] != O3TU_OLD_ORIGINAL_HASH:
            raise RuntimeError('Backup O3TU não é original.')
    EXPECTED_CLEAN_ROMFS_SHA256 = digest
    # Retain backups until all three restored files have been verified.
    shutil.copy2(rb, romfs)
    shutil.copy2(mb, manifest)
    if current_o3tu_entry is not None:
        shutil.copy2(pb, pack)
    pairs = [(romfs, rb), (manifest, mb)]
    if current_o3tu_entry is not None:
        pairs.append((pack, pb))
    for original, backup in pairs:
        validate_copy(original, backup)
    preflight()
    MARKER.unlink(missing_ok=True)
    for backup in (rb, mb, pb):
        backup.unlink(missing_ok=True)
    print('[OK] Original restaurado e validado.')


def diagnostic():
    if is_v4_installed():
        status()
        return
    preflight()
    if TRAD_ROOT is None or not TRAD_ROOT.is_dir():
        print('[PENDENTE] Payload TraducaoCompleta ausente; aplicação dos 126 recursos não validada.')
    else:
        preflight(require_payload=True)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Tradução alpha.2c / beta.1 / beta.1c')
    parser.add_argument('--root', type=Path, default=BASE)
    parser.add_argument('--payload', type=Path)
    parser.add_argument('--action', choices=('diagnostic', 'install', 'restore'), default='diagnostic')
    options = parser.parse_args()
    BASE = options.root.resolve()
    LAUNCH = BASE / 'TriAevum.launch.json'
    MARKER = BASE / 'traducao_ptbr_v4_instalada.json'
    TRAD_ROOT = options.payload.resolve() if options.payload else BASE / 'TraducaoCompleta/citra/romfs'
    globals()[options.action]()


# Integracao experimental de cobertura Noto Sans com backup reversivel.
_install_before_noto = install
_restore_before_noto = restore


def install():
    """Install game translation first; publish new HD pack only after success."""
    _install_before_noto()
    if OPEN_FONT_PACK_TO_INSTALL is None:
        return
    import os
    import tempfile
    pack = contained(locate_o3tu().parent / 'font_coverage.zip')
    receipt = contained(pack.with_name('font_coverage.ptbr-noto.json'))
    if receipt.exists():
        raise RuntimeError('Recibo Noto Sans anterior existente; não sobrescrito.')
    old_backup = None
    if pack.exists():
        old_backup = contained(pack.with_name('font_coverage.ptbr-noto.backup.zip'))
        if old_backup.exists():
            raise RuntimeError('Backup da fonte HD anterior já existe.')
        shutil.copy2(pack, old_backup)
        validate_copy(pack, old_backup)
    temp = pack.with_name(pack.name + '.ptbr.tmp')
    try:
        temp.write_bytes(OPEN_FONT_PACK_TO_INSTALL)
        if sha256_file(temp) != OPEN_FONT_PACK_SHA256:
            raise RuntimeError('Falha ao gravar cobertura Noto Sans.')
        os.replace(temp, pack)
        receipt.write_text(json.dumps({
            'format': 'ptbr-noto-font-v1',
            'sha256': OPEN_FONT_PACK_SHA256,
            'had_original': old_backup is not None,
        }, indent=2), encoding='utf-8')
    finally:
        temp.unlink(missing_ok=True)
    print('[OK] Fonte HD Noto Sans instalada localmente; restauração disponível.')


def restore():
    """Restore original game and any replaced font pack when provenance matches."""
    pack = contained(locate_o3tu().parent / 'font_coverage.zip')
    receipt = contained(pack.with_name('font_coverage.ptbr-noto.json'))
    metadata = None
    if receipt.is_file():
        metadata = json.loads(receipt.read_text(encoding='utf-8'))
        if metadata.get('format') != 'ptbr-noto-font-v1' or not pack.is_file() or sha256_file(pack) != metadata.get('sha256'):
            raise RuntimeError('Fonte Noto Sans alterada externamente; restauração recusada.')
        if metadata.get('had_original') and not pack.with_name('font_coverage.ptbr-noto.backup.zip').is_file():
            raise RuntimeError('Backup anterior da fonte HD ausente.')
    _restore_before_noto()
    if metadata is not None:
        if metadata.get('had_original'):
            import os
            backup = contained(pack.with_name('font_coverage.ptbr-noto.backup.zip'))
            os.replace(backup, pack)
        else:
            pack.unlink()
        receipt.unlink()
        print('[OK] Pacote HD anterior restaurado (ou Noto Sans removida).')
