# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path
root = Path(SPECPATH)
payload = Path(os.environ['OOT3D_PAYLOAD_ROOT']).resolve()
extra_hd = []
open_font = os.environ.get('OOT3D_OPEN_FONT')
if open_font:
    font_path = Path(open_font).resolve()
    if not font_path.is_file():
        raise RuntimeError('Fonte aberta selecionada não encontrada')
    extra_hd.append((str(font_path), 'open-font'))
    extra_hd.append((str(font_path.with_name('OFL.txt')), 'open-font'))
    extra_hd.append((str(root / 'prepare_open_font_pack.py'), '.'))
    extra_hd.append((str(root / 'build_open_hd_qbf.py'), '.'))
if os.environ.get('OOT3D_HD_BUNDLE'):
    extra_hd.append((os.environ['OOT3D_HD_BUNDLE'], 'hd-runtime'))
a = Analysis(
    [str(root / 'OoT3D_PTBR_TriAevum_v1.2.1.py')],
    pathex=[str(root)], binaries=[],
    datas=[(str(root / 'Instalador_Traducao_PTBR_OoT3D_V4_compat_test.py'), '.'),
           (str(root / 'payload-manifest.json'), '.'),
           (str(root / 'font_mode.py'), '.'),
           (str(payload), 'TraducaoCompleta/citra/romfs'),
           (str(root / 'hd_textures.py'), '.'), (str(root / 'hd-recipe.json'), '.'), (str(root / 'navi-hud-overlay.png'), '.')] + extra_hd,
    hiddenimports=['hashlib', 'json', 'shutil', 'struct', 'time', 'zipfile', 'argparse',
                   'csv', 'subprocess', 'tempfile', 'uuid', 'PIL.Image', 'PIL.ImageDraw', 'PIL.ImageFont', 'PIL.PngImagePlugin', 'fontTools.ttLib'],
    hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[], noarchive=False, optimize=0,
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [],
          name=os.environ['OOT3D_BUILD_NAME'], debug=False,
          bootloader_ignore_signals=False, strip=False, upx=False,
          runtime_tmpdir=None, console=False, disable_windowed_traceback=False,
          argv_emulation=False, target_arch=None, codesign_identity=None, entitlements_file=None)
