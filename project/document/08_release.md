# 08 リリース

## 1. 文書情報
- 文書名: リリース判定記録
- プロジェクト名: topDownTest
- 作成日: 2026-03-02
- 作成者: GitHub Copilot
- 版数: v1.0

## 2. 入力成果物
- `project/document/07_system_test.md`
- `project/src/test/07_system_result.md`
- `project/document/A1_project_final_summary.md`
- `project/document/A2_release_notes.md`
- `project/document/A3_push_operation_guide.md`
- `project/document/Z0_deploy_checklist_windows_xampp.md`
- `HOWTOUSE.md`

## 3. 最終判定
- 出荷判定: **Conditional Go**

## 4. 判定根拠
- 01〜07工程は承認済み（07は条件付き承認）。
- v150要件（空白を含むパス対応）の証跡を05〜07で確認済み。
  - 05: 空白パス単体実行で `status=ok`
  - 06: フロントHTTP確認 `FE_SPACE_PATH_OK`
  - 07: システム確認 `SYS_FE_SPACE_PATH_OK`
- 既存要件（正常系/異常系/出力配置/エラーコード）に差異なし。

## 5. リリース条件（未完了タスク）
1. 本番SMTP設定を実施すること。
2. Windows Server 2019 / XAMPP 実機で最終確認を実施すること。
3. GitHub使用者の明示合意後に、タグ作成・push・GitHub Release作成を実施すること。

## 6. 成果物整合確認
- A1/A2/A3 は 2026-03-02 時点で最新化済み。
- 利用手順は `HOWTOUSE.md` を参照先として整合済み。
- デプロイ手順は `Z0_deploy_checklist_windows_xampp.md` と整合済み。

## 7. タグ・リリース実施状況
- 新規タグ作成: 未実施（合意待ち）
- GitHub Releases本体作成: 未実施（合意待ち）
- 既存公開リリース: `v1.2.0`（https://github.com/1087285/topDownTest/releases/tag/v1.2.0）
