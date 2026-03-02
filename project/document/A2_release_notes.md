# A2 リリースノート（毎回更新前提）

## 1. 文書情報
- 文書名: リリースノート（毎回更新前提）
- プロジェクト名: topDownTest
- 初版作成日: 2026-02-25
- 最終更新日: 2026-03-02
- 作成者: GitHub Copilot
- 版数: v2.7
- 文書種別: 継続更新（Living Document / Mandatory Update）

## 2. 運用ポリシー（必須）
- 本文書は、**変更が発生するたびに必ず更新**する。
- 変更の種類（要件・設計・実装・試験・運用）を問わず、1変更につき1エントリを追加する。
- 工程成果物（`01`〜`07`、`A0`、`A1`、`A3`、`Z0`、`README.md`）の更新と同一タイミングで本書を更新する。
- 本書未更新の変更は「未完了」とみなす。

## 3. 更新タイミング
1. 変更内容を反映（コード/文書）
2. 該当テストまたは確認を実施
3. 本書へエントリ追加（本章テンプレート準拠）
4. `A1_project_final_summary.md` の判定影響を確認

## 4. 記載テンプレート（毎回同形式）
| No | 日時 | 区分 | 対象 | 変更内容 | 確認結果 | 影響範囲 | 担当 |
|---|---|---|---|---|---|---|---|
| 例: 001 | 2026-02-25 02:41 | 実装/評価 | `submit.php`, `function_extractor.py` | UTF-8/Shift-JIS対応追加 | 単体・結合・システム評価OK | FE/BE/運用手順 | GitHub Copilot |

