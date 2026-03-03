# 02 基本設計

## 1. 文書情報

| 項目 | 内容 |
|------|------|
| 文書名 | 基本設計書 |
| 版数 | v1.2.0 |
| 作成日 | 2026-03-02 |
| 最終更新日 | 2026-03-02（v1.2.0 差分更新） |
| 作成者 | GitHub Copilot（02_basic_design_agent） |
| 参照元 | `project/document/01_requirements.md` v1.2.0、`requests/minutes_v120.md` |
| ステータス | レビュー待ち |

---

## 2. システム概要

本アプリは **PyQt6 ベースのスタンドアロンデスクトップアプリ** である。  
`QWebEngineView` 上にHTML/CSS/JSで構成されたUIを描画し、`QWebChannel` を介してPythonバックエンドと双方向通信する。  
HTTPサーバーは一切使用せず、ファイルI/Oはすべてページ内JSがPythonを呼び出すことで処理される。

```
┌─────────────────────────────────────────────────┐
│             QMainWindow (PyQt6)                 │
│  ┌─────────────────────────────────────────┐    │
│  │         QWebEngineView                  │    │
│  │  ┌──────────┐  ┌──────────────────────┐ │    │
│  │  │ 左ペイン  │  │      右ペイン         │ │    │
│  │  │ファイル  │  │  エディタ(CodeMirror) │ │    │
│  │  │ ツリー   │  │  プレビュー(marked.js)│ │    │
│  │  └──────────┘  └──────────────────────┘ │    │
│  │           HTML / CSS / JavaScript        │    │
│  └──────────────────┬──────────────────────┘    │
│                     │ QWebChannel               │
│  ┌──────────────────▼──────────────────────┐    │
│  │      Python バックエンド                 │    │
│  │  ファイルI/O (os / pathlib / chardet)    │    │
│  │  バリデーション / エラー処理             │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

---

## 3. システム構成

### 3.1 論理構成

| レイヤー | 技術要素 | 役割 |
|----------|----------|------|
| アプリシェル | PyQt6 `QMainWindow` | ウィンドウ生成・アプリライフサイクル管理 |
| Web ビュー | `QWebEngineView` | HTML/CSS/JS のレンダリングエンジン |
| 通信ブリッジ | `QWebChannel` | JS ⇔ Python 間メソッド呼び出し・シグナル配信 |
| フロントエンド | HTML / CSS / JavaScript | ファイルツリー / エディタ / プレビュー描画 |
| エディタ | CodeMirror（JS ライブラリ） | Markdown シンタックスハイライト付きエディタ |
| プレビュー | marked.js（JS ライブラリ） | Markdown → HTML リアルタイムレンダリング |
| バックエンド | Python（os / pathlib / chardet） | ファイルI/O・バリデーション・エラー処理 |
| ビルド | PyInstaller | `.exe` 単一ファイルへのパッケージング |

### 3.2 配置構成

```
mdFileReader/
├── main.py                   # アプリエントリーポイント（QMainWindow 起動）
├── backend.py                # QWebChannel に公開する Python クラス
├── resources/
│   ├── ui.html               # メイン HTML（QWebEngineView にロード）
│   ├── style.css             # スタイルシート
│   ├── app.js                # メイン JavaScript
│   ├── codemirror/           # CodeMirror ライブラリ
│   └── marked.min.js         # marked.js ライブラリ
├── build/                    # PyInstaller ビルド出力（.exe）
└── project/                  # 開発ドキュメント類
```

> **リソース同梱方針：** `resources/` フォルダ全体を PyInstaller の `--add-data` で `.exe` に同梱する。  
> HTML は `QWebEngineView.setUrl(QUrl.fromLocalFile(...))` でロードする。

---

## 4. データフロー

### 4.1 アプリケーションフロー（全体）

```
[起動] ─→ QMainWindow 生成 ─→ QWebEngineView に ui.html ロード
          ─→ QWebChannel セットアップ（backend オブジェクト公開）
          ─→ QWebEngineView に acceptDrops(True) 設定
          ─→ JS の new QWebChannel() 完了
          ─→ [ユーザー操作待ち]

[フォルダ選択]
  ユーザ ─→ フォルダ選択ボタン押下
         ─→ JS: backend.selectFolder() 呼び出し
         ─→ Python: QFileDialog でフォルダ選択ダイアログ表示
         ─→ Python: 選択パスを返却 → folderSelected シグナル発火
         ─→ JS: ツリーデータ要求 → backend.getTree(path)
         ─→ Python: フォルダ内 .md ファイルを再帰取得 → JSON 返却
         ─→ JS: 左ペインにツリー描画

