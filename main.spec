# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_all

datas = [('Lib/site-packages/sv_ttk/sv.tcl', 'sv_ttk'),
            ('Lib/site-packages/sv_ttk/theme/light.tcl', 'sv_ttk/theme'),
            ('Lib/site-packages/sv_ttk/theme/dark.tcl', 'sv_ttk/theme'),
            ('Lib/site-packages/sv_ttk/theme/sprites_dark.tcl', 'sv_ttk/theme'),
            ('Lib/site-packages/sv_ttk/theme/sprites_light.tcl', 'sv_ttk/theme'),
            ('Lib/site-packages/sv_ttk/theme/spritesheet_dark.png', 'sv_ttk/theme'),
            ('Lib/site-packages/sv_ttk/theme/spritesheet_light.png', 'sv_ttk/theme'),
            ('client.py', '.')]
binaries = []
hiddenimports = ['tkinter', 'sv_ttk', 'PIL._tkinter_finder', 'requests', 'zipfile', 'speedtest', 'tkinterdnd2']
tmp_ret = collect_all('tkinterdnd2')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    Tree('.\\assets', 'assets\\'),
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
