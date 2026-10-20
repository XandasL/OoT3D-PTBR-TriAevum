"""Complete PT-BR translation with optional 128px coverage; no texture/runtime installation."""
from pathlib import Path
import hashlib
import importlib.util
import io
import json
import os
import shutil
import struct
import zipfile
import csv
import subprocess
import sys
import uuid

HERE = Path(__file__).resolve().parent
BASE = HERE
LAUNCH = BASE / 'TriAevum.launch.json'
TRAD_ROOT = BASE / 'TraducaoCompleta/citra/romfs'
MARKER = BASE / 'traducao_ptbr_textos.json'
FONT_MODE_OPTION = 'original'
CLEAN_SHA256 = 'dae620379c805e96a6187c212dc2b177cf5fdb0c184d526a06ebaeeaa481aa56'
FORMAT = 'oot3d_ptbr_texts_v1'


def module(name):
    spec = importlib.util.spec_from_file_location('ptbr_' + name, HERE / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


parser = module('Instalador_Traducao_PTBR_OoT3D_V4_compat_test')
fonts = module('font_mode')
transactions = module('transaction_guard')


def sha256_file(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write(path, data):
    transactions.durable_replace(path, data)


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode('utf-8')


def assert_closed():
    if sys.platform == 'win32':
        result = subprocess.run(['tasklist', '/FO', 'CSV', '/NH'], capture_output=True,
                                text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        names = {row[0].lower() for row in csv.reader(result.stdout.splitlines()) if row}
        busy = any(n.startswith(('triaevum', 'oot3d_native')) for n in names)
    else:
        result = subprocess.run(['ps', '-A', '-o', 'comm='], capture_output=True, text=True, check=True)
        busy = any(n.lower().startswith(('triaevum', 'oot3d_native')) for n in result.stdout.splitlines())
    if busy:
        raise RuntimeError('Feche o jogo e o TriAevum antes de instalar ou alterar a fonte.')


def contained(path):
    path = path.resolve()
    if not path.is_relative_to(BASE.resolve()):
        raise RuntimeError('Caminho fora da instalação: ' + str(path))
    return path


def profile_path(text):
    text = text.replace('\\', '/')
    for prefix in ('${runtime_dir}/', '${profile_dir}/'):
        if text.startswith(prefix):
            text = text[len(prefix):]
            break
    if '${' in text:
        raise RuntimeError('Variável de caminho desconhecida.')
    return contained(BASE / text)


def locate_runtime():
    launch = json.loads(LAUNCH.read_text(encoding='utf-8-sig'))
    if launch.get('format') != 'oot3d_native_game_launch_profile_v1':
        raise RuntimeError('Perfil de execução desconhecido.')
    args = launch['arguments']
    manifest = profile_path(args[args.index('--a32-process-manifest') + 1])
    data = json.loads(manifest.read_text(encoding='utf-8-sig'))
    if data.get('format') != 'oot3d_native_process_manifest_v1':
        raise RuntimeError('Manifesto desconhecido.')
    source = data['source']
    romfs = contained(manifest.parent / source['romfs_image_path'])
    if source.get('romfs_service_offset') != 0 or any(
            source.get(k) != romfs.stat().st_size
            for k in ('romfs_service_size', 'romfs_image_file_size')):
        raise RuntimeError('Tamanho ou offset do RomFS incompatível.')
    return manifest, data, romfs


def font_path():
    args = json.loads(LAUNCH.read_text(encoding='utf-8-sig'))['arguments']
    return profile_path(args[args.index('--topscreen-texture-overrides') + 1]).parent / 'font_coverage.zip'


def read_resource(romfs, name):
    _, index = parser.index_romfs(romfs)
    entry = index[name.lower()]
    with romfs.open('rb') as f:
        f.seek(entry['absolute'])
        return f.read(entry['size'])


def prepared_resources(native):
    parser.TRAD_ROOT = TRAD_ROOT
    parser.EXPECTED_CLEAN_ROMFS_SHA256 = parser.BETA_ROMFS_SHA256
    parser.PRESERVED_NATIVE_FONT = native
    expected = json.loads((HERE / 'payload-manifest.json').read_text(encoding='utf-8'))
    sources = parser.collect_translation()
    actual = {x['source_rel']: sha256_file(x['source']) for x in sources}
    if actual != expected:
        raise RuntimeError('Os 112 recursos da tradução não correspondem ao pacote validado.')
    return {x['target'].lower(): parser.prepare_payload(x) for x in parser.collect_v4_items()}


def make_font(native):
    assets = HERE / 'font-hd-128'
    contract = json.loads((assets / 'manifest.json').read_text(encoding='utf-8'))
    atlas = (assets / 'atlas.a4').read_bytes()
    end = 16 + int.from_bytes(native[4:6], 'little') * 8
    if (contract.get('format') != 'ptbr_font_128_atlas_v1'
            or contract.get('cell') != 128
            or digest(native) != contract['native_sha256']
            or digest(native[16:end]) != contract['directory_sha256']
            or digest(atlas) != contract['atlas_sha256']):
        raise RuntimeError('Fonte 128 ou fonte original incompatível.')
    coverage = native[:13] + bytes((128, 128, 2)) + native[16:end] + atlas
    if digest(coverage) != contract['coverage_sha256']:
        raise RuntimeError('Cobertura da fonte 128 inválida.')
    nh, ch = digest(native), digest(coverage)
    manifest = {'format': 'oot3d_qbf_coverage_v1', 'runtime_enabled': True,
                'minimum_output_height': 480, 'status': 'native_atlas_coverage_ready',
                'fonts': [{'romfs_path': 'message/eu/ltn16.qbf',
                           'native_file': 'native/' + nh + '.qbf',
                           'coverage_file': 'coverage/' + ch + '.qbf',
                           'native_sha256': nh, 'coverage_sha256': ch,
                           'logical_cell': [16, 16], 'coverage_cell': [128, 128],
                           'density': 8, 'fallback_code': int.from_bytes(native[8:10], 'little'),
                           'replacement_metric_differences': 0,
                           'characters': [{'code': struct.unpack_from('<H', native, 16+i*8)[0],
                                           'native_glyph': struct.unpack_from('<H', native, 18+i*8)[0],
                                           'coverage_glyph': struct.unpack_from('<H', native, 18+i*8)[0],
                                           'native_metrics_hex': native[20+i*8:24+i*8].hex()}
                                          for i in range((end-16)//8)]}]}
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_STORED) as z:
        z.writestr(zipfile.ZipInfo('native/' + nh + '.qbf'), native)
        z.writestr(zipfile.ZipInfo('coverage/' + ch + '.qbf'), coverage)
        z.writestr(zipfile.ZipInfo('manifest.json'), encoded(manifest))
    return output.getvalue()


def state():
    if not MARKER.exists():
        return None
    data = json.loads(MARKER.read_text(encoding='utf-8'))
    if data.get('format') != FORMAT:
        raise RuntimeError('Recibo de instalação desconhecido.')
    return data


def is_installed():
    return state() is not None


def locate_clean_romfs():
    receipt = state()
    if receipt:
        launch = json.loads((BASE / 'TriAevum.launch.json.antes_ptbr_textos').read_text(encoding='utf-8'))
        args = launch['arguments']
        manifest = profile_path(args[args.index('--a32-process-manifest')+1])
        data = json.loads(manifest.read_text(encoding='utf-8'))
        return contained(manifest.parent / data['source']['romfs_image_path'])
    return locate_runtime()[2]


def validate_installed():
    receipt = state()
    if receipt is None:
        raise RuntimeError('Tradução dos textos não instalada.')
    backup = BASE / 'TriAevum.launch.json.antes_ptbr_textos'
    if (sha256_file(LAUNCH) != receipt['launch_sha256']
            or sha256_file(backup) != receipt['backup_sha256']):
        raise RuntimeError('Perfil ou backup alterado após a instalação; nada foi substituído.')
    manifest, _, romfs = locate_runtime()
    if (sha256_file(manifest) != receipt['manifest_sha256']
            or sha256_file(romfs) != receipt['romfs_sha256']):
        raise RuntimeError('Dados instalados alterados; nada foi substituído.')
    fonts.read_state(font_path())
    return receipt


def set_font_mode(mode):
    transactions.refuse_pending(BASE)
    if mode not in ('original', 'hd'):
        raise ValueError('Modo de fonte inválido.')
    assert_closed()
    validate_installed()
    native = read_resource(locate_runtime()[2], 'message/eu/ltn16.qbf')
    record = {'format': 'oot3d_ptbr_v130_transaction_v1',
              'operation': 'change_font', 'phase': 'changing',
              'target_mode': mode, 'transaction_id': uuid.uuid4().hex, 'launch_sha256': sha256_file(LAUNCH)}
    journal = transactions.write_journal(BASE, record)
    result = fonts.choose(font_path(), mode, (lambda: make_font(native)) if mode == 'hd' else None)
    transactions.complete_journal(journal)
    print('[OK] Fonte ' + ('HD 128' if mode == 'hd' else 'original') + '; textos PT-BR preservados.')
    return result


def apply_translation(mode):
    """Recover a verified interrupted operation, then honor the current choice."""
    if mode not in ('original', 'hd'):
        raise ValueError('Modo de fonte inválido.')
    print('[INFO] Verificando operações anteriores...')
    print('[INFO] ' + recover())
    global FONT_MODE_OPTION
    FONT_MODE_OPTION = mode
    return install()


def install():
    transactions.refuse_pending(BASE)
    if FONT_MODE_OPTION not in ('original', 'hd'):
        raise ValueError('Modo de fonte inválido.')
    assert_closed()
    if is_installed():
        return set_font_mode(FONT_MODE_OPTION)
    if (BASE / 'traducao_ptbr_v4_instalada.json').exists():
        raise RuntimeError('Restaure a tradução antiga com seu instalador antes de migrar para esta versão.')
    original_manifest, data, clean = locate_runtime()
    if sha256_file(clean) != CLEAN_SHA256:
        raise RuntimeError('A instalação precisa usar a base original beta.1.1 validada.')
    native = read_resource(clean, 'message/eu/ltn16.qbf')
    resources = prepared_resources(native)
    hd = make_font(native) if FONT_MODE_OPTION == 'hd' else None
    pack = font_path()
    if fonts.read_state(pack) is not None:
        raise RuntimeError('Há uma fonte gerenciada por outra instalação; restaure-a antes de continuar.')
    backup = BASE / 'TriAevum.launch.json.antes_ptbr_textos'
    folder = contained(BASE / 'data/mods/ptbr-textos')
    if backup.exists() or folder.exists():
        raise RuntimeError('Arquivos de instalação anteriores encontrados; não serão sobrescritos.')
    original_launch = LAUNCH.read_bytes()
    journal_record = {'format': 'oot3d_ptbr_v130_transaction_v1',
                      'operation': 'install', 'phase': 'preparing',
                      'original_launch_sha256': digest(original_launch),
                      'clean_romfs_sha256': CLEAN_SHA256,
                      'transaction_id': uuid.uuid4().hex, 'font_mode': FONT_MODE_OPTION,
                      'font_before_sha256': fonts.file_hash(pack)}
    journal = transactions.write_journal(BASE, journal_record)
    try:
        write(backup, original_launch)
        _checkpoint('install_backup')
        folder.mkdir(parents=True)
        _checkpoint('install_copy_start')
        output = folder / 'romfs.bin'
        shutil.copyfile(clean, output)
        _checkpoint('install_copy_end')
        header, index = parser.index_romfs(clean)
        if not set(resources) <= set(index):
            raise RuntimeError('Recursos da tradução ausentes da base.')
        with output.open('r+b') as f:
            for name, payload in resources.items():
                entry = index[name.lower()]
                if len(payload) == entry['size']:
                    f.seek(entry['absolute']); f.write(payload)
                else:
                    f.seek(0, 2); end = f.tell(); position = (end+15) & ~15
                    f.write(bytes(position-end)); f.write(payload)
                    f.seek(entry['meta_abs']+8)
                    f.write(struct.pack('<QQ', position-header['file_data_offset'], len(payload)))
        # Verify all translation payloads and preserve every unrelated resource.
        _, updated = parser.index_romfs(output)
        with clean.open('rb') as a, output.open('rb') as b:
            for name, before in index.items():
                after = updated[name]
                a.seek(before['absolute']); b.seek(after['absolute'])
                expected = resources[name] if name in resources else a.read(before['size'])
                if b.read(after['size']) != expected:
                    raise RuntimeError('Recurso divergente: ' + name)
        # Ensure translated bytes reach disk before exposing this RomFS in the launch profile.
        with output.open('r+b') as translated_file:
            os.fsync(translated_file.fileno())
        transactions.sync_directory(folder)
        for key in ('code_bin_path', 'exheader_path'):
            path = contained(original_manifest.parent / data['source'][key])
            data['source'][key] = os.path.relpath(path, folder).replace('\\', '/')
        data['source'].update(romfs_image_path='romfs.bin', romfs_image_file_size=output.stat().st_size,
                              romfs_service_size=output.stat().st_size)
        data['source_path_scopes'] = {key: 'relative' for key in ('code_bin_path', 'exheader_path', 'romfs_image_path')}
        manifest = folder / 'process-manifest.json'
        write(manifest, encoded(data))
        _checkpoint('install_manifest')
        launch = json.loads(original_launch)
        args = launch['arguments']
        args[args.index('--a32-process-manifest')+1] = '${profile_dir}/data/mods/ptbr-textos/process-manifest.json'
        # Stage receipt before switching launch; pending journal prevents false success.
        receipt_contents = encoded({'format': FORMAT, 'launch_sha256': digest(encoded(launch)),
                              'backup_sha256': digest(original_launch),
                              'romfs_sha256': sha256_file(output), 'manifest_sha256': sha256_file(manifest),
                              'resource_sha256': {name: digest(payload) for name, payload in resources.items()}})
        journal_record['phase'] = 'PREPARED'
        journal_record['launch'] = launch
        journal_record['receipt'] = json.loads(receipt_contents)
        journal_record['expected_launch_sha256'] = digest(encoded(launch))
        journal_record['translated_romfs_sha256'] = sha256_file(output)
        transactions.update_journal(journal, journal_record)
        _checkpoint('install_prepared')
        fonts.choose(pack, FONT_MODE_OPTION, (lambda: hd) if hd else None)
        _checkpoint('install_font')
        journal_record['phase'] = 'COMMITTING'
        transactions.update_journal(journal, journal_record)
        _checkpoint('install_before_launch')
        if sha256_file(LAUNCH) != digest(original_launch):
            raise transactions.PendingTransaction('Perfil alterado durante a instalação.')
        write(LAUNCH, encoded(launch))
        _checkpoint('install_after_launch')
        # The receipt is committed only after activation; the journal remains until then.
        write(MARKER, receipt_contents)
        _checkpoint('install_receipt')
        validate_installed()
        journal_record['phase'] = 'COMMITTED'
        transactions.update_journal(journal, journal_record)
        _checkpoint('install_committed')
        finish_transaction(journal_record)
    except Exception:
        # If anything fails, leave the durable journal and all recovery evidence intact.
        # This avoids a second failure in cleanup destroying user data or backups.
        raise
    print('[OK] Tradução completa instalada, incluindo texturas originais PT-BR; configurações gráficas preservadas.')


def _checkpoint(name):
    """Crash injection hook for subprocess tests."""


def finish_transaction(record):
    identity = record.get('transaction_id')
    if not isinstance(identity,str) or len(identity)!=32 or any(c not in '0123456789abcdef' for c in identity):
        raise transactions.PendingTransaction('Identidade de transação inválida.')
    archive = contained(BASE/'data/mods/ptbr-recovery'/identity)
    archive.mkdir(parents=True,exist_ok=True)
    write(archive/'journal.json',encoded(record))
    transactions.complete_journal(BASE/'traducao_ptbr_v130.pending.json')


def _original_runtime(launch_bytes):
    args=json.loads(launch_bytes)['arguments']
    manifest=profile_path(args[args.index('--a32-process-manifest')+1])
    document=json.loads(manifest.read_text(encoding='utf-8'))
    clean=contained(manifest.parent/document['source']['romfs_image_path'])
    if sha256_file(clean)!=CLEAN_SHA256:
        raise transactions.PendingTransaction('RomFS original alterado; recuperação recusada.')
    return clean


def recover():
    assert_closed()
    record=transactions.pending(BASE)
    if record is None:
        transactions.refuse_pending(BASE)
        # A font journal can outlive a completed main journal.
        fonts.recover(font_path())
        return 'Nenhuma transação principal pendente.'
    journal=BASE/'traducao_ptbr_v130.pending.json'
    operation=record.get('operation')
    if operation=='change_font':
        if sha256_file(LAUNCH)!=record['launch_sha256']:
            raise transactions.PendingTransaction('Perfil alterado por terceiros.')
        fonts.recover(font_path())
        native=read_resource(locate_runtime()[2],'message/eu/ltn16.qbf')
        mode=record['target_mode']
        fonts.choose(font_path(),mode,(lambda:make_font(native)) if mode=='hd' else None)
        finish_transaction(record)
        return 'Troca de fonte recuperada.'
    backup=BASE/'TriAevum.launch.json.antes_ptbr_textos'
    if operation=='install':
        current=sha256_file(LAUNCH)
        original_hash=record['original_launch_sha256']
        expected=record.get('expected_launch_sha256')
        if current not in {original_hash,expected}:
            raise transactions.PendingTransaction('Perfil alterado por terceiros; recuperação recusada.')
        if record['phase']=='preparing':
            # Activation and font mutation have not started. Preserve incomplete
            # output as evidence, never overwrite or delete unknown user content.
            if current!=original_hash or fonts.file_hash(font_path())!=record['font_before_sha256']:
                raise transactions.PendingTransaction('Estado original alterado; revisão manual necessária.')
            _original_runtime(LAUNCH.read_bytes())
            if MARKER.exists():raise transactions.PendingTransaction('Recibo inesperado; revisão manual necessária.')
            if backup.exists() and sha256_file(backup)!=original_hash:
                raise transactions.PendingTransaction('Backup original alterado.')
            identity=record['transaction_id']
            archive=contained(BASE/'data/mods/ptbr-recovery'/identity)
            archive.mkdir(parents=True,exist_ok=True)
            folder=contained(BASE/'data/mods/ptbr-textos')
            if folder.exists():
                allowed={'romfs.bin','process-manifest.json','process-manifest.json.ptbr-write.tmp'}
                if any(x.name not in allowed or not x.is_file() for x in folder.iterdir()):
                    raise transactions.PendingTransaction('Arquivos desconhecidos no staging; revisão necessária.')
                target=contained(archive/'interrupted-staging')
                if target.exists():raise transactions.PendingTransaction('Destino de recuperação já existe.')
                folder.rename(target);transactions.sync_directory(folder.parent)
            if backup.exists():
                target=contained(archive/'original-launch.json')
                if target.exists():raise transactions.PendingTransaction('Backup de recuperação já existe.')
                backup.rename(target);transactions.sync_directory(backup.parent)
            record['phase']='ABORTED_ORIGINAL_PRESERVED'
            finish_transaction(record)
            return 'Perfil original preservado; dados incompletos arquivados para auditoria.'
        receipt=record['receipt'];launch=record['launch']
        if digest(encoded(launch))!=expected or receipt.get('launch_sha256')!=expected:
            raise transactions.PendingTransaction('Jornal de recuperação divergente.')
        if not backup.is_file() or sha256_file(backup)!=original_hash:
            raise transactions.PendingTransaction('Backup original ausente ou alterado.')
        _original_runtime(backup.read_bytes())
        folder=contained(BASE/'data/mods/ptbr-textos')
        if (sha256_file(folder/'romfs.bin')!=receipt['romfs_sha256'] or
            sha256_file(folder/'process-manifest.json')!=receipt['manifest_sha256']):
            raise transactions.PendingTransaction('Dados traduzidos alterados; recuperação recusada.')
        if MARKER.exists() and MARKER.read_bytes()!=encoded(receipt):
            raise transactions.PendingTransaction('Recibo alterado por terceiros.')
        fonts.recover(font_path())
        native=read_resource(folder/'romfs.bin','message/eu/ltn16.qbf');mode=record['font_mode']
        fonts.choose(font_path(),mode,(lambda:make_font(native)) if mode=='hd' else None)
        if sha256_file(LAUNCH) not in {original_hash,expected}:
            raise transactions.PendingTransaction('Perfil alterado durante recuperação.')
        if sha256_file(LAUNCH)!=expected:write(LAUNCH,encoded(launch))
        if MARKER.exists() and MARKER.read_bytes()!=encoded(receipt):
            raise transactions.PendingTransaction('Recibo alterado por terceiros.')
        if not MARKER.exists():write(MARKER,encoded(receipt))
        validate_installed();record['phase']='COMMITTED';finish_transaction(record)
        return 'Instalação verificada e recuperada.'
    if operation=='restore':
        return _finish_restore(record)
    raise transactions.PendingTransaction('Operação de recuperação desconhecida.')


def _finish_restore(record):
    original=record['original_launch'].encode('utf-8')
    receipt=record['receipt']
    original_hash=record['original_launch_sha256']
    if digest(original)!=original_hash or sha256_file(LAUNCH) not in {original_hash,receipt['launch_sha256']}:
        raise transactions.PendingTransaction('Perfil alterado; restauração recusada.')
    _original_runtime(original)
    folder=contained(BASE/'data/mods/ptbr-textos')
    expected={folder/'romfs.bin':receipt['romfs_sha256'],folder/'process-manifest.json':receipt['manifest_sha256'],
              MARKER:record['receipt_file_sha256'],BASE/'TriAevum.launch.json.antes_ptbr_textos':original_hash}
    # Validate every deletion before deleting any artifact. Missing files are
    # permitted after an interrupted cleanup, but foreign bytes never are.
    if folder.exists() and any(p not in expected for p in folder.iterdir()):
        raise transactions.PendingTransaction('Arquivos desconhecidos na instalação; restauração recusada.')
    for path,sha in expected.items():
        if path.exists() and sha256_file(path)!=sha:
            raise transactions.PendingTransaction('Artefato alterado por terceiros: '+str(path))
    pack=font_path()
    if sha256_file(LAUNCH) not in {original_hash,receipt['launch_sha256']}:
        raise transactions.PendingTransaction('Perfil alterado durante restauração.')
    if sha256_file(LAUNCH)!=original_hash:write(LAUNCH,original)
    _checkpoint('restore_profile')
    journal=BASE/'traducao_ptbr_v130.pending.json'
    record['phase']='ORIGINAL_PROFILE_ACTIVE';transactions.update_journal(journal,record)
    fonts.recover(pack);fonts.restore_previous(pack)
    _checkpoint('restore_font')
    if fonts.file_hash(pack)!=record['original_font_sha256']:
        raise transactions.PendingTransaction('Fonte anterior não confirmada; backups preservados.')
    _original_runtime(LAUNCH.read_bytes())
    record['phase']='CLEANUP';transactions.update_journal(journal,record)
    for path in expected:
        if path.exists():
            path.unlink();transactions.sync_directory(path.parent)
        _checkpoint('restore_remove_'+path.name)
    if folder.exists():folder.rmdir();transactions.sync_directory(folder.parent)
    record['phase']='RESTORED';finish_transaction(record)
    return 'Perfil e fonte anteriores restaurados; saves e packs preservados.'


def apply_restore():
    print('[INFO] ' + recover())
    if is_installed():
        return restore()
    _original_runtime(LAUNCH.read_bytes())
    fonts.read_state(font_path())
    return 'Perfil original verificado; nenhuma tradução ativa para remover.'


def restore():
    transactions.refuse_pending(BASE);assert_closed()
    receipt=validate_installed();pack=font_path();font_state=fonts.read_state(pack)
    if font_state and font_state['had_original']:
        original_font=fonts.file_hash(fonts.paths(pack)[1])
    elif font_state:original_font=None
    else:original_font=fonts.file_hash(pack)
    backup=BASE/'TriAevum.launch.json.antes_ptbr_textos';original=backup.read_bytes()
    record={'format':'oot3d_ptbr_v130_transaction_v1','operation':'restore','phase':'RESTORING',
            'transaction_id':uuid.uuid4().hex,'receipt':receipt,'receipt_file_sha256':sha256_file(MARKER),'original_launch':original.decode('utf-8'),
            'original_launch_sha256':digest(original),'original_font_sha256':original_font}
    transactions.write_journal(BASE,record)
    _checkpoint('restore_intent')
    print('[OK] '+_finish_restore(record))


def diagnostic():
    if transactions.pending(BASE) is not None:
        print('[INFO] Operação interrompida detectada. Clique em Instalar / aplicar fonte ou Restaurar original para recuperar automaticamente.')
        return
    transactions.refuse_pending(BASE)
    fonts.read_state(font_path())
    if not is_installed() and ((BASE/'TriAevum.launch.json.antes_ptbr_textos').exists() or
                              (BASE/'data/mods/ptbr-textos').exists()):
        raise transactions.PendingTransaction('Backup ou staging órfão; preserve os arquivos e revise a recuperação.')
    if is_installed():
        validate_installed()
        font_state = fonts.read_state(font_path())
        print('[OK] Tradução completa instalada. Fonte: ' + (font_state['mode'] if font_state else 'original'))
    else:
        print('Base original: ' + ('validada' if sha256_file(locate_runtime()[2]) == CLEAN_SHA256 else 'incompatível'))
