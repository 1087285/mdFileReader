# mdFileReader

Markdown ファイル（`.md`）の**表示・編集・保存**ができるスタンドアロンデスクトップアプリケーションです。

- Windows 10 / 11 上で `.exe` をダブルクリックするだけで起動（インストール不要）
- Python / 開発環境の知識なしに利用可能
- CodeMirror によるシンタックスハイライト付き Markdown エディタ
- marked.js によるリアルタイム Markdown プレビュー
- 完全ローカル動作（外部サーバー・ネットワーク接続不要）

---

## 動作環境

| 項目 | 要件 |
|------|------|
| OS | Windows 10 / Windows 11 |
| 配布形式 | PyInstaller 生成 `.exe` 単一ファイル |
| インストール | 不要（任意のフォルダに配置して実行） |
| ネットワーク | 不要（完全ローカル動作） |

---

## 起動方法（エンドユーザー向け）

1. `mdFileReader.exe` を任意のフォルダに配置する
2. ダブルクリックして起動する
3. ツールバーの **「フォルダ選択」** ボタンを押して、Markdown ファイルが入ったフォルダを選択する
4. 左ペインのツリーからファイルをクリックして開く
5. 編集後は **「保存」** ボタン または **`Ctrl+S`** で保存する

---

## 機能一覧

| 機能 | 説明 |
|------|------|
| ファイルツリー表示 | 選択フォルダ配下の `.md` ファイルを左ペインにツリー表示 |
| Markdown エディタ | CodeMirror によるシンタックスハイライト付きエディタ |
| リアルタイムプレビュー | marked.js による Markdown → HTML プレビュー |
| エディタ/プレビュー切替 | ツールバーのトグルボタンで表示/非表示を切替 |
| 保存 | 保存ボタン / `Ctrl+S` で保存。読み込み時のエンコード（UTF-8 / Shift-JIS 等）のまま保存（新規ファイルは UTF-8） |
| 新規ファイル作成 | ツリー右クリック → 「新規ファイル」 |
| ファイル削除 | ツリー右クリック → 「削除」（確認ダイアログあり） |
| 名前変更 | ツリー右クリック → 「名前変更」 |
| 文字コード自動判定 | UTF-8 / Shift-JIS 等を chardet で自動判定。Shift-JIS は Windows 互換（cp932）に正規化して読み込み |

---

## 既知の制約（v1.0.0）

- フォルダ作成は `.gitkeep` ファイル経由（`createFolder` スロット未実装）
- GUI 動作確認は Windows 実機が必要（Linux / macOS 非対応）

---

## 開発者向け情報

### フォルダ構成

- [requests](requests) : 議事録（`minutes_v*.md`）
- [agent](agent) : エージェント定義
- [skills](skills) : スキル定義
- [project/document](project/document) : 工程成果物（要件定義〜リリース）
- [project/src](project/src) : ソースコード（Python / HTML / CSS / JS）
- [project/test](project/test) : pytest テストコード

### 開発環境セットアップ

```bash
# Python 仮想環境作成
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 依存パッケージインストール
pip install -r project/src/requirements.txt

# JS リソースのダウンロード（初回のみ）
python project/src/setup_resources.py

# 開発用起動
python project/src/main.py
```

### PyInstaller ビルド（Windows 実機）

```bash
# Windows 実機で実行すること
pip install pyinstaller

cd project/src
python setup_resources.py   # リソースが未配置の場合
pyinstaller mdFileReader.spec
# dist/mdFileReader.exe が生成される
```

### テスト実行

```bash
pip install pytest
pytest project/test/ -v
```

### Git 運用ルール

- プッシュ時の更新内容（コミットメッセージ・PR説明）は日本語で記載する
- 更新内容は「概要」「変更点」「確認結果」が分かる形式で記載する

### 工程成果物 一覧

- [project/document/01_requirements.md](project/document/01_requirements.md)
- [project/document/02_basic_design.md](project/document/02_basic_design.md)
- [project/document/03_detailed_design.md](project/document/03_detailed_design.md)
- [project/document/04_implementation.md](project/document/04_implementation.md)
- [project/document/05_unit_test.md](project/document/05_unit_test.md)
- [project/document/06_integration_test.md](project/document/06_integration_test.md)
- [project/document/07_system_test.md](project/document/07_system_test.md)
- [project/document/08_release.md](project/document/08_release.md)

