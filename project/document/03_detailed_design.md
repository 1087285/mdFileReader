# 03 詳細設計

## 1. 文書情報

| 項目 | 内容 |
|------|------|
| 文書名 | 詳細設計書 |
| 版数 | v1.0.0 |
| 作成日 | 2026-03-02 |
| 作成者 | GitHub Copilot（03_detailed_design_agent） |
| 参照元 | `project/document/02_basic_design.md` v1.0.0 |
| ステータス | 承認済み（2026-03-02） |

---

## 2. フロントエンド詳細設計（HTML / CSS / JavaScript）

### 2.1 HTML 構造仕様（`resources/ui.html`）

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>mdFileReader</title>
  <link rel="stylesheet" href="style.css">
  <!-- CodeMirror -->
  <link rel="stylesheet" href="codemirror/codemirror.min.css">
  <link rel="stylesheet" href="codemirror/theme/default.css">
  <script src="codemirror/codemirror.min.js"></script>
  <script src="codemirror/mode/markdown/markdown.js"></script>
  <!-- marked.js -->
  <script src="marked.min.js"></script>
  <!-- QWebChannel -->
  <script src="qwebchannel.js"></script>
</head>
<body>
  <!-- ツールバー -->
  <div id="toolbar">
    <button id="btn-select-folder">フォルダ選択</button>
    <span id="current-folder-path">（フォルダ未選択）</span>
    <button id="btn-save">保存</button>
    <button id="btn-toggle-editor">エディタ</button>
    <button id="btn-toggle-preview">プレビュー</button>
  </div>

  <!-- メインコンテンツ -->
  <div id="main">
    <!-- 左ペイン: ファイルツリー -->
    <div id="left-pane">
      <div id="tree-container"></div>
    </div>
    <!-- リサイザー -->
    <div id="resizer"></div>
    <!-- 右ペイン: エディタ + プレビュー -->
    <div id="right-pane">
      <div id="editor-container">
        <textarea id="editor"></textarea>
      </div>
      <div id="preview-container"></div>
    </div>
  </div>

  <!-- ステータスバー -->
  <div id="status-bar">
    <span id="status-message"></span>
  </div>

  <!-- コンテキストメニュー -->
  <ul id="context-menu" class="hidden">
    <li id="ctx-new-file">新規ファイル</li>
    <li id="ctx-rename">名前変更</li>
    <li id="ctx-delete">削除</li>
  </ul>

  <script src="app.js"></script>
</body>
</html>
```

### 2.1.1 画面表示責務（HTML / CSS / JavaScript）

| 要素ID | 役割 | 担当モジュール |
|--------|------|---------------|
| `#toolbar` | ツールバー全体 | CSS |
| `#btn-select-folder` | フォルダ選択ダイアログ要求 | BridgeClient |
| `#current-folder-path` | 現在のフォルダパス表示 | TreeView |
| `#btn-save` | 保存ボタン | EditorView |
| `#btn-toggle-editor` | エディタ表示/非表示トグル | EditorView |
| `#btn-toggle-preview` | プレビュー表示/非表示トグル | PreviewView |
| `#tree-container` | ファイルツリー描画エリア | TreeView |
| `#resizer` | 左右ペイン幅調整ドラッグバー | CSS + JS |
| `#editor-container` | CodeMirror 描画コンテナ | EditorView |
| `#preview-container` | marked.js レンダリング表示エリア | PreviewView |
| `#status-bar` / `#status-message` | ステータス通知 | StatusBar |
| `#context-menu` | 右クリックコンテキストメニュー | TreeView |

### 2.2 確認ダイアログ仕様

| アクション | ダイアログ種別 | メッセージ例 | キャンセル時の動作 |
|------------|---------------|-------------|-------------------|
| ファイル削除 | `window.confirm()` | `"「ファイル名」を削除しますか？"` | 削除処理を中断する |
| 同名ファイルへの名前変更 | `window.confirm()` | `"「ファイル名」は既に存在します。上書きしますか？"` | 名前変更処理を中断する |

