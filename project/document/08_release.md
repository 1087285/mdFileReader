# 08 リリース

## 1. 文書情報

| 項目 | 内容 |
|------|------|
| 文書名 | リリース記録 |
| 版数 | v1.0.0 |
| 作成日 | 2026-03-02 |
| 作成者 | GitHub Copilot（08_release_agent） |
| 参照元 | `project/document/07_system_test.md` v1.0.0 |
| ステータス | レビュー待ち（08工程再実行 2026-03-02） |

---

## 2. 入力成果物

| 工程 | 成果物 | 状態 |
|------|--------|------|
| 工程1 要件定義 | `project/document/01_requirements.md` v1.0.0 | ✅ 承認済み |
| 工程2 基本設計 | `project/document/02_basic_design.md` v1.0.0 | ✅ 承認済み |
| 工程3 詳細設計 | `project/document/03_detailed_design.md` v1.0.0 | ✅ 承認済み |
| 工程4 実装 | `project/document/04_implementation.md` v1.0.0 + `project/src/` | ✅ 承認済み |
| 工程5 単体評価 | `project/document/05_unit_test.md` v1.0.0（pytest 22件 PASS） | ✅ 承認済み |
| 工程6 結合評価 | `project/document/06_integration_test.md` v1.0.0（pytest 19件 PASS） | ✅ 承認済み |
| 工程7 システム評価 | `project/document/07_system_test.md` v1.0.0（Conditional Go 判定） | ✅ 承認済み |

---

## 3. 最終判定

| 判定 | 内容 |
|------|------|
| **Conditional Go（条件付き可）** | Python 層全機能（pytest 41件 PASS）確認済み。Windows 実機受入テスト完了をリリース最終条件とする。 |

---

## 4. 判定根拠

| 確認区分 | 件数 | 結果 |
|---------|------|------|
| 単体テスト（pytest） | 22 | ✅ 全 PASS |
| 結合テスト（pytest） | 19 | ✅ 全 PASS |
| GUI 受入テスト（実機） | 17 | ⚠️ 実機確認待ち |
| 発見不具合 | 2（BUG-BE-01, BUG-IT-01） | ✅ 全て是正済み |
| HTTP サーバー不使用 | — | ✅ コードレビュー確認済み |
| HTML リソース同梱 | — | ✅ setup_resources.py 実行済み |

---

## 5. リリース条件（未完了タスク）

Windows 実機での以下の作業完了後、最終 Go 判定とする。

| # | タスク | 担当 | 状態 |
|---|--------|------|------|
| 1 | `setup_resources.py` を実行してリソースを配置 | リリース担当者 | ✅ 実行済み（リソース同梱確認済み） |
| 2 | `pyinstaller project/src/mdFileReader.spec` で実行ファイルビルド | 08エージェント（自動） | ✅ ビルド完了（`project/src/dist/mdFileReader`、Linux ELF、192MB）⚠️ Windows .exe は Windows 実機でのビルドが必要 |
| 3 | `ACC-OK-01〜10`（正常系受入テスト）全件手動確認 | リリース担当者 | ⚠️ 実機確認待ち |
| 4 | `ACC-NG-01〜07`（異常系受入テスト）全件手動確認（`ACC-NG-03` は pytest 確認済み） | リリース担当者 | ⚠️ 実機確認待ち |
| 5 | `git tag v1.0.0 && git push origin v1.0.0` 実行 | リリース担当者 | ⚠️ 実機確認後に実行 |
| 6 | GitHub Releases 本体作成・`A2_release_notes.md` の v1.0.0 セクションを本文として反映 | リリース担当者 | ⚠️ タグ作成後に実行 |
| 7 | `mdFileReader.exe`（Windows 実機ビルド）を GitHub Releases にアタッチ | リリース担当者 | ⚠️ Windows ビルド後に実行 |
| 8 | リリース URL を `A1_project_final_summary.md` と `A2_release_notes.md` に記入 | リリース担当者 | ⚠️ Releases 作成後に記入 |

