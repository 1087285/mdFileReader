# 04 実装

## 1. 文書情報

| 項目 | 内容 |
|------|------|
| 文書名 | 実装記録 |
| 版数 | v1.1.0 |
| 作成日 | 2026-03-02 |
| 作成者 | GitHub Copilot（04_implementation_agent） |
| 参照元 | `project/document/03_detailed_design.md` v1.1.0 |
| ステータス | 承認済み（2026-03-02） |

---

## 2. 実装方針

| 項目 | 方針 |
|------|------|
| 言語 | Python 3.12 / HTML / CSS / JavaScript (ES5+) |
| フレームワーク | PyQt6 + QWebEngineView + QWebChannel |
| 文字コード | ソース全体 UTF-8。ファイル読み込みは chardet で自動判定（`shift_jis` → `cp932` に展開）。保存は読み込み時に検出したエンコードで書き込み（新規ファイルは UTF-8 デフォルト） |
| ライブラリ取得 | 第三者 JS ライブラリは `setup_resources.py` で自動取得（CDN/GitHub） |
| ディレクトリ | `project/src/` にすべての実装コードを配置 |

---

## 3. 実装ファイル一覧

### 3.1 フロントエンド（`project/src/resources/`）

| ファイル名 | 役割 | 設計ID |
|------------|------|--------|
| `resources/ui.html` | メイン HTML。DOM 構造・ライブラリ読み込み | COMP-04 / REQ-UI-08 |
| `resources/style.css` | 全スタイル定義（ダークテーマ・左右ペイン・ステータスバー等） | REQ-UI-01 |
| `resources/app.js` | BridgeClient / TreeView / EditorView / PreviewView / StatusBar / App を 1 ファイルで実装 | COMP-05〜09 |
| `resources/qwebchannel.js` | Qt 公式 QWebChannel JS クライアント（GitHub からダウンロード） | REQ-PROC-11 |
| `resources/marked.min.js` | Markdown → HTML レンダリング（CDN からダウンロード） | REQ-UI-03 |
| `resources/codemirror/codemirror.min.js` | CodeMirror エディタ本体 | REQ-UI-02 |
| `resources/codemirror/codemirror.min.css` | CodeMirror スタイル | REQ-UI-02 |
| `resources/codemirror/mode/markdown/markdown.js` | CodeMirror Markdown モード | REQ-UI-02 |

### 3.2 バックエンド（`project/src/`）

| ファイル名 | 役割 | 設計ID |
|------------|------|--------|
| `main.py` | アプリエントリーポイント。`QApplication` 起動 | §3.1 |
| `main_window.py` | `QMainWindow` 継承。`QWebEngineView`・`QWebChannel` セットアップ・HTML ロード | COMP-01 |
| `backend_bridge.py` | `QObject` 継承。`@pyqtSlot` で JS 公開メソッドを提供し `FileService` に委譲 | COMP-02 |
| `file_service.py` | ファイルI/O全処理（ツリー・読み込み・保存・作成・削除・リネーム・バリデーション） | COMP-03 |
| `requirements.txt` | Python 依存ライブラリ一覧 | §7 引継ぎ |
| `setup_resources.py` | 第三者 JS ライブラリの取得・配置スクリプト | §7 引継ぎ |
| `mdFileReader.spec` | PyInstaller ビルドスペックファイル | §5 ビルド |

---

## 4. 設計との差分

### 4.1 追加実装（設計から変更・追加した点）

| # | 対象 | 変更内容 | 理由 |
|---|------|----------|------|
| 1 | `qwebchannel.js` 取得方法 | PyInstaller 同梱パス配置から、GitHub 公式リポジトリからのダウンロードに変更 | PyQt6 pip インストール版にはスタンドアロンの `qwebchannel.js` が含まれていないため |
| 2 | 新規フォルダ作成 | `createFolder` スロットは未実装とし、`.gitkeep` ファイルを作成してフォルダを生成する簡易実装とした | `BackendBridge` の `createFolder` は詳細設計に未定義だったため。次版で正式スロット追加を推奨 |
| 3 | `resource_path()` ヘルパー | `main_window.py` に定義し、PyInstaller ビルドと開発実行の両方に対応 | 詳細設計どおり |
| 4 | `app.js` モジュール構成 | ES Module ではなく即時実行パターン（`const Xxx = (() => {...})()` ）を採用 | `QWebEngineView` + `QWebChannel` 環境では ES Modules の動作が不安定な可能性があるため |