### 2.3 バリデーション仕様（フロントエンド）

| バリデーション項目 | 判定条件 | NG 時の動作 |
|-------------------|----------|------------|
| 新規ファイル名入力 | 空文字・空白のみは NG | StatusBar にエラー表示 |
| 新規ファイル名入力 | `.md` 以外の拡張子は NG | StatusBar にエラー表示（`.md` を自動付与する案も可） |
| 名前変更入力 | 空文字・空白のみは NG | StatusBar にエラー表示 |
| 保存操作 | 現在開いているファイルがない場合は NG | StatusBar に「ファイルが選択されていません」表示 |

### 2.4 文字コード受理仕様

- JS 側は Python から返却された `content` を文字列としてそのまま扱う（文字コード変換は Python 側が完結）。
- `encoding` フィールドは参照情報として受け取るが、JS 側での処理は不要。

### 2.5 画面イベント仕様

| イベント | 発生要素 | 処理 |
|----------|----------|------|
| `click` | `#btn-select-folder` | `BridgeClient.selectFolder()` 呼び出し |
| `click` | `#btn-save` | `EditorView.save()` 呼び出し |
| `keydown` (Ctrl+S) | `document` | `EditorView.save()` 呼び出し |
| `click` | `#btn-toggle-editor` | `EditorView.toggle()` でエディタ表示切替 |
| `click` | `#btn-toggle-preview` | `PreviewView.toggle()` でプレビュー表示切替 |
| `click` ファイルノード | `#tree-container` | `TreeView.onFileClick(path)` → ファイル読み込み |
| `click` フォルダノード | `#tree-container` | `TreeView.onFolderToggle(path)` → 開閉 |
| `contextmenu` | `#tree-container` | `TreeView.showContextMenu(event, path)` |
| `click` | `#ctx-new-file` | `TreeView.onNewFile()` |
| `click` | `#ctx-rename` | `TreeView.onRename(path)` |
| `click` | `#ctx-delete` | `TreeView.onDelete(path)` |
| `change` | CodeMirror instance | `EditorView.onChange()` → プレビュー更新・未保存フラグ ON |
| `mousedown` → `mousemove` | `#resizer` | 左右ペイン幅のリサイズ |

### 2.6 画面遷移仕様

```
[初期状態]
  ツリー空表示、エディタ空、プレビュー空、ステータス「フォルダを選択してください」

[フォルダ選択後]
  ツリーに .md ファイル一覧表示、current-folder-path 更新

[ファイル選択後]
  エディタにファイル内容表示、プレビュー更新、未保存フラグ OFF

[編集中]
  ステータスバー「未保存の変更があります」を常時表示

[保存後]
  ステータスバー「保存しました」（3秒後に消去）、未保存フラグ OFF

[エラー発生]
  ステータスバーに赤字でエラーメッセージ表示（5秒後に消去）
```

### 2.7 フロントエンドモジュール仕様

#### 2.7.1 BridgeClient（`app.js` 内）

**役割:** `QWebChannel` を介して Python `BackendBridge` メソッドを呼び出すラッパー。

**初期化処理:**
```javascript
// QWebChannel 接続確立後に backend オブジェクトを取得
new QWebChannel(qt.webChannelTransport, (channel) => {
  window._backend = channel.objects.backend;
  App.init();  // アプリ本体の初期化
});
```

**公開メソッド一覧:**

| メソッド名 | 引数 | 説明 |
|------------|------|------|
| `selectFolder()` | なし | フォルダ選択ダイアログを開き、選択パスを取得する |
| `getTree(folderPath)` | `folderPath: string` | フォルダ配下のツリーJSONを取得する |
| `readFile(filePath)` | `filePath: string` | ファイル内容を読み込む |
| `saveFile(filePath, content)` | `filePath: string`, `content: string` | ファイルをUTF-8で保存する |
| `createFile(filePath)` | `filePath: string` | 新規 `.md` ファイルを作成する |
| `deleteFile(filePath)` | `filePath: string` | ファイルを削除する |
| `renameFile(oldPath, newPath)` | `oldPath: string`, `newPath: string` | ファイル/フォルダ名を変更する |

