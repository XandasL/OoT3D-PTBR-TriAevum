"""Prepare the optional tested runtime bundle; never includes textures or ROM."""
import argparse
import shutil
from pathlib import Path
from hd_textures import recipe, digest, bounded, encoded_json, validate_bundle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--executable', type=Path, required=True)
    parser.add_argument('--upstream', type=Path, required=True)
    parser.add_argument('--patch', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    rules = recipe()
    sources = {name: args.executable if name.endswith('.exe') else args.executable.parent / name
               for name in rules['runtime_files']}
    sources.update({'source/TriAevum-source.zip': args.upstream / 'source/TriAevum-source.zip',
                    'source/menus-HD.patch': args.patch})
    for name, expected in {**rules['runtime_files'], **rules['source_files']}.items():
        if digest(sources[name].read_bytes()) != expected:
            raise RuntimeError(f'Arquivo diferente do build validado: {name}')
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        raise RuntimeError('Use uma pasta de saída vazia para preservar bundles anteriores.')
    for name, source in sources.items():
        target = bounded(output, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    for name in ('LICENSE', 'THIRD_PARTY_NOTICES.md', 'LICENSE_SCOPE.md'):
        shutil.copy2(args.upstream / name, output / name)
    shutil.copytree(args.upstream / 'LICENSES', output / 'LICENSES')
    offer = (args.upstream / 'SOURCE_OFFER.md').read_text(encoding='utf-8')
    offer += ('\n\nLocal PT-BR HD extension\n\nThis bundle contains the modified generic Windows runtime. '
              'The upstream corresponding-source archive is included at source/TriAevum-source.zip, '
              'and the local changes are in source/menus-HD.patch. No ROM, prepared game image, '
              'private title plugin, save or texture PNG is included. The runtime and source hashes '
              'are pinned in the installer hd-recipe.json.\n')
    (output / 'SOURCE_OFFER.md').write_text(offer, encoding='utf-8')
    (output / 'manifest.json').write_bytes(encoded_json({
        'format': 'oot3d_ptbr_hd_runtime_v1', 'files': rules['runtime_files']}))
    validate_bundle(output)
    print(output)


if __name__ == '__main__':
    main()
