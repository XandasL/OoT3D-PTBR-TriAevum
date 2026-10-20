"""Build native Windows/Linux installers; never publishes a release."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import struct
import subprocess
import sys
import urllib.request
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
VERSION = '1.3.0'
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
    args = parser.parse_args()
    if args.payload:
        payload = args.payload.resolve()
    else:
        source = args.source_zip or ROOT / 'build/reference-v1.0.0.zip'
        if not source.exists():
            source.parent.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(SOURCE_URL, source)
        payload = extract_payload(source)
    validate_payload(payload)
    print('Payload validado: 112 recursos, incluindo texturas PT-BR originais.')
    if args.prepare_only:
        return
    machine = platform.machine().lower()
    if struct.calcsize('P') != 8 or machine not in ('amd64', 'x86_64') or sys.platform not in ('win32', 'linux'):
        raise RuntimeError('Build destinado a Windows/Linux x64.')
    label = 'Windows-x64' if sys.platform == 'win32' else 'Linux-x86_64'
    name = f'OoT3D_PTBR_TriAevum_v{VERSION}_{label}'
    env = os.environ.copy()
    env['OOT3D_PAYLOAD_ROOT'] = str(payload)
    env['OOT3D_BUILD_NAME'] = name
    subprocess.run([sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean',
                    '--distpath', str(ROOT/'dist'), '--workpath', str(ROOT/'build/pyinstaller'),
                    str(ROOT/'installer/OoT3D_PTBR_TriAevum_v1.3.0.spec')], check=True, env=env, cwd=ROOT)
    binary = ROOT/'dist'/(name + ('.exe' if sys.platform == 'win32' else ''))
    output = ROOT/'artifacts'
    output.mkdir(exist_ok=True)
    report = output/(name+'-self-test.json')
    subprocess.run([str(binary), '--self-test-report', str(report)], check=True, timeout=120)
    if not json.loads(report.read_text(encoding='utf-8')).get('ok'):
        raise RuntimeError('Autoteste do executável falhou.')
    archive = output/(name+'.zip')
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, strict_timestamps=False) as z:
        z.write(binary, binary.name)
        z.write(ROOT/'installer/LEIA-ME_v1.3.0.txt', 'LEIA-ME.txt')
        z.write(ROOT/'installer/CREDITOS.txt', 'CREDITOS.txt')
    sha = hashlib.sha256(archive.read_bytes()).hexdigest()
    (output/(archive.name+'.sha256')).write_text(sha+'  '+archive.name+'\n', encoding='utf-8')
    print('Pacote:', archive)


if __name__ == '__main__':
    main()