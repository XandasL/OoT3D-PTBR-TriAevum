# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path
root = Path(SPECPATH)
payload = Path(os.environ['OOT3D_PAYLOAD_ROOT']).resolve()
a = Analysis(
    [str(root / 'OoT3D_PTBR_TriAevum_v1.3.0.py')], pathex=[str(root)], binaries=[],
    datas=[(str(root / name), '.') for name in (
        'text_translation.py', 'font_mode.py',
        'Instalador_Traducao_PTBR_OoT3D_V4_compat_test.py', 'payload-manifest.json', 'LEIA-ME_v1.3.0.txt')]
        + [(str(root / 'font-hd-128'), 'font-hd-128'),
           (str(payload), 'TraducaoCompleta/citra/romfs')],
    hiddenimports=['__future__', 'hashlib', 'json', 'shutil', 'struct', 'time', 'zipfile', 'argparse',
                   'csv', 'subprocess', 'tempfile', 'uuid'],
    hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=['PIL', 'fontTools'],
    noarchive=False, optimize=0)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name=os.environ['OOT3D_BUILD_NAME'],
          debug=False, bootloader_ignore_signals=False, strip=False, upx=False,
          runtime_tmpdir=None, console=False, disable_windowed_traceback=False,
          argv_emulation=False, target_arch=None, codesign_identity=None, entitlements_file=None)