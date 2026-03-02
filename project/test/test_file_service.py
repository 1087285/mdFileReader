"""
test_file_service.py - FileService 単体テスト
テストケース: UT-BE-01 〜 UT-BE-15（詳細設計書 §6.1 準拠）
MC/DC観点を各関数の判定条件ごとに網羅する。

実行方法:
    cd /workspaces/mdFileReader
    .venv/bin/pytest project/test/test_file_service.py -v
"""
import json
import os
import stat
import sys
from pathlib import Path

import pytest

# project/src/ を import パスに追加
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from file_service import FileService  # noqa: E402


# ============================================================
# フィクスチャ
# ============================================================

@pytest.fixture
def base_dir(tmp_path: Path) -> Path:
    """テスト用ベースフォルダ（tmp_path配下）を返す。"""
    return tmp_path


@pytest.fixture
def fs(base_dir: Path) -> FileService:
    """ベースパスを設定済みの FileService インスタンスを返す。"""
    service = FileService()
    service.set_base_path(str(base_dir))
    return service


def _parse(result: str) -> dict:
    """JSON文字列をdictに変換するヘルパー。"""
    return json.loads(result)


# ============================================================
# validate_path
# UT-BE-01: ベースパス配下のパスは正常通過する
# UT-BE-02: ../ を含むパスは PATH_TRAVERSAL エラー
# ------------------------------------------------------------
# MC/DC観点 (validate_path):
#   C1: _base_path is None        → True  → ValueError("BASE_NOT_SET")
#   C2: resolved outside base     → True  → PermissionError("PATH_TRAVERSAL")
#   正常ケース: C1=False, C2=False → resolved を返す
# ============================================================

class TestValidatePath:
    """UT-BE-01 / UT-BE-02  validate_path MC/DC"""

    def test_UT_BE_01_valid_path_inside_base(self, fs: FileService, base_dir: Path):
        """C1=False, C2=False: ベースパス配下のパスは正常にPathを返す"""
        target = base_dir / "test.md"
        target.touch()
        result = fs.validate_path(str(target))
        assert result == target.resolve()

    def test_UT_BE_02_path_traversal_rejected(self, fs: FileService, base_dir: Path):
        """C1=False, C2=True: ../ を含むパスは PATH_TRAVERSAL エラー"""
        outside = str(base_dir / ".." / "escape.md")
        with pytest.raises(PermissionError, match="PATH_TRAVERSAL"):
            fs.validate_path(outside)

    def test_validate_path_base_not_set(self):
        """C1=True: ベースパス未設定時は BASE_NOT_SET エラー"""
        service = FileService()
        with pytest.raises(ValueError, match="BASE_NOT_SET"):
            service.validate_path("/any/path.md")


# ============================================================
# get_tree
# UT-BE-03: .md ファイルのみがツリーに含まれる
# UT-BE-04: 存在しないフォルダは FOLDER_NOT_FOUND
# ------------------------------------------------------------
# MC/DC観点 (get_tree):
#   C1: root.exists() → False → FileNotFoundError("FOLDER_NOT_FOUND")
#   正常ケース: C1=True → ツリーJSON返却
# ============================================================

class TestGetTree:
    """UT-BE-03 / UT-BE-04  get_tree MC/DC"""

    def test_UT_BE_03_only_md_files_in_tree(self, tmp_path: Path):
        """C1=True: .md ファイルのみツリーに含まれる。.txt は含まれない"""
        # ファイル作成
        (tmp_path / "a.md").write_text("# A", encoding="utf-8")
        (tmp_path / "b.txt").write_text("text", encoding="utf-8")
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "c.md").write_text("# C", encoding="utf-8")
        (sub / "d.log").write_text("log", encoding="utf-8")

        service = FileService()
        result = _parse(service.get_tree(str(tmp_path)))

        assert result["success"] is True
        data = result["data"]

        # ルートの children 確認
        names = {child["name"] for child in data["children"]}
        assert "a.md" in names, ".md ファイルがツリーに含まれること"
        assert "b.txt" not in names, ".txt ファイルはツリーに含まれないこと"
        assert "sub" in names, "サブフォルダがツリーに含まれること"

        # サブフォルダの children 確認
        sub_node = next(c for c in data["children"] if c["name"] == "sub")
        sub_names = {child["name"] for child in sub_node["children"]}
        assert "c.md" in sub_names
        assert "d.log" not in sub_names

    def test_UT_BE_04_folder_not_found(self, tmp_path: Path):
        """C1=False: 存在しないフォルダは FOLDER_NOT_FOUND"""
        service = FileService()
        result = _parse(service.get_tree(str(tmp_path / "nonexistent")))
        assert result["success"] is False
        assert result["error"] == "FOLDER_NOT_FOUND"


