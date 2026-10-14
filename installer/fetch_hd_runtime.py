"""Download the hash-pinned generic runtime input for the Windows HD build."""
import hashlib
import json
import os
from pathlib import Path
import stat
import urllib.request
import urllib.parse
import zipfile
from hd_textures import validate_bundle, bounded

ROOT = Path(__file__).resolve().parents[1]

def main():
    rules = json.loads((ROOT/'installer/hd-runtime-download.json').read_text(encoding='utf-8'))
    parsed = urllib.parse.urlsplit(rules['url'])
    if (rules.get('format') != 'oot3d_hd_runtime_download_v1' or parsed.scheme != 'https' or
            parsed.netloc != 'api.github.com' or
            not parsed.path.startswith('/repos/XandasL/OoT3D-PTBR-TriAevum/releases/assets/')):
        raise RuntimeError('Origem do runtime HD desconhecida.')
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        raise RuntimeError('GITHUB_TOKEN é necessário para acessar o insumo do draft.')
    request = urllib.request.Request(rules['url'], headers={
        'Accept': 'application/octet-stream', 'User-Agent': 'PTBR-installer-v1.2'})
    # A GitHub asset redirects to storage: never forward the credential there.
    request.add_unredirected_header('Authorization', 'Bearer '+token)
    archive = ROOT/'build/hd-runtime-input-v1.2.zip'
    archive.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(request, timeout=120) as response, archive.open('wb') as out:
        count = 0
        while block := response.read(1024*1024):
            count += len(block)
            if count > rules['size']:
                raise RuntimeError('Runtime HD maior que o insumo validado.')
            out.write(block)
    if archive.stat().st_size != rules['size'] or hashlib.sha256(archive.read_bytes()).hexdigest() != rules['sha256']:
        raise RuntimeError('SHA-256/tamanho do runtime HD incorreto.')
    output = ROOT/'build/hd-runtime-v1.2'
    if output.exists() and any(output.iterdir()):
        raise RuntimeError('Destino não vazio: preserve o bundle existente.')
    with zipfile.ZipFile(archive) as z:
        seen = set()
        if sum(i.file_size for i in z.infolist()) > 512*1024*1024:
            raise RuntimeError('Arquivo descompactado grande demais.')
        for item in z.infolist():
            if item.is_dir():
                continue
            if item.filename in seen or stat.S_ISLNK(item.external_attr >> 16):
                raise RuntimeError('Entrada duplicada ou link no bundle.')
            seen.add(item.filename)
            target = bounded(output, item.filename)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(z.read(item))
    validate_bundle(output)
    print('Runtime HD validado:', output)

if __name__ == '__main__':
    main()
