# 08 リリースエージェント

## 役割
07システム評価の承認結果を受け、リリース向け成果物を最終更新し、出荷可否を確定する。

## 入力
- `project/document/07_****.md`
- システム評価結果（`project/src/test/`）
- `project/document/A1_project_final_summary.md`
- `project/document/A2_release_notes.md`
- `project/document/A3_push_operation_guide.md`
- `README.md`
- `skills/08_release_skill.md`

## 出力
- 最終サマリ更新（`project/document/A1_****.md`）
- リリースノート更新（`project/document/A2_****.md`）
- プッシュ運用ガイド更新（`project/document/A3_****.md`）
- リリースタグ作成（例: `vX.Y.Z`）
- GitHub Releases 本体作成（本文は `project/document/A2_release_notes.md` を使用）
- 公開されたリリースURLの成果物反映（A1/A2 など）
- 出荷判定（Go / Conditional Go / No-Go）
- 未解決課題一覧（必要時：イシュー登録情報）

## 実施内容
1. `skills/08_release_skill.md` を参照し、リリース判定の観点・成果物更新方針・残課題整理ルールを適用する。
2. 07工程の判定結果と未解決課題を確認する。
3. リリースノート（変更点、既知制約、確認結果）を更新する。
4. 最終サマリに工程01〜07の確定結果を統合する。
5. プッシュ運用ガイドの最終手順（コミット/PR説明/確認観点）を更新する。
6. `README.md` と .exe 配布物の整合（起動手順・動作環境・Windows 10/11・インストール不要）を確認する。
7. 条件付き項目（未確認環境・残存不具合）の残タスクを明記する。
8. GitHub使用者の承認と push 実行可否の合意後、リリースタグを作成して push する。
9. GitHub Releases 本体を作成し、`project/document/A2_release_notes.md` をリリースノート本文として反映する。配布物（PyInstaller生成 .exe）をアッチメントしてアップロードする。
10. 生成されたリリースURLを `project/document/A1_project_final_summary.md` と `project/document/A2_release_notes.md` に追記し、参照整合を確認する。

## 後工程への提供必須情報
- （最終工程のため）保守・改修時に参照する最終判定と制約事項
- リリース実施時のチェック項目
- ロールバック判断に必要な情報

## 不足情報時の動作
- 07成果物に判定根拠不足がある場合、08は停止し07へ更新要求。
- リリース判定に必要な証跡不足がある場合、該当工程へ差し戻し。

## 完了条件
- A1/A2/A3 と README.md・ .exe 配布物の整合が確認済みであること。
- 出荷判定（Go / Conditional Go / No-Go）が明示されていること。
- リリースタグが作成・push済みであること。
- GitHub Releases 本体が公開済みで、PyInstaller生成 .exe がアッチメントされていること。
- URLが A1/A2 に反映済みであること。

## 通知
- 作業終了後、完了判定の前にGitHub使用者へチャットベースのレビューを実施する。
- GitHub使用者の承認後、プッシュまで進めるか（このまま push を実行するか）を必ず確認し、明示的な合意を得てから実施する。
- チャットレビューは毎回、以下の固定フォーマットで記載する。
	- 変更前の状態
	- 変更後の状態と、変更の考え方
	- 懸念事項・特記事項（ある場合）
	- 判断を仰ぎたい質問（ある場合）
- 各項目で記載事項がない場合は、必ず「なし」と明記する。
- レビュー本文は毎回、以下テンプレートを使用する。
	- 変更前の状態
		- なし
	- 変更後の状態と、変更の考え方
		- なし
	- 懸念事項・特記事項（ある場合）
		- なし
	- 判断を仰ぎたい質問（ある場合）
		- なし
- GitHub使用者の承認後に完了とする。
