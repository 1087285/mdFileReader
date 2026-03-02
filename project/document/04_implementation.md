# 04 実装

## 1. 文書情報
- 文書名: 実装記録
- プロジェクト名: topDownTest
- 作成日: 2026-03-02
- 作成者: GitHub Copilot
- 版数: v1.8
## 2. 実装方針
- 詳細設計（`03_detailed_design.md`）に基づき、フロントエンド（PHP）とバックエンド（Python）を分割実装する。
- 異常時は標準エラーJSON（`status`, `error_code`, `message`, `run_id`）を返す。
- 出力は `result.csv` と集約コピー先フォルダを生成し、両者をユーザ指定パスと同一階層に配置したうえで完了通知（SMTP設定時）を行う。
- 集約コピー先フォルダは `copied_results` を第一候補とし、同名衝突時は `copied_results_1`, `copied_results_2` ... を採番して既存フォルダを上書きしない。

## 3. 実装ファイル一覧
### 3.1 フロントエンド
- `project/src/frontend/index.php`
  - 入力項目（フォルダパス、メールアドレス）
  - 確認ダイアログ（OK/キャンセル）
  - キャンセル時の入力保持
- `project/src/frontend/styles.css`
  - 画面スタイル定義（入力、ダイアログ、結果表示の視認性確保）
- `project/src/frontend/app.js`
  - 確認ダイアログ制御（表示/OK/キャンセル）
- `project/src/frontend/submit.php`
  - 入力値受領・最低限のバリデーション
  - `app.py` 実行、JSON結果の表示
  - エラーコード/実行ID表示

### 3.2 バックエンド
- `project/src/backend/app.py`（実行エントリ）
- `project/src/backend/input_validator.py`（入力検証）
- `project/src/backend/i_file_scanner.py`（iファイル探索）
- `project/src/backend/function_extractor.py`（関数抽出）
- `project/src/backend/normalizer.py`（コメント/改行除去）
- `project/src/backend/matcher.py`（一致判定）
- `project/src/backend/exporter.py`（CSV生成・コピー）
- `project/src/backend/notifier.py`（メール通知）
- `project/src/backend/error_formatter.py`（標準エラー応答）
- `project/src/backend/db_updater.py`（database操作）
- `project/src/backend/update_database.py`（日次更新用CLI）

## 4. 設計との差分
- 既存差分を解消: 出力先をバックエンド配下から、ユーザ指定パスと同一階層へ修正。
- メール通知は `SMTP_HOST` 未設定時に送信スキップし、主処理は継続する実装。
- 文字コード対応を追加: フロント入力と `.i` ファイル読込で UTF-8 / Shift-JIS（Windows-31J/CP932）を受け付け、内部処理を UTF-8 に統一。
- 文字コード判定不能時は `INVALID_ENCODING` を返す標準エラー処理を追加。

## 4.1 追加実装（文字コード対応）
- `project/src/frontend/submit.php`
  - POST入力値を `UTF-8` / `SJIS-win` / `CP932` 判定し、UTF-8へ正規化してバックエンドへ引き渡す。
  - 判定不能時は画面上で入力エラー（UTF-8/Shift-JIS利用案内）を表示する。
- `project/src/backend/encoding_normalizer.py`
  - 文字列/バイト列の文字コード判定・UTF-8正規化機能を追加。
  - `.i` ファイル読込用のフォールバック関数を追加。
- `project/src/backend/function_extractor.py`
  - `.i` ファイル読込を UTF-8固定からフォールバック読込へ変更。
- `project/src/backend/error_formatter.py`
  - `EncodingError` を `INVALID_ENCODING` として標準エラー応答へ変換。