**コールバックパターン（すべて共通）:**
```javascript
_backend.saveFile(filePath, content, (responseJson) => {
  const res = JSON.parse(responseJson);
  if (res.success) {
    StatusBar.showSuccess("保存しました");
  } else {
    StatusBar.showError(res.error);
  }
});
```

---

#### 2.7.2 TreeView（`app.js` 内）

**役割:** ファイルツリーの描画・操作・コンテキストメニュー管理。

**状態変数:**

| 変数名 | 型 | 説明 |
|--------|----|------|
| `_rootPath` | string | 現在のルートフォルダパス |
| `_selectedPath` | string \| null | 現在選択中のファイルパス |

**主要関数仕様:**

| 関数名 | 引数 | 戻り値 | 処理内容 |
|--------|------|--------|----------|
| `render(treeData)` | `treeData: object` | void | ツリーJSONを再帰的に `<ul>/<li>` でHTMLレンダリングし `#tree-container` に挿入する |
| `onFileClick(filePath)` | `filePath: string` | void | `BridgeClient.readFile()` を呼び出し、成功時に `EditorView.load(content)` と `PreviewView.update(content)` を実行する |
| `onFolderToggle(folderPath)` | `folderPath: string` | void | フォルダノードの `expanded` クラスをトグルし子要素の表示/非表示を切り替える |
| `showContextMenu(event, targetPath)` | `event: MouseEvent`, `targetPath: string` | void | `#context-menu` を表示し `_contextTarget` にパスをセットする |
| `hideContextMenu()` | なし | void | `#context-menu` を非表示にする |
| `onNewFile()` | なし | void | `prompt()` でファイル名入力 → バリデーション → `BridgeClient.createFile()` → ツリー再描画 |
| `onRename(targetPath)` | `targetPath: string` | void | `prompt()` で新名前入力 → バリデーション → 同名確認 → `BridgeClient.renameFile()` → ツリー再描画 |
| `onDelete(targetPath)` | `targetPath: string` | void | `confirm()` で確認 → `BridgeClient.deleteFile()` → ツリー再描画。削除対象が現在開いているファイルの場合はエディタもクリアする |
| `refresh()` | なし | void | `BridgeClient.getTree(_rootPath)` を再呼び出しし `render()` をやり直す |

---

#### 2.7.3 EditorView（`app.js` 内）

**役割:** CodeMirror エディタの初期化・内容管理・保存処理・未保存フラグ管理。

**状態変数:**

| 変数名 | 型 | 説明 |
|--------|----|------|
| `_editor` | CodeMirror instance | CodeMirror インスタンス |
| `_currentFilePath` | string \| null | 現在編集中のファイルパス |
| `_isDirty` | boolean | 未保存変更ありフラグ |
| `_visible` | boolean | エディタペインの表示状態 |

**CodeMirror 初期化設定:**
```javascript
_editor = CodeMirror.fromTextArea(document.getElementById("editor"), {
  mode: "markdown",
  lineNumbers: true,
  lineWrapping: true,
  theme: "default",
  extraKeys: {
    "Ctrl-S": () => EditorView.save()
  }
});
```

**主要関数仕様:**

| 関数名 | 引数 | 戻り値 | 処理内容 |
|--------|------|--------|----------|
| `load(filePath, content)` | `filePath: string`, `content: string` | void | `_editor.setValue(content)` でエディタに内容をセット。`_currentFilePath` を更新。`_isDirty = false`。`StatusBar.clear()` |
| `onChange()` | なし | void | `_isDirty = true` にセット。`StatusBar.showWarning("未保存の変更があります")`。`PreviewView.update(_editor.getValue())` |
| `save()` | なし | void | `_currentFilePath` が null なら `StatusBar.showError("ファイルが選択されていません")` で早期リターン。`BridgeClient.saveFile()` 呼び出し |
| `toggle()` | なし | void | `_visible` をトグルし `#editor-container` の表示/非表示を切り替える |
| `clear()` | なし | void | `_editor.setValue("")`。`_currentFilePath = null`。`_isDirty = false` |
| `getValue()` | なし | string | `_editor.getValue()` を返す |