### 4.2 03詳細設計とのトレーサビリティ

| 設計関数/モジュール | 実装ファイル | 実装完了 |
|--------------------|-------------|---------|
| `FileService.validate_path` | `file_service.py` | ✅ |
| `FileService.get_tree` / `_build_tree_node` | `file_service.py` | ✅ |
| `FileService.read_file` | `file_service.py` | ✅ |
| `FileService.save_file` | `file_service.py` | ✅ |
| `FileService.create_file` | `file_service.py` | ✅ |
| `FileService.delete_file` | `file_service.py` | ✅ |
| `FileService.rename_file` | `file_service.py` | ✅ |
| `BackendBridge.selectFolder` | `backend_bridge.py` | ✅ |
| `BackendBridge.getTree` | `backend_bridge.py` | ✅ |
| `BackendBridge.readFile` | `backend_bridge.py` | ✅ |
| `BackendBridge.saveFile` | `backend_bridge.py` | ✅ |
| `BackendBridge.createFile` | `backend_bridge.py` | ✅ |
| `BackendBridge.deleteFile` | `backend_bridge.py` | ✅ |
| `BackendBridge.renameFile` | `backend_bridge.py` | ✅ |
| `MainWindow._setup_window/webview/channel/html` | `main_window.py` | ✅ |
| `BridgeClient` | `resources/app.js` | ✅ |
| `StatusBar` | `resources/app.js` | ✅ |
| `PreviewView` | `resources/app.js` | ✅ |
| `EditorView` | `resources/app.js` | ✅ |
| `TreeView` | `resources/app.js` | ✅ |
| HTML 構造 (`ui.html`) | `resources/ui.html` | ✅ |
| CSS スタイル (`style.css`) | `resources/style.css` | ✅ |

---

## 5. 単体評価への引継ぎ

### 5.1 テスト対象ファイル

| テスト対象 | ファイル | テスト方式 |
|------------|---------|------------|
| `FileService` 全関数 | `file_service.py` | pytest + 一時ディレクトリ |
| `BackendBridge` スロット | `backend_bridge.py` | PyQt6 QApplication + Mock / pytest-qt |
| フロントエンドロジック | `resources/app.js` | 手動 + ブラウザ開発ツール |

### 5.2 スモークテスト実施結果（2026-03-02）

| テストID | 観点 | 結果 |
|----------|------|------|
| UT-BE-01 | `validate_path`: ベースパス配下は正常通過 | ✅ PASS |
| UT-BE-02 | `validate_path`: `../` を含むパスは `PATH_TRAVERSAL` | ✅ PASS |
| UT-BE-03 | `get_tree`: `.md` ファイルのみがツリーに含まれる | ✅ PASS |
| UT-BE-05 | `read_file`: UTF-8 ファイルを正常に読み込む | ✅ PASS |
| UT-BE-08 | `save_file`: UTF-8 で保存される | ✅ PASS |
| UT-BE-10 | `create_file`: 新規ファイルが作成される | ✅ PASS |
| UT-BE-12 | `delete_file`: ファイルが削除される | ✅ PASS |
| UT-BE-14 | `rename_file`: ファイル名が変更される | ✅ PASS |

### 5.3 未実施テスト（単体評価工程（05）で実施）

| テストID | 観点 | 理由 |
|----------|------|------|
| UT-BE-04 | `get_tree`: 存在しないフォルダは `FOLDER_NOT_FOUND` | 05 工程で実施 |
| UT-BE-06 | `read_file`: Shift-JIS ファイルが文字化けなく読まれる | 05 工程で実施 |
| UT-BE-07 | `read_file`: 存在しないファイルは `FILE_NOT_FOUND` | 05 工程で実施 |
| UT-BE-09 | `save_file`: 権限なしファイルへの保存は `PERMISSION_DENIED` | 05 工程で実施 |
| UT-BE-11 | `create_file`: 同名ファイル存在時は `FILE_EXISTS` | 05 工程で実施 |
| UT-BE-13 | `delete_file`: 存在しないファイルは `FILE_NOT_FOUND` | 05 工程で実施 |
| UT-BE-15 | `rename_file`: 同名ファイル存在時は `FILE_EXISTS` | 05 工程で実施 |
| UT-FE-01〜05 | フロントエンドロジック全般 | 05 工程でアプリ起動後に手動確認 |