---

## 6. 成果物整合確認

| 成果物 | 確認項目 | 状態 |
|--------|---------|------|
| `README.md` | アプリ概要・起動方法・機能一覧・開発者向け情報が最新化されている | ✅ 更新済み（工程8） |
| `A1_project_final_summary.md` | 工程1〜8の判定結果が統合されている | ✅ 更新済み（工程8） |
| `A2_release_notes.md` | v1.0.0 の変更点・既知制約・リリース URL 欄が記載されている | ✅ 更新済み（URL 欄は実機後に記入） |
| `A3_push_operation_guide.md` | push 手順・リリースタグ手順が記載されている | ✅ 更新済み（工程8） |
| `project/src/requirements.txt` | 依存パッケージが固定バージョンで記載されている | ✅ 確認済み |
| `project/src/mdFileReader.spec` | PyInstaller ビルド設定が正しい | ✅ 確認済み |
| `project/src/setup_resources.py` | JS/CSS リソースの自動ダウンロードが正常動作する | ✅ 実行確認済み |

---

## 7. タグ・リリース実施状況

| 項目 | 状態 |
|------|------|
| リリースタグ `v1.0.0` | ⚠️ 実機受入テスト完了後に作成・push |
| GitHub Releases 本体 | ⚠️ タグ作成後に作成 |
| Linux 実行ファイルビルド | ✅ `project/src/dist/mdFileReader`（ELF 64-bit, 192MB）生成済み |
| Windows `.exe` ビルド | ⚠️ Windows 実機での PyInstaller ビルドが必要 |
| `.exe` アタッチ（GitHub Releases） | ⚠️ Windows ビルド後にアタッチ |
| リリース URL の A1/A2 への反映 | ⚠️ Releases 作成後に記入 |

---

## 8. 既知制約（v1.0.0）

| # | 制約 | 暫定対応 | 推奨対応（次バージョン） |
|---|------|---------|---------------------|
| 1 | `createFolder` スロット未実装 | フォルダパスに `.md` ファイルを作成すると親フォルダが自動生成される（`.gitkeep` ワークアラウンド） | `BackendBridge` に `createFolder` スロットを追加 |
| 2 | Linux / macOS 非対応 | — | Qt のクロスプラットフォーム性を活かして対応可能 |

---

## 9. 工程ゲート

| # | 確認項目 | 状態 |
|---|----------|------|
| 1 | 工程1〜7 の全成果物が承認済みである | ✅ 確認済み |
| 2 | pytest 自動テスト 41 件が全 PASS している | ✅ 確認済み |
| 3 | 発見不具合が全て是正済みである | ✅ BUG-BE-01, BUG-IT-01 是正済み |
| 4 | README.md・A1/A2/A3 が最新化されている | ✅ 更新済み |
| 5 | リリース条件（実機受入テスト・ビルド・タグ・Releases）が明示されている | ✅ §5 に記載済み |
| 6 | GitHub 使用者のレビュー承認が完了している | ✅ 承認済み（2026-03-02） |

---

## 10. 差分開発情報

### 10.1 変更一覧

| 変更種別 | 対象 | 内容 |
|----------|------|------|
| 新規作成 | 本文書全体 | `07_system_test.md` v1.0.0 をもとに初版を新規作成 |
| 更新 | `README.md` | topDownTest の旧記述を mdFileReader v1.0.0 の内容に全面更新 |
| 新規作成 | `project/document/A1_project_final_summary.md` | プロジェクト最終サマリ v1.0.0 を初版作成 |
| 新規作成 | `project/document/A2_release_notes.md` | リリースノート v1.0.0 を初版作成 |
| 新規作成 | `project/document/A3_push_operation_guide.md` | push 運用ガイド v1.0.0 を初版作成 |
| 更新 | `agent/08_release_agent.md` | PyInstaller ビルド工程（ステップ6）を追加 |
| 更新 | 本文書（08_release.md） | 08工程再実行に伴い §5・§7・§10 を更新（2026-03-02） |

