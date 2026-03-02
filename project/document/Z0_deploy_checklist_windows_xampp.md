# Z0 デプロイ確認チェックリスト（Windows Server 2019 / XAMPP Apache）

## 1. 文書情報
- 文書名: デプロイ確認チェックリスト
- プロジェクト名: topDownTest
- 作成日: 2026-02-24
- 作成者: GitHub Copilot
- 版数: v1.1

## 2. 目的
本番環境（Windows Server 2019 / XAMPP Apache）へ手動デプロイする際の、作業漏れ防止と最終受入確認を行う。

## 3. 前提
- 配置先は `C:\xampp\htdocs\github\test1`。
- フロントエンドは PHP、バックエンドは Python を利用する。
- `project/src/backend/database.json` は最新化されていること。

## 4. デプロイ前チェック
- [ ] リポジトリの最新ソースを取得済み。
- [ ] 成果物（要件/設計/評価）を最新化済み。
- [ ] 結合評価結果がOK（正常系・異常系）。
- [ ] システム評価結果が条件付きOK以上。
- [ ] SMTP設定値（`SMTP_HOST`, 必要に応じて `SMTP_PORT`, `SMTP_FROM`）を確認済み。
- [ ] 社内サーバ参照パスと権限を確認済み。

## 5. 配置手順（手動）
1. XAMPP Apache を停止する（必要に応じて）。
2. 配置先 `C:\xampp\htdocs\github\test1` の既存資材をバックアップする。
3. 以下を配置する。
   - `project/src/frontend/` → `C:\xampp\htdocs\github\test1\frontend`
   - `project/src/backend/` → `C:\xampp\htdocs\github\test1\backend`
4. Python 実行環境（`python` または `python3`）がサーバで利用可能であることを確認する。
5. `submit.php` から `app.py` が実行できる権限を確認する。
6. Apache を起動する。

## 6. 初期設定チェック
- [ ] `backend/database.json` が存在する。
- [ ] 日次更新コマンドを実行できる。
  - 例: `python update_database.py --server-root <社内サーバルート> --database database.json`
- [ ] メール通知設定（環境変数）を反映済み。
- [ ] 文字コード設定（UTF-8/Shift-JIS入力を許容するPHP設定・実行環境）を確認済み。
- [ ] Windows Defender/セキュリティ設定で必要な実行がブロックされていない。

## 7. 動作確認（本番同等）
### 7.1 正常系
- [ ] `index.php` にアクセスできる。
- [ ] フォルダパスとメールアドレスを入力できる。
- [ ] 決定押下後、確認ダイアログに入力値が表示される。
- [ ] キャンセル押下で入力値を保持したまま画面に戻る。
- [ ] OK押下で処理が実行され、`status=ok` 相当の結果が得られる。
- [ ] `result.csv` が生成される。
- [ ] `copied_results` に一致対象の `result.html` がコピーされる。
- [ ] SMTP設定時に完了メールが到達する。

### 7.2 異常系
- [ ] 不正パス入力で `INPUT_PATH_NOT_FOUND` が返る。
- [ ] `.i` ファイルなしで `I_FILE_NOT_FOUND` が返る。
- [ ] 不正メール形式で `INVALID_EMAIL` が返る。
- [ ] 判定不能文字コードの `.i` 入力で `INVALID_ENCODING` が返る。
- [ ] 異常時に `run_id` が表示される。
- [ ] トレースバック全文が利用者画面へ露出しない。

## 8. 日次運用チェック
- [ ] `database.json` の日次更新ジョブ（タスクスケジューラ等）を設定した。
- [ ] 更新失敗時の通知先（担当者/連絡手段）を定義した。
- [ ] 障害時のイシュー登録フローを運用メンバーへ共有した。

## 9. ロールバック手順
1. Apache を停止する。
2. 事前バックアップを `C:\xampp\htdocs\github\test1` へ復元する。
3. Apache を再起動する。
4. 画面アクセスと最小動作確認を行う。
5. イシューを登録し、差し戻し工程（01～07の該当工程）を特定する。

## 10. 最終判定
- [ ] デプロイ可
- [ ] 条件付きデプロイ可（条件: ____________________）
- [ ] デプロイ不可（理由: ____________________）

## 11. 実施記録
- 実施日:
- 実施者:
- 対象バージョン:
- 判定:
- 備考:
