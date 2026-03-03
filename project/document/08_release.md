# 08 リリース

## 1. 文書情報

| 項目 | 内容 |
|------|------|
| 文書名 | リリース記録 |
| 版数 | v1.3.0 |
| 作成日 | 2026-03-02 |
| 最終更新日 | 2026-03-03（v1.3.0 D&D 禁止仕様反映） |
| 作成者 | GitHub Copilot（08_release_agent） |
| 参照元 | `project/document/07_system_test.md` v1.3.0 |
| ステータス | レビュー待ち |

---

## 2. 入力成果物

| 工程 | 成果物 | 状態 |
|------|--------|------|
| 工程1 要件定義 | `project/document/01_requirements.md` v1.3.0 | ✅ 承認済み |
| 工程2 基本設計 | `project/document/02_basic_design.md` v1.3.0 | ✅ 承認済み |
| 工程3 詳細設計 | `project/document/03_detailed_design.md` v1.3.0 | ✅ 承認済み |
| 工程4 実装 | `project/document/04_implementation.md` v1.3.0 + `project/src/` | ✅ 承認済み |
| 工程5 単体評価 | `project/document/05_unit_test.md` v1.3.0（pytest 25件 PASS） | ✅ 承認済み |
| 工程6 結合評価 | `project/document/06_integration_test.md` v1.3.0（pytest 24件 PASS） | ✅ 承認済み |
| 工程7 システム評価 | `project/document/07_system_test.md` v1.3.0（Conditional Go 判定） | ✅ 承認済み |

---

## 3. 最終判定

| 判定 | 内容 |
|------|------|
| **Conditional Go（条件付き可）** | Python 層全機能（pytest 49件 PASS）確認済み。Windows 実機受入テスト完了をリリース最終条件とする。 |

---

## 4. 判定根拠

| 確認区分 | 件数 | 結果 |
|---------|------|------|
| 単体テスト（pytest） | 25 | ✅ 全 PASS |
| 結合テスト（pytest） | 24 | ✅ 全 PASS |
| GUI 受入テスト（実機） | 24 | ⚠️ 実機確認待ち |
| 発見不具合 | 2（BUG-BE-01, BUG-IT-01） | ✅ 全て是正済み |
| HTTP サーバー不使用 | — | ✅ コードレビュー確認済み |
| HTML リソース同梱 | — | ✅ setup_resources.py 実行済み |

---

## 5. リリース条件（未完了タスク）

Windows 実機での以下の作業完了後、最終 Go 判定とする。

| # | タスク | 担当 | 状態 |
|---|--------|------|------|
| 1 | `setup_resources.py` を実行してリソースを配置 | リリース担当者 | ✅ 実行済み（リソース同梱確認済み） |
| 2 | `pyinstaller project/src/mdFileReader.spec` で実行ファイルビルド | リリース担当者 | ⚠️ Windows 実機ビルド待ち |
| 3 | `ACC-OK-01～15`（正常系受入テスト）全件手動確認 | リリース担当者 | ⚠️ 実機確認待ち |
| 4 | `ACC-NG-01〜09`（異常系受入テスト）全件手動確認（`ACC-NG-03` は pytest 確認済み） | リリース担当者 | ⚠️ 実機確認待ち |
| 5 | `git tag v1.3.0 && git push origin v1.3.0` 実行 | リリース担当者 | ⬜ 未実施 |
| 6 | GitHub Releases 本体作成・`A2_release_notes.md` の v1.3.0 セクションを本文として反映 | リリース担当者 | ⬜ 未実施 |
| 7 | `mdFileReader.exe`（Windows 実機ビルド）を GitHub Releases にアタッチ | リリース担当者 | ⬜ 未実施 |
| 8 | リリース URL を `A1_project_final_summary.md` と `A2_release_notes.md` に記入 | リリース担当者 | ⬜ 未実施 |

---

## 6. 成果物整合確認

| 成果物 | 確認項目 | 状態 |
|--------|---------|------|
| `README.md` | アプリ概要・起動方法・機能一覧・開発者向け情報が最新化されている | ✅ 更新済み（工程8 v1.3.0） |
| `A1_project_final_summary.md` | 工程1〜8の判定結果が統合されている | ✅ 更新済み（工程8 v1.3.0） |
| `A2_release_notes.md` | v1.3.0 の変更点・既知制約・リリース URL 欄が記載されている | ✅ 更新済み（URL はリリース後記入） |
| `A3_push_operation_guide.md` | push 手順・リリースタグ手順が v1.3.0 に整合している | ✅ 更新済み（工程8 v1.3.0） |
| `project/src/requirements.txt` | 依存パッケージが固定バージョンで記載されている | ✅ 確認済み |
| `project/src/mdFileReader.spec` | PyInstaller ビルド設定が正しい | ✅ 確認済み |
| `project/src/setup_resources.py` | JS/CSS リソースの自動ダウンロードが正常動作する | ✅ 実行確認済み |

