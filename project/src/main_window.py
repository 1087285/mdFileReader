"""
main_window.py - メインウィンドウ
QMainWindow を継承し、QWebEngineView と QWebChannel をセットアップする。
"""
import sys
from pathlib import Path

from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtWidgets import QMainWindow

from backend_bridge import BackendBridge
from file_service import FileService


def resource_path(relative: str) -> Path:
    """PyInstaller の一時展開先または開発時ソース相対パスを返す。"""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    return base / relative


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._setup_window()
        self._setup_webview()
        self._setup_channel()
        self._load_html()

    # ------------------------------------------------------------------
    # セットアップ
    # ------------------------------------------------------------------

    def _setup_window(self) -> None:
        """ウィンドウタイトルと初期サイズを設定する。"""
        self.setWindowTitle("mdFileReader")
        self.resize(1280, 800)

    def _setup_webview(self) -> None:
        """QWebEngineView を中央ウィジェットとして配置する。"""
        self._view = QWebEngineView(self)
        self.setCentralWidget(self._view)

    def _setup_channel(self) -> None:
        """QWebChannel を生成し BackendBridge を 'backend' として登録する。"""
        self._file_service = FileService()
        self._bridge = BackendBridge(self._file_service, self)

        self._channel = QWebChannel(self)
        self._channel.registerObject("backend", self._bridge)
        self._view.page().setWebChannel(self._channel)

    def _load_html(self) -> None:
        """同梱リソースの ui.html を QUrl.fromLocalFile() でロードする。"""
        html_path = resource_path("resources/ui.html")
        self._view.setUrl(QUrl.fromLocalFile(str(html_path)))
