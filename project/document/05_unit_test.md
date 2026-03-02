# 05 単体評価

## 1. 文書情報
- 文書名: 単体評価記録
- プロジェクト名: topDownTest
- 作成日: 2026-03-02
- 作成者: GitHub Copilot
- 版数: v2.1

## 2. 目的
詳細設計どおりにモジュール単位で実装されていることを、正常系/異常系に加えて、関数ごとにMC/DC（Modified Condition/Decision Coverage）100%達成の観点で確認する。

## 3. 対象モジュール
- `input_validator.py`
- `i_file_scanner.py`
- `function_extractor.py`
- `normalizer.py`
- `matcher.py`
- `error_formatter.py`
- `app.py`
- `exporter.py`
- `notifier.py`（SMTP未設定時の安全動作を含む）
- `encoding_normalizer.py`（UTF-8/Shift-JIS判定とUTF-8正規化）
- `submit.php`（`normalize_to_utf8`）
- `index.php`（submit/cancel/ok イベントハンドラ）

## 4. 実施方法
- バックエンド実装ディレクトリで各モジュール関数を直接呼び出す単体評価スクリプトを実行。
- 条件分岐を含む判定ロジックは、各条件が判定結果へ独立に影響することを示すMC/DCケースを作成し、関数単位で達成率100%を確認する。
- MC/DCケースは「条件一覧」「判定式」「ケース番号」「期待結果」「実測結果」を `project/src/test/05_unit_result.md` に記録する。
- 関数ごとのMC/DC達成状況（達成/未達、未達理由、対応方針）を `project/src/test/05_unit_result.md` に記録する。
- 実施結果は `project/src/test/05_unit_result.md` に記録。
- `result.csv` と `copied_results` がユーザ指定パスと同一階層へ配置されることを確認する。

## 5. MC/DC観点の作成ルール
- 各意思決定（if/elif/複合条件）ごとに、構成する全ての基本条件を識別する。
- 各基本条件について、他条件を固定したまま当該条件のみを変化させ、判定結果が変わるケース対を少なくとも1組用意する。
- 正常系・異常系ケースは、可能な限りMC/DCケースと統合して重複を避ける。
- 入出力境界値（空文字、None、未設定、不正文字コード、パス不存在など）はMC/DCケース作成時に優先的に採用する。

## 6. 判定
- 全対象モジュールの単体ケースがOKであること。
- 条件分岐を持つ判定ロジックで、識別した全基本条件に対するMC/DCケース対が成立し、関数ごとのMC/DC達成率が100%であること。
- 文字コード対応（UTF-8/Shift-JIS/判定不能）の単体評価がOKであること。
- Windows環境想定で、空白を含む入力パスが単一文字列として受理され、正常終了すること。
- 上記を満たした場合、結合評価へ進行可能。

## 7. MC/DC実施結果（2026-03-02）
- `project/src/test/05_unit_result.md` に、判定ID D01〜D09のMC/DC成立を記録。
- 既存JSONケース（`001_normal`〜`005_invalid_encoding`）に加え、補完スクリプトで不足判定を追加確認。
- 補完実行コマンド: `/usr/bin/python3 project/src/test/run_mcdc_supplement_tests.py`
- 補完実行結果: `status=ok`, `total=9`, `passed=9`, `failed=0`
- D09（同名衝突時の連番採番）を追加し、出力重複回避要件の単体評価観点を補完。

## 8. 未評価関数補完結果（2026-02-26）
- `project/src/test/run_frontend_php_unit_tests.php` を実行し、`submit.php` の `normalize_to_utf8`（FE01〜FE04）を直接評価。
- `project/src/test/run_frontend_js_unit_tests.js` を実行し、`index.php` の無名イベントハンドラ3件（FE05〜FE07）を直接評価。
- 実行結果はいずれも `status=ok`（PHP: 4/4、JS: 3/3）。
- これにより、05工程時点の未評価関数は0件。

## 8.1 フロント不正パス表示確認（2026-02-26）
- 実行内容: `php -S 127.0.0.1:18080 -t project/src/frontend` 起動後、`curl` で `submit.php` へ不正パスをPOST。
- 確認観点: 不正パス時にフロントエンドがバックエンド実行前に入力エラー画面を返し、メッセージ「指定されたフォルダパスが存在しません」を表示すること。
- 実行結果: `FE_INVALID_PATH_OK`。
- 判定: FE-D01（入力不正時画面表示）の不正パス観点を満たす。

## 9. 工程ゲート（次工程進行確認）
- 単体評価成果物を作成後、GitHub使用者へレビュー確認を依頼する。
- 承認された場合のみ06工程（結合評価）へ進行する。
- 未承認の場合は05工程で修正し、再レビューを実施する。
- レビュー時は [A0 工程承認チェックリスト](A0_phase_approval_checklist.md) を参照する。
- 05_unit_test.md の更新要否判断は `agent/05_unit_test_agent.md` を唯一の起点とし、差分がない場合は更新しない。

## 10. 05工程での追加反映（2026-02-26）
- 04工程で `index.php` のインラインJavaScriptを `app.js` へ分離したことに伴い、`project/src/test/run_frontend_js_unit_tests.js` を更新した。
- 更新内容: `index.php` 内 `<script>` 抽出前提から、`project/src/frontend/app.js` を優先読込する方式へ変更（後方互換として旧方式も保持）。
- 再実行結果: `node project/src/test/run_frontend_js_unit_tests.js` は `status=ok`, `passed=3/3` を確認。
- 影響評価: FE-D03（責務分離）に追従しつつ、FE-D04（既存導線回帰）の判定結果は維持。

## 11. 05工程での追加反映（v130 → v140）
- `project/src/backend/exporter.py` の同名衝突回避実装（`copied_results_1`, `copied_results_2` ...）に対応し、単体評価観点を追加。
- `project/src/test/run_mcdc_supplement_tests.py` に D09_collision を追加し、連番採番ロジックを直接評価。
- `project/src/test/run_json_tests.py` を再実行し、`001_normal`〜`005_invalid_encoding` の 5/5 OK を確認。
- `003_no_i_files` ケースの前提となる空入力ディレクトリ（`project/src/test/sample_input_empty/`）を補完し、期待どおり `I_FILE_NOT_FOUND` で一致することを確認。

## 12. 05工程での追加反映（v140 → v150）
- 既存単体評価（`run_json_tests.py`、`run_mcdc_supplement_tests.py`）を再実行し、いずれも全件OKを確認。
- 空白を含む入力パス観点を追加し、以下コマンドで `app.py` の正常終了を確認。
	- `/usr/bin/python3 project/src/backend/app.py --input-path "project/src/test/sample input space" --email user@example.com`
- 応答JSONをパースし、`input_path` が `'project/src/test/sample input space'` として受理されることを確認。
- 判定: v150要件（Windows空白パス対応）は現行実装で充足。05工程ではコード変更なし。
