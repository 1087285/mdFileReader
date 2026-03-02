"""
setup_resources.py
開発環境での初回セットアップスクリプト。
qwebchannel.js・CodeMirror・marked.js を resources/ に配置する。

使い方:
    pip install -r requirements.txt
    python setup_resources.py
"""
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

# Windows での日本語出力対応
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


BASE = Path(__file__).parent
RESOURCES = BASE / "resources"
CODEMIRROR = RESOURCES / "codemirror"
CODEMIRROR_MODE = CODEMIRROR / "mode" / "markdown"

# すべての CDN URL
MARKED_URL      = "https://cdn.jsdelivr.net/npm/marked/marked.min.js"
CM_JS_URL       = "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/codemirror.min.js"
CM_CSS_URL      = "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/codemirror.min.css"
CM_MD_URL       = "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/markdown/markdown.min.js"
QWEBCHANNEL_URL = "https://raw.githubusercontent.com/qt/qtwebchannel/refs/heads/dev/src/webchannel/qwebchannel.js"


def download(url: str, dest: Path) -> None:
    if dest.exists():
        print(f"  [スキップ] {dest.name} は既に存在します")
        return
    print(f"  ダウンロード中: {url}")
    urllib.request.urlretrieve(url, dest)
    print(f"  → {dest}")


def copy_qwebchannel() -> None:
    """PyQt6 パッケージ内の qwebchannel.js をコピーする。見つからない場合は GitHub からダウンロードする。"""
    dest = RESOURCES / "qwebchannel.js"
    if dest.exists():
        print(f"  [スキップ] qwebchannel.js は既に存在します")
        return

    # PyQt6 のインストール先を特定
    result = subprocess.run(
        [sys.executable, "-c", "import PyQt6; import os; print(os.path.dirname(PyQt6.__file__))"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        pyqt6_dir = Path(result.stdout.strip())
        candidates = [
            pyqt6_dir / "Qt6" / "resources" / "qtwebchannel" / "qwebchannel.js",
            pyqt6_dir / "Qt" / "resources" / "qtwebchannel" / "qwebchannel.js",
        ]
        for src in candidates:
            if src.exists():
                shutil.copy2(src, dest)
                print(f"  コピー: {src} → {dest}")
                return

    # PyQt6 パッケージに含まれていない場合は GitHub からダウンロード
    print(f"  PyQt6 内に qwebchannel.js が見つかりません。GitHub からダウンロードします...")
    download(QWEBCHANNEL_URL, dest)


def main() -> None:
    print("=== mdFileReader リソースセットアップ ===\n")

    RESOURCES.mkdir(exist_ok=True)
    CODEMIRROR.mkdir(exist_ok=True)
    CODEMIRROR_MODE.mkdir(parents=True, exist_ok=True)

    print("[1] qwebchannel.js をコピー")
    copy_qwebchannel()

    print("\n[2] marked.js をダウンロード")
    download(MARKED_URL, RESOURCES / "marked.min.js")

    print("\n[3] CodeMirror をダウンロード")
    download(CM_JS_URL,  CODEMIRROR / "codemirror.min.js")
    download(CM_CSS_URL, CODEMIRROR / "codemirror.min.css")
    # mode/markdown ディレクトリ内に markdown.js として配置（ui.html の script src と一致）
    download(CM_MD_URL,  CODEMIRROR_MODE / "markdown.js")

    print("\n=== セットアップ完了 ===")
    print("次のコマンドでアプリを起動できます:")
    print("  python main.py")


if __name__ == "__main__":
    main()
