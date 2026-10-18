"""Build native Windows/Linux installers; never publishes a release."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import shutil
import struct
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
VERSION = '1.2.1'
SOURCE_URL = 'https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/download/v1.0.0/OoT3D_PTBR_TriAevum_v1.0.zip'
SOURCE_SHA256 = '7bdcb391d4ae746d456c1bcb853371bd8be1bb9a3b9e63311aab1b487b300f7b'


def extract_payload(source_zip):
    if hashlib.sha256(source_zip.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise RuntimeError('ZIP de referência não corresponde à release validada.')
    with zipfile.ZipFile(source_zip) as z:
        names = [n for n in z.namelist() if n.endswith('.exe')]
        if len(names) != 1:
            raise RuntimeError('Executável de referência ausente ou ambíguo.')
        raw = z.read(names[0])
    pos = raw.rfind(b'MEI\x0c\x0b\x0a\x0b\x0e')
    if pos < 0 or pos + 88 > len(raw):
        raise RuntimeError('CArchive inválido.')
    _, total, toc_offset, toc_size, _, _ = struct.unpack_from('!8sIIII64s', raw, pos)
    start = pos + 88 - total
    off = start + toc_offset
    end = off + toc_size
    if start < 0 or off < start or end > pos:
        raise RuntimeError('Tabela CArchive fora dos limites.')
    dest_root = ROOT / 'test-input'
    seen = set()
    while off < end:
        if off + 18 > end:
            raise RuntimeError('Registro CArchive truncado.')
        length, position, compressed, size, flag, kind = struct.unpack_from('!IIIIBc', raw, off)
        if length < 18 or off + length > end:
            raise RuntimeError('Registro CArchive inválido.')
        name = raw[off + 18:off + length].split(b'\0')[0].decode().replace('\\', '/')
        if name.startswith('TraducaoCompleta/'):
            dest = (dest_root / name).resolve()
            if not dest.is_relative_to(dest_root.resolve()) or name in seen or size > 32 * 1024 * 1024:
                raise RuntimeError('Payload inseguro ou duplicado.')
            if start + position < start or start + position + compressed > pos:
                raise RuntimeError('Payload CArchive fora dos limites.')
            data = raw[start + position:start + position + compressed]
            if flag:
                data = zlib.decompress(data)
            if len(data) != size:
                raise RuntimeError('Payload CArchive truncado.')
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            seen.add(name)
        off += length
    if off != end or len(seen) != 112:
        raise RuntimeError('Esperava exatamente 112 arquivos de tradução.')
    return dest_root / 'TraducaoCompleta/citra/romfs'


def validate_payload(payload):
    expected = json.loads((ROOT / 'installer/payload-manifest.json').read_text(encoding='utf-8'))
    actual = {p.relative_to(payload).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in payload.rglob('*') if p.is_file() and not p.relative_to(payload).as_posix().startswith('scene/fazer/')}
    if actual != expected:
        raise RuntimeError('Payload da tradução não corresponde aos 112 recursos validados.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--payload', type=Path)
    parser.add_argument('--source-zip', type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--hd-runtime', type=Path, help='Bundle HD validado; somente Windows x64')
    args = parser.parse_args()
    hd_runtime_mode = None
    if args.hd_runtime:
        if sys.platform != 'win32':
            raise RuntimeError('O runtime HD opcional foi validado somente no Windows x64.')
        from hd_textures import validate_bundle, recipe
        hd_runtime_mode = recipe().get('runtime_mode', 'bundled')
        validate_bundle(args.hd_runtime)
    if args.payload:
        payload = args.payload.resolve()
    else:
        source = args.source_zip or ROOT / 'build/reference-v1.0.0.zip'
        if not source.exists():
            source.parent.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(SOURCE_URL, source)
        payload = extract_payload(source)
    validate_payload(payload)
    print('Payload validado: 112 arquivos; nenhuma execução do EXE antigo.')
    if args.prepare_only:
        return
    machine = platform.machine().lower()
    if struct.calcsize('P') != 8 or machine not in ('amd64', 'x86_64') or sys.platform not in ('win32', 'linux'):
        raise RuntimeError('Builds destinados aos alvos oficiais Windows/Linux x64.')
    label = 'Windows-x64' if sys.platform == 'win32' else 'Linux-x86_64'
    name = f'OoT3D_PTBR_TriAevum_v{VERSION}_{label}'
    if args.hd_runtime:
        name += '_HD'
    env = os.environ.copy()
    env['OOT3D_PAYLOAD_ROOT'] = str(payload)
    env['OOT3D_BUILD_NAME'] = name
    with tempfile.TemporaryDirectory(prefix='hd-deploy-', dir=ROOT/'build') as temporary:
        if args.hd_runtime:
            from hd_textures import prepare_deploy_bundle
            env['OOT3D_HD_BUNDLE'] = str(prepare_deploy_bundle(args.hd_runtime, Path(temporary)))
        else:
            env.pop('OOT3D_HD_BUNDLE', None)
        subprocess.run([sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean',
                        '--distpath', str(ROOT/'dist'), '--workpath', str(ROOT/'build/pyinstaller'),
                        str(ROOT/'installer/OoT3D_PTBR_TriAevum_v1.2.1.spec')], check=True, env=env, cwd=ROOT)
    binary = ROOT/'dist'/(name + ('.exe' if sys.platform == 'win32' else ''))
    output = ROOT/'artifacts'
    output.mkdir(exist_ok=True)
    report = output/(name+'-self-test.json')
    subprocess.run([str(binary), '--self-test-report', str(report)], check=True, timeout=120)
    if not json.loads(report.read_text(encoding='utf-8')).get('ok'):
        raise RuntimeError('Autoteste do executável falhou.')
    if args.hd_runtime and hd_runtime_mode != 'verified_native_copy':
        source_archive = output/f'OoT3D_PTBR_TriAevum_v{VERSION}_Fontes-HD.zip'
        with zipfile.ZipFile(source_archive, 'w', zipfile.ZIP_DEFLATED, strict_timestamps=False) as z:
            for path in sorted(args.hd_runtime.rglob('*')):
                if path.is_file() and path.name not in ('TriAevum-PTBR-HD.exe', 'nvngx_dlss.dll', 'amd_fidelityfx_vk.dll', 'manifest.json'):
                    z.write(path, path.relative_to(args.hd_runtime).as_posix())
            z.writestr('LEIA-ME-FONTES.txt', 'Fontes exatos do runtime HD distribuido na v1.2.1.\n'
                       'Extraia source/TriAevum-source.zip e aplique source/menus-HD.patch com\n'
                       'git apply --ignore-whitespace. Instrucoes e dependencias estao no arquivo original.\n'
                       'Os nomes/commits de origem constam em SOURCE_ARCHIVE_MANIFEST.json.\n'
                       'Este pacote e opcional para jogar. Nenhuma ROM, plugin privado ou textura PNG incluida.\n')
        source_hash = hashlib.sha256(source_archive.read_bytes()).hexdigest()
        (output/(source_archive.name+'.sha256')).write_text(source_hash+'  '+source_archive.name+'\n', encoding='utf-8')
    variants = [(label + ('_HD' if args.hd_runtime else ''), '')] if sys.platform == 'win32' else [
        ('Linux-x86_64-AppImage', 'AppImage'), ('Linux-x86_64-Flatpak', 'Flatpak')]
    for variant, runtime in variants:
        package_name = f'OoT3D_PTBR_TriAevum_v{VERSION}_{variant}'
        archive = output/(package_name+'.zip')
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, strict_timestamps=False) as z:
            z.write(binary, binary.name)
            readme = (ROOT/'installer/LEIA-ME_v1.2.1.txt').read_text(encoding='utf-8')
            if runtime:
                readme = ('PACOTE LINUX: '+runtime+'\nVALIDACAO FUNCIONAL NO JOGO PENDENTE.\nHD exclusivo do Windows.\n\n') + readme
            z.writestr('LEIA-ME.txt', readme)
            z.write(ROOT/'installer/CREDITOS.txt', 'CREDITOS.txt')
            z.write(ROOT/'installer/TEXTURAS_CREDITOS.md', 'TEXTURAS-CREDITOS.md')
            for path in sorted((ROOT/'installer/PILLOW-LICENSES').rglob('*')):
                if path.is_file():
                    z.write(path, 'Licencas/Pillow/' + path.relative_to(ROOT/'installer/PILLOW-LICENSES').as_posix())
            if args.hd_runtime:
                z.write(ROOT/'installer/HD_INTEGRACAO.md', 'TEXTURAS-HD.md')
                z.write(args.hd_runtime/'LICENSE', 'Licencas/LICENSE-TriAevum.txt')
                z.write(args.hd_runtime/'THIRD_PARTY_NOTICES.md', 'Licencas/THIRD_PARTY_NOTICES.md')
                z.write(args.hd_runtime/'LICENSE_SCOPE.md', 'Licencas/LICENSE_SCOPE.md')
                for path in sorted((args.hd_runtime/'LICENSES').rglob('*')):
                    if path.is_file():
                        z.write(path, 'Licencas/componentes/' + path.relative_to(args.hd_runtime/'LICENSES').as_posix())
                if hd_runtime_mode == 'verified_native_copy':
                    z.writestr('FONTES.txt', 'O launcher HD copia o TriAevum.exe validado desta instalação, sem alterar seus bytes.\n'
                               'O instalador não inclui nem substitui o executável original ou DLLs.\n'
                               'Fontes correspondentes do runtime oficial beta.1.1:\n'
                               'https://github.com/coccofresco/TriAevum/tree/v0.8.0-beta.1.1\n')
                else:
                    z.writestr('FONTES.txt', 'Fontes correspondentes do runtime HD modificado e seu patch:\n'
                               'OoT3D_PTBR_TriAevum_v1.2.1_Fontes-HD.zip, na mesma release.\n'
                               'https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/tag/1.2.1\n'
                               'Download gratuito e opcional para jogar; licencas acompanham este pacote.\n')
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        (output/(archive.name+'.sha256')).write_text(digest+'  '+archive.name+'\n', encoding='utf-8')
        print('Pacote:', archive)
        print('SHA-256:', digest)



if __name__ == '__main__':
    main()
