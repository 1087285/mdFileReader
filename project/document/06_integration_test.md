# 06 結合評価

## 1. 文書情報

| 項目 | 内容 |
|------|------|
| 文書名 | 結合評価記録 |
| 版数 | v1.1.0 |
| 作成日 | 2026-03-02 |
| 作成者 | GitHub Copilot（06_integration_test_agent） |
| 参照元 | `project/document/02_basic_design.md` v1.1.0, `project/document/05_unit_test.md` v1.1.0 |
| ステータス | 承認済み（2026-03-02） |

---

## 2. 目的

基本設計書（02）で定義したサブシステム連携が正しく動作することを評価する。  
具体的には `BackendBridge` → `FileService` の委譲フローおよびパストラバーサルガードの連携動作を検証する。

---

## 3. 実施範囲

| 評価区分 | 範囲 | 実施方法 |
|---------|------|---------|
| Python 層 E2E（IT-01〜IT-08） | BackendBridge + FileService の統合呼び出し | 自動（pytest） |
| QWebChannel 連携（IT-09） | JS BridgeClient ↔ BackendBridge のメソッド呼び出し・コールバック | 手動（Windows 実機） |
| 完全 E2E フロー（IT-10） | フォルダ選択→ツリー表示→編集→保存の全画面フロー | 手動（Windows 実機） |

---

## 4. 実施方法

| 項目 | 内容 |
|------|------|
| テストフレームワーク | pytest 9.0.2 |
| Python バージョン | Python 3.12.3 (venv) |
| テストファイル | `project/test/test_integration.py` |
| 実行コマンド | `.venv/bin/pytest project/test/test_integration.py -v` |
| IT-09〜10 | Windows 実機 GUI 手動確認 |

---

## 5. 判定

### 5.1 自動テスト結果（IT-01〜IT-08）

| テストID | 観点 | 区分 | 実績 |
|---------|------|------|------|
| IT-01 | BackendBridge.getTree → ツリー JSON が返る | 正常 | ✅ PASS |
| IT-01 | BackendBridge.getTree → 非存在フォルダは FOLDER_NOT_FOUND | 異常 | ✅ PASS |
| IT-02 | BackendBridge.readFile → ファイル内容・パスが返る | 正常 | ✅ PASS |
| IT-02 | BackendBridge.readFile → 非存在ファイルは FILE_NOT_FOUND | 異常 | ✅ PASS |
| IT-02 | BackendBridge.readFile → フォルダ外アクセスは PATH_TRAVERSAL | 異常 | ✅ PASS |
| IT-03 | BackendBridge.saveFile → ファイル内容が更新される | 正常 | ✅ PASS |
| IT-03 | BackendBridge.saveFile → 新規ファイルへの保存が可能 | 正常 | ✅ PASS |
| IT-03a | BackendBridge.saveFile → cp932 エンコード指定で Shift-JIS ファイルが正しく保存される | 正常 | ✅ PASS |
| IT-03b | BackendBridge.saveFile → cp932 で表現できない文字は `ENCODE_SAVE_ERROR` | 異常 | ✅ PASS |
| IT-04 | BackendBridge.createFile → 空ファイルが作成される | 正常 | ✅ PASS |
| IT-04 | BackendBridge.createFile → 重複ファイルは FILE_EXISTS | 異常 | ✅ PASS |
| IT-05 | BackendBridge.deleteFile → ファイルが削除される | 正常 | ✅ PASS |
| IT-05 | BackendBridge.deleteFile → 非存在ファイルは FILE_NOT_FOUND | 異常 | ✅ PASS |
| IT-06 | BackendBridge.renameFile → ファイル名が変更される | 正常 | ✅ PASS |
| IT-06 | BackendBridge.renameFile → 同名移動先は FILE_EXISTS | 異常 | ✅ PASS |
| IT-07 | readFile フォルダ外アクセスブロック | 異常 | ✅ PASS |
| IT-07 | saveFile フォルダ外アクセスブロック | 異常 | ✅ PASS |
| IT-07 | createFile フォルダ外アクセスブロック | 異常 | ✅ PASS |
| IT-07 | deleteFile フォルダ外アクセスブロック | 異常 | ✅ PASS |
| IT-07 | renameFile 移動先フォルダ外アクセスブロック | 異常 | ✅ PASS |
| IT-08 | Python 層 E2E: 作成→読込→保存→リネーム→削除の連続操作 | 正常 | ✅ PASS |

**自動テスト集計: 21 / 21 PASS（pytest、BackendBridge + FileService 統合）**

---

### 5.2 手動確認テスト（IT-09〜IT-10）

> ⚠️ `QWebChannel` + JavaScript DOM 操作は GUI 実機が必要なため Linux devcontainer では実行不可。  
> Windows 実機での手動確認が必要。

