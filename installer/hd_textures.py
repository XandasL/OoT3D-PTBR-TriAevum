"""Optional, reversible HD extension. Never patches the ROM or original launcher."""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import struct
import subprocess
import tempfile
import uuid

HERE = Path(__file__).resolve().parent
RECEIPT = 'data/mods/ptbr-hd/installation.json'
EXE = 'TriAevum-PTBR-HD.exe'
PROFILE = 'TriAevum-PTBR-HD.launch.json'
CONFIG = 'data/config/TriAevum-PTBR-HD.json'
FORMAT = 'oot3d_ptbr_hd_install_v1'
DEPLOY_FORMAT = 'oot3d_ptbr_hd_runtime_deploy_v1'
SOURCE_DOWNLOAD = 'https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/download/1.2.1/OoT3D_PTBR_TriAevum_v1.2.1_Fontes-HD.zip'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def recipe():
    rules = read_json(HERE / 'hd-recipe.json')
    allowed = {EXE, 'amd_fidelityfx_vk.dll', 'nvngx_dlss.dll'}
    if rules.get('format') != 'oot3d_ptbr_hd_recipe_v1' or set(rules['runtime_files']) != allowed:
        raise RuntimeError('Receita HD desconhecida ou arquivos de runtime não autorizados.')
    for item in rules['aliases']:
        for name in (item['original'], item['translated']):
            if '/' in name or '\\' in name or not name.endswith('.png'):
                raise RuntimeError('Nome de alias inválido na receita HD.')
    return rules


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.ptbr-hd-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def encoded_json(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def canonical(path):
    # Normalize lexical '..' even if Windows cannot resolve a missing child.
    return Path(os.path.abspath(path)).resolve()


def bounded(root, relative):
    root = canonical(root)
    path = root / relative
    resolved = canonical(path)
    if path.is_symlink() or not resolved.is_relative_to(root) or resolved == root:
        raise RuntimeError(f'Caminho fora da pasta permitida: {relative}')
    return path


def assert_closed():
    if os.name != 'nt':
        raise RuntimeError('O componente HD foi validado somente no Windows x64.')
    result = subprocess.run(['tasklist', '/FO', 'CSV', '/NH'], capture_output=True,
                            text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
    for row in csv.reader(io.StringIO(result.stdout)):
        if row and row[0].lower().startswith('triaevum') and row[0].lower().endswith('.exe'):
            raise RuntimeError('Feche o jogo e o Forge antes de instalar ou remover o HD.')


def validate_base(root, rules):
    if digest(bounded(root, 'TriAevum.exe').read_bytes()) != rules['original_runtime_sha256']:
        raise RuntimeError('Runtime diferente do TriAevum 0.8 Windows validado; nada foi alterado.')
    for name, expected in rules['original_dependencies'].items():
        if digest(bounded(root, name).read_bytes()) != expected:
            raise RuntimeError(f'Dependência original diferente da validada: {name}')
    marker = read_json(bounded(root, 'traducao_ptbr_v4_instalada.json'))
    if (marker.get('format') != 'oot3d_ptbr_full_translation_install_v4' or
            marker.get('original_romfs_sha256') != rules['clean_romfs_sha256']):
        raise RuntimeError('Instale e valide a tradução para a base 0.8 antes do HD.')
    # The beta.1.1 compatibility path supports both a HD coverage font pack
    # and native-font tilde aliases. HD texture replacement is independent of
    # which of these two valid Portuguese-font modes is active.
    supported_font_policies = {
        'preserve_native_hd_normalized_tildes',
        'preserve_native_font_tilde_alias_patch',
    }
    if (marker.get('translation_files') != 112 or marker.get('menu_eu_mirrors') != 14 or
            marker.get('patch_operations') != 126 or
            marker.get('font_policy') not in supported_font_policies):
        raise RuntimeError('A tradução precisa estar completa e usar uma política de fonte PT-BR compatível com a base 0.8.')
    romfs = canonical(marker['romfs_path'])
    if not romfs.is_relative_to(canonical(root)) or not romfs.is_file():
        raise RuntimeError('O RomFS do recibo não pertence a esta instalação.')
    # Compare the full installed image before preparing any file mutation.
    hashed = hashlib.sha256()
    with romfs.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            hashed.update(block)
    if hashed.hexdigest() != marker.get('installed_romfs_sha256'):
        raise RuntimeError('O RomFS mudou depois da tradução; verifique o status primeiro.')


def validate_bundle(bundle, rules=None, *, require_sources=True):
    rules = rules or recipe()
    bundle = canonical(bundle)
    manifest = read_json(bundle / 'manifest.json')
    expected = rules['runtime_files']
    deploy = manifest.get('format') == DEPLOY_FORMAT
    if (manifest.get('format') not in ('oot3d_ptbr_hd_runtime_v1', DEPLOY_FORMAT) or
            manifest.get('files') != expected or (deploy and require_sources)):
        raise RuntimeError('O pacote do runtime HD não corresponde ao build validado.')
    for name, sha in expected.items():
        if digest(bounded(bundle, name).read_bytes()) != sha:
            raise RuntimeError(f'Arquivo do runtime HD corrompido: {name}')
    if deploy:
        if manifest.get('source_files') != rules['source_files'] or manifest.get('source_url') != SOURCE_DOWNLOAD:
            raise RuntimeError('Referência aos fontes correspondentes inválida.')
        allowed = set(expected) | {'manifest.json', 'LICENSE', 'THIRD_PARTY_NOTICES.md', 'SOURCE_OFFER.md'}
        if (bundle / 'source').exists() or any(p.relative_to(bundle).as_posix() not in allowed
                                               for p in bundle.rglob('*') if p.is_file()):
            raise RuntimeError('Arquivos extras no runtime de distribuição.')
    else:
        for name, sha in rules['source_files'].items():
            if digest(bounded(bundle, name).read_bytes()) != sha:
                raise RuntimeError(f'Código-fonte/patch do bundle HD diferente: {name}')
    for name in ('LICENSE', 'THIRD_PARTY_NOTICES.md', 'SOURCE_OFFER.md'):
        if not bounded(bundle, name).is_file():
            raise RuntimeError(f'Pacote HD incompleto: {name}')
    return bundle


def prepare_deploy_bundle(source, output, rules=None):
    rules = rules or recipe()
    source = validate_bundle(source, rules)
    output = canonical(output)
    if output.exists() and any(output.iterdir()):
        raise RuntimeError('Destino do runtime de distribuição precisa estar vazio.')
    output.mkdir(parents=True, exist_ok=True)
    for name in (*rules['runtime_files'], 'LICENSE', 'THIRD_PARTY_NOTICES.md'):
        bounded(output, name).write_bytes(bounded(source, name).read_bytes())
    (output / 'SOURCE_OFFER.md').write_text(
        'Corresponding source code and local patch are available at no charge:\n\n' + SOURCE_DOWNLOAD +
        '\n\nSource file hashes are recorded in manifest.json and the installer recipe.\n', encoding='utf-8')
    (output / 'manifest.json').write_bytes(encoded_json({
        'format': DEPLOY_FORMAT, 'files': rules['runtime_files'],
        'source_files': rules['source_files'], 'source_url': SOURCE_DOWNLOAD}))
    return validate_bundle(output, rules, require_sources=False)


def locate_pack(selected):
    selected = canonical(selected)
    candidates = [selected] if (selected / 'pack.json').is_file() else sorted(
        {p.parent for p in selected.rglob('pack.json')})
    if len(candidates) != 1:
        raise RuntimeError('Selecione a pasta de um único pacote de texturas (pack.json).')
    pack = candidates[0]
    options = read_json(pack / 'pack.json').get('options', {})
    if options.get('use_new_hash', True) is not False or options.get('flip_png_files') is not True:
        raise RuntimeError('Este componente exige o esquema legacy/flip do pacote 4K validado.')
    return pack


def repair_navi_hud(data, rules):
    """Compose only the missing Navi slot; never change the external source PNG."""
    from PIL import Image
    repair = rules['navi_repair']
    overlay_data = bounded(HERE, repair['overlay']).read_bytes()
    if digest(overlay_data) != repair['overlay_sha256']:
        raise RuntimeError('Recurso de correção da Navi alterado.')
    with Image.open(io.BytesIO(data)) as decoded:
        if list(decoded.size) != repair['image_size']:
            raise RuntimeError('Dimensões inesperadas no HUD da Navi.')
        image = decoded.convert('RGBA')
    x0, y0, x1, y1 = repair['box']
    if not (0 <= x0 < x1 <= image.width and 0 <= y0 < y1 <= image.height):
        raise RuntimeError('Retângulo de correção da Navi inválido.')
    with Image.open(io.BytesIO(overlay_data)) as decoded:
        overlay = decoded.convert('RGBA')
    if overlay.size != (x1-x0, y1-y0):
        overlay = overlay.resize((x1-x0, y1-y0), Image.Resampling.LANCZOS)
    image.paste(overlay, (x0, y0))
    out = io.BytesIO()
    image.save(out, format='PNG')
    return out.getvalue()


def navi_backup_key(rules):
    repair = rules.get('navi_repair')
    return ('pack', 'UI/PTBR_HASHES/' + repair['translated']) if repair else None


def plan_install(root, selected_pack, bundle):
    root = canonical(root)
    rules = recipe()
    validate_base(root, rules)
    bundle = validate_bundle(bundle, rules, require_sources=False)
    pack = locate_pack(selected_pack)
    for relative, expected in rules['pack_files'].items():
        if digest(bounded(pack, relative).read_bytes()) != expected:
            raise RuntimeError(f'O pacote não contém a imagem traduzida/TopScreen validada: {relative}')
    changes = []

    def add(scope, relative, data, keep=False):
        target = bounded(root if scope == 'install' else pack, relative)
        before = target.read_bytes() if target.is_file() else None
        if target.exists() and before is None:
            raise RuntimeError(f'O destino não é um arquivo: {target}')
        if before is not None and before != data and relative != CONFIG:
            repair = rules.get('navi_repair')
            known_navi = ((scope, relative) == navi_backup_key(rules) and
                          digest(before) == rules['pack_files']['UI/' + repair['source']])
            if not known_navi:
                raise RuntimeError(f'Arquivo existente difere; nada será sobrescrito: {target}')
        changes.append({'scope': scope, 'path': relative, 'data': data, 'before': before,
                        'keep': keep, 'preserve': before == data})

    for name in rules['runtime_files']:
        add('install', name, bounded(bundle, name).read_bytes())
    for item in rules['aliases']:
        source = bounded(pack, 'UI/' + item['original'])
        data = source.read_bytes()
        if len(data) < 33 or data[:8] != b'\x89PNG\r\n\x1a\n' or data[12:16] != b'IHDR':
            raise RuntimeError(f'PNG inválido: {source}')
        w, h = struct.unpack_from('>II', data, 16)
        nw, nh = item['native_size']
        if (w <= nw or h <= nh or w > 16384 or h > 16384 or
                w * nh != h * nw or w & (w - 1) or h & (h - 1)):
            raise RuntimeError(f'Resolução/aspecto inesperado: {source}')
        if rules.get('navi_repair', {}).get('source') == item['original']:
            data = repair_navi_hud(data, rules)
        add('pack', 'UI/PTBR_HASHES/' + item['translated'], data)
    profile = read_json(bounded(root, 'TriAevum.launch.json'))
    if profile.get('format') != 'oot3d_native_game_launch_profile_v1':
        raise RuntimeError('Perfil de lançamento desconhecido.')
    args = profile['arguments']
    if args.count('--config') != 1:
        raise RuntimeError('O perfil precisa de uma única opção --config para isolar as preferências HD.')
    index = args.index('--config')
    args[index + 1] = '${profile_dir}/' + CONFIG
    add('install', PROFILE, encoded_json(profile))
    own_config = bounded(root, CONFIG)
    config = read_json(own_config if own_config.is_file() else bounded(root, 'data/config/TriAevum.json'))
    azahar = config.setdefault('Graphics', {}).setdefault('TexturePacks', {}).setdefault('Azahar', {})
    azahar.update(LoadCustomTextures=True, LoadDirectory=str(pack))
    add('install', CONFIG, encoded_json(config), keep=True)
    return root, pack, changes


def validate_receipt(root):
    state = read_json(bounded(root, RECEIPT))
    rules = recipe()
    if state.get('format') != FORMAT or state.get('state') not in ('installing', 'installed'):
        raise RuntimeError('Recibo HD desconhecido; restauração cancelada.')
    pack = canonical(state['pack_root'])
    allowed = {('install', name) for name in rules['runtime_files']}
    allowed |= {('install', PROFILE), ('install', CONFIG)}
    allowed |= {('pack', 'UI/PTBR_HASHES/' + item['translated']) for item in rules['aliases']}
    transaction = state.get('transaction', '')
    if len(transaction) != 32 or any(c not in '0123456789abcdef' for c in transaction):
        raise RuntimeError('Identificador de transação HD inválido.')
    seen = set()
    for index, row in enumerate(state['files']):
        key = (row['scope'], row['path'])
        if key not in allowed or key in seen:
            raise RuntimeError('Caminho não autorizado ou duplicado no recibo HD.')
        seen.add(key)
        if row['keep'] != (key == ('install', CONFIG)) or row['preserve'] != (row['before_sha256'] == row['sha256']):
            raise RuntimeError('Política de propriedade inconsistente no recibo HD.')
        bounded(root if row['scope'] == 'install' else pack, row['path'])
        if row.get('backup'):
            backup = bounded(root, row['backup'])
            valid_owner = key == ('install', CONFIG)
            if key == navi_backup_key(rules):
                valid_owner = row['before_sha256'] == rules['pack_files']['UI/' + rules['navi_repair']['source']]
            if (not valid_owner or
                    row['backup'] != f'data/mods/ptbr-hd/backups/{transaction}/{index}.bin' or
                    digest(backup.read_bytes()) != row['before_sha256']):
                raise RuntimeError('Backup HD inválido.')
    if seen != allowed:
        raise RuntimeError('Recibo HD incompleto.')
    return state, pack


def _undo(root, installed_restore):
    state, pack = validate_receipt(root)
    for row in state['files']:
        if row['preserve'] or (installed_restore and row['keep']):
            continue
        target = bounded(root if row['scope'] == 'install' else pack, row['path'])
        if target.exists() and digest(target.read_bytes()) not in (row['sha256'], row.get('before_sha256')):
            raise RuntimeError(f'Arquivo mudou após a instalação; restauração cancelada: {target}')
    for row in reversed(state['files']):
        if row['preserve'] or (installed_restore and row['keep']):
            continue
        target = bounded(root if row['scope'] == 'install' else pack, row['path'])
        if row.get('backup'):
            atomic_write(target, bounded(root, row['backup']).read_bytes())
        else:
            target.unlink(missing_ok=True)
    bounded(root, RECEIPT).unlink()
    for row in state['files']:
        if row.get('backup'):
            try:
                bounded(root, row['backup']).unlink()
            except OSError:
                pass  # Restored state is already committed; harmless backup may remain.


def install(root, selected_pack, bundle, dry_run=False):
    if not dry_run:
        assert_closed()
    root = canonical(root)
    if bounded(root, RECEIPT).exists():
        state, _ = validate_receipt(root)
        if state['state'] == 'installing':
            raise RuntimeError('Instalação HD interrompida. Remova/restaure o HD antes de repetir.')
        raise RuntimeError('O HD já possui recibo. Remova-o antes de mudar o pacote.')
    root, pack, changes = plan_install(root, selected_pack, bundle)
    if dry_run:
        return {'files': len(changes), 'aliases': len(recipe()['aliases']), 'pack': str(pack)}
    state = {'format': FORMAT, 'state': 'installing', 'transaction': uuid.uuid4().hex,
             'pack_root': str(pack), 'files': []}
    for index, item in enumerate(changes):
        row = {k: item[k] for k in ('scope', 'path', 'keep', 'preserve')}
        row['sha256'] = digest(item['data'])
        row['before_sha256'] = digest(item['before']) if item['before'] is not None else None
        if item['before'] is not None and not item['preserve']:
            row['backup'] = f'data/mods/ptbr-hd/backups/{state["transaction"]}/{index}.bin'
            backup = bounded(root, row['backup'])
            if backup.exists():
                raise RuntimeError('Backup de outra instalação encontrado. Verifique antes de repetir.')
            atomic_write(backup, item['before'])
        state['files'].append(row)
    atomic_write(bounded(root, RECEIPT), encoded_json(state))
    try:
        for item in changes:
            if not item['preserve']:
                atomic_write(bounded(root if item['scope'] == 'install' else pack, item['path']), item['data'])
        for row in state['files']:
            target = bounded(root if row['scope'] == 'install' else pack, row['path'])
            if digest(target.read_bytes()) != row['sha256']:
                raise RuntimeError(f'Falha ao verificar a gravação: {target}')
        state['state'] = 'installed'
        atomic_write(bounded(root, RECEIPT), encoded_json(state))
    except Exception:
        _undo(root, installed_restore=False)
        raise
    return {'launcher': str(root / EXE), 'aliases': len(recipe()['aliases'])}


def restore(root):
    assert_closed()
    root = canonical(root)
    if not bounded(root, RECEIPT).exists():
        return False
    state, _ = validate_receipt(root)
    _undo(root, installed_restore=state['state'] == 'installed')
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--pack', type=Path)
    parser.add_argument('--runtime', type=Path)
    parser.add_argument('--action', choices=('check', 'install', 'restore'), default='check')
    options = parser.parse_args()
    if options.action == 'restore':
        print(restore(options.root))
    else:
        if not options.pack or not options.runtime:
            parser.error('--pack e --runtime são obrigatórios para check/install')
        print(install(options.root, options.pack, options.runtime, options.action == 'check'))
