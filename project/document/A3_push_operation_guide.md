# A3 プッシュ運用ガイド

## 1. 文書情報

| 項目 | 内容 |
|------|------|
| 文書名 | プッシュ運用ガイド |
| 版数 | v1.0.0 |
| 作成日 | 2026-03-02 |
| 作成者 | GitHub Copilot（08_release_agent） |

---

## 2. 目的

ソースコード・成果物の GitHub push / リリースタグ作成を安全に行うための手順を定める。

---

## 3. 運用ポリシー

| # | ポリシー |
|---|----------|
| 1 | コミットメッセージ・PR 説明は日本語で記載する |
| 2 | 更新内容は「概要」「変更点」「確認結果」の 3 項目を必ず記載する |
| 3 | push 前に `pytest project/test/ -v` を実行し全 PASS を確認する |
| 4 | リリースタグ（`vX.Y.Z`）は工程8 完了後にのみ作成する |

---

## 4. コミットメッセージ雛形

```
[概要]

〇〇の実装 / 〇〇工程の完了 / バグ修正: 〇〇

[変更点]
- project/src/file_service.py: PermissionError 正規化対応
- project/test/test_file_service.py: pytest 22ケース追加
- project/document/05_unit_test.md: 単体評価記録を作成

[確認結果]
- pytest project/test/ -v: 41 / 41 PASS
- Python 構文チェック: 全ファイル OK
```

---

## 5. 標準 push 手順

```bash
# 1. 差分確認
git status
git diff

# 2. テスト実行
cd /workspaces/mdFileReader
.venv/bin/pytest project/test/ -v

# 3. ステージング
git add -A

# 4. コミット（雛形を使用）
git commit

# 5. プッシュ
git push origin main
```

---

## 5.1 リリース時の追加手順（工程8）

```bash
# ビルド環境に応じた手順

# Linux / Codespace 環境でのビルド（Linux ELF binary）
cd /workspaces/mdFileReader/project/src
/workspaces/mdFileReader/.venv/bin/pyinstaller mdFileReader.spec
# → project/src/dist/mdFileReader（Linux ELF, 192MB）が生成される

# Windows 環境でのビルド（Windows .exe）
# cd project\src
# pyinstaller mdFileReader.spec
# → dist\mdFileReader.exe が生成される

# 3. リリースタグ作成・push（Linux / Codespace 側）
git tag v1.0.0
git push origin v1.0.0

# 4. GitHub Releases 作成
# https://github.com/1087285/mdFileReader/releases/new
# タグ: v1.0.0
# リリースノート本文: A2_release_notes.md の v1.0.0 セクションをコピー
# Attachments: mdFileReader.exe をアップロード

# 5. リリース URL を A1/A2 に記入してコミット・push
```

---

## 6. push 前チェックリスト

| # | 確認項目 |
|---|----------|
| 1 | `pytest project/test/ -v` が全 PASS |
| 2 | `python -m py_compile project/src/*.py` で構文エラーなし |
| 3 | コミットメッセージに「概要」「変更点」「確認結果」が含まれている |
| 4 | `project/document/` 配下の成果物が最新化されている |
| 5 | （リリース時）Windows 実機受入テストが全件完了している |

---

## 7. 更新履歴

| 版数 | 日付 | 変更内容 |
|------|------|----------|
| v1.0.0 | 2026-03-02 | 初版作成 |