[ファイル選択]
  ユーザ ─→ ツリーのファイルノードをクリック
         ─→ JS: backend.readFile(filePath) 呼び出し
         ─→ Python: ファイル読み込み（chardet 文字コード自動判定。Shift-JIS/UTF-8 必対応）→ エンコード内部保持 → JSON 返却
         ─→ JS: CodeMirror エディタに内容を反映
         ─→ JS: marked.js でリアルタイムプレビュー更新

[編集]
  ユーザ ─→ エディタ上でテキスト入力
         ─→ JS: CodeMirror onChange → marked.js でプレビューをリアルタイム更新
         ─→ JS: 未保存フラグ ON → ステータスバーに「未保存の変更があります」表示

[保存]
  ユーザ ─→ 保存ボタンクリック または Ctrl+S
         ─→ JS: backend.saveFile(filePath, content) 呼び出し
         ─→ Python: **読み込み時に判定したエンコード**で上書き保存（不明時は UTF-8 フォールバック）→ JSON 返却
         ─→ JS: 未保存フラグ OFF → ステータスバーに「保存しました」表示

[ファイル削除]
  ユーザ ─→ ファイルノードの削除操作
         ─→ JS: 確認ダイアログ表示 → ユーザー確認
         ─→ JS: backend.deleteFile(filePath) 呼び出し
         ─→ Python: ファイル削除 → JSON 返却
         ─→ JS: ツリー更新

[新規作成 / 名前変更]
  ユーザ ─→ 新規作成 / 名前変更操作
         ─→ JS: backend.createFile(path) / backend.renameFile(oldPath, newPath)
         ─→ Python: 操作実行 → JSON 返却
         ─→ JS: ツリー更新

[ドラッグ＆ドロップ]
  ユーザ ─→ .md ファイルをウィンドウ上にドロップ
         ─→ JS: dragover イベントで event.preventDefault()（ブラウザデフォルト動作キャンセル）
         ─→ JS: drop イベントでファイルパスを取得 → backend.openDroppedFile(filePath) 呼び出し
         ─→ Python: 拡張子バリデーション（.md のみ許可）
         ─→ Python: ファイルの親フォルダが現ルートフォルダ外の場合 → 親フォルダをルートに自動設定 → getTree() 相当の処理
         ─→ Python: readFile(filePath) と同一の読み込みフロー（chardet 文字コード自動判定・エンコード保持）
         ─→ Python: ツリーデータ + ファイル内容を JSON で返却
         ─→ JS: ツリーを再描画 → ドロップファイルを選択状態に設定 → エディタ・プレビューを更新
