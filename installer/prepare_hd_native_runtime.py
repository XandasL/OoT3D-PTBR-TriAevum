"""Create the marker bundle for the verified native TriAevum beta.1.1 runtime."""
import argparse
from pathlib import Path

from hd_textures import (
    NATIVE_RUNTIME_MODE, SOURCE_DOWNLOAD, encoded_json, recipe, validate_bundle,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    rules = recipe()
    if rules.get('runtime_mode') != NATIVE_RUNTIME_MODE:
        raise RuntimeError('A receita não seleciona o modo de runtime nativo.')
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        raise RuntimeError('A pasta de saída precisa estar vazia.')
    output.mkdir(parents=True, exist_ok=True)

    files = {
        'LICENSE': (
            'This installer does not distribute or modify the TriAevum executable. '
            'The optional HD launcher is copied byte-for-byte from the user\'s verified '
            'TriAevum beta.1.1 installation. Consult the original TriAevum distribution '
            'for its license terms.\n'
        ),
        'THIRD_PARTY_NOTICES.md': (
            'The native HD launcher reuses the user\'s already-installed TriAevum '
            'runtime and dependencies; this bundle contains no upstream binary.\n'
            'Upstream release and notices: https://github.com/coccofresco/TriAevum/releases/tag/v0.8.0-beta.1.1\n'
        ),
        'LICENSE_SCOPE.md': (
            'Scope: the PT-BR HD component creates a byte-for-byte copy of the verified '
            'local TriAevum.exe under a separate launcher name. It does not modify or '
            'replace the original executable or its DLL dependencies.\n'
        ),
        'SOURCE_OFFER.md': (
            'The runtime used by the HD launcher is the exact verified TriAevum beta.1.1 '
            'executable from the user\'s installation; it is not bundled here.\n\n'
            'Corresponding source code: ' + SOURCE_DOWNLOAD + '\n'
        ),
    }
    for name, content in files.items():
        (output / name).write_text(content, encoding='utf-8')
    (output / 'manifest.json').write_bytes(encoded_json({
        'format': 'oot3d_ptbr_hd_runtime_v1',
        'runtime_mode': NATIVE_RUNTIME_MODE,
        'files': rules['runtime_files'],
        'source_files': rules['source_files'],
        'source_url': SOURCE_DOWNLOAD,
    }))
    validate_bundle(output)
    print('Bundle HD beta.1.1 validado:', output)


if __name__ == '__main__':
    main()
