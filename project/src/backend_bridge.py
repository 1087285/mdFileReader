"""
backend_bridge.py - QWebChannel 公開ブリッジ
@pyqtSlot でデコレートされたメソッドを JS へ公開し、
FileService に処理を委譲する。
"""
from PyQt6.QtCore import QObject, pyqtSlot

from file_service import FileService


class BackendBridge(QObject):
    """JavaScript から QWebChannel 経由で呼び出し可能なバックエンドクラス。"""

    def __init__(self, file_service: FileService, parent=None) -> None:
        super().__init__(parent)
        self._fs = file_service

    # ------------------------------------------------------------------
    # フォルダ選択
    # ------------------------------------------------------------------

    @pyqtSlot(result=str)
    def selectFolder(self) -> str:
        """
        フォルダ選択ダイアログを開き、選択されたパスを返す。
        未選択時は空文字列を返す。
        QFileDialog は GUI 環境でのみ使用するため遅延 import する。
        """
        from PyQt6.QtWidgets import QFileDialog  # noqa: PLC0415
        path = QFileDialog.getExistingDirectory(
            None,
            "フォルダを選択してください",
            "",
            QFileDialog.Option.ShowDirsOnly,
        )
        return path or ""

    # ------------------------------------------------------------------
    # ツリー取得
    # ------------------------------------------------------------------

    @pyqtSlot(str, result=str)
    def getTree(self, folder_path: str) -> str:
        """フォルダ配下の .md ファイルツリーを JSON で返す。"""
        return self._fs.get_tree(folder_path)

    # ------------------------------------------------------------------
    # ファイル読み込み
    # ------------------------------------------------------------------

    @pyqtSlot(str, result=str)
    def readFile(self, file_path: str) -> str:
        """ファイルを読み込み、内容を JSON で返す。"""
        return self._fs.read_file(file_path)

    # ------------------------------------------------------------------
    # ファイル保存
    # ------------------------------------------------------------------

    @pyqtSlot(str, str, str, result=str)
    def saveFile(self, file_path: str, content: str, encoding: str) -> str:
        """ファイルを元のエンコードで保存し、結果を JSON で返す。"""
        return self._fs.save_file(file_path, content, encoding)

    # ------------------------------------------------------------------
    # ファイル作成
    # ------------------------------------------------------------------

    @pyqtSlot(str, result=str)
    def createFile(self, file_path: str) -> str:
        """新規 .md ファイルを作成し、結果を JSON で返す。"""
        return self._fs.create_file(file_path)

    # ------------------------------------------------------------------
    # ファイル削除
    # ------------------------------------------------------------------

    @pyqtSlot(str, result=str)
    def deleteFile(self, file_path: str) -> str:
        """ファイルを削除し、結果を JSON で返す。"""
        return self._fs.delete_file(file_path)

    # ------------------------------------------------------------------
    # ファイル名変更
    # ------------------------------------------------------------------

    @pyqtSlot(str, str, result=str)
    def renameFile(self, old_path: str, new_path: str) -> str:
        """ファイル/フォルダ名を変更し、結果を JSON で返す。"""
        return self._fs.rename_file(old_path, new_path)
