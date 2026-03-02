# A0 工程承認チェックリスト

## 1. 文書情報
- 文書名: 工程承認チェックリスト
- プロジェクト名: topDownTest
- 作成日: 2026-02-24
- 作成者: GitHub Copilot
- 版数: v2.0

## 2. 目的
各工程（01〜07）で、次工程へ進む前に GitHub 使用者がレビュー・承認するための共通チェックリストを定義する。

## 3. 運用ルール
- 各工程の成果物作成後に本チェックリストを使用してレビューする。
- 判定は `承認 / 条件付き承認 / 差戻し` のいずれかとする。
- `差戻し` の場合は、同工程で修正後に再レビューする。
- `条件付き承認` の場合は、条件と期限を明記して次工程へ進む。

## 4. 判定基準
| 判定 | 定義 | 次アクション |
|---|---|---|
| 承認 | 受入条件を満たし、重大な懸念がない | 次工程へ進行 |
| 条件付き承認 | 軽微な課題はあるが、進行可能 | 条件を明記して次工程へ進行 |
| 差戻し | 受入条件未達、または重大課題あり | 当該工程へ差戻し・修正 |

## 5. 工程別チェックリスト

### 5.1 01 要件定義
- [ ] 要求/制約/前提が分類されている
- [ ] 機能・非機能・運用・保守要件が定義されている
- [ ] 文字コード要件（UTF-8 / Shift-JIS）が定義されている
- [ ] 入出力（入力パス、メール、result.csv、コピー成果物）が明確である
- [ ] 正常系/異常系の受入条件が定義されている
- [ ] 未決事項と追加確認事項が明示されている

判定: [ ] 承認  [ ] 条件付き承認  [ ] 差戻し

### 5.2 02 基本設計
- [ ] FE/BE の責務分離が明確である
- [ ] データフロー（入力→処理→出力→通知）が定義されている
- [ ] 永続データ/一時データの役割が定義されている
- [ ] 異常時停止・イシュー登録方針が定義されている
- [ ] 03工程へ渡すI/F情報が揃っている

判定: [ ] 承認  [ ] 条件付き承認  [ ] 差戻し

### 5.3 03 詳細設計
- [ ] 画面仕様（入力・確認ダイアログ・送信）が具体化されている
- [ ] バックエンド処理仕様（探索・抽出・正規化・比較・出力・通知）が定義されている
- [ ] ファイル仕様（result.csv / database.json / 一時JSON）が定義されている
- [ ] 例外仕様（入力不正、未存在パス、比較失敗等）が定義されている
- [ ] 04工程が解釈なしで実装可能な粒度である

判定: [ ] 承認  [ ] 条件付き承認  [ ] 差戻し

### 5.4 04 実装
- [ ] 実装が03詳細設計とトレース可能である
- [ ] FE（入力/確認/送信）とBE（比較/出力/通知）が実装済みである
- [ ] 文字コード正規化（UTF-8 / Shift-JIS受理、内部UTF-8統一）が実装されている
- [ ] 出力配置（集約フォルダ・result.csv 同一階層）が実装されている
- [ ] 異常時の標準エラー応答が実装されている
- [ ] 05工程へ渡すテスト対象・既知制約が整理されている

判定: [ ] 承認  [ ] 条件付き承認  [ ] 差戻し

### 5.5 05 単体評価
- [ ] 正常系/異常系のテストケースが実施されている
- [ ] 文字コードケース（UTF-8 / Shift-JIS / 判定不能）が実施されている
- [ ] 期待値・実績・判定（OK/NG）が記録されている
- [ ] NG時の原因工程推定が記録されている
- [ ] 未解決課題と影響が整理されている
- [ ] 06工程へ引継ぎ情報が揃っている

判定: [ ] 承認  [ ] 条件付き承認  [ ] 差戻し

### 5.6 06 結合評価
- [ ] E2Eフロー（入力→比較→出力→通知）が評価されている
- [ ] 境界条件（空/大量/不一致）が評価されている
- [ ] 文字コード異常（`INVALID_ENCODING`）が評価されている
- [ ] 不具合の再現手順と影響範囲が記録されている
- [ ] 07工程へ引継ぐ課題が整理されている
- [ ] 基本設計との整合が確認されている

判定: [ ] 承認  [ ] 条件付き承認  [ ] 差戻し

### 5.7 07 システム評価
- [ ] 要件トレーサビリティに基づく最終評価が実施されている
- [ ] 正常系/異常系の最終判定が記録されている
- [ ] 運用条件（Windows Server 2019 / XAMPP / 手動デプロイ）で成立性を確認している
- [ ] READMEの文字コード運用手順と実装の整合が確認されている
- [ ] README手順と実装の整合が確認されている
- [ ] リリース可否と残課題が明示されている