---

## 6. PyInstaller ビルド手順

```bash
# 1. 依存ライブラリをインストール
pip install -r requirements.txt

# 2. リソースを取得（初回のみ）
python setup_resources.py

# 3. ビルド実行
pyinstaller mdFileReader.spec

# 出力先: dist/mdFileReader.exe
```

> **補足:** `--onefile` モードでは初回起動時に一時フォルダへ展開するため、初回起動は数秒かかる場合がある。

---

## 7. 工程ゲート（次工程進行確認）

| # | 確認項目 | 状態 |
|---|----------|------|
| 1 | 主要機能が詳細設計どおりに `project/src/` へ実装されている | ✅ 承認済み |
| 2 | スモークテストが全件 PASS している | ✅ 承認済み |
| 3 | 実装差分（対象ファイル・要点・確認結果）が記録されている | ✅ 承認済み |
| 4 | PyInstaller ビルド手順が記録されている | ✅ 承認済み |
| 5 | GitHub 使用者のレビュー承認が完了している | ✅ 承認済み |

---

## 8. 差分開発情報

### 8.1 変更一覧

| 変更種別 | 対象 | 内容 |
|----------|------|------|
| 新規作成 | `project/src/` 全ファイル | `03_detailed_design.md` v1.0.0 をもとに初版を実装 |

---

### 8.2 v1.1.0 変更内容（Shift-JIS 対応）

#### 変更ファイル一覧

| ファイル | 変更内容 |
|----------|----------|
| `file_service.py` | ① `read_file`: chardet 判定後 `shift_jis` / `shift_jis_2004` → `cp932` に正規化を追加<br>② `save_file`: シグネチャを `(file_path, content, encoding="utf-8")` に変更し、指定エンコードで保存<br>③ `UnicodeEncodeError` 時に `ENCODE_SAVE_ERROR` を返す処理を追加<br>④ `_KNOWN_CODES` に `"ENCODE_SAVE_ERROR"` を追加 |
| `backend_bridge.py` | `saveFile` スロットを `@pyqtSlot(str, str, str, result=str)` に変更し `encoding` 引数を追加 |
| `resources/app.js` | ① `BridgeClient.saveFile`: `encoding` 引数追加<br>② `EditorView`: `_currentEncoding` 状態変数を追加<br>③ `EditorView.load()`: `encoding` パラメータ追加・`_currentEncoding` 保持<br>④ `EditorView.save()`: `_currentEncoding` を `BridgeClient.saveFile()` に渡す<br>⑤ `EditorView.clear()`: `_currentEncoding = "utf-8"` リセット追加<br>⑥ `EditorView.getCurrentEncoding()` を公開<br>⑦ `TreeView._onFileClick()`: `res.data.encoding` を `EditorView.load()` に渡す<br>⑧ `TreeView` リネーム後の `load()` 呼び出しに `getCurrentEncoding()` を渡す |

#### 回帰確認観点

| # | 確認観点 | 確認方法 |
|---|----------|----------|
| 1 | UTF-8 ファイルが引き続き正常に読み書きできる | 既存 UTF-8 .md ファイルを開いて編集・保存し内容が保持されること |
| 2 | Shift-JIS ファイルが読み込み時に文字化けしない | cp932 エンコードの .md ファイルを開き日本語が正常表示されること |
| 3 | Shift-JIS ファイルを保存しても文字化けしない | 上記ファイルを編集・保存後、テキストエディタ（cp932）で開き正常であること |
| 4 | UTF-8 で表現できない文字を cp932 ファイルに保存すると `ENCODE_SAVE_ERROR` が返る | 絵文字等を cp932 ファイルに入力して保存し、エラー表示されること |

### 8.2 実装上の既知制約

| # | 制約内容 | 対応方針 |
|---|----------|----------|
| 1 | 新規フォルダ作成が `.gitkeep` 方式の簡易実装 | 次版で `BackendBridge.createFolder` スロットを追加する |
| 2 | `qwebchannel.js` は GitHub 生ソースをダウンロード | PyInstaller ビルド時は `resources/qwebchannel.js` として同梱済みのため問題なし |
| 3 | GUI テスト（`BackendBridge` + `QWebEngineView` 統合動作）は実機（Windows）確認が必要 | 単体評価・結合評価工程で実施 |