| テストID | 確認手順 | 期待結果 | 状態 |
|---------|---------|---------|------|
| IT-09a | アプリ起動 → JS `backend.getTree(path, cb)` がコールバックで JSON を受信する | `cb` が呼ばれ `res.success === true` でツリーデータが届く | ⚠️ 未実施 |
| IT-09b | アプリ起動 → JS `backend.readFile(path, cb)` がコールバックで内容を受信する | `res.data.content` にファイル内容が含まれる | ⚠️ 未実施 |
| IT-09c | アプリ起動 → JS `backend.saveFile(path, content, encoding, cb)` がコールバックで成功を返す | `res.success === true` かつファイルが指定エンコードで更新される | ⚠️ 未実施 |
| IT-09d | アプリ起動 → JS `backend.selectFolder(cb)` でフォルダ選択ダイアログが開く | `cb` が選択パス文字列で呼ばれる | ⚠️ 未実施 |
| IT-10 | アプリ起動 → フォルダ選択 → ツリー表示 → ファイルをクリック → 編集 → Ctrl+S → ステータスバー確認 | ツリー描画・エディタ表示・保存成功メッセージが正常に動作する | ⚠️ 未実施 |

---

## 6. 不具合一覧

| 不具合ID | 対象 | 概要 | 原因工程 | 是正内容 | 状態 |
|---------|------|------|---------|---------|------|
| BUG-IT-01 | `backend_bridge.py` | `from PyQt6.QtWidgets import QFileDialog` のトップレベル import が `libGL.so.1` 依存のため headless 環境でインポートエラー | 工程4（実装） | `selectFolder` メソッド内に遅延 import（`from PyQt6.QtWidgets import QFileDialog`）へ変更 | ✅ 是正済み |

---

## 7. 工程ゲート（次工程進行確認）

| # | 確認項目 | 状態 |
|---|----------|------|
| 1 | IT-01〜IT-08 の全 pytest テストが PASS している | ✅ 確認済み（19 / 19 PASS） |
| 2 | フォルダ外アクセスが BackendBridge 全メソッドでブロックされる | ✅ 確認済み（IT-07 × 5ケース） |
| 3 | Python 層 E2E フロー（作成→読込→保存→リネーム→削除）が正常動作する | ✅ 確認済み（IT-08） |
| 4 | IT-09〜IT-10 の未実施事項がシステム評価への引継ぎ事項として記録されている | ✅ §8 に記録済み |
| 5 | 発見不具合 BUG-IT-01 が是正済みであり、是正後テストが PASS している | ✅ 確認済み |
| 6 | GitHub 使用者のレビュー承認が完了している | ✅ 承認済み（2026-03-02） |

---

## 8. システム評価への引継ぎ事項

| # | 引継ぎ項目 | 詳細 |
|---|------------|------|
| 1 | IT-09（QWebChannel 連携）未実施 | Windows 実機で JS BridgeClient → BackendBridge のコールバックフローを手動確認 |
| 2 | IT-10（完全 E2E）未実施 | Windows 実機でフォルダ選択→ツリー→編集→保存の全画面フローを確認 |
| 3 | selectFolder（QFileDialog）未確認 | Qt の GUI ダイアログが正しく表示・選択パスを返すことを実機で確認 |
| 4 | PyInstaller ビルド後の動作未確認 | `.exe` 単体起動での全機能確認をシステム評価で実施 |

---

## 9. 差分開発情報

### 9.1 変更一覧

| 変更種別 | 対象 | 内容 |
|----------|------|------|
| 新規作成 | 本文書全体 | `05_unit_test.md` v1.0.0 をもとに初版を新規作成 |
| バグ修正 | `project/src/backend_bridge.py` | BUG-IT-01: QFileDialog をトップレベルから `selectFolder` 内の遅延 import へ移動 |
| 新規作成 | `project/test/test_integration.py` | pytest 結合テストファイル（19 ケース、IT-01〜IT-08） |

---

### 9.2 v1.1.0 変更内容（Shift-JIS 対応）

| 変更種別 | 対象 | 内容 |
|----------|------|------|
| テスト内容変更 | `test_integration.py` – IT-03 / IT-07 | `bridge.saveFile()` 呼び出しに `encoding` 引数を追加 |
| テスト追加 | `test_integration.py` – IT-03a | cp932 エンコード指定で Shift-JIS 保存 → バイト列を cp932 で読み直して内容一致を確認 |
| テスト追加 | `test_integration.py` – IT-03b | 絵文字を cp932 ファイルへ保存 → `ENCODE_SAVE_ERROR` を確認 |
| 手動確認内容変更 | IT-09c | `backend.saveFile` 呼び出しのシグネチャを `(path, content, encoding, cb)` に更新 |
