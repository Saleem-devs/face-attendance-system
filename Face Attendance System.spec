# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules


# Static resources to bundle
extra_datas = [
    ('desktop', 'desktop'),
    ('backend', 'backend'),
    ('web_dashboard/out', 'web_dashboard/out'),
    ('data', 'data'),
    ('db', 'db'),
]

# Package data for face_recognition models
extra_datas += collect_data_files('face_recognition_models')
extra_datas += collect_data_files('face_recognition')

# Hidden imports so uvicorn/fastapi/starlette load inside bundle
extra_hiddenimports = []
extra_hiddenimports += collect_submodules('uvicorn')
extra_hiddenimports += collect_submodules('fastapi')
extra_hiddenimports += collect_submodules('starlette')


a = Analysis(
    ['desktop/main.py'],
    pathex=[],
    binaries=[],
    datas=extra_datas,
    hiddenimports=extra_hiddenimports,
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
    [],
    exclude_binaries=True,
    name='Face Attendance System',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Face Attendance System',
)
app = BUNDLE(
    coll,
    name='Face Attendance System.app',
    icon='desktop/assets/app_icon.png',
    bundle_identifier='Face Attendance System',
    info_plist={
        'NSCameraUsageDescription': 'Face capture is required to register and mark attendance.'
    }
)