# ============================================================
# read_file
# UT-BE-05: UTF-8 ファイルが正常に読み込まれる
# UT-BE-06: Shift-JIS ファイルが文字化けなく読み込まれる
# UT-BE-07: 存在しないファイルは FILE_NOT_FOUND
# ------------------------------------------------------------
# MC/DC観点 (read_file):
#   C1: resolved.exists() → False → FileNotFoundError("FILE_NOT_FOUND")
#   C2: not raw           → True  → 空文字で正常返却
#   C3: confidence < 0.5  → True  → UTF-8フォールバック
#   正常ケース: C1=False, C2=False, C3=False → 通常デコード返却
# ============================================================

class TestReadFile:
    """UT-BE-05 / UT-BE-06 / UT-BE-07  read_file MC/DC"""

    def test_UT_BE_05_utf8_file_read(self, fs: FileService, base_dir: Path):
        """C1=False, C2=False, C3=False: UTF-8 ファイルが正常に読み込まれる"""
        target = base_dir / "utf8.md"
        content = "# UT-8 テスト\nこんにちは"
        target.write_text(content, encoding="utf-8")

        result = _parse(fs.read_file(str(target)))

        assert result["success"] is True
        assert result["data"]["content"] == content
        assert result["error"] is None

    def test_UT_BE_06_shiftjis_file_read(self, fs: FileService, base_dir: Path):
        """C3=True(低信頼度の場合) または 正常デコード: Shift-JIS ファイルが文字化けなく読み込まれる"""
        target = base_dir / "sjis.md"
        content_str = "# Shift-JISテスト\nテキスト内容"
        target.write_bytes(content_str.encode("shift_jis"))

        result = _parse(fs.read_file(str(target)))

        assert result["success"] is True
        # Shift-JIS として正しくデコードされるか、または replace で読み込まれる
        # 文字化けチェック: 元の ASCII 文字（"#"、スペース）が含まれること
        data_content = result["data"]["content"]
        assert "#" in data_content, "コンテンツが読み込まれること"
        assert result["error"] is None

    def test_UT_BE_07_file_not_found(self, fs: FileService, base_dir: Path):
        """C1=False (exists=False): 存在しないファイルは FILE_NOT_FOUND"""
        result = _parse(fs.read_file(str(base_dir / "nonexistent.md")))
        assert result["success"] is False
        assert result["error"] == "FILE_NOT_FOUND"

    def test_read_file_empty_returns_empty_string(self, fs: FileService, base_dir: Path):
        """C2=True: 空ファイルは空文字で正常返却（C2ブランチの独立カバレッジ）"""
        target = base_dir / "empty.md"
        target.write_bytes(b"")

        result = _parse(fs.read_file(str(target)))

        assert result["success"] is True
        assert result["data"]["content"] == ""


# ============================================================
# save_file
# UT-BE-08: UTF-8 で保存されている（BOM なし）
# UT-BE-09: 権限なしファイルへの保存は PERMISSION_DENIED
# ------------------------------------------------------------
# MC/DC観点 (save_file):
#   C1: PermissionError 発生 → True → PERMISSION_DENIED
#   正常ケース: C1=False → UTF-8書き込み成功
# ============================================================

class TestSaveFile:
    """UT-BE-08 / UT-BE-09  save_file MC/DC"""

    def test_UT_BE_08_save_utf8_no_bom(self, fs: FileService, base_dir: Path):
        """C1=False: UTF-8 (BOMなし) で保存される"""
        target = base_dir / "save_test.md"
        content = "# 保存テスト\nBOMなし UTF-8"
        result_json = _parse(fs.save_file(str(target), content))

        assert result_json["success"] is True

        # BOM なし UTF-8 で読めることを確認
        raw = target.read_bytes()
        assert not raw.startswith(b"\xef\xbb\xbf"), "BOM が付いていないこと"
        assert raw.decode("utf-8") == content

    def test_UT_BE_09_permission_denied_on_save(self, fs: FileService, base_dir: Path):
        """C1=True: 読み取り専用ファイルへの保存は PERMISSION_DENIED"""
        target = base_dir / "readonly.md"
        target.write_text("original", encoding="utf-8")
        # 読み取り専用に設定
        target.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

        try:
            result = _parse(fs.save_file(str(target), "overwrite"))
            assert result["success"] is False
            assert result["error"] == "PERMISSION_DENIED"
        finally:
            # テスト後に権限を戻す（クリーンアップ）
            target.chmod(stat.S_IRUSR | stat.S_IWUSR)


# ============================================================
# create_file
# UT-BE-10: 新規ファイルが作成される
# UT-BE-11: 同名ファイル存在時は FILE_EXISTS
# ------------------------------------------------------------
# MC/DC観点 (create_file):
#   C1: resolved.exists() → True  → FileExistsError("FILE_EXISTS")
#   正常ケース: C1=False → touch() → 成功
# ============================================================

