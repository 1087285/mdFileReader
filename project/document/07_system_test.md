# 07 システム評価

## 1. 文書情報
- 文書名: システム評価記録
- プロジェクト名: topDownTest
- 作成日: 2026-03-02
- 作成者: GitHub Copilot
- 版数: v1.7

## 2. 目的
要件（`requests/minutes_v*.md` のうち版数が最大のファイル および `01_requirements.md`）に対して、E2Eで成立することを確認する。

## 3. 評価観点
- 入力: フォルダパス/メールアドレス
- UI: 確認ダイアログ、OK/キャンセル挙動
- 処理: iファイル探索、抽出、正規化、一致判定
- 文字コード: UTF-8/Shift-JIS（Windows-31J/CP932）受理と内部UTF-8正規化
- 出力: `result.csv`、集約コピー先フォルダ（`copied_results` または連番付き）（ユーザ指定パスと同一階層配置）
- 通知: SMTP設定時の送信、未設定時の安全なスキップ
- 異常: 標準エラーJSON返却
- 利用手順: `HOWTOUSE.md` の運用整合

## 4. 実施結果
- システム評価結果: `project/src/test/07_system_result.md`

## 5. 判定
- 重大不具合なし。要件に対してリリース判定は「条件付きOK」。
- 条件: 本番SMTP設定およびWindows Server 2019 / XAMPP環境での最終現地確認を実施すること。

## 5.3 再実施記録（2026-03-02 / v140追従）
- 実行内容:
	- `python3 app.py --input-path ../test/sample_input --email test@example.com`（2回連続実行）
	- `python3 app.py --input-path ../test/not_found_path --email test@example.com`
	- `python3 app.py --input-path ../test/sample_input_empty --email test@example.com`
	- `python3 app.py --input-path ../test/sample_input --email invalid-mail`
	- `python3 project/src/test/run_json_tests.py`
- 実行結果:
	- 正常系: `status=ok`（`copied_dir=/workspaces/topDownTest/project/src/test/copied_results_2` / `copied_results_3`）
	- 異常系: `INPUT_PATH_NOT_FOUND`, `I_FILE_NOT_FOUND`, `INVALID_EMAIL` を確認
	- JSONケース: 5/5 OK（`INVALID_ENCODING` 含む）
- 判定:
	- 同名フォルダ衝突時に連番付きフォルダへ出力され、既存フォルダが上書きされないことを確認。
	- 利用手順参照先を `HOWTOUSE.md` とする要件との整合を確認。

## 5.1 再実施記録（2026-02-26）
- 実行内容: 正常系1件、異常系4件（`INPUT_PATH_NOT_FOUND` / `I_FILE_NOT_FOUND` / `INVALID_EMAIL` / `INVALID_ENCODING`）を順次再実行
- 実行結果: 正常系 `status=ok`、異常系4件は期待どおり `status=error` を返却
- 判定: 要件トレーサビリティ判定を維持し、リリース判定は引き続き「条件付きOK」

## 5.2 再実施記録（2026-02-26 追補）
- 実行内容:
	- `/usr/bin/python3 app.py --input-path ../test/sample_input --email test@example.com`
	- `/usr/bin/python3 app.py --input-path ../test/not_found_path --email test@example.com`
	- `/usr/bin/python3 app.py --input-path ../test/sample_input_empty --email test@example.com`
	- `/usr/bin/python3 app.py --input-path ../test/sample_input --email invalid-mail`
	- `/usr/bin/python3 project/src/test/run_json_tests.py`
	- `php -S 127.0.0.1:18082 -t project/src/frontend` + `curl` POST による不正パス画面表示確認
- 実行結果:
	- 正常系: `status=ok`（`run_id=20260226_061624_125517`）
	- 異常系: `INPUT_PATH_NOT_FOUND`（`run_id=20260226_061632_577177`）、`I_FILE_NOT_FOUND`（`run_id=20260226_061632_696934`）、`INVALID_EMAIL`（`run_id=20260226_061632_824296`）
	- JSONケース: 5/5 OK（`INVALID_ENCODING` を含む）
	- フロントHTTP確認: `SYS_FE_INVALID_PATH_OK`
- 判定: 04〜06工程の更新内容を含め、要件トレーサビリティ判定は維持（差異なし）

## 6. 工程ゲート（完了承認確認）
- システム評価成果物を作成後、GitHub使用者へレビュー確認を依頼する。
- 承認された場合にプロジェクト完了とする。
- 未承認の場合は07工程で修正し、再レビューを実施する。
- レビュー時は [A0 工程承認チェックリスト](A0_phase_approval_checklist.md) を参照する。
- 07_system_test.md の更新要否判断は `agent/07_system_test_agent.md` を唯一の起点とし、差分がない場合は更新しない。

## 7. 再実施記録（2026-02-26 / 06工程後追補）
- 実行内容:
	- `/usr/bin/python3 app.py --input-path ../test/sample_input --email test@example.com`
	- `/usr/bin/python3 app.py --input-path ../test/not_found_path --email test@example.com`
	- `/usr/bin/python3 project/src/test/run_json_tests.py`
	- `php -S 127.0.0.1:18082 -t project/src/frontend` + `curl` POST（不正パス表示確認）
- 実行結果:
	- 正常系: `status=ok`（`run_id=20260226_070600_302453`）
	- 異常系: `INPUT_PATH_NOT_FOUND`（`run_id=20260226_070603_425990`）
	- JSONケース: 5/5 OK（`INVALID_ENCODING` を含む）
	- フロントHTTP確認: `SYS_FE_INVALID_PATH_OK`
- 判定:
	- 05/06工程での更新（`index.php` と `app.js` 分離、JSテスト追従）反映後も、要件トレーサビリティ判定に差異なし。
	- リリース判定は引き続き「条件付きOK」。

## 8. 再実施記録（2026-03-02 / v150追従）
- 実行内容:
	- `/usr/bin/python3 app.py --input-path ../test/sample_input --email test@example.com`
	- `/usr/bin/python3 app.py --input-path ../test/not_found_path --email test@example.com`
	- `/usr/bin/python3 app.py --input-path ../test/sample_input_empty --email test@example.com`
	- `/usr/bin/python3 app.py --input-path ../test/sample_input --email invalid-mail`
	- `/usr/bin/python3 project/src/test/run_json_tests.py`
	- `php -S 127.0.0.1:18083 -t project/src/frontend` + `curl --data-urlencode` による空白パスPOST
- 実行結果:
	- 正常系: `status=ok`（`run_id=20260302_064421_846974`、`copied_dir=/workspaces/topDownTest/project/src/test/copied_results_7`）
	- 異常系: `INPUT_PATH_NOT_FOUND`（`run_id=20260302_064424_566200`）、`I_FILE_NOT_FOUND`（`run_id=20260302_064424_631471`）、`INVALID_EMAIL`（`run_id=20260302_064424_703950`）
	- JSON回帰: 5/5 OK（`INVALID_ENCODING` を含む）
	- フロントHTTP確認: `SYS_FE_SPACE_PATH_OK`
	- フロント応答内JSON: `input_path=/workspaces/topDownTest/project/src/test/sample input space`、`result_csv=/workspaces/topDownTest/project/src/test/result.csv`、`copied_dir=/workspaces/topDownTest/project/src/test/copied_results`
- 判定:
	- v150追加要件（空白を含むパスの受理・連携）をシステム観点で満たす
	- 既存要件（正常系/異常系/出力配置/エラーコード体系）に差異なし