## アプリ実行（ひな形）

### 1) フロントエンド（PHP）

- [project/src/frontend](project/src/frontend) を XAMPP の公開ディレクトリへ配置する
- 例: `C:\xampp\htdocs\github\test1\frontend`
- `index.php` にアクセスして、フォルダパスとメールアドレスを入力する

### 2) バックエンド（Python）

- 配置先: [project/src/backend](project/src/backend)
- 実行エントリ: `app.py`
- 実行例:
   - `python app.py --input-path <対象iファイルルート> --email <通知先メール>`

### 3) database.json の日次更新

- 実行スクリプト: `update_database.py`
- 実行例:
   - `python update_database.py --server-root <社内サーバルート> --database database.json`
- 方針: [project/src/backend/database.json](project/src/backend/database.json) は運用上の基準データとしてGit管理対象に残す

### 4) メール通知設定

- `SMTP_HOST` を設定する
- 必要に応じて `SMTP_PORT` と `SMTP_FROM` を設定する
- 未設定時はメール送信をスキップして結果のみ返す

### 5) 実行結果JSON仕様

- 成功時は `status=ok` を返す
- 失敗時は `status=error` を返す

成功時の例:

- `{"status":"ok","run_id":"...","input_path":"...","matched_count":1,"total_count":2,"result_csv":"...","copied_dir":"..."}`

失敗時の例:

- `{"status":"error","error_code":"INPUT_PATH_NOT_FOUND","message":"...","run_id":"..."}`

主な `error_code`:

- `INPUT_PATH_NOT_FOUND`: 指定した入力パスが存在しない
- `INVALID_EMAIL`: メールアドレス形式が不正
- `INVALID_ENCODING`: 文字コードを判定できない入力/ファイル
- `I_FILE_NOT_FOUND`: 指定パス配下に `.i` ファイルがない
- `INTERNAL_ERROR`: 想定外エラー

### 5.1) テストケースJSON（入力/期待値）

- 再利用可能なテストケースは `project/src/test/cases/<case_id>/` 配下に配置
- 各ケースは以下2ファイルで構成
   - `input.json`: 実行入力（前処理、引数、フィクスチャ）
   - `expected.json`: 期待値（終了コード、応答JSONの部分一致条件）
- 実行コマンド:
   - `python3 project/src/test/run_json_tests.py`
- 単一ケース実行:
   - `python3 project/src/test/run_json_tests.py --case-id 001_normal`

### 6) 文字コードの取り扱い

- Web入力値（フォルダパス、メール）は `UTF-8` と `Shift-JIS（Windows-31J/CP932）` を受け付ける
- `.i` ファイル読み込み時も `UTF-8` / `Shift-JIS（Windows-31J/CP932）` を受け付ける
- アプリ内部処理は `UTF-8` に正規化して比較する

## 本番デプロイ（Windows Server 2019 / XAMPP）

デプロイは手動で実施します。配置先は `C:\xampp\htdocs\github\test1` です。

### 配置先

- フロントエンド: `C:\xampp\htdocs\github\test1\frontend`
- バックエンド: `C:\xampp\htdocs\github\test1\backend`

### 手順（要約）

1. 既存配置をバックアップする
2. [project/src/frontend](project/src/frontend) と [project/src/backend](project/src/backend) を配置する
3. Python実行環境と実行権限（`submit.php` → `app.py`）を確認する
4. `backend/database.json` を確認し、必要に応じて `update_database.py` を実行する
5. Apache起動後、`index.php` で正常系・異常系の受入確認を実施する

### 詳細チェックリスト

- デプロイ前チェック、受入確認、日次運用、ロールバックは
   [project/document/Z0_deploy_checklist_windows_xampp.md](project/document/Z0_deploy_checklist_windows_xampp.md)
   を参照してください。

## 備考

- 要求・要件・出力が変更された場合は、[HOWTOUSE.md](HOWTOUSE.md) の更新可否を必ず確認してください。
- 変更が発生した場合は、[project/document/A2_release_notes.md](project/document/A2_release_notes.md) を毎回必ず更新してください。
- プッシュ時は、[project/document/A3_push_operation_guide.md](project/document/A3_push_operation_guide.md) に従い、雛形（`.gitmessage_ja.txt`）を必ず使用してください。
