# mdFileReader.spec
# PyInstaller ビルドスクリプト
#
# ビルド方法:
#   pyinstaller mdFileReader.spec
#
# 生成物:
#   dist/mdFileReader.exe

import os
from pathlib import Path

SRC = Path(SPECPATH)  # .spec ファイルと同じディレクトリ = project/src/

block_cipher = None

a = Analysis(
    [str(SRC / "main.py")],
    pathex=[str(SRC)],
    binaries=[],
    datas=[
        # resources フォルダ全体を同梱
        (str(SRC / "resources"), "resources"),
    ],
    hiddenimports=[
        "chardet",
        "PyQt6.QtWebEngineWidgets",
        "PyQt6.QtWebEngineCore",
        "PyQt6.QtWebChannel",
        "PyQt6.QtPrintSupport",
    ],
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
    name="mdFileReader",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,    # コンソールウィンドウ非表示
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon="resources/icon.ico",  # アイコンファイルを用意した場合はコメントアウトを解除
)