## 4.2 03詳細設計とのトレーサビリティ
| 設計ID/設計項目 | 実装ファイル | 実装内容 | 状態 |
|---|---|---|---|
| FE-D01（入力検証・不正時画面表示） | `project/src/frontend/submit.php` | 空入力/メール形式不正/入力パス不存在で入力エラー画面を返却。文字コード判定不能時も入力エラー画面を返却。 | 実装済み |
| FE-D02（確認ダイアログ制御） | `project/src/frontend/index.php` | submit時に確認ダイアログを表示し、キャンセルで入力保持、OKで送信を実行。 | 実装済み |
| 2.6 画面遷移仕様（入力フォーム/確認/入力エラー/結果） | `project/src/frontend/index.php`, `project/src/frontend/submit.php` | 妥当入力は確認ダイアログ経由で実行、不正入力は入力エラー画面、実行後は結果表示を返却。 | 実装済み |
| FE-D05（Windows空白パス送信） | `project/src/frontend/submit.php` | `--input-path` 引数を `escapeshellarg` で単一引数化し、空白を含むパスを欠損なく `app.py` へ送信。 | 実装済み |
| BE-D01（入力検証） | `project/src/backend/input_validator.py` | 入力パス存在とメール形式を検証し、不正時は例外化。 | 実装済み |
| BE-D02（文字コード正規化） | `project/src/backend/encoding_normalizer.py`, `project/src/backend/function_extractor.py` | UTF-8/Shift-JISを判定してUTF-8へ正規化し、`.i` 読込時にも適用。 | 実装済み |
| BE-D03〜BE-D08（探索/抽出/正規化/一致/出力/通知） | `project/src/backend/i_file_scanner.py`, `function_extractor.py`, `normalizer.py`, `matcher.py`, `exporter.py`, `notifier.py`, `app.py` | 詳細設計の処理順で実装し、出力は同一階層配置、標準JSON応答で結果返却。 | 実装済み |
| BE-D09（出力重複回避） | `project/src/backend/exporter.py` | `copied_results` が既存時は連番付き未使用フォルダを採番し、既存フォルダを上書きしない。 | 実装済み |
| BE-D10（Windows空白パス受理） | `project/src/backend/input_validator.py`, `project/src/backend/app.py` | 空白を含むパスを不正扱いせず `os.path.isdir` で実在判定し、探索処理へ引き渡す。 | 実装済み |

## 5. 単体評価への引継ぎ
- テスト対象: 入力検証、探索、抽出、正規化、一致判定、出力、異常整形
- 主要確認点:
  - 可変階層探索と複数関数抽出
  - 正規化後ロジック一致判定
  - `result.csv` と集約コピー先フォルダ生成（ユーザ指定パス同一階層配置）
  - 集約コピー先フォルダ同名衝突時の連番採番（`copied_results_1`, `copied_results_2` ...）
  - 異常時の `error_code` 返却
  - 入力エラー画面遷移（入力不正時）と確認ダイアログ遷移（OK/キャンセル）

## 6. 工程ゲート（次工程進行確認）
- 実装成果物を作成後、GitHub使用者へレビュー確認を依頼する。
- 承認された場合のみ05工程（単体評価）へ進行する。
- 未承認の場合は04工程で修正し、再レビューを実施する。
- レビュー時は [A0 工程承認チェックリスト](A0_phase_approval_checklist.md) を参照する。
- 04_implementation.md の更新要否判断は `agent/04_implementation_agent.md` を唯一の起点とし、差分がない場合は更新しない。

## 7. 04工程での追加反映（2026-02-26）
- `project/src/frontend/submit.php` に、入力パス不存在をバックエンド実行前に判定して入力エラー画面を返す処理を追加。
- `agent/04_implementation_agent.md`、`prompt/04_implementation_prompt.md`、`skills/04_implementation_skill.md` に、`project/src/` 実装反映を必須化する記載を追加。

## 8. 04工程での追加反映（責務分離）
- `project/src/frontend/index.php` からインラインCSS/JavaScriptを除去し、画面骨格生成に責務を集約。
- `project/src/frontend/styles.css` を新規追加し、画面スタイル責務を分離。
- `project/src/frontend/app.js` を新規追加し、確認ダイアログ制御と入力保持責務を分離。
- FE-D03（画面表現責務分離）、FE-D04（既存導線回帰）に対応する実装差分として記録。

## 9. 04工程での追加反映（v130 → v140）
- `project/src/backend/exporter.py` に、集約コピー先フォルダの同名衝突回避（`copied_results`, `copied_results_1`, ...）を実装。
- 既存フォルダの上書きを禁止し、未使用名の新規フォルダへ出力する方式へ変更。
- `project/src/test/run_mcdc_supplement_tests.py` に、同名衝突時の連番採番観点（D09_collision）を追加。
- 利用手順文書として `HOWTOUSE.md` を新規作成し、運用上の参照先を明確化。

## 10. 04工程での追加反映（v140 → v150）
- コード確認の結果、Windows環境で空白を含むフォルダパス対応は既存実装で充足しているため、`project/src/` のコード変更は不要と判断。
- `project/src/frontend/submit.php` の `escapeshellarg($inputPath)` により、空白を含むパスを単一引数で `app.py` へ受け渡す実装を確認。
- `project/src/backend/input_validator.py` の検証は `os.path.isdir(input_path)` を使用しており、空白文字を理由とした棄却がないことを確認。
- 03詳細設計で追加された FE-D05 / BE-D10 のトレーサビリティを本書へ追記。