---

#### 2.7.4 PreviewView（`app.js` 内）

**役割:** marked.js によるリアルタイム Markdown → HTML レンダリング。

**marked.js 初期化設定:**
```javascript
marked.setOptions({
  breaks: true,   // 改行を <br> に変換
  gfm: true       // GitHub Flavored Markdown 有効
});
```

**主要関数仕様:**

| 関数名 | 引数 | 戻り値 | 処理内容 |
|--------|------|--------|----------|
| `update(markdownText)` | `markdownText: string` | void | `marked.parse(markdownText)` で HTML 変換し `#preview-container` の `innerHTML` にセットする |
| `toggle()` | なし | void | `_visible` をトグルし `#preview-container` の表示/非表示を切り替える |
| `clear()` | なし | void | `#preview-container` の `innerHTML` を空にする |

---

#### 2.7.5 StatusBar（`app.js` 内）

**役割:** ステータスバーへの通知表示管理。

**主要関数仕様:**

| 関数名 | 引数 | 戻り値 | 処理内容 |
|--------|------|--------|----------|
| `showSuccess(message)` | `message: string` | void | `#status-message` を緑色スタイルで表示。3秒後に自動クリア |
| `showWarning(message)` | `message: string` | void | `#status-message` をオレンジ色スタイルで **常時** 表示（自動クリアなし） |
| `showError(message)` | `message: string` | void | `#status-message` を赤色スタイルで表示。5秒後に自動クリア |
| `clear()` | なし | void | `#status-message` を空にする |

> **未保存フラグ表示の補足:** `showWarning("未保存の変更があります")` は `_isDirty` が `true` の間ずっと表示する。`EditorView.save()` 成功後に `showSuccess()` で上書きすることで警告が消える。

---

## 3. バックエンド詳細設計（Python）

### 3.1 モジュール設計

| ファイル名 | クラス/モジュール | 役割 |
|------------|-----------------|------|
| `main.py` | `main()` 関数 | `QApplication` を生成し `MainWindow` を起動するエントリーポイント |
| `main_window.py` | `MainWindow(QMainWindow)` | ウィンドウ生成・`QWebEngineView` 配置・`QWebChannel` セットアップ・HTML ロード |
| `backend_bridge.py` | `BackendBridge(QObject)` | `@pyqtSlot` でJS公開メソッドを提供。`FileService` に処理を委譲する |
| `file_service.py` | `FileService` | ファイルI/O・バリデーション・文字コード自動判定の全実装を担当 |

### 3.2 クラス設計

#### 3.2.1 `MainWindow` クラス（`main_window.py`）

```python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._setup_window()
        self._setup_webview()
        self._setup_channel()
        self._load_html()

    def _setup_window(self) -> None:
        """ウィンドウタイトル・初期サイズを設定する"""
        # setWindowTitle("mdFileReader")
        # resize(1200, 800)

    def _setup_webview(self) -> None:
        """QWebEngineView を中央ウィジェットとして配置する"""

    def _setup_channel(self) -> None:
        """QWebChannel を生成し BackendBridge オブジェクトを 'backend' として登録する"""

    def _load_html(self) -> None:
        """同梱リソースの ui.html を QUrl.fromLocalFile() でロードする"""
```

---

#### 3.2.2 `BackendBridge` クラス（`backend_bridge.py`）

```python
class BackendBridge(QObject):
    def __init__(self, file_service: FileService, parent=None):
        super().__init__(parent)
        self._fs = file_service
```

**公開メソッド一覧（`@pyqtSlot`）:**

