# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['portfolio_app/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('portfolio_app/resources/', 'resources/'),
        ('portfolio_app/styles/', 'styles/'),
    ],
    hiddenimports=[
        'PySide6.QtSvg',
        'PySide6.QtXml',
        'PySide6.QtQuick',
        'PySide6.QtQml',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PortfolioApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # UPX KAPALI — virüs yanlış pozitif önlemi
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='portfolio_app/resources/icons/app_icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='PortfolioApp',
)