## 5. 変更履歴（最新が先頭）
| No | 日時 | 区分 | 対象 | 変更内容 | 確認結果 | 影響範囲 | 担当 |
|---|---|---|---|---|---|---|---|
| 018 | 2026-03-02 16:50 | 評価/リリース文書 | `project/document/05_unit_test.md`, `project/src/test/05_unit_result.md`, `project/document/06_integration_test.md`, `project/src/test/06_integration_result.md`, `project/src/test/06_integration_abnormal_result.md`, `project/document/07_system_test.md`, `project/src/test/07_system_result.md`, `project/document/A1_project_final_summary.md`, `project/document/A2_release_notes.md`, `project/document/A3_push_operation_guide.md`, `project/document/08_release.md` | v150要件（空白パス対応）の05〜07再評価証跡を反映し、08工程の出荷判定（Conditional Go）を文書化 | 05: JSON 5/5 OK・空白パス実行OK、06: `FE_SPACE_PATH_OK`、07: `SYS_FE_SPACE_PATH_OK` を確認。A1/A2/A3/08の整合更新完了 | 評価証跡、最終判定、リリース運用文書 | GitHub Copilot |
| 017 | 2026-03-02 16:20 | リリース/最終文書 | `project/document/A1_project_final_summary.md`, `project/document/A2_release_notes.md`, GitHub Release `v1.2.0` | GitHub Release `v1.2.0` を公開し、A1へ公開URL（https://github.com/1087285/topDownTest/releases/tag/v1.2.0）を追記 | `gh release view v1.2.0 --json name,tagName,isDraft,isPrerelease,url` で公開状態（`isDraft=false`）を確認、`git push origin main` でA1追記反映済み | リリース配布情報、最終報告参照性、運用文書整合 | GitHub Copilot |
| 016 | 2026-03-02 15:55 | 要件/実装/評価/運用文書 | `project/document/01_requirements.md`, `project/document/02_basic_design.md`, `project/document/03_detailed_design.md`, `project/document/04_implementation.md`, `project/document/05_unit_test.md`, `project/document/06_integration_test.md`, `project/document/07_system_test.md`, `project/src/backend/exporter.py`, `project/src/test/run_mcdc_supplement_tests.py`, `project/src/test/sample_input_empty/.gitkeep`, `HOWTOUSE.md`, `README.md`, `project/document/A1_project_final_summary.md`, `project/document/A2_release_notes.md`, `project/document/A3_push_operation_guide.md` | v140差分（同名フォルダ衝突時の連番回避、HOWTOUSE運用）を01〜07工程へ反映し、08工程としてA1/A2/A3を最終更新 | `run_mcdc_supplement_tests.py`（9/9 OK）, `run_json_tests.py`（5/5 OK）, 07再実行で `copied_results_2`/`copied_results_3` 確認、異常系 `INPUT_PATH_NOT_FOUND`/`I_FILE_NOT_FOUND`/`INVALID_EMAIL` と `INVALID_ENCODING` を確認 | 出力処理、テスト証跡、最終文書、リリース判断資料 | GitHub Copilot |
| 015 | 2026-02-26 08:35 | 実装/試験/最終文書 | `project/src/frontend/index.php`, `project/src/frontend/styles.css`, `project/src/frontend/app.js`, `project/src/test/run_frontend_js_unit_tests.js`, `project/document/05_unit_test.md`, `project/document/06_integration_test.md`, `project/document/07_system_test.md`, `project/document/A1_project_final_summary.md`, `project/document/A2_release_notes.md` | フロント責務分離（CSS/JS外出し）を反映し、JS単体テストを新構成へ追従、05〜07再実行結果と最終サマリを更新 | `run_frontend_js_unit_tests.js`（3/3 OK）, `run_json_tests.py`（5/5 OK）, HTTP確認 `FE_HTTP_INVALID_PATH_OK` / `SYS_FE_INVALID_PATH_OK`, 正常系 run_id=`20260226_070600_302453` | FE構成、試験資産、最終成果物整合 | GitHub Copilot |
| 014 | 2026-02-26 08:20 | 要件/運用/文書 | `agent/01_requirements_agent.md`, `prompt/01_requirements_prompt.md`, `skills/01_requirements_skill.md`, `agent/02_basic_design_agent.md`, `prompt/02_basic_design_prompt.md`, `README.md`, `project/document/07_system_test.md`, `project/document/A2_release_notes.md` | 議事録入力を固定版（`minutes_v120.md`）から `requests/minutes_v*.md` の最新版（版数最大）参照へ統一し、01/02工程および運用手順へ反映 | 文書差分確認で反映完了、`minutes_v120.md` の固定参照は履歴用途（`A2_release_notes.md`）のみであることを検索確認 | 工程入力整合、運用手順、要件トレーサビリティ | GitHub Copilot |
| 013 | 2026-02-26 08:05 | システム評価/文書 | `project/document/07_system_test.md`, `project/src/test/07_system_result.md`, `project/document/A2_release_notes.md`, `project/document/A0_phase_approval_checklist.md` | 07工程を進行し、正常系/異常系再実施に加えてフロントHTTP不正パス表示確認（SYS_FE_INVALID_PATH_OK）を最終証跡へ反映 | `app.py` 正常系 `status=ok`、異常系3ケース期待どおり、`run_json_tests.py`（5/5 OK）、HTTP確認 `SYS_FE_INVALID_PATH_OK` | 07工程証跡、最終トレーサビリティ、完了承認判断材料 | GitHub Copilot |
| 012 | 2026-02-26 07:50 | 結合評価/文書 | `project/document/06_integration_test.md`, `project/src/test/06_integration_result.md`, `project/src/test/06_integration_abnormal_result.md`, `project/document/A2_release_notes.md`, `project/document/A0_phase_approval_checklist.md` | 06工程を進行し、正常系/異常系の再実施結果に加えてフロントHTTP不正パス表示（FE_HTTP_INVALID_PATH_OK）を結合評価証跡へ追加 | `update_database.py`更新OK、`app.py`正常系`status=ok`、異常系3ケース期待どおり、`run_json_tests.py`（5/5 OK）、HTTP確認 `FE_HTTP_INVALID_PATH_OK` | 06工程証跡、FE-BE連携異常系、07工程引継ぎ精度 | GitHub Copilot |
| 011 | 2026-02-26 07:35 | 単体評価/文書 | `project/document/05_unit_test.md`, `project/src/test/05_unit_result.md`, `project/document/A2_release_notes.md`, `project/document/A0_phase_approval_checklist.md` | 05工程進行として、04追加実装（不正パス時の入力エラー画面）の単体評価証跡を追加し、05成果物を更新 | `run_json_tests.py`（5/5 OK）, `run_mcdc_supplement_tests.py`（8/8 OK）, `run_frontend_php_unit_tests.php`（4/4 OK）, `run_frontend_js_unit_tests.js`（3/3 OK）, HTTP確認 `FE_INVALID_PATH_OK` | 05工程証跡、FE異常系品質、06工程引継ぎ精度 | GitHub Copilot |
| 010 | 2026-02-26 07:20 | 実装/工程定義 | `project/src/frontend/submit.php`, `agent/04_implementation_agent.md`, `prompt/04_implementation_prompt.md`, `skills/04_implementation_skill.md`, `project/document/04_implementation.md` | 04工程で `project/src/` 実装を必須化し、入力パス不存在をフロントで入力エラー画面表示する実装を追加 | `php -l project/src/frontend/submit.php` で構文OK、文書差分確認で反映完了を確認 | FE異常系UX、04工程運用ルール、05工程引継ぎ品質 | GitHub Copilot |
| 009 | 2026-02-26 07:05 | 実装/文書 | `project/document/04_implementation.md`, `project/document/A2_release_notes.md`, `project/document/A0_phase_approval_checklist.md` | 04工程実施として、03詳細設計の入力エラー画面・画面遷移・設計IDを実装記録へトレースし、単体評価引継ぎ観点を更新 | 文書差分確認により04工程成果物と工程履歴の更新完了を確認 | 実装トレーサビリティ、05工程引継ぎ、工程管理 | GitHub Copilot |
| 008 | 2026-02-26 06:45 | 詳細設計/文書 | `project/document/03_detailed_design.md`, `project/document/A2_release_notes.md` | 03工程実施として、入力エラー画面・画面遷移・設計ID付きテスト観点を詳細設計へ反映 | 文書差分確認により03工程成果物の更新完了を確認 | 詳細設計品質、04工程実装明確化 | GitHub Copilot |
| 007 | 2026-02-26 06:20 | 基本設計/文書 | `project/document/02_basic_design.md`, `project/document/A2_release_notes.md` | 02工程実施として、入力不正時の画面遷移・UI責務・引継ぎ事項を基本設計へ明記 | 文書差分確認により02工程成果物の更新完了を確認 | 基本設計品質、03工程引継ぎ明確化 | GitHub Copilot |
| 006 | 2026-02-26 06:10 | 基本設計/文書 | `project/document/02_basic_design.md`, `project/document/A2_release_notes.md` | 要件トレーサビリティに「入力不正時の画面表示」マッピングを追加 | 文書差分確認により反映完了を確認 | 要件トレーサビリティ、後工程設計整合 | GitHub Copilot |
| 005 | 2026-02-26 06:00 | 要件/文書 | `minutes_v120.md`, `agent/01_requirements_agent.md`, `prompt/01_requirements_prompt.md`, `skills/01_requirements_skill.md`, `agent/02_basic_design_agent.md`, `prompt/02_basic_design_prompt.md`, `project/document/01_requirements.md`, `project/document/07_system_test.md`, `README.md` | `minutes_v120.md` 差分（不正入力時の画面表示要件）を工程定義と成果物に反映し、参照議事録を v120 に統一 | 文書差分確認により反映完了を確認（`minutes_v110.md` 参照は履歴用途1件のみ） | 要件トレーサビリティ、工程入力整合、運用文書 | GitHub Copilot |
| 004 | 2026-02-26 03:31 | 評価/文書 | `project/src/test/06_integration_result.md`, `project/src/test/06_integration_abnormal_result.md`, `project/src/test/07_system_result.md`, `project/document/06_integration_test.md`, `project/document/07_system_test.md`, `project/document/A0_phase_approval_checklist.md` | 01〜07工程の順次実行を再実施し、結合/システム評価証跡と工程記録を更新 | `/usr/bin/python3 project/src/test/run_json_tests.py`（5/5 OK）, `/usr/bin/python3 project/src/test/run_mcdc_supplement_tests.py`（8/8 OK）, 正常系/異常系E2E再実行OK | 評価証跡、工程管理、リリース判断資料 | GitHub Copilot |
| 003 | 2026-02-25 09:10 | 実装/評価/文書 | `project/src/test/run_json_tests.py`, `project/src/test/cases/*`, `README.md`, `project/src/test/05_unit_result.md`, `project/src/test/06_integration_result.md`, `project/src/test/07_system_result.md` | テスト入力JSON/期待値JSONの再利用方式を追加し、JSON駆動テスト実行と各評価結果への引き継ぎ記録を反映 | `/usr/bin/python3 project/src/test/run_json_tests.py` 実行結果: 5/5 OK | テスト運用、評価証跡、後工程引き継ぎ | GitHub Copilot |
| 002 | 2026-02-25 02:50 | 運用/文書 | `A3_push_operation_guide.md`, `.gitmessage_ja.txt`, `README.md` | プッシュ運用ガイドを追加し、雛形使用必須ルールを明文化 | `git push origin main` 成功（Exit Code: 0） | Git運用手順、変更記録品質 | GitHub Copilot |
| 001 | 2026-02-25 02:41 | 要件/設計/実装/評価 | `minutes_v110.md`, `01`〜`07`, `README.md` | 文字コード要件（UTF-8/Shift-JIS）追加と実装・評価反映 | 05:14/14 OK、06:正常+異常4ケースOK、07:条件付きOK | 入力処理、`.i`読込、異常応答、運用チェック | GitHub Copilot |

## 6. 更新チェックリスト
- [ ] 変更内容を1行で要約した
- [ ] 対象ファイル/工程を明記した
- [ ] 確認結果（コマンド・判定）を記録した
- [ ] 影響範囲（機能/運用/文書）を記載した
- [ ] A1と矛盾がないことを確認した
