# topDownTest

機能安全業務における単体評価テスト結果の紐づけアプリ開発用リポジトリです。

利用者向けの実行手順は [HOWTOUSE.md](HOWTOUSE.md) を参照してください。

## フォルダ構成

- [requests](requests) : 議事録（`minutes_v*.md` を版管理、最新版を入力に使用）
- [agent](agent) : エージェント定義
- [prompt](prompt) : プロンプト定義
- [skills](skills) : スキル定義
- [project/document](project/document) : 工程成果物（要件定義・設計など）
- [project/src/frontend](project/src/frontend) : フロントエンド（PHP）
- [project/src/backend](project/src/backend) : バックエンド（Python）
- [project/src/test](project/src/test) : テスト関連

## 使い方（開発開始時）

1. [requests](requests) 配下の `minutes_v*.md` から版数が最大のファイル（最新版）を参照して工程の対象と成果物を確認する
2. 工程に応じた md ファイルを [project/document](project/document) に作成する
   - 要件定義: `01_****.md`
   - 基本設計: `02_****.md`
   - 詳細設計: `03_****.md`
3. 実装は [project/src/frontend](project/src/frontend) と [project/src/backend](project/src/backend) に分けて進める
4. 評価結果は [project/src/test](project/src/test) に整理する

## 文書命名ルール

- 基本の工程文書は `01`〜`07` の接頭辞を使用する（例: `01_****.md`〜`07_****.md`）
- 特殊用途のチェックリストは英数字接頭辞を使用する
   - 工程承認チェックリスト: [project/document/A0_phase_approval_checklist.md](project/document/A0_phase_approval_checklist.md)
   - デプロイ確認チェックリスト: [project/document/Z0_deploy_checklist_windows_xampp.md](project/document/Z0_deploy_checklist_windows_xampp.md)

## Git運用ルール

- プッシュ時に記載する更新内容（コミットメッセージ・PR説明・変更履歴）は日本語で記載する。
- 更新内容は「概要」「変更点」「確認結果」が分かる形式で記載する。

### コミットテンプレート

- テンプレートファイル: [.gitmessage_ja.txt](.gitmessage_ja.txt)
- 設定コマンド（リポジトリ単位）:
   - `git config commit.template .gitmessage_ja.txt`
- 設定後は `git commit` 実行時に、同じ構成（概要/変更点/確認結果）で文面を作成できる。

## project/document 一覧

- [project/document/01_requirements.md](project/document/01_requirements.md)
- [project/document/02_basic_design.md](project/document/02_basic_design.md)
- [project/document/03_detailed_design.md](project/document/03_detailed_design.md)
- [project/document/04_implementation.md](project/document/04_implementation.md)
- [project/document/05_unit_test.md](project/document/05_unit_test.md)
- [project/document/06_integration_test.md](project/document/06_integration_test.md)
- [project/document/07_system_test.md](project/document/07_system_test.md)
- [project/document/A0_phase_approval_checklist.md](project/document/A0_phase_approval_checklist.md)
- [project/document/A2_release_notes.md](project/document/A2_release_notes.md)
- [project/document/A3_push_operation_guide.md](project/document/A3_push_operation_guide.md)
- [project/document/Z0_deploy_checklist_windows_xampp.md](project/document/Z0_deploy_checklist_windows_xampp.md)

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