| メソッド名 | PyQt シグネチャ | 処理内容 |
|------------|---------------|----------|
| `selectFolder(callback)` | `@pyqtSlot(result=str)` | `QFileDialog.getExistingDirectory()` を呼び出し、選択パスを文字列で返す。未選択時は `""` を返す |
| `getTree(folder_path, callback)` | `@pyqtSlot(str, result=str)` | `FileService.get_tree(folder_path)` を呼び出し、結果JSONを返す |
| `readFile(file_path, callback)` | `@pyqtSlot(str, result=str)` | `FileService.read_file(file_path)` を呼び出し、結果JSONを返す |
| `saveFile(file_path, content, callback)` | `@pyqtSlot(str, str, result=str)` | `FileService.save_file(file_path, content)` を呼び出し、結果JSONを返す |
| `createFile(file_path, callback)` | `@pyqtSlot(str, result=str)` | `FileService.create_file(file_path)` を呼び出し、結果JSONを返す |
| `deleteFile(file_path, callback)` | `@pyqtSlot(str, result=str)` | `FileService.delete_file(file_path)` を呼び出し、結果JSONを返す |
| `renameFile(old_path, new_path, callback)` | `@pyqtSlot(str, str, result=str)` | `FileService.rename_file(old_path, new_path)` を呼び出し、結果JSONを返す |

**レスポンス生成ヘルパー（内部）:**
```python
def _ok(self, data) -> str:
    return json.dumps({"success": True, "data": data, "error": None}, ensure_ascii=False)

def _err(self, code: str) -> str:
    return json.dumps({"success": False, "data": None, "error": code}, ensure_ascii=False)
```

---

#### 3.2.3 `FileService` クラス（`file_service.py`）

**初期化:**
```python
class FileService:
    def __init__(self):
        self._base_path: Path | None = None  # 現在選択中のルートフォルダ
```

**主要関数仕様:**

##### `set_base_path(folder_path: str) -> None`
- `self._base_path = Path(folder_path).resolve()` でルートを記録する。

---

##### `validate_path(target_path: str) -> Path`
- **処理:**
  1. `Path(target_path).resolve()` で絶対パスに変換する。
  2. `self._base_path` が None → `ValueError("BASE_NOT_SET")` を送出する。
  3. `resolved` が `self._base_path` の配下でない場合 → `PermissionError("PATH_TRAVERSAL")` を送出する。
  4. 正常なら `resolved` を返す。

---

##### `get_tree(folder_path: str) -> str`
- **処理:**
  1. `set_base_path(folder_path)` を呼び出し `_base_path` を更新する。
  2. `_build_tree_node(path)` を再帰呼び出しし、ネストされた `dict` を構築する。
  3. `json.dumps()` で JSON 文字列に変換し、`{"success": True, "data": {...}, "error": None}` 形式で返す。
- **例外処理:** `FileNotFoundError` → `FOLDER_NOT_FOUND`

##### `_build_tree_node(path: Path) -> dict`（内部）
```python
# 例
{
  "name": "docs",
  "path": "/absolute/path/docs",
  "type": "folder",      # or "file"
  "children": [...]      # フォルダの場合のみ
}
```
- `path.is_dir()` の場合、`sorted(path.iterdir())` で子要素を列挙し、フォルダを先に・`.md` ファイルのみを含める。

---

##### `read_file(file_path: str) -> str`
- **処理:**
  1. `validate_path(file_path)` でバリデーション。
  2. `raw = path.read_bytes()` でバイト列を読み込む。
  3. `chardet.detect(raw)` で文字コードを判定する。
  4. `raw.decode(detected_encoding, errors='replace')` でデコードする。
  5. `chardet` スコアが 0.5 未満の場合は UTF-8 でフォールバック。
  6. `{"success": True, "data": {"path": str, "content": str, "encoding": str}, "error": None}` を返す。
- **例外処理:** `FileNotFoundError` → `FILE_NOT_FOUND` / `PermissionError` → `PERMISSION_DENIED` / デコード失敗 → `ENCODING_ERROR`

---

##### `save_file(file_path: str, content: str) -> str`
- **処理:**
  1. `validate_path(file_path)` でバリデーション。
  2. `path.write_text(content, encoding="utf-8")` で UTF-8 (BOM なし) 書き込み。
  3. `{"success": True, "data": None, "error": None}` を返す。