判定: [ ] 承認  [ ] 条件付き承認  [ ] 差戻し

## 6. 承認記録
| 工程 | 判定 | 条件/差戻し理由 | 承認者 | 承認日 |
|---|---|---|---|---|
| 01 要件定義 | 承認 | - | GitHub使用者 | 2026-02-25 |
| 02 基本設計 | 承認 | - | GitHub使用者 | 2026-02-25 |
| 03 詳細設計 | 承認 | - | GitHub使用者 | 2026-02-25 |
| 04 実装 | 承認 | - | GitHub使用者 | 2026-02-25 |
| 05 単体評価 | 承認 | - | GitHub使用者 | 2026-02-25 |
| 06 結合評価 | 承認 | - | GitHub使用者 | 2026-02-25 |
| 07 システム評価 | 条件付き承認 | 本番SMTP設定およびWindows Server 2019 / XAMPP実機での最終確認実施 | GitHub使用者 | 2026-02-25 |

## 7. 更新記録
| No | 日時 | 更新内容 | 対象 | 実施者 |
|---|---|---|---|---|
| 010 | 2026-02-26 08:35 | 最終成果物更新として、FE責務分離後の05〜07再実行結果をA1/A2へ反映した内容を承認記録へ連携 | `project/document/A1_project_final_summary.md`, `project/document/A2_release_notes.md`, `project/document/05_unit_test.md`, `project/document/06_integration_test.md`, `project/document/07_system_test.md` | GitHub Copilot |
| 009 | 2026-02-26 08:05 | 07工程を進行し、正常系/異常系再実施およびフロントHTTP不正パス表示確認を最終評価証跡へ反映した内容を承認記録へ連携 | `project/document/07_system_test.md`, `project/src/test/07_system_result.md`, `project/document/A2_release_notes.md` | GitHub Copilot |
| 008 | 2026-02-26 07:50 | 06工程を進行し、正常系/異常系再実施およびフロントHTTP不正パス表示確認を結合評価証跡へ反映した内容を承認記録へ連携 | `project/document/06_integration_test.md`, `project/src/test/06_integration_result.md`, `project/src/test/06_integration_abnormal_result.md`, `project/document/A2_release_notes.md` | GitHub Copilot |
| 007 | 2026-02-26 07:35 | 05工程を進行し、不正パス時の入力エラー画面表示を含む単体評価証跡を追加した内容を承認記録へ連携 | `project/document/05_unit_test.md`, `project/src/test/05_unit_result.md`, `project/document/A2_release_notes.md` | GitHub Copilot |
| 006 | 2026-02-26 07:20 | 04工程で `project/src/` 実装反映を必須化し、入力パス不存在時の入力エラー画面表示実装を追加した内容を承認記録へ連携 | `project/src/frontend/submit.php`, `agent/04_implementation_agent.md`, `prompt/04_implementation_prompt.md`, `skills/04_implementation_skill.md`, `project/document/04_implementation.md`, `project/document/A2_release_notes.md` | GitHub Copilot |
| 005 | 2026-02-26 07:05 | 04工程を実施し、入力エラー画面・画面遷移・設計IDの実装トレーサビリティを実装記録へ反映した内容を承認記録へ連携 | `project/document/04_implementation.md`, `project/document/A2_release_notes.md` | GitHub Copilot |
| 004 | 2026-02-26 06:45 | 03工程を実施し、入力エラー画面・画面遷移・設計ID付きテスト観点を詳細設計へ反映した内容を承認記録へ連携 | `project/document/03_detailed_design.md`, `project/document/A2_release_notes.md` | GitHub Copilot |
| 003 | 2026-02-26 06:30 | 02工程を再実施し、入力不正時の画面遷移/UI責務/引継ぎ事項を基本設計へ反映した内容を承認記録へ連携 | `project/document/02_basic_design.md`, `project/document/A2_release_notes.md` | GitHub Copilot |
| 002 | 2026-02-26 03:31 | 01〜07工程の順次実行を再実施し、06/07評価証跡と工程文書を更新 | `project/src/test/06_integration_result.md`, `project/src/test/06_integration_abnormal_result.md`, `project/src/test/07_system_result.md`, `project/document/06_integration_test.md`, `project/document/07_system_test.md` | GitHub Copilot |
| 001 | 2026-02-25 09:20 | JSON再利用テスト方式の反映に伴う評価証跡（05/06/07）およびA1/A2更新を承認記録へ連携 | `project/src/test/05_unit_result.md`, `project/src/test/06_integration_result.md`, `project/src/test/07_system_result.md`, `project/document/A1_project_final_summary.md`, `project/document/A2_release_notes.md` | GitHub Copilot |