```

---

## 5. 機能構成（コンポーネント）

### 5.1 コンポーネント一覧

| コンポーネントID | 名称 | 種別 | 説明 |
|-----------------|------|------|------|
| COMP-01 | MainWindow | Python | アプリウィンドウ。`QMainWindow` を継承。`QWebEngineView` を配置し `QWebChannel` を初期化する。D&D 受付のため `acceptDrops(True)` を設定する |
| COMP-02 | BackendBridge | Python | `QObject` を継承し `@pyqtSlot` でJSから呼び出し可能なメソッドを提供するクラス。D&D ファイル処理メソッド（`openDroppedFile`）を含む |
| COMP-03 | FileService | Python | ファイルI/O処理（ツリー取得・読み込み・保存・作成・削除・名前変更・バリデーション）を担当 |
| COMP-04 | UIPage | HTML/CSS | `QWebEngineView` にロードされるメインHTML。左右ペインのレイアウトを定義 |
| COMP-05 | TreeView | JavaScript | 左ペインのファイルツリー描画・操作ロジック |
| COMP-06 | EditorView | JavaScript | CodeMirror エディタの初期化・内容取得・変更検知・未保存フラグ管理 |
| COMP-07 | PreviewView | JavaScript | marked.js によるMarkdownレンダリング・右ペインへの表示切替ロジック |
| COMP-08 | StatusBar | JavaScript | 未保存変更通知・保存完了通知・エラー通知を画面下部のステータスバーに表示 |
| COMP-09 | BridgeClient | JavaScript | `QWebChannel` を介して `BackendBridge` のメソッドを呼び出すJS側ラッパー |

### 5.2 責務分離表

| 処理内容 | 担当 | コンポーネント |
|----------|------|----------------|
| ウィンドウ生成・アプリ起動 | Python | COMP-01 |
| QWebChannel セットアップ | Python | COMP-01 |
| フォルダ選択ダイアログ表示 | Python | COMP-02, COMP-03 |
| フォルダ内 `.md` ツリー取得 | Python | COMP-03 |
| ファイル読み込み（文字コード自動判定・エンコード保持） | Python | COMP-03 |
| ファイル保存（読み込み時エンコードで保持保存） | Python | COMP-03 |
| ファイル作成・削除・名前変更 | Python | COMP-03 |
| パスバリデーション（フォルダ外アクセス禁止） | Python | COMP-03 |
| ツリーUI描画・操作 | JavaScript | COMP-05 |
| エディタ表示・編集・変更検知 | JavaScript | COMP-06 |
| リアルタイムプレビュー | JavaScript | COMP-07 |
| エディタ/プレビュー表示切替（トグル） | JavaScript | COMP-06, COMP-07 |
| 未保存変更通知・保存完了通知 | JavaScript | COMP-08 |
| JS ⇔ Python 呼び出しラッパー | JavaScript | COMP-09 |
| Ctrl+S ショートカット処理 | JavaScript | COMP-06 |
| 削除確認ダイアログ表示 | JavaScript | COMP-05 |
| D&D イベント受付（dragover/drop） | JavaScript | COMP-09, COMP-05 |
| D&D ファイル処理（拡張子検証・ルート切替・表示） | Python | COMP-02, COMP-03 |

---

## 6. データ設計（基本）

### 6.1 ファイルツリーデータ構造

```json
{
  "success": true,
  "data": {
    "name": "myFolder",
    "path": "/path/to/myFolder",
    "type": "folder",
    "children": [
      {
        "name": "README.md",
        "path": "/path/to/myFolder/README.md",
        "type": "file"
      },
      {
        "name": "subFolder",
        "path": "/path/to/myFolder/subFolder",
        "type": "folder",
        "children": [...]
      }
    ]
  },
  "error": null
}
```

| フィールド | 型 | 説明 |
|------------|----|------|
| `name` | String | ファイル/フォルダ名 |
| `path` | String | 絶対パス |
| `type` | String | `"file"` または `"folder"` |
| `children` | Array / null | フォルダの場合のみ子要素一覧 |

### 6.2 ファイル読み込みデータ構造

```json
{
  "success": true,
  "data": {
    "path": "/path/to/file.md",
    "content": "# Hello\n\nMarkdown content here.",
    "encoding": "utf-8"
  },
  "error": null
}
```

---

## 7. インターフェース方針

### 7.0 文字コード方針

| 操作 | 方針 |
|------|------|
| 読み込み | `chardet` で文字コードを自動判定してデコードする。**Shift-JIS（`cp932`）・UTF-8 は必対応**。判定したエンコードを内部保持する |
| 保存 | **読み込み時に判定したエンコード**で書き込む。エンコード不明の場合は BOM なし UTF-8 でフォールバック。新規ファイルのデフォルトは BOM なし UTF-8 |
| JS ⇔ Python 通信 | すべて UTF-8 の JSON 文字列でやり取りする |

### 7.1 応答JSON要約

JS ← Python のすべての返却値は以下の統一フォーマットを使用する。

```json
{
  "success": <Boolean>,
  "data": <Any | null>,
  "error": <String | null>
}
```

### 7.2 応答JSON項目定義

#### 成功応答（success=true）

| フィールド | 値 |
|------------|----|
| `success` | `true` |
| `data` | 操作結果データ（型は操作により異なる） |
| `error` | `null` |

#### 失敗応答（success=false）

| フィールド | 値 |
|------------|----|
| `success` | `false` |
| `data` | `null` |
| `error` | エラーメッセージ文字列（例: `"FOLDER_NOT_FOUND"`, `"PERMISSION_DENIED"` 等） |

### 7.3 error_code 定義（基本設計）

| error_code | 発生条件 |
|------------|----------|
| `FOLDER_NOT_FOUND` | 指定フォルダが存在しない |
| `FILE_NOT_FOUND` | 指定ファイルが存在しない |
| `PERMISSION_DENIED` | 読み取り・書き込み権限なし |
| `PATH_TRAVERSAL` | 指定フォルダ外へのアクセス試行 |
| `ENCODING_ERROR` | 文字コード判定・デコード失敗（UTF-8 フォールバック後も失敗） |
| `ENCODE_SAVE_ERROR` | 元エンコードで表現できない文字を含む内容の保存失敗 |
| `FILE_EXISTS` | 同名ファイルが既に存在する（名前変更時） |
| `INVALID_EXTENSION` | `.md` 以外の拡張子のファイルが D&D でドロップされた |
| `UNKNOWN_ERROR` | 上記以外の予期しないエラー |

### 7.4 FE 判定ルール

```
if response.success:
    → 正常処理（data を使用）