- **例外処理:** `PermissionError` → `PERMISSION_DENIED`

---

##### `create_file(file_path: str) -> str`
- **処理:**
  1. `validate_path(file_path)` でバリデーション。
  2. `path.touch(exist_ok=False)` で空ファイルを作成する。`exist_ok=False` により既存ファイルの場合は `FileExistsError` を送出。
  3. `{"success": True, "data": None, "error": None}` を返す。
- **例外処理:** `FileExistsError` → `FILE_EXISTS`

---

##### `delete_file(file_path: str) -> str`
- **処理:**
  1. `validate_path(file_path)` でバリデーション。
  2. `path.unlink()` でファイルを削除する。
  3. `{"success": True, "data": None, "error": None}` を返す。
- **例外処理:** `FileNotFoundError` → `FILE_NOT_FOUND` / `PermissionError` → `PERMISSION_DENIED`

---

##### `rename_file(old_path: str, new_path: str) -> str`
- **処理:**
  1. `validate_path(old_path)` と `validate_path(new_path)` の両方でバリデーション。
  2. `old.rename(new)` でリネームを実行する。
  3. `{"success": True, "data": None, "error": None}` を返す。
- **例外処理:** `FileNotFoundError` → `FILE_NOT_FOUND` / `FileExistsError` → `FILE_EXISTS` / `PermissionError` → `PERMISSION_DENIED`

### 3.3 QWebChannel インターフェース仕様一覧

| JS 呼び出しメソッド | Python スロット | 引数（JS→Python） | 戻り値JSON（Python→JS） | 備考 |
|--------------------|-----------------|--------------------|------------------------|------|
| `backend.selectFolder(cb)` | `selectFolder()` | なし | `string`（フォルダパス or `""`） | ダイアログ表示はメインスレッドで実行 |
| `backend.getTree(path, cb)` | `getTree(str)` | `folderPath: string` | `{success, data: treeNode, error}` | |
| `backend.readFile(path, cb)` | `readFile(str)` | `filePath: string` | `{success, data: {path,content,encoding}, error}` | |
| `backend.saveFile(path, content, cb)` | `saveFile(str,str)` | `filePath, content: string` | `{success, data: null, error}` | |
| `backend.createFile(path, cb)` | `createFile(str)` | `filePath: string` | `{success, data: null, error}` | |
| `backend.deleteFile(path, cb)` | `deleteFile(str)` | `filePath: string` | `{success, data: null, error}` | |
| `backend.renameFile(old, new, cb)` | `renameFile(str,str)` | `oldPath, newPath: string` | `{success, data: null, error}` | |

> **`select​Folder` の戻り値について:** `QWebChannel` では `result=str` のスロットはコールバック形式になる。JS 側では `backend.selectFolder((path) => { ... })` のように呼び出す。

### 3.4 ファイル仕様

#### `resources/ui.html`
- アプリのメイン HTML。`QWebEngineView.setUrl()` でロードされる。
- `qwebchannel.js`・`codemirror/`・`marked.min.js`・`app.js`・`style.css` を相対パスで読み込む。

#### `resources/qwebchannel.js`
- Qt が提供する公式ファイル。`PyQt6` パッケージ内の以下から取得する。
  - パス例: `site-packages/PyQt6/Qt6/resources/qtwebchannel/qwebchannel.js`

#### `resources/codemirror/`
- CodeMirror の最小構成を配置する。
  - `codemirror.min.js`
  - `codemirror.min.css`
  - `mode/markdown/markdown.js`

#### `resources/marked.min.js`
- marked.js の CDN ビルド版を使用する（`marked@14.x` 以降）。

#### `resources/app.js`
- フロントエンドの全 JavaScript を 1 ファイルに集約する。
- BridgeClient / TreeView / EditorView / PreviewView / StatusBar の各モジュールを即時実行関数（IIFE）または ES モジュールで管理する。

#### `resources/style.css`
- 左右ペイン分割・ツールバー・ステータスバーのスタイルを定義する。