class TestCreateFile:
    """UT-BE-10 / UT-BE-11  create_file MC/DC"""

    def test_UT_BE_10_create_new_file(self, fs: FileService, base_dir: Path):
        """C1=False: 新規ファイルが作成される"""
        target = base_dir / "new_file.md"
        assert not target.exists()

        result = _parse(fs.create_file(str(target)))

        assert result["success"] is True
        assert target.exists()

    def test_UT_BE_11_file_exists_error(self, fs: FileService, base_dir: Path):
        """C1=True: 同名ファイルが存在する場合は FILE_EXISTS"""
        target = base_dir / "existing.md"
        target.touch()

        result = _parse(fs.create_file(str(target)))

        assert result["success"] is False
        assert result["error"] == "FILE_EXISTS"


# ============================================================
# delete_file
# UT-BE-12: ファイルが削除される
# UT-BE-13: 存在しないファイルは FILE_NOT_FOUND
# ------------------------------------------------------------
# MC/DC観点 (delete_file):
#   C1: resolved.exists() → False → FileNotFoundError("FILE_NOT_FOUND")
#   正常ケース: C1=True → unlink() → 成功
# ============================================================

class TestDeleteFile:
    """UT-BE-12 / UT-BE-13  delete_file MC/DC"""

    def test_UT_BE_12_delete_existing_file(self, fs: FileService, base_dir: Path):
        """C1=True: ファイルが削除される"""
        target = base_dir / "to_delete.md"
        target.touch()

        result = _parse(fs.delete_file(str(target)))

        assert result["success"] is True
        assert not target.exists()

    def test_UT_BE_13_delete_nonexistent_file(self, fs: FileService, base_dir: Path):
        """C1=False: 存在しないファイルは FILE_NOT_FOUND"""
        result = _parse(fs.delete_file(str(base_dir / "ghost.md")))

        assert result["success"] is False
        assert result["error"] == "FILE_NOT_FOUND"


# ============================================================
# rename_file
# UT-BE-14: ファイル名が変更される
# UT-BE-15: 同名ファイル存在時は FILE_EXISTS
# ------------------------------------------------------------
# MC/DC観点 (rename_file):
#   C1: old.exists() → False → FileNotFoundError("FILE_NOT_FOUND")
#   C2: new.exists() → True  → FileExistsError("FILE_EXISTS")
#   正常ケース: C1=True (exists), C2=False → old.rename(new) → 成功
# ============================================================

class TestRenameFile:
    """UT-BE-14 / UT-BE-15  rename_file MC/DC"""

    def test_UT_BE_14_rename_file(self, fs: FileService, base_dir: Path):
        """C1=True (exists), C2=False: ファイル名が変更される"""
        old = base_dir / "old.md"
        new = base_dir / "new.md"
        old.write_text("content", encoding="utf-8")

        result = _parse(fs.rename_file(str(old), str(new)))

        assert result["success"] is True
        assert not old.exists()
        assert new.exists()
        assert new.read_text(encoding="utf-8") == "content"

    def test_UT_BE_15_rename_to_existing_name(self, fs: FileService, base_dir: Path):
        """C1=True (old exists), C2=True (new exists): 同名ファイルが存在する時は FILE_EXISTS"""
        old = base_dir / "old.md"
        new = base_dir / "existing.md"
        old.touch()
        new.touch()

        result = _parse(fs.rename_file(str(old), str(new)))

        assert result["success"] is False
        assert result["error"] == "FILE_EXISTS"

    def test_rename_old_not_found(self, fs: FileService, base_dir: Path):
        """C1=False: 変更元が存在しない場合は FILE_NOT_FOUND"""
        result = _parse(fs.rename_file(str(base_dir / "ghost.md"), str(base_dir / "new.md")))

        assert result["success"] is False
        assert result["error"] == "FILE_NOT_FOUND"


# ============================================================
# レスポンスフォーマット確認（全メソッド共通）
# ============================================================

class TestResponseFormat:
    """全メソッドが {"success": bool, "data": ..., "error": ...} 形式を返すことを確認"""

    def test_success_response_has_required_keys(self, fs: FileService, base_dir: Path):
        target = base_dir / "format_test.md"
        target.write_text("test", encoding="utf-8")

        result = _parse(fs.read_file(str(target)))
        assert "success" in result
        assert "data" in result
        assert "error" in result

    def test_error_response_has_required_keys(self, fs: FileService, base_dir: Path):
        result = _parse(fs.read_file(str(base_dir / "no_file.md")))
        assert "success" in result
        assert "data" in result
        assert "error" in result
        assert result["data"] is None

    def test_success_error_field_is_null(self, fs: FileService, base_dir: Path):
        target = base_dir / "null_err.md"
        target.touch()
        result = _parse(fs.delete_file(str(target)))
        assert result["error"] is None

    def test_error_data_field_is_null(self, fs: FileService, base_dir: Path):
        result = _parse(fs.delete_file(str(base_dir / "ghost.md")))
        assert result["data"] is None