else:
    → StatusBar にエラーメッセージを表示（error フィールドを使用）
    → 操作をロールバック（UIの状態を操作前に戻す）
```

---

## 8. 機能配置

### 8.1 フロントエンド機能（JavaScript）

| 機能ID | 機能名 | 説明 | 関連コンポーネント |
|--------|--------|------|--------------------|
| FE-01 | ツリー表示 | 取得したツリーJSONを左ペインに描画する | COMP-05 |
| FE-02 | ファイルノードクリック処理 | クリック時にファイル読み込みを要求し、エディタ・プレビューを更新する | COMP-05, COMP-06, COMP-07 |
| FE-03 | フォルダ開閉トグル | ツリー内のフォルダノードを開閉する | COMP-05 |
| FE-04 | エディタ初期化 | CodeMirror を Markdown モードで初期化する | COMP-06 |
| FE-05 | エディタ変更検知 | `onChange` で未保存フラグを ON にし、リアルタイムプレビューを更新する | COMP-06, COMP-07, COMP-08 |
| FE-06 | プレビュー更新 | エディタ内容を marked.js でレンダリングし右ペインに表示する | COMP-07 |
| FE-07 | エディタ/プレビュー切替 | トグルボタンでエディタ・プレビューの表示/非表示を切り替える | COMP-06, COMP-07 |
| FE-08 | 保存ショートカット | `Ctrl+S` を検知してバックエンドに保存を要求する | COMP-06 |
| FE-09 | 削除確認ダイアログ | ファイル削除前にJS標準の `confirm()` ダイアログを表示する | COMP-05 |
| FE-10 | ステータスバー通知 | 未保存変更・保存完了・エラーをステータスバーに表示する | COMP-08 |
| FE-11 | QWebChannel 初期化 | `qwebchannel.js` を使い `new QWebChannel()` で BackendBridge に接続する | COMP-09 |
| FE-12 | D&D イベントハンドリング | `dragover` で `event.preventDefault()` を実行し、`drop` でファイルパスを取得して `backend.openDroppedFile()` を呼び出す | COMP-09, COMP-05 |
| FE-13 | D&D 後のツリー・エディタ更新 | D&D 成功時にツリーを再描画し、ドロップファイルを選択状態に設定してエディタ・プレビューを更新する（`FE-02` と同等） | COMP-05, COMP-06, COMP-07 |
| FE-14 | D&D エラー表示 | 非対応拡張子ドロップ時または処理エラー時にステータスバーにエラーメッセージを表示する | COMP-08 |

### 8.2 バックエンド機能（Python）

| 機能ID | 機能名 | 説明 | 関連コンポーネント |
|--------|--------|------|--------------------|
| BE-01 | フォルダ選択 | `QFileDialog.getExistingDirectory()` を呼び出し選択パスをJSに返す | COMP-02 |
| BE-02 | ツリー取得 | `pathlib.Path.rglob("*.md")` で再帰取得し、ネストされたJSON構造で返す | COMP-03 |
| BE-03 | ファイル読み込み | `chardet` で文字コード判定（**Shift-JIS `cp932`/UTF-8 必対応**）→ デコードしエンコードを内部保持してコンテンツ文字列で返す | COMP-03 |
| BE-04 | ファイル保存 | **読み込み時に判定したエンコード**で上書き保存。不明時は BOM なし UTF-8 でフォールバック。成功/失敗をJSONで返す | COMP-03 |
| BE-05 | 新規ファイル作成 | 空の `.md` ファイルを作成し成功/失敗をJSONで返す | COMP-03 |
| BE-06 | ファイル削除 | 対象ファイルを削除し成功/失敗をJSONで返す | COMP-03 |
| BE-07 | 名前変更 | ファイル/フォルダの名前を変更し成功/失敗をJSONで返す | COMP-03 |
| BE-08 | パスバリデーション | 操作対象パスがベースフォルダ配下かを `Path.resolve()` で検証する | COMP-03 |
| BE-09 | エラーハンドリング | 例外を捕捉し統一JSONフォーマットでエラーを返す | COMP-02, COMP-03 |
| BE-10 | D&D ファイル処理 | `openDroppedFile(filePath)` として公開。① 拡張子バリデーション（`.md` のみ）、② ルートフォルダ判定（外部の場合は親フォルダをルートに自動設定）、③ `BE-02` 相当のツリー取得、④ `BE-03` 相当のファイル読み込み（chardet 判定・エンコード保持）を順に実行し、ツリーデータ＋ファイル内容を返す | COMP-02, COMP-03 |

### 8.3 画面遷移とUI責務

```
┌──────────────────────────────────────────────────────────────┐
│  QMainWindow                                                 │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  [フォルダ選択ボタン]  [現在のフォルダパス表示]          │  │
│  ├──────────────┬─────────────────────────────────────────┤  │
│  │  左ペイン     │  右ペイン                                │  │
│  │              │  [保存ボタン] [エディタ表示トグル] [プレビュー表示トグル] │  │
│  │ ・ファイル    │  ┌──────────────┬──────────────────────┐ │  │
│  │   ツリー      │  │  CodeMirror  │  marked.js プレビュー │ │  │
│  │              │  │  エディタ    │  （左右分割）          │ │  │
│  │ ・右クリック  │  └──────────────┴──────────────────────┘ │  │
│  │   コンテキスト│                                          │  │
│  │   メニュー   │                                          │  │
│  │  （新規/削除/ │                                          │  │
│  │   名前変更）  │                                          │  │
│  ├──────────────┴─────────────────────────────────────────┤  │
│  │  ステータスバー: [未保存の変更があります / 保存しました / エラー] │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

