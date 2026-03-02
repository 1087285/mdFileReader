"""
test_integration.py - BackendBridge + FileService 結合テスト
テストケース: IT-01 〜 IT-08
QWebChannel 統合（JS↔Python）は GUI 実機が必要なため手動確認（IT-09, IT-10）。

実行方法:
    cd /workspaces/mdFileReader
    .venv/bin/pytest project/test/test_integration.py -v
"""
import json
import sys
from pathlib import Path

import pytest

# project/src/ を import パスに追加
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# ============================================================
# Qt アプリケーション初期化（QObject 使用のために必要）
# QCoreApplication は非GUI環境でも動作する
# ============================================================

@pytest.fixture(scope="session")
def qt_app():
    """セッションスコープの QCoreApplication。QObject の使用に必要。"""
    from PyQt6.QtCore import QCoreApplication
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication(sys.argv)
    yield app


@pytest.fixture
def base_dir(tmp_path: Path) -> Path:
    """テスト用ベースフォルダ。"""
    return tmp_path


@pytest.fixture
def bridge(qt_app, base_dir: Path):
    """BackendBridge + FileService の統合フィクスチャ。"""
    from backend_bridge import BackendBridge
    from file_service import FileService

    fs = FileService()
    fs.set_base_path(str(base_dir))
    b = BackendBridge(fs)
    return b


def _parse(result: str) -> dict:
    return json.loads(result)


# ============================================================
# IT-01: BackendBridge.getTree → FileService ツリー取得統合
# ============================================================

class TestGetTreeIntegration:
    """IT-01: ツリー取得の BackendBridge → FileService 連携"""

    def test_IT_01_getTree_returns_tree(self, bridge, base_dir: Path):
        """.md ファイルを含むフォルダのツリーが BackendBridge 経由で返る"""
        (base_dir / "top.md").write_text("# Top", encoding="utf-8")
        (base_dir / "other.txt").write_text("txt", encoding="utf-8")
        sub = base_dir / "docs"
        sub.mkdir()
        (sub / "sub.md").write_text("# Sub", encoding="utf-8")

        result = _parse(bridge.getTree(str(base_dir)))

        assert result["success"] is True
        data = result["data"]
        assert data["type"] == "folder"

        names = {c["name"] for c in data["children"]}
        assert "top.md" in names
        assert "other.txt" not in names, ".txt はツリーに含まれない"
        assert "docs" in names

    def test_IT_01_getTree_nonexistent_folder(self, bridge, base_dir: Path):
        """存在しないフォルダは FOLDER_NOT_FOUND で返る"""
        result = _parse(bridge.getTree(str(base_dir / "nonexistent")))
        assert result["success"] is False
        assert result["error"] == "FOLDER_NOT_FOUND"


# ============================================================
# IT-02: BackendBridge.readFile → FileService ファイル読込統合
# ============================================================

class TestReadFileIntegration:
    """IT-02: ファイル読込の BackendBridge → FileService 連携"""

    def test_IT_02_readFile_returns_content(self, bridge, base_dir: Path):
        """UTF-8 ファイルが BackendBridge 経由で読み込まれる"""
        target = base_dir / "sample.md"
        content = "# Integration Test\n結合テスト内容"
        target.write_text(content, encoding="utf-8")

        result = _parse(bridge.readFile(str(target)))

        assert result["success"] is True
        assert result["data"]["content"] == content
        assert result["data"]["path"] == str(target.resolve())

    def test_IT_02_readFile_not_found(self, bridge, base_dir: Path):
        """存在しないファイルは FILE_NOT_FOUND で返る"""
        result = _parse(bridge.readFile(str(base_dir / "ghost.md")))
        assert result["success"] is False
        assert result["error"] == "FILE_NOT_FOUND"

    def test_IT_02_readFile_path_traversal_blocked(self, bridge, base_dir: Path):
        """フォルダ外アクセスが BackendBridge 経由でもブロックされる"""
        outside = str(base_dir / ".." / "escape.md")
        result = _parse(bridge.readFile(outside))
        assert result["success"] is False
        assert result["error"] == "PATH_TRAVERSAL"


# ============================================================
# IT-03: BackendBridge.saveFile → FileService ファイル保存統合
# ============================================================