---

## 4. 例外処理設計

### 4.1 エラーコード定義

| error_code | 発生条件 | Python 例外 | JS での表示メッセージ例 |
|------------|----------|-------------|------------------------|
| `FOLDER_NOT_FOUND` | 指定フォルダが存在しない | `FileNotFoundError` | `"フォルダが見つかりません"` |
| `FILE_NOT_FOUND` | 指定ファイルが存在しない | `FileNotFoundError` | `"ファイルが見つかりません"` |
| `PERMISSION_DENIED` | 読み取り・書き込み権限なし | `PermissionError` | `"アクセスが拒否されました"` |
| `PATH_TRAVERSAL` | 指定フォルダ外へのアクセス | `PermissionError` | `"フォルダ外へのアクセスは禁止されています"` |
| `ENCODING_ERROR` | 文字コード判定・デコード失敗 | UnicodeDecodeError 等 | `"文字コードを判定できませんでした"` |
| `FILE_EXISTS` | 同名ファイルが既に存在する | `FileExistsError` | `"同名のファイルが既に存在します"` |
| `BASE_NOT_SET` | ベースパスが未設定 | `ValueError` | `"フォルダが選択されていません"` |
| `UNKNOWN_ERROR` | 上記以外の例外 | `Exception` | `"予期しないエラーが発生しました"` |

### 4.2 Python 側の共通例外ハンドリングパターン

```python
def _safe_execute(self, func, *args) -> str:
    """全スロットの共通ラッパー。例外を捕捉して error_code に変換する"""
    try:
        return func(*args)
    except FileNotFoundError as e:
        return self._err(str(e))
    except PermissionError as e:
        return self._err(str(e))
    except FileExistsError:
        return self._err("FILE_EXISTS")
    except ValueError as e:
        return self._err(str(e))
    except Exception:
        return self._err("UNKNOWN_ERROR")
```

---

## 5. PyInstaller ビルド設定

### 5.1 `.spec` ファイル設定方針

| 設定項目 | 値・方針 |
|----------|----------|
| `onefile` | `True`（単一 `.exe` 出力） |
| `windowed` | `True`（コンソールウィンドウ非表示） |
| `name` | `mdFileReader` |
| `datas` | `[("resources", "resources")]`（`resources/` フォルダ全体を同梱） |
| `hiddenimports` | `["chardet", "PyQt6.QtWebEngineWidgets", "PyQt6.QtWebChannel"]` |
| `icon` | 任意の `.ico` ファイル（実装工程で用意） |

### 5.2 リソースパス解決

PyInstaller でパッケージ化した場合、実行時のリソースパスは通常と異なる。以下のヘルパー関数を `main_window.py` に定義する。

```python
import sys
from pathlib import Path

def resource_path(relative_path: str) -> Path:
    """PyInstaller の一時展開先または開発時ソース相対パスを返す"""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    return base / relative_path
```

---

## 6. 単体評価観点（設計時定義）

### 6.1 テスト観点と対象モジュール