| UI要素 | 担当レイヤー | 説明 |
|--------|-------------|------|
| フォルダ選択ボタン | JS → Python | クリックで `BE-01` を呼び出す |
| ファイルツリー | JavaScript | `FE-01`〜`FE-03` で描画・操作 |
| 右クリックコンテキストメニュー | JavaScript | 新規作成・削除・名前変更を提供 |
| CodeMirror エディタ | JavaScript | `FE-04`〜`FE-05`, `FE-08` が担当 |
| marked.js プレビュー | JavaScript | `FE-06` が担当 |
| エディタ/プレビュートグルボタン | JavaScript | `FE-07` が担当 |
| 保存ボタン | JavaScript | クリックで `BE-04` を呼び出す |
| ステータスバー | JavaScript | `FE-10` が担当（未保存/保存完了/エラー） |

---

## 9. 例外時方針

| 異常ケース | BE 処理 | FE 処理 |
|------------|---------|---------|
| フォルダ未存在 | `FOLDER_NOT_FOUND` を返却 | ステータスバーにエラー表示、ツリーを更新しない |
| ファイル読み込み失敗（権限エラー等） | `PERMISSION_DENIED` を返却 | ステータスバーにエラー表示、エディタ内容を保持 |
| ファイル保存失敗 | `PERMISSION_DENIED` を返却 | ステータスバーにエラー表示、未保存フラグを維持 |
| フォルダ外アクセス | `PATH_TRAVERSAL` を返却 | ステータスバーにエラー表示 |
| 文字コード判定失敗 | UTF-8 フォールバック。失敗時は `ENCODING_ERROR` を返却 | ステータスバーに警告表示 |
| エンコード非対応文字の保存失敗 | `ENCODE_SAVE_ERROR` を返却（データを破棄しない） | ステータスバーにエラー表示、未保存フラグを維持 |
| 削除対象が存在しない | `FILE_NOT_FOUND` を返却 | ステータスバーにエラー表示 |
| D&D で非対応拡張子ファイルをドロップ | `INVALID_EXTENSION` を返却 | ステータスバーにエラー表示（`FE-14`） |
| D&D で Shift-JIS ファイルをドロップ（文字化け防止） | BE-10 内で必ず `BE-03` の chardet 判定フローを経由。`cp932` 検出で正常デコード | 文字化けなくエディタ表示。エラー時は `ENCODING_ERROR` をステータスバーに表示 |
| 同名ファイルへの名前変更 | JS 側で先に確認ダイアログを表示。ユーザ確認後に BE を呼び出す | 確認ダイアログ（`confirm()`）表示 |
| 未保存変更あり状態でファイル切替 | BE 処理なし | ステータスバーに「未保存の変更があります」を常時表示（ダイアログなし） |
| 予期しない例外 | `UNKNOWN_ERROR` を返却 | ステータスバーにエラー表示 |

