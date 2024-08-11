# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[ ('Lib/site-packages/sv_ttk/sv.tcl', 'sv_ttk'),
            ('Lib/site-packages/sv_ttk/theme/light.tcl', 'sv_ttk/theme'),
            ('Lib/site-packages/sv_ttk/theme/dark.tcl', 'sv_ttk/theme'),
            ('Lib/site-packages/sv_ttk/theme/sprites_dark.tcl', 'sv_ttk/theme'),
            ('Lib/site-packages/sv_ttk/theme/sprites_light.tcl', 'sv_ttk/theme'),
            ('Lib/site-packages/sv_ttk/theme/spritesheet_dark.png', 'sv_ttk/theme'),
            ('Lib/site-packages/sv_ttk/theme/spritesheet_light.png', 'sv_ttk/theme'),
            ('client.py', '.')],
    hiddenimports=['tkinter', 'sv_ttk', 'PIL._tkinter_finder', 'requests', 'zipfile', 'speedtest'],
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
