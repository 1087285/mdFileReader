# 06 結合評価

## 1. 文書情報
- 文書名: 結合評価記録
- プロジェクト名: topDownTest
- 作成日: 2026-03-02
- 作成者: GitHub Copilot
- 版数: v1.7

## 2. 目的
基本設計どおりに、フロントエンド/バックエンド/出力生成が連携することを確認する。

## 3. 実施範囲
- 正常系: DB更新→比較実行→CSV/コピー成果物生成
- 異常系: 入力パス不正、iファイル未検出、メール不正、文字コード不正
- 配置要件: `result.csv` と集約コピーがユーザ指定パスと同一階層へ出力されること
- 衝突回避要件: 集約コピー先フォルダが同名の場合は連番付きフォルダ（`copied_results_1` など）へ出力されること
- 運用文書要件: 利用手順文書は `HOWTOUSE.md` を参照すること

## 4. 実施結果
- 正常系結果: `project/src/test/06_integration_result.md`
- 異常系結果: `project/src/test/06_integration_abnormal_result.md`

## 5. 判定
- 正常系・異常系とも期待どおり。
- 追加した文字コード異常ケース（`INVALID_ENCODING`）も期待どおり。
- 同名フォルダ衝突時の連番出力（`copied_results_1`）も期待どおり。
- システム評価へ進行可能。

## 5.3 再実施記録（2026-03-02 / v140追従）
- 実行内容:
	- `python3 update_database.py --server-root ../test/sample_internal_server --database database.json`
	- `python3 app.py --input-path ../test/sample_input --email test@example.com`
	- `python3 app.py --input-path ../test/sample_input --email test@example.com`（連続実行で同名衝突確認）
	- `python3 app.py --input-path ../test/not_found_path --email test@example.com`
	- `python3 app.py --input-path ../test/sample_input_empty --email test@example.com`
	- `python3 app.py --input-path ../test/sample_input --email invalid-mail`
	- `python3 project/src/test/run_json_tests.py --case-id 005_invalid_encoding`
- 実行結果:
	- 正常系1回目: `status=ok`, `copied_dir=/workspaces/topDownTest/project/src/test/copied_results`
	- 正常系2回目: `status=ok`, `copied_dir=/workspaces/topDownTest/project/src/test/copied_results_1`
	- 異常系: `INPUT_PATH_NOT_FOUND`, `I_FILE_NOT_FOUND`, `INVALID_EMAIL`, `INVALID_ENCODING` を期待どおり確認
- 判定:
	- フロント→バックエンド→出力生成→異常応答の結合動作は維持
	- v140追加要件（同名衝突時の連番回避）を満たす
	- 利用手順の参照先として `HOWTOUSE.md` を確認済み

## 8. 再実施記録（2026-03-02 / v150追従）
- 実行内容:
	- `python3 update_database.py --server-root ../test/sample_internal_server --database database.json`
	- `python3 app.py --input-path ../test/sample_input --email test@example.com`
	- `python3 app.py --input-path ../test/not_found_path --email test@example.com`
	- `python3 app.py --input-path ../test/sample_input_empty --email test@example.com`
	- `python3 app.py --input-path ../test/sample_input --email invalid-mail`
	- `php -S 127.0.0.1:18082 -t project/src/frontend` + `curl --data-urlencode` による空白パスPOST
- 実行結果:
	- 正常系: `status=ok`, `matched_count=1`, `total_count=2`, `copied_dir=/workspaces/topDownTest/project/src/test/copied_results_5`
	- 異常系: `INPUT_PATH_NOT_FOUND`, `I_FILE_NOT_FOUND`, `INVALID_EMAIL` を期待どおり確認
	- フロントHTTP確認: `FE_SPACE_PATH_OK`
	- フロント応答内JSON: `input_path=/workspaces/topDownTest/project/src/test/sample input space`、`result_csv=/workspaces/topDownTest/project/src/test/result.csv`、`copied_dir=/workspaces/topDownTest/project/src/test/copied_results_6`
- 判定:
	- v150追加要件（空白を含むパスの受理・連携）を結合観点で満たす
	- 既存の正常系/異常系連携動作に影響なし

## 5.1 再実施記録（2026-02-26）
- 実行内容: `run_json_tests.py` をケース単位（`001_normal`〜`005_invalid_encoding`）で順次実行
- 実行結果: 5ケースすべて `status=ok`（各1/1 合格）
- 判定: フロント→バックエンド→出力/異常応答の連携結果は前回記録と一致

## 5.2 再実施記録（2026-02-26 追補）
- 実行内容:
	- `/usr/bin/python3 update_database.py --server-root ../test/sample_internal_server --database database.json`
	- `/usr/bin/python3 app.py --input-path ../test/sample_input --email test@example.com`
	- `/usr/bin/python3 app.py --input-path ../test/not_found_path --email test@example.com`
	- `/usr/bin/python3 app.py --input-path ../test/sample_input_empty --email test@example.com`
	- `/usr/bin/python3 app.py --input-path ../test/sample_input --email invalid-mail`
	- `php -S 127.0.0.1:18081 -t project/src/frontend` + `curl` POST による不正パス画面表示確認
- 実行結果:
	- 正常系は `status=ok`（`matched_count=1`, `total_count=2`）
	- 異常系は `INPUT_PATH_NOT_FOUND`, `I_FILE_NOT_FOUND`, `INVALID_EMAIL` を期待どおり返却
	- フロントHTTP確認は `FE_HTTP_INVALID_PATH_OK`
- 判定: 04/05の更新内容を含め、06工程の連携要件を満たすことを再確認

## 6. 工程ゲート（次工程進行確認）
- 結合評価成果物を作成後、GitHub使用者へレビュー確認を依頼する。
- 承認された場合のみ07工程（システム評価）へ進行する。
- 未承認の場合は06工程で修正し、再レビューを実施する。
- レビュー時は [A0 工程承認チェックリスト](A0_phase_approval_checklist.md) を参照する。
- 06_integration_test.md の更新要否判断は `agent/06_integration_test_agent.md` を唯一の起点とし、差分がない場合は更新しない。

## 7. 再実施記録（2026-02-26 / 04-05更新追従）
- 正常系（DB更新→比較実行）
	- `update_database.py` 実行後、`app.py --input-path ../test/sample_input --email test@example.com` を実施
	- 結果: `status=ok`, `matched_count=1`, `total_count=2`
- 異常系（個別実行）
	- 入力パス不正: `INPUT_PATH_NOT_FOUND`
	- iファイル未検出: `I_FILE_NOT_FOUND`
	- メール形式不正: `INVALID_EMAIL`
- 回帰スイート
	- `project/src/test/run_json_tests.py` 実行結果: `total=5`, `passed=5`, `failed=0`
- フロントHTTP連携
	- `php -S 127.0.0.1:18081 -t project/src/frontend` + `curl` POST を実施
	- 結果: `FE_HTTP_INVALID_PATH_OK`
- 影響評価
	- `index.php` から `app.js` へのJavaScript分離後も、フロント→バックエンド→異常表示の結合動作は維持
	- 出力配置要件（`result.csv` / `copied_results` 同一階層配置）に影響なし