---

## 10. 詳細設計への引継ぎ事項

### 10.1 Python 側（詳細設計で実装単位に分解するべき項目）

| # | 引継ぎ項目 | 説明 |
|---|------------|------|
| 1 | `MainWindow` クラス定義 | `QMainWindow` 継承、`QWebEngineView` 配置、`QWebChannel` セットアップ、HTMLロード処理 |
| 2 | `BackendBridge` クラス定義 | `QObject` 継承、`@pyqtSlot` デコレータによるJS公開メソッド（BE-01〜BE-09） |
| 3 | `FileService` クラス定義 | ファイルI/O全処理の内部実装。**`chardet` で Shift-JIS(想定 `cp932`)/UTF-8 判定、エンコード保持ロジック、元エンコード保持保存**。`chardet` 依存関係のバージョン固定も含む |
| 4 | PyInstaller スペックファイル | `resources/` の `--add-data` 設定、`.exe` 単一ファイル化設定 |

### 10.2 JavaScript 側（詳細設計で実装単位に分解するべき項目）

| # | 引継ぎ項目 | 説明 |
|---|------------|------|
| 1 | `ui.html` 構造定義 | 左右ペイン、ステータスバー、ボタン配置の HTML 骨格 |
| 2 | `app.js` モジュール構成 | TreeView / EditorView / PreviewView / StatusBar / BridgeClient の各モジュール実装 |
| 3 | `qwebchannel.js` 利用方法 | Qt 公式の `qwebchannel.js` を `resources/` に同梱し、JS 側で `new QWebChannel()` を初期化する |
| 4 | CodeMirror 設定 | Markdown モード有効化、テーマ、`Ctrl+S` キーバインド設定 |
| 5 | marked.js 設定 | オプション（改行挙動等）の初期設定方針 |

---

## 11. 工程ゲート（次工程進行確認）

| # | 確認項目 | 状態 |
|---|----------|------|
| 1 | すべての要件（REQ-*）に対する設計要素が本文書に対応付けられている | ⬜ レビュー待ち |
| 2 | Python 側と JavaScript 側の責務境界が明確に定義されている | ⬜ レビュー待ち |
| 3 | QWebChannel 連携インターフェース（メソッド・JSON形式）が定義されている | ⬜ レビュー待ち |
| 4 | 詳細設計で実装単位に分解できる粒度になっている | ⬜ レビュー待ち |
| 5 | GitHub 使用者のレビュー承認が完了している | ⬜ レビュー待ち |

---

## 12. 要件トレーサビリティ（要約）

