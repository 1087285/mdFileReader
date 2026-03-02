"""
file_service.py - ファイルI/Oサービス
ファイル操作・バリデーション・文字コード自動判定を担当する。
"""
import json
from pathlib import Path
from typing import Any

import chardet


class FileService:
    """ファイル操作の全処理を担当するサービスクラス。"""

    def __init__(self) -> None:
        self._base_path: Path | None = None

    # ------------------------------------------------------------------
    # ベースパス管理
    # ------------------------------------------------------------------

    def set_base_path(self, folder_path: str) -> None:
        """ルートフォルダパスを記録する。"""
        self._base_path = Path(folder_path).resolve()

    # ------------------------------------------------------------------
    # バリデーション
    # ------------------------------------------------------------------

    def validate_path(self, target_path: str) -> Path:
        """
        ターゲットパスがベースフォルダ配下であることを検証し、
        解決済み絶対パスを返す。

        Raises:
            ValueError: ベースパスが未設定の場合 ("BASE_NOT_SET")
            PermissionError: フォルダ外アクセス試行の場合 ("PATH_TRAVERSAL")
        """
        if self._base_path is None:
            raise ValueError("BASE_NOT_SET")

        resolved = Path(target_path).resolve()

        # resolved が base_path 配下かチェック（base_path 自体も許可）
        try:
            resolved.relative_to(self._base_path)
        except ValueError:
            raise PermissionError("PATH_TRAVERSAL")

        return resolved

    # ------------------------------------------------------------------
    # ツリー取得
    # ------------------------------------------------------------------

    def get_tree(self, folder_path: str) -> str:
        """
        フォルダ配下の .md ファイルをツリーJSON文字列で返す。

        Returns:
            JSON文字列: {"success": true, "data": <treeNode>, "error": null}
        """
        try:
            self.set_base_path(folder_path)
            root = self._base_path
            if not root.exists():
                raise FileNotFoundError("FOLDER_NOT_FOUND")
            data = self._build_tree_node(root)
            return _ok(data)
        except FileNotFoundError as e:
            return _err(str(e) if str(e) in _KNOWN_CODES else "FOLDER_NOT_FOUND")
        except PermissionError as e:
            return _err(_perm_code(e))
        except Exception:
            return _err("UNKNOWN_ERROR")

    def _build_tree_node(self, path: Path) -> dict:
        """
        パスに対応するツリーノードを再帰的に構築する。
        フォルダはフォルダ優先・.md ファイルのみをソートして含める。
        """
        node: dict[str, Any] = {
            "name": path.name,
            "path": str(path),
            "type": "folder" if path.is_dir() else "file",
        }
        if path.is_dir():
            children = []
            try:
                entries = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
                for entry in entries:
                    if entry.is_dir():
                        children.append(self._build_tree_node(entry))
                    elif entry.is_file() and entry.suffix.lower() == ".md":
                        children.append(self._build_tree_node(entry))
            except PermissionError:
                pass
            node["children"] = children
        return node

    # ------------------------------------------------------------------
    # ファイル読み込み
    # ------------------------------------------------------------------

    def read_file(self, file_path: str) -> str:
        """
        ファイルを文字コード自動判定して読み込む。

        Returns:
            JSON文字列: {"success": true, "data": {"path": str, "content": str, "encoding": str}, "error": null}
        """
        try:
            resolved = self.validate_path(file_path)
            if not resolved.exists():
                raise FileNotFoundError("FILE_NOT_FOUND")

            raw = resolved.read_bytes()

            # 空ファイルの場合
            if not raw:
                return _ok({"path": str(resolved), "content": "", "encoding": "utf-8"})

            # chardet で文字コード判定
            detected = chardet.detect(raw)
            encoding = detected.get("encoding") or "utf-8"
            confidence = detected.get("confidence") or 0.0

            # 信頼度が低い場合は UTF-8 フォールバック
            if confidence < 0.5:
                encoding = "utf-8"

            # Windows 互換: shift_jis / shift-jis → cp932 に展開
            if encoding and encoding.lower().replace("-", "_") in ("shift_jis", "shift_jis_2004"):
                encoding = "cp932"

            try:
                content = raw.decode(encoding, errors="replace")
            except (LookupError, UnicodeDecodeError):
                try:
                    content = raw.decode("utf-8", errors="replace")
                    encoding = "utf-8"
                except Exception:
                    raise UnicodeDecodeError("utf-8", raw, 0, len(raw), "ENCODING_ERROR")

            return _ok({"path": str(resolved), "content": content, "encoding": encoding})

        except FileNotFoundError as e:
            return _err(str(e) if str(e) in _KNOWN_CODES else "FILE_NOT_FOUND")
        except PermissionError as e:
            return _err(_perm_code(e))
        except (UnicodeDecodeError, LookupError):
            return _err("ENCODING_ERROR")
        except ValueError as e:
            return _err(str(e) if str(e) in _KNOWN_CODES else "BASE_NOT_SET")
        except Exception:
            return _err("UNKNOWN_ERROR")

    # ------------------------------------------------------------------
    # ファイル保存
    # ------------------------------------------------------------------

    def save_file(self, file_path: str, content: str, encoding: str = "utf-8") -> str:
        """
        ファイルを指定エンコード (BOM なし) で上書き保存する。
        encoding が未指定の場合は UTF-8 を使用する。

        Returns:
            JSON文字列: {"success": true, "data": null, "error": null}
        """
        try:
            resolved = self.validate_path(file_path)
            resolved.write_text(content, encoding=encoding or "utf-8")
            return _ok(None)
        except UnicodeEncodeError:
            return _err("ENCODE_SAVE_ERROR")
        except PermissionError as e:
            return _err(_perm_code(e))
        except ValueError as e:
            return _err(str(e) if str(e) in _KNOWN_CODES else "BASE_NOT_SET")
        except Exception:
            return _err("UNKNOWN_ERROR")

    # ------------------------------------------------------------------
    # ファイル作成
    # ------------------------------------------------------------------

    def create_file(self, file_path: str) -> str:
        """
        空の .md ファイルを新規作成する。

        Returns:
            JSON文字列: {"success": true, "data": null, "error": null}
        """
        try:
            resolved = self.validate_path(file_path)
            if resolved.exists():
                raise FileExistsError("FILE_EXISTS")
            resolved.parent.mkdir(parents=True, exist_ok=True)
            resolved.touch()
            return _ok(None)
        except FileExistsError:
            return _err("FILE_EXISTS")
        except PermissionError as e:
            return _err(_perm_code(e))
        except ValueError as e:
            return _err(str(e) if str(e) in _KNOWN_CODES else "BASE_NOT_SET")
        except Exception:
            return _err("UNKNOWN_ERROR")

    # ------------------------------------------------------------------
    # ファイル削除
    # ------------------------------------------------------------------

    def delete_file(self, file_path: str) -> str:
        """
        ファイルを削除する。

        Returns:
            JSON文字列: {"success": true, "data": null, "error": null}
        """
        try:
            resolved = self.validate_path(file_path)
            if not resolved.exists():
                raise FileNotFoundError("FILE_NOT_FOUND")
            resolved.unlink()
            return _ok(None)
        except FileNotFoundError as e:
            return _err(str(e) if str(e) in _KNOWN_CODES else "FILE_NOT_FOUND")
        except PermissionError as e:
            return _err(_perm_code(e))
        except ValueError as e:
            return _err(str(e) if str(e) in _KNOWN_CODES else "BASE_NOT_SET")
        except Exception:
            return _err("UNKNOWN_ERROR")

    # ------------------------------------------------------------------
    # ファイル名変更
    # ------------------------------------------------------------------

    def rename_file(self, old_path: str, new_path: str) -> str:
        """
        ファイル/フォルダの名前を変更する。

        Returns:
            JSON文字列: {"success": true, "data": null, "error": null}
        """
        try:
            old = self.validate_path(old_path)
            new = self.validate_path(new_path)

            if not old.exists():
                raise FileNotFoundError("FILE_NOT_FOUND")
            if new.exists():
                raise FileExistsError("FILE_EXISTS")

            old.rename(new)
            return _ok(None)
        except FileNotFoundError as e:
            return _err(str(e) if str(e) in _KNOWN_CODES else "FILE_NOT_FOUND")
        except FileExistsError:
            return _err("FILE_EXISTS")
        except PermissionError as e:
            return _err(_perm_code(e))
        except ValueError as e:
            return _err(str(e) if str(e) in _KNOWN_CODES else "BASE_NOT_SET")
        except Exception:
            return _err("UNKNOWN_ERROR")


# ------------------------------------------------------------------
# ヘルパー関数（モジュールレベル）
# ------------------------------------------------------------------

# エラーコードとして有効な文字列セット
_KNOWN_CODES: frozenset[str] = frozenset({
    "PATH_TRAVERSAL", "PERMISSION_DENIED", "FILE_NOT_FOUND",
    "FILE_EXISTS", "FOLDER_NOT_FOUND", "BASE_NOT_SET",
    "ENCODING_ERROR", "ENCODE_SAVE_ERROR", "UNKNOWN_ERROR",
})


def _ok(data: Any) -> str:
    """成功レスポンスJSON文字列を生成する。"""
    return json.dumps({"success": True, "data": data, "error": None}, ensure_ascii=False)


def _err(code: str) -> str:
    """失敗レスポンスJSON文字列を生成する。"""
    return json.dumps({"success": False, "data": None, "error": code}, ensure_ascii=False)


def _perm_code(e: Exception) -> str:
    """PermissionError のメッセージが既知エラーコードの場合はそのまま返し、
    OS由来のメッセージ（例: '[Errno 13] ...'）の場合は 'PERMISSION_DENIED' を返す。"""
    msg = str(e)
    return msg if msg in _KNOWN_CODES else "PERMISSION_DENIED"
