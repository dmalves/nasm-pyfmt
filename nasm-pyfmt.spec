# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller specification for a single-file nasm-pyfmt executable.
# Entry point: src/nasm_pyfmt/cli.py (same as the nasm-pyfmt console script in pyproject.toml).
# Regenerate after CLI changes: uv run pyinstaller nasm-pyfmt.spec --clean --noconfirm

# Trace imports starting from the CLI module; nasm_pyfmt is pulled in via imports.
a = Analysis(
    ['src/nasm_pyfmt/cli.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

# One-file bundle: bootloader + embedded Python + app (console, not GUI).
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='nasm-pyfmt',
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