| 要件ID | 要件名 | 対応設計要素 |
|--------|--------|-------------|
| REQ-IN-01 | フォルダ指定 | BE-01, FE-11 |
| REQ-IN-02 | ファイル選択 | FE-02, BE-03 |
| REQ-IN-03 | テキスト入力 | FE-04, FE-05 |
| REQ-IN-04 | 保存操作 | FE-08, BE-04 |
| REQ-PROC-01 | ツリー取得 | BE-02, FE-01 |
| REQ-PROC-02 | パスバリデーション | BE-08 |
| REQ-PROC-03 | 読み込み | BE-03 |
| REQ-PROC-04 | 文字コード自動判定（Shift-JIS/UTF-8 必対応） | BE-03（chardet） |
| REQ-PROC-04a | エンコード保持 | BE-03（内部保持）, BE-04 |
| REQ-PROC-05 | 上書き保存（読み込み時エンコード） | BE-04 |
| REQ-PROC-06 | エンコード保持保存・新規 UTF-8 デフォルト | BE-04 |
| REQ-PROC-07 | 新規ファイル作成 | BE-05 |
| REQ-PROC-08 | ファイル削除 | BE-06, FE-09 |
| REQ-PROC-09 | 名前変更 | BE-07 |
| REQ-PROC-10 | フォルダ外アクセス禁止 | BE-08 |
| REQ-PROC-11 | QWebChannel 連携 | COMP-01, COMP-02, COMP-09 |
| REQ-PROC-12 | HTTP サーバー不使用 | システム構成（§2） |
| REQ-OUT-01 | ファイルツリー表示 | FE-01 |
| REQ-OUT-02 | エディタ表示 | FE-04 |
| REQ-OUT-03 | プレビュー表示 | FE-06 |
| REQ-OUT-04 | 保存完了通知 | FE-10（StatusBar） |
| REQ-OUT-05 | エラー通知 | FE-10（StatusBar） |
| REQ-UI-01 | 分割レイアウト | §8.3 画面レイアウト |
| REQ-UI-02 | エディタ | FE-04（CodeMirror） |
| REQ-UI-03 | プレビュー | FE-06（marked.js） |
| REQ-UI-04 | 表示切替 | FE-07 |
| REQ-UI-05 | 保存ボタン | §8.3 UI要素表 |
| REQ-UI-06 | Ctrl+S 保存 | FE-08 |
| REQ-UI-07 | フォルダ選択 | BE-01（ダイアログ） |
| REQ-UI-08 | HTML リソース同梱 | §3.2 配置構成 |
| REQ-UI-09 | D&D ドロップ対象領域 | FE-12（drop イベント対象を右ペイン全体に設定） |
| REQ-UI-10 | D&D エラー表示 | FE-14（StatusBar） |
| REQ-IN-05 | D&D ファイル入力 | FE-12, BE-10 |
| REQ-PROC-02a | D&D ファイル受付 | BE-10（openDroppedFile） |
| REQ-PROC-02b | D&D パスバリデーション | BE-10（拡張子チェック） |
| REQ-PROC-02c | D&D 後のツリー更新 | BE-10（ルート切替 + BE-02 相当）, FE-13 |
| REQ-PROC-02d | D&D 後の表示動作 | BE-10（BE-03 相当）, FE-13（FE-02 相当） |
| REQ-ERR-09 | D&D 非対応ファイル異常系 | BE-10（INVALID_EXTENSION）, FE-14 |
| REQ-ERR-10 | D&D Shift-JIS 文字化け防止 | BE-10 → BE-03（chardet 強制適用） |
| REQ-OPS-01〜05 | 運用要件 | §3 システム構成、§9 例外時方針 |
| REQ-MNT-01〜04 | 保守要件 | §3.2 配置構成、開発プロセス |
| REQ-ERR-01〜10 | 例外・異常時要件 | §9 例外時方針 |

---

## 13. 差分開発情報

### 13.0 版数履歴

| 版数 | 内容 | 日付 |
|------|------|------|
| v1.0.0 | `01_requirements.md` v1.0.0 をもとに初版を新規作成 | 2026-03-02 |
| v1.1.0 | `01_requirements.md` v1.1.0 の変更（Shift-JIS 対応強化、エンコード保持保存）を反映 | 2026-03-02 |
| v1.2.0 | `01_requirements.md` v1.2.0 の変更（D&D 機能追加・Shift-JIS D&D 文字化け対応）を反映 | 2026-03-02 |

### 13.1 変更一覧（v1.0.0 → v1.1.0）

| 変更種別 | 対象 | 内容 |
|----------|------|------|
| 変更 | 文字コード方針 §7.0 | 保存を「UTF-8 固定」から「読み込み時エンコードで保持保存」に変更。Shift-JIS 必対応を明記 |
| 変更 | データフロー §4.1 | 読み込みフローに「エンコード内部保持」を追記。保存フローを「UTF-8 固定」から「元エンコード保持」に変更 |
| 変更 | 責務分離表 §5.2 | 「UTF-8」記述を「読み込み時エンコードで保持保存」に変更 |
| 変更 | BE-03 / BE-04 §8.2 | BE-03 に Shift-JIS 必対応・エンコード保持を追記。BE-04 を元エンコード保持保存に変更 |
| 追加 | error_code `ENCODE_SAVE_ERROR` §7.3 | エンコード非対応文字の保存失敗用 error_code を追加 |
| 追加 | 例外時方針 §9 | `ENCODE_SAVE_ERROR` の異常時方針を追加 |
| 変更 | 引継ぎ項目 #3 §10.1 | `FileService` に Shift-JIS 判定・エンコード保持ロジックを明記 |
| 変更 | 要件トレーサビリティ §12 | REQ-PROC-04a 追加、REQ-PROC-04/05/06 の対応設計要素を更新 |

### 13.2 詳細設計への追加引継ぎ（v1.1.0）