class TestSaveFileIntegration:
    """IT-03: ファイル保存の BackendBridge → FileService 連携"""

    def test_IT_03_saveFile_writes_content(self, bridge, base_dir: Path):
        """BackendBridge.saveFile がファイルに内容を書き込む（UTF-8）"""
        target = base_dir / "write_test.md"
        target.write_text("initial", encoding="utf-8")

        result = _parse(bridge.saveFile(str(target), "# 更新済みコンテンツ", "utf-8"))

        assert result["success"] is True
        assert target.read_text(encoding="utf-8") == "# 更新済みコンテンツ"

    def test_IT_03_saveFile_creates_new_file(self, bridge, base_dir: Path):
        """BackendBridge.saveFile が新規ファイルを作成する"""
        target = base_dir / "new_via_save.md"
        result = _parse(bridge.saveFile(str(target), "new content", "utf-8"))
        assert result["success"] is True
        assert target.exists()

    def test_IT_03a_saveFile_cp932(self, bridge, base_dir: Path):
        """BackendBridge.saveFile が cp932 でファイルを保存する"""
        target = base_dir / "cp932_save.md"
        content = "# Shift-JIS保存テスト\n日本語テキスト"

        result = _parse(bridge.saveFile(str(target), content, "cp932"))

        assert result["success"] is True
        # cp932 で読み直して内容が一致すること
        saved = target.read_bytes().decode("cp932")
        assert saved == content

    def test_IT_03b_saveFile_encode_save_error(self, bridge, base_dir: Path):
        """cp932 で表現できない文字を保存すると ENCODE_SAVE_ERROR が返る"""
        target = base_dir / "emoji.md"
        content = "# テスト\n絵文字: 🎉"

        result = _parse(bridge.saveFile(str(target), content, "cp932"))

        assert result["success"] is False
        assert result["error"] == "ENCODE_SAVE_ERROR"


# ============================================================
# IT-04: BackendBridge.createFile → FileService ファイル作成統合
# ============================================================

class TestCreateFileIntegration:
    """IT-04: ファイル作成の BackendBridge → FileService 連携"""

    def test_IT_04_createFile_creates_empty_file(self, bridge, base_dir: Path):
        """BackendBridge.createFile が空ファイルを作成する"""
        target = base_dir / "created.md"
        result = _parse(bridge.createFile(str(target)))
        assert result["success"] is True
        assert target.exists()
        assert target.read_bytes() == b""

    def test_IT_04_createFile_duplicate_returns_error(self, bridge, base_dir: Path):
        """同名ファイルへの createFile は FILE_EXISTS を返す"""
        target = base_dir / "dup.md"
        target.touch()
        result = _parse(bridge.createFile(str(target)))
        assert result["success"] is False
        assert result["error"] == "FILE_EXISTS"


# ============================================================
# IT-05: BackendBridge.deleteFile → FileService ファイル削除統合
# ============================================================

class TestDeleteFileIntegration:
    """IT-05: ファイル削除の BackendBridge → FileService 連携"""

    def test_IT_05_deleteFile_removes_file(self, bridge, base_dir: Path):
        """BackendBridge.deleteFile がファイルを削除する"""
        target = base_dir / "to_delete.md"
        target.touch()
        result = _parse(bridge.deleteFile(str(target)))
        assert result["success"] is True
        assert not target.exists()

    def test_IT_05_deleteFile_not_found(self, bridge, base_dir: Path):
        """存在しないファイルの削除は FILE_NOT_FOUND を返す"""
        result = _parse(bridge.deleteFile(str(base_dir / "ghost.md")))
        assert result["success"] is False
        assert result["error"] == "FILE_NOT_FOUND"


# ============================================================
# IT-06: BackendBridge.renameFile → FileService ファイル名変更統合
# ============================================================

class TestRenameFileIntegration:
    """IT-06: ファイル名変更の BackendBridge → FileService 連携"""

    def test_IT_06_renameFile_changes_name(self, bridge, base_dir: Path):
        """BackendBridge.renameFile がファイル名を変更する"""
        old = base_dir / "old.md"
        new = base_dir / "new.md"
        old.write_text("content", encoding="utf-8")

        result = _parse(bridge.renameFile(str(old), str(new)))

        assert result["success"] is True
        assert not old.exists()
        assert new.read_text(encoding="utf-8") == "content"

    def test_IT_06_renameFile_to_existing(self, bridge, base_dir: Path):
        """同名ファイルへのリネームは FILE_EXISTS を返す"""
        old = base_dir / "old.md"
        new = base_dir / "existing.md"
        old.touch()
        new.touch()
        result = _parse(bridge.renameFile(str(old), str(new)))
        assert result["success"] is False
        assert result["error"] == "FILE_EXISTS"


