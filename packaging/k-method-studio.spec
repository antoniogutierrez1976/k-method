# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None

# Base directory is repository root
repo_root = os.path.abspath(os.path.join(SPECPATH, ".."))

datas = [
    (os.path.join(repo_root, "scripts", "harness", "gui", "static"), os.path.join("scripts", "harness", "gui", "static")),
]

hidden_imports = [
    "uvicorn",
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
    "starlette",
    "starlette.staticfiles",
    "fastapi",
    "fastapi.responses",
    "google.genai",
]

a = Analysis(
    [os.path.join(repo_root, "scripts", "harness", "gui", "launch.py")],
    pathex=[repo_root],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="k-method-studio",
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