| # | 引継ぎ項目 | 詳細 |
|---|------------|------|
| 1 | `FileService.read_file` | 判定エンコード（`cp932` 実質適用）を返却値に含めること |
| 2 | `FileService.save_file` | 引数に 「エンコード」を受け取り、そのエンコードで書き込む。変換失敗時は `ENCODE_SAVE_ERROR` を返す |
| 3 | `BackendBridge` (`saveFile` メソッド) | JS がエンコードを指定できるように API シグネチャにエンコード引数を追加するか、バックエンド内部で保持するかを詳細設計で決定する |

### 13.4 変更一覧（v1.1.0 → v1.2.0）

**変更背景:** 要件定義 v1.2.0 で D&D 機能要件（REQ-IN-05、REQ-PROC-02a〜02d、REQ-UI-09〜10、REQ-ERR-09〜10）が追加された。Shift-JIS ファイルを D&D した際の文字化けを防ぐため、D&D 処理を既存の chardet 判定フロー（BE-03）に必ず通す設計とする。

| 変更種別 | 対象 | 内容 |
|----------|------|------|
| 変更 | §1 文書情報 | 版数 v1.2.0、参照元に `minutes_v120.md` 追加 |
| 変更 | §4.1 フロー | D&D フローを追加（拡張子検証→ルート切替→読み込み→表示） |
| 変更 | §5.1 COMP-01 | D&D 受付（`acceptDrops(True)`）の役割を追記 |
| 変更 | §5.1 COMP-02 | `openDroppedFile` メソッドの役割を追記 |
| 変更 | §5.2 責務分離表 | D&D イベント受付（JS）・D&D ファイル処理（Python）を追加 |
| 追加 | §7.3 error_code | `INVALID_EXTENSION` を追加 |
| 追加 | §8.1 FE-12〜14 | D&D イベントハンドリング・更新・エラー表示機能を追加 |
| 追加 | §8.2 BE-10 | D&D ファイル処理（`openDroppedFile`）機能を追加 |
| 追加 | §9 例外時方針 | D&D 非対応拡張子・Shift-JIS 文字化け防止の例外方針を追加 |
| 追加 | §12 トレーサビリティ | REQ-IN-05、REQ-PROC-02a〜02d、REQ-UI-09〜10、REQ-ERR-09〜10 の対応を追加 |

### 13.5 詳細設計への追加引継ぎ（v1.2.0）

| # | 引継ぎ項目 | 詳細 |
|---|------------|------|
| 1 | `BackendBridge.openDroppedFile(filePath)` | D&D で取得したファイルパスを受け取る `@pyqtSlot`。① `.md` 拡張子チェック → ② ルートフォルダ判定・切替 → ③ `FileService.get_tree()` → ④ `FileService.read_file()` の順で処理。戻り値は `{success, data: {tree, fileContent, encoding, path}, error}` |
| 2 | JS 側 D&D ハンドラ | `document` または右ペイン DOM に `dragover`/`drop` リスナーを設定。`event.preventDefault()` で Qt デフォルト動作をキャンセル。`drop` 時に `event.dataTransfer.files[0].path` を取得して `backend.openDroppedFile()` を呼び出す |
| 3 | `QWebEngineView` の D&D 設定 | `MainWindow` 初期化時に `self.web_view.setAcceptDrops(True)` を設定し、Python 側で `dragEnterEvent`/`dropEvent` を受け付ける方式か、JS 側の `drop` イベントで処理する方式かを詳細設計で決定する（JS 側 drop イベント優先を推奨） |

### 13.6 回帰確認観点（v1.2.0）

| # | 観点 |
|---|------|
| 1 | ファイルツリーからの選択（既存機能）が D&D 追加後も正常動作すること |
| 2 | D&D で UTF-8 ファイルを開いた場合に文字化けが発生しないこと |
| 3 | D&D で Shift-JIS ファイルを開いた場合に文字化けが発生しないこと（本バグ修正の核心） |
| 4 | D&D 後にファイルツリーが正しく更新・選択状態になること |
| 5 | D&D で非 `.md` ファイルをドロップした場合にエラーが表示されアプリがクラッシュしないこと |

### 13.3 回帰確認観点（v1.1.0）

| # | 観点 |
|---|------|
| 1 | v1.0.0 で動作していた UTF-8 ファイルの読み込み・保存フローが引き続き正常動作すること |
| 2 | Shift-JIS ファイルの読み込み→編集→保存の往復でエンコードが維持されること |
| 3 | 新規ファイル作成時のデフォルトエンコードが BOM なし UTF-8 であること |

