# 08 リリースプロンプト

## 目的
07システム評価の承認結果を受け、リリース向け成果物を最終更新し、出荷可否を確定する。

## 入力
- `project/document/07_****.md`
- システム評価結果（`project/src/test/`）
- `project/document/A1_project_final_summary.md`
- `project/document/A2_release_notes.md`
- `project/document/A3_push_operation_guide.md`
- `README.md`
- `skills/08_release_skill.md`

## 指示
1. 07工程の判定結果と未解決課題を確認する。
2. `A2_release_notes.md` を最新の変更内容・制約・確認結果で更新する。
3. `A3_push_operation_guide.md` を最新の運用手順・確認観点で更新する。
4. `A1_project_final_summary.md` に工程01～07の最終結果を統合する。
5. `README.md` と .exe 配布物の整合（起動手順・動作環境・Windows 10/11・インストール不要）を確認する。
6. 出荷判定（Go / Conditional Go / No-Go）と残課題を明示する。
7. GitHub使用者の承認と push 実行可否の合意後、リリースタグ（例: `vX.Y.Z`）を作成して push する。
8. GitHub Releases 本体を作成し、本文に `A2_release_notes.md` を使用する。PyInstaller生成 .exe を配布物としてアッチメントする。
9. 公開されたリリースURLを `A1_project_final_summary.md` と `A2_release_notes.md` に追記する。

## 出力形式
- リリース関連成果物（Markdown）を `project/document/` に保存
- 最終判定サマリ（Go / Conditional Go / No-Go）を記載
- リリースタグ（`vX.Y.Z`）を作成・push
- GitHub Releases 本体（リリースノート付き）を作成
- リリースURLを A1/A2 に反映

## 停止条件
- 07成果物に判定根拠不足がある場合は停止し、07へ差戻しを明示する。
- リリース判定に必要な証跡不足がある場合は停止し、不足工程を明示する。

## 工程ゲート（完了承認確認）
- 成果物生成後、完了判定の前にGitHub使用者へチャットベースのレビューを実施する。
- チャットでは変更前の状態、変更後の状態と変更の考え方、懸念事項・特記事項（ある場合）、判断を仰ぎたい質問（ある場合）を説明する。
- GitHub使用者の承認後、pushまで進めるかを確認し、明示的な合意後に push とリリース作成を実施する。
- GitHub使用者が承認した場合にリリース工程完了とする。未承認の場合は08工程で修正し再確認を実施する。