# ============================================================
# IT-07: フォルダ外アクセスブロック（全メソッド共通）
# ============================================================

class TestPathTraversalIntegration:
    """IT-07: BackendBridge 全メソッドでフォルダ外アクセスがブロックされる"""

    def test_IT_07_readFile_traversal_blocked(self, bridge, base_dir: Path):
        result = _parse(bridge.readFile(str(base_dir / ".." / "x.md")))
        assert result["error"] == "PATH_TRAVERSAL"

    def test_IT_07_saveFile_traversal_blocked(self, bridge, base_dir: Path):
        result = _parse(bridge.saveFile(str(base_dir / ".." / "x.md"), "x", "utf-8"))
        assert result["error"] == "PATH_TRAVERSAL"

    def test_IT_07_createFile_traversal_blocked(self, bridge, base_dir: Path):
        result = _parse(bridge.createFile(str(base_dir / ".." / "x.md")))
        assert result["error"] == "PATH_TRAVERSAL"

    def test_IT_07_deleteFile_traversal_blocked(self, bridge, base_dir: Path):
        result = _parse(bridge.deleteFile(str(base_dir / ".." / "x.md")))
        assert result["error"] == "PATH_TRAVERSAL"

    def test_IT_07_renameFile_traversal_blocked(self, bridge, base_dir: Path):
        inside = base_dir / "inside.md"
        inside.touch()
        result = _parse(bridge.renameFile(str(inside), str(base_dir / ".." / "x.md")))
        assert result["error"] == "PATH_TRAVERSAL"


# ============================================================
# IT-08: 連続操作フロー（作成→読込→編集→保存→削除）
# ============================================================

class TestE2EFlowIntegration:
    """IT-08: Python 層 E2E フロー（作成 → 読込 → 編集 → 保存 → 削除）"""

    def test_IT_08_full_crud_flow(self, bridge, base_dir: Path):
        """
        1. getTree でツリーにファイルが存在しないことを確認
        2. createFile で新規ファイル作成
        3. readFile でファイル内容を読込（空）
        4. saveFile でコンテンツを書き込み
        5. readFile で書き込み内容を確認
        6. renameFile でファイル名を変更
        7. deleteFile でファイルを削除
        8. getTree で削除後ツリーを確認
        """
        md_path = base_dir / "e2e.md"

        # Step 1: ツリーに e2e.md がないことを確認
        tree_result = _parse(bridge.getTree(str(base_dir)))
        initial_names = {c["name"] for c in tree_result["data"]["children"]}
        assert "e2e.md" not in initial_names

        # Step 2: ファイル作成
        create_result = _parse(bridge.createFile(str(md_path)))
        assert create_result["success"] is True
        assert md_path.exists()

        # Step 3: 読込（空ファイル）
        read_result = _parse(bridge.readFile(str(md_path)))
        assert read_result["success"] is True
        assert read_result["data"]["content"] == ""

        # Step 4: 保存
        save_result = _parse(bridge.saveFile(str(md_path), "# E2E テスト\n本文", "utf-8"))
        assert save_result["success"] is True

        # Step 5: 保存内容確認
        read2_result = _parse(bridge.readFile(str(md_path)))
        assert read2_result["data"]["content"] == "# E2E テスト\n本文"

        # Step 6: リネーム
        renamed = base_dir / "e2e_renamed.md"
        rename_result = _parse(bridge.renameFile(str(md_path), str(renamed)))
        assert rename_result["success"] is True
        assert not md_path.exists()
        assert renamed.exists()

        # Step 7: 削除
        delete_result = _parse(bridge.deleteFile(str(renamed)))
        assert delete_result["success"] is True
        assert not renamed.exists()

        # Step 8: ツリー確認（削除後）
        tree_final = _parse(bridge.getTree(str(base_dir)))
        final_names = {c["name"] for c in tree_final["data"]["children"]}
        assert "e2e.md" not in final_names
        assert "e2e_renamed.md" not in final_names