| テストID | 対象モジュール | テスト観点 | 正常/異常 |
|----------|--------------|------------|-----------|
| UT-BE-01 | `FileService.validate_path` | ベースパス配下のパスは正常通過する | 正常 |
| UT-BE-02 | `FileService.validate_path` | `../` を含むパスは `PATH_TRAVERSAL` エラー | 異常 |
| UT-BE-03 | `FileService.get_tree` | `.md` ファイルのみがツリーに含まれる | 正常 |
| UT-BE-04 | `FileService.get_tree` | 存在しないフォルダは `FOLDER_NOT_FOUND` | 異常 |
| UT-BE-05 | `FileService.read_file` | UTF-8 ファイルが正常に読み込まれる | 正常 |
| UT-BE-06 | `FileService.read_file` | Shift-JIS ファイルが文字化けなく読み込まれる | 正常 |
| UT-BE-07 | `FileService.read_file` | 存在しないファイルは `FILE_NOT_FOUND` | 異常 |
| UT-BE-08 | `FileService.save_file` | UTF-8 で保存されている（BOM なし） | 正常 |
| UT-BE-09 | `FileService.save_file` | 権限なしファイルへの保存は `PERMISSION_DENIED` | 異常 |
| UT-BE-10 | `FileService.create_file` | 新規ファイルが作成される | 正常 |
| UT-BE-11 | `FileService.create_file` | 同名ファイル存在時は `FILE_EXISTS` | 異常 |
| UT-BE-12 | `FileService.delete_file` | ファイルが削除される | 正常 |
| UT-BE-13 | `FileService.delete_file` | 存在しないファイルは `FILE_NOT_FOUND` | 異常 |
| UT-BE-14 | `FileService.rename_file` | ファイル名が変更される | 正常 |
| UT-BE-15 | `FileService.rename_file` | 同名ファイル存在時は `FILE_EXISTS` | 異常 |
| UT-FE-01 | `StatusBar.showWarning` | 未保存フラグ ON 時に常時表示されている | 正常 |
| UT-FE-02 | `StatusBar.showSuccess` | 保存成功後に3秒で消える | 正常 |
| UT-FE-03 | `EditorView.save` | ファイル未選択時は `StatusBar.showError` が呼ばれる | 異常 |
| UT-FE-04 | `TreeView.onDelete` | confirm キャンセル時は `deleteFile` が呼ばれない | 異常 |
| UT-FE-05 | `TreeView.onNewFile` | 空文字入力時はエラーが表示される | 異常 |

---

## 7. 実装への引継ぎ事項

| # | 引継ぎ項目 | 詳細 |
|---|------------|------|
| 1 | 依存ライブラリ | `PyQt6`, `PyQt6-WebEngine`, `chardet`, `PyInstaller`。`requirements.txt` に固定バージョンで記載すること |
| 2 | `qwebchannel.js` 取得 | `pip show PyQt6` でインストール先を確認し、`Qt6/resources/qtwebchannel/qwebchannel.js` を `resources/` にコピーする |
| 3 | CodeMirror 取得 | npmまたはCDNから `codemirror@5.x` の最小ビルドを `resources/codemirror/` に配置する |
| 4 | marked.js 取得 | CDNから `marked.min.js` を `resources/` に配置する |
| 5 | `resource_path()` ヘルパー | PyInstaller と開発時の両方に対応するため必ず使用すること |
| 6 | メインスレッド制約 | `QFileDialog` 等の Qt UI 操作はメインスレッドで実行すること（QWebChannel のコールバックは別スレッドで呼ばれる場合がある） |
| 7 | HTML ロード方法 | `QWebEngineView.setUrl(QUrl.fromLocalFile(str(resource_path("resources/ui.html"))))` を使用すること |

---

## 8. 工程ゲート（次工程進行確認）

| # | 確認項目 | 状態 |
|---|----------|------|
| 1 | Python 全クラスの関数仕様（引数・戻り値・例外）が定義されている | ✅ 承認済み |
| 2 | JavaScript 全モジュールの関数仕様が定義されている | ✅ 承認済み |
| 3 | QWebChannel 連携インターフェースが実装可能な粒度で定義されている | ✅ 承認済み |
| 4 | 例外処理・error_code が全ケースで定義されている | ✅ 承認済み |
| 5 | PyInstaller ビルド設定方針が定義されている | ✅ 承認済み |
| 6 | 単体評価観点が定義されている | ✅ 承認済み |
| 7 | GitHub 使用者のレビュー承認が完了している | ✅ 承認済み（2026-03-02） |

---

## 9. 差分開発情報

### 9.1 変更一覧

| 変更種別 | 対象 | 内容 |
|----------|------|------|
| 新規作成 | 本文書全体 | `02_basic_design.md` v1.0.0 をもとに初版を新規作成 |

### 9.2 実装工程（04）への必須引継ぎ

- 初版のため差分なし。§7「実装への引継ぎ事項」を参照。

### 9.3 回帰確認観点（03観点）

- 初版のため回帰確認不要。