---

## 7. タグ・リリース実施状況

| 項目 | 状態 |
|------|------|
| リリースタグ `v1.3.0` | ⬜ 未作成 |
| GitHub Releases 本体 | ⬜ 未作成 |
| Linux 実行ファイルビルド | ✅ `project/src/dist/mdFileReader` 生成済み（Linux ELF） |
| GitHub Actions ワークフロー | ✅ `.github/workflows/build-release.yml` 作成済み |
| Windows `.exe` 自動ビルド | ⬜ タグ push 後に実行 |
| `.exe` アタッチ（GitHub Releases） | ⬜ 未実施 |
| リリース URL の A1/A2 への反映 | ⬜ 未記入 |

---

## 8. 既知制約（v1.3.0）

| # | 制約 | 暫定対応 | 推奨対応（次バージョン） |
|---|------|---------|---------------------|
| 1 | `createFolder` スロット未実装 | フォルダパスに `.md` ファイルを作成すると親フォルダが自動生成される（`.gitkeep` ワークアラウンド） | `BackendBridge` に `createFolder` スロットを追加 |
| 2 | Linux / macOS 非対応 | — | Qt のクロスプラットフォーム性を活かして対応可能 |

---

## 9. 工程ゲート

| # | 確認項目 | 状態 |
|---|----------|------|
| 1 | 工程1〜7 の全成果物が承認済みである | ✅ 確認済み |
| 2 | pytest 自動テスト 49 件が全 PASS している | ✅ 確認済み |
| 3 | 発見不具合が全て是正済みである | ✅ BUG-BE-01, BUG-IT-01 是正済み |
| 4 | README.md・A1/A2/A3 が最新化されている | ✅ 更新済み |
| 5 | リリース条件（実機受入テスト・ビルド・タグ・Releases）が明示されている | ✅ §5 に記載済み |
| 6 | GitHub 使用者のレビュー承認が完了している | ⬜ レビュー待ち |

---

## 10. 差分開発情報

### 10.1 変更一覧

| 変更種別 | 対象 | 内容 |
|----------|------|------|
| 新規作成 | 本文書全体 | `07_system_test.md` v1.0.0 をもとに初版を新規作成 |
| 更新 | `README.md` | mdFileReader v1.3.0 の仕様（D&D 禁止）に整合するよう更新 |
| 更新 | `project/document/A1_project_final_summary.md` | プロジェクト最終サマリを v1.3.0 に更新 |
| 更新 | `project/document/A2_release_notes.md` | リリースノートへ v1.3.0 を追加 |
| 更新 | `project/document/A3_push_operation_guide.md` | リリースタグ手順を v1.3.0 に更新 |

### 10.2 v1.1.0 変更内容（Shift-JIS 対応）

| 変更種別 | 対象 | 内容 |
|----------|------|------|
| 更新 | 入力成果物 §2 | 全工程成果物を v1.1.0 に更新 |
| 更新 | 最終判定 §3 | pytest 45 件 PASS に更新 |
| 更新 | 判定根拠 §4 | UT 24件・IT 21件・GUI 20件に更新 |
| 更新 | リリース条件 §5 | ACC-OK-13（ENCODE_SAVE_ERROR 実機確認）まで正常系受入テストを拡張 |

### 10.3 v1.2.0 変更内容（D&D 許可対応）

| 変更種別 | 対象 | 内容 |
|----------|------|------|
| 入力成果物更新 | §2 全工程 | 全工程成果物を v1.2.0 に更新 |
| 最終判定更新 | §3 | pytest 58 件 PASS に更新 |
| 判定根拠更新 | §4 | UT 32件・IT 26件・GUI 25件に更新 |
| リリース条件更新 | §5 | 正常系受入テストを ACC-OK-16、異常系を ACC-NG-09 まで拡張 |

### 10.4 v1.3.0 変更内容（D&D 禁止仕様反映）

| 変更種別 | 対象 | 内容 |
|----------|------|------|
| 入力成果物更新 | §2 全工程 | 全工程成果物を v1.3.0 に更新 |
| 最終判定更新 | §3 | pytest 49 件 PASS に更新 |
| 判定根拠更新 | §4 | UT 25件・IT 24件・GUI 24件に更新 |
| リリース条件更新 | §5 | 受入テストを ACC-OK-15、ACC-NG-09 に整合 |
| 実施状況更新 | §7 | v1.3.0 タグ/Releases は未実施状態に更新 |
