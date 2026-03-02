/*!
 * app.js - mdFileReader フロントエンド
 *
 * モジュール構成:
 *   BridgeClient  - QWebChannel 経由で Python BackendBridge を呼び出すラッパー
 *   StatusBar     - ステータスバー通知管理
 *   PreviewView   - marked.js Markdown プレビュー
 *   EditorView    - CodeMirror エディタ管理
 *   TreeView      - ファイルツリー描画・操作
 *   App           - 全体初期化・イベント配線
 */

"use strict";

/* ============================================================
   BridgeClient
   ============================================================ */
const BridgeClient = (() => {
  let _backend = null;

  function init(backendObj) {
    _backend = backendObj;
  }

  function _call(method, args, callback) {
    if (!_backend) {
      callback({ success: false, data: null, error: "BRIDGE_NOT_READY" });
      return;
    }
    const wrappedCb = (jsonStr) => {
      try {
        callback(JSON.parse(jsonStr));
      } catch (e) {
        callback({ success: false, data: null, error: "PARSE_ERROR" });
      }
    };
    _backend[method](...args, wrappedCb);
  }

  return {
    init,

    selectFolder(callback) {
      if (!_backend) { callback(""); return; }
      _backend.selectFolder((path) => callback(path));
    },

    getTree(folderPath, callback) {
      _call("getTree", [folderPath], callback);
    },

    readFile(filePath, callback) {
      _call("readFile", [filePath], callback);
    },

    saveFile(filePath, content, encoding, callback) {
      _call("saveFile", [filePath, content, encoding], callback);
    },

    createFile(filePath, callback) {
      _call("createFile", [filePath], callback);
    },

    deleteFile(filePath, callback) {
      _call("deleteFile", [filePath], callback);
    },

    renameFile(oldPath, newPath, callback) {
      _call("renameFile", [oldPath, newPath], callback);
    },
  };
})();


/* ============================================================
   StatusBar
   ============================================================ */
const StatusBar = (() => {
  let _el = null;
  let _msgEl = null;
  let _timer = null;

  function init() {
    _el = document.getElementById("status-bar");
    _msgEl = document.getElementById("status-message");
  }

  function _set(message, cssClass, autoClearMs) {
    if (_timer) { clearTimeout(_timer); _timer = null; }
    _el.className = cssClass;
    _msgEl.textContent = message;
    if (autoClearMs > 0) {
      _timer = setTimeout(() => clear(), autoClearMs);
    }
  }

  function showSuccess(message) { _set(message, "success", 3000); }
  function showWarning(message) { _set(message, "warning", 0); }
  function showError(message)   { _set(message, "error", 5000); }
  function clear()              { _set("", "", 0); }

  return { init, showSuccess, showWarning, showError, clear };
})();


/* ============================================================
   PreviewView
   ============================================================ */
const PreviewView = (() => {
  let _container = null;
  let _divider   = null;
  let _visible   = false;

  function init() {
    _container = document.getElementById("preview-container");
    _divider   = document.getElementById("divider");

    // marked.js の基本設定
    marked.setOptions({ breaks: true, gfm: true });
  }

  function update(markdownText) {
    if (_container) {
      _container.innerHTML = marked.parse(markdownText || "");
    }
  }

  function show() {
    _visible = true;
    _container.classList.remove("hidden");
    _divider.classList.remove("hidden");
    document.getElementById("btn-toggle-preview").classList.add("active");
  }

  function hide() {
    _visible = false;
    _container.classList.add("hidden");
    _divider.classList.add("hidden");
    document.getElementById("btn-toggle-preview").classList.remove("active");
  }

  function toggle() {
    _visible ? hide() : show();
  }

  function clear() {
    if (_container) _container.innerHTML = "";
  }

  function isVisible() { return _visible; }

  return { init, update, show, hide, toggle, clear, isVisible };
})();


/* ============================================================
   EditorView
   ============================================================ */
const EditorView = (() => {
  let _editor          = null;
  let _currentFilePath = null;
  let _currentEncoding = "utf-8";
  let _isDirty         = false;
  let _visible         = true;

  function init() {
    _editor = CodeMirror.fromTextArea(document.getElementById("editor"), {
      mode: "markdown",
      lineNumbers: true,
      lineWrapping: true,
      theme: "default",
      indentUnit: 2,
      tabSize: 2,
      extraKeys: {
        "Ctrl-S": () => save(),
      },
    });

    // CodeMirror の textarea を含む div の高さを 100% にする
    const editorContainer = document.getElementById("editor-container");
    editorContainer.appendChild(_editor.getWrapperElement());
    _editor.getWrapperElement().style.height = "100%";
    _editor.setSize(null, "100%");

    _editor.on("change", () => _onChange());
  }

  function _onChange() {
    _isDirty = true;
    StatusBar.showWarning("未保存の変更があります");
    PreviewView.update(_editor.getValue());
  }

  function load(filePath, content, encoding) {
    _currentFilePath = filePath;
    _currentEncoding = encoding || "utf-8";
    _isDirty = false;
    // change イベントを発火させないよう一時的に off
    _editor.off("change", _onChange);
    _editor.setValue(content);
    _editor.off("change", _onChange);
    _editor.on("change", () => _onChange());
    StatusBar.clear();
    PreviewView.update(content);
  }

  function save() {
    if (!_currentFilePath) {
      StatusBar.showError("ファイルが選択されていません");
      return;
    }
    BridgeClient.saveFile(_currentFilePath, _editor.getValue(), _currentEncoding, (res) => {
      if (res.success) {
        _isDirty = false;
        StatusBar.showSuccess("保存しました");
      } else {
        StatusBar.showError(_errorMessage(res.error));
      }
    });
  }

  function toggle() {
    _visible = !_visible;
    const container = document.getElementById("editor-container");
    if (_visible) {
      container.classList.remove("hidden");
      document.getElementById("btn-toggle-editor").classList.add("active");
    } else {
      container.classList.add("hidden");
      document.getElementById("btn-toggle-editor").classList.remove("active");
    }
  }

  function clear() {
    _currentFilePath = null;
    _currentEncoding = "utf-8";
    _isDirty = false;
    _editor.off("change", _onChange);
    _editor.setValue("");
    _editor.on("change", () => _onChange());
  }

  function getValue()           { return _editor ? _editor.getValue() : ""; }
  function getCurrentPath()     { return _currentFilePath; }
  function getCurrentEncoding() { return _currentEncoding; }
  function isDirty()            { return _isDirty; }
  function isVisible()          { return _visible; }
  function refresh()            { if (_editor) _editor.refresh(); }

  return { init, load, save, toggle, clear, getValue, getCurrentPath, getCurrentEncoding, isDirty, isVisible, refresh };
})();


/* ============================================================
   TreeView
   ============================================================ */
const TreeView = (() => {
  let _rootPath       = null;
  let _selectedPath   = null;
  let _contextTarget  = null;
  let _expandedPaths  = new Set();

  function init() {
    const container = document.getElementById("tree-container");

    // コンテキストメニューの外クリックで非表示
    document.addEventListener("click", () => _hideContextMenu());
    document.addEventListener("contextmenu", (e) => {
      if (!e.target.closest("#context-menu") && !e.target.closest("#tree-container")) {
        _hideContextMenu();
      }
    });

    document.getElementById("ctx-new-file").addEventListener("click", () => _onNewFile());
    document.getElementById("ctx-new-folder").addEventListener("click", () => _onNewFolder());
    document.getElementById("ctx-rename").addEventListener("click", () => _onRename());
    document.getElementById("ctx-delete").addEventListener("click", () => _onDelete());

    // 左右リサイザー
    _initResizer();
  }

  function render(treeData) {
    const container = document.getElementById("tree-container");
    container.innerHTML = "";
    if (!treeData) return;
    _rootPath = treeData.path;
    document.getElementById("current-folder-path").textContent = treeData.path;
    document.getElementById("current-folder-path").title = treeData.path;
    const root = _buildNode(treeData, 0);
    container.appendChild(root);
  }

  function _buildNode(node, depth) {
    const wrapper = document.createElement("div");
    wrapper.classList.add("tree-node");

    const label = document.createElement("div");
    label.classList.add("tree-label");
    label.style.paddingLeft = `${8 + depth * 16}px`;
    label.dataset.path = node.path;
    label.dataset.type = node.type;

    const icon = document.createElement("span");
    icon.classList.add("icon");

    if (node.type === "folder") {
      const isExp = _expandedPaths.has(node.path);
      icon.textContent = isExp ? "📂" : "📁";
      label.appendChild(icon);
      label.appendChild(_nameSpan(node.name));

      label.addEventListener("click", (e) => {
        e.stopPropagation();
        _onFolderToggle(node.path, label, icon, childrenEl);
      });
      label.addEventListener("contextmenu", (e) => {
        e.preventDefault();
        e.stopPropagation();
        _showContextMenu(e, node.path, node.type);
      });

      wrapper.appendChild(label);

      const childrenEl = document.createElement("div");
      childrenEl.classList.add("tree-children");
      if (!_expandedPaths.has(node.path)) childrenEl.classList.add("hidden");
      if (node.children) {
        node.children.forEach((child) => childrenEl.appendChild(_buildNode(child, depth + 1)));
      }
      wrapper.appendChild(childrenEl);
    } else {
      icon.textContent = "📄";
      label.appendChild(icon);
      label.appendChild(_nameSpan(node.name));

      if (node.path === _selectedPath) label.classList.add("selected");

      label.addEventListener("click", (e) => {
        e.stopPropagation();
        _onFileClick(node.path, label);
      });
      label.addEventListener("contextmenu", (e) => {
        e.preventDefault();
        e.stopPropagation();
        _showContextMenu(e, node.path, node.type);
      });
      wrapper.appendChild(label);
    }

    return wrapper;
  }

  function _nameSpan(name) {
    const s = document.createElement("span");
    s.classList.add("name");
    s.textContent = name;
    return s;
  }

  function _onFolderToggle(folderPath, label, icon, childrenEl) {
    if (_expandedPaths.has(folderPath)) {
      _expandedPaths.delete(folderPath);
      childrenEl.classList.add("hidden");
      icon.textContent = "📁";
    } else {
      _expandedPaths.add(folderPath);
      childrenEl.classList.remove("hidden");
      icon.textContent = "📂";
    }
  }

  function _onFileClick(filePath, labelEl) {
    // 選択状態を更新
    document.querySelectorAll(".tree-label.selected").forEach((el) => el.classList.remove("selected"));
    labelEl.classList.add("selected");
    _selectedPath = filePath;

    BridgeClient.readFile(filePath, (res) => {
      if (res.success) {
        EditorView.load(filePath, res.data.content, res.data.encoding);
        if (!PreviewView.isVisible()) PreviewView.show();
      } else {
        StatusBar.showError(_errorMessage(res.error));
      }
    });
  }

  function refresh() {
    if (!_rootPath) return;
    BridgeClient.getTree(_rootPath, (res) => {
      if (res.success) {
        render(res.data);
      } else {
        StatusBar.showError(_errorMessage(res.error));
      }
    });
  }

  function _showContextMenu(e, targetPath, targetType) {
    _contextTarget = { path: targetPath, type: targetType };
    const menu = document.getElementById("context-menu");
    menu.classList.remove("hidden");

    // 画面端に収まるよう位置調整
    const mx = Math.min(e.clientX, window.innerWidth - menu.offsetWidth - 10);
    const my = Math.min(e.clientY, window.innerHeight - menu.offsetHeight - 10);
    menu.style.left = `${mx}px`;
    menu.style.top  = `${my}px`;
  }

  function _hideContextMenu() {
    document.getElementById("context-menu").classList.add("hidden");
  }

  function _onNewFile() {
    _hideContextMenu();
    if (!_rootPath) { StatusBar.showError("フォルダが選択されていません"); return; }

    const basePath = (_contextTarget && _contextTarget.type === "folder")
      ? _contextTarget.path
      : _rootPath;

    const name = window.prompt("新規ファイル名を入力してください（.md は自動付与）:");
    if (name === null) return;
    const trimmed = name.trim();
    if (!trimmed) { StatusBar.showError("ファイル名を入力してください"); return; }
    const fileName = trimmed.endsWith(".md") ? trimmed : trimmed + ".md";
    const filePath = basePath + "/" + fileName;

    BridgeClient.createFile(filePath, (res) => {
      if (res.success) {
        refresh();
        StatusBar.showSuccess(`"${fileName}" を作成しました`);
      } else {
        StatusBar.showError(_errorMessage(res.error));
      }
    });
  }

  function _onNewFolder() {
    _hideContextMenu();
    if (!_rootPath) { StatusBar.showError("フォルダが選択されていません"); return; }

    const basePath = (_contextTarget && _contextTarget.type === "folder")
      ? _contextTarget.path
      : _rootPath;

    const name = window.prompt("新規フォルダ名を入力してください:");
    if (name === null) return;
    const trimmed = name.trim();
    if (!trimmed) { StatusBar.showError("フォルダ名を入力してください"); return; }

    // フォルダ作成は空の .gitkeep を使わず Python 側で mkdir する
    // backend_bridge に createFolder がないため、ダミーファイルを作って後で削除する方法ではなく
    // 実装としてはフォルダパス + "/.mdkeep" を createFile で作成し、ツリー表示時にフォルダとして認識させる
    // → より正確には createFolder スロットが必要だが、今回は簡易対応としてフォルダ内に .gitkeep を作成する
    const folderPath = basePath + "/" + trimmed;
    const keepPath   = folderPath + "/.gitkeep";

    BridgeClient.createFile(keepPath, (res) => {
      if (res.success) {
        refresh();
        StatusBar.showSuccess(`"${trimmed}" フォルダを作成しました`);
      } else {
        StatusBar.showError(_errorMessage(res.error));
      }
    });
  }

  function _onRename() {
    _hideContextMenu();
    if (!_contextTarget) return;

    const oldPath = _contextTarget.path;
    const oldName = oldPath.split("/").pop();
    const newName = window.prompt("新しい名前を入力してください:", oldName);
    if (newName === null) return;
    const trimmed = newName.trim();
    if (!trimmed) { StatusBar.showError("名前を入力してください"); return; }

    const dir = oldPath.substring(0, oldPath.lastIndexOf("/"));
    const newPath = dir + "/" + trimmed;

    if (newPath === oldPath) return;

    // 新名前の確認（同名チェックは Python 側で FILE_EXISTS として返ってくる）
    BridgeClient.renameFile(oldPath, newPath, (res) => {
      if (res.success) {
        // 現在開いているファイルがリネームされた場合、パスを更新
        if (_selectedPath === oldPath) {
          _selectedPath = newPath;
          EditorView.load(newPath, EditorView.getValue(), EditorView.getCurrentEncoding());
        }
        refresh();
        StatusBar.showSuccess(`"${oldName}" → "${trimmed}" に変更しました`);
      } else {
        if (res.error === "FILE_EXISTS") {
          const overwrite = window.confirm(`"${trimmed}" は既に存在します。上書きしますか？`);
          if (!overwrite) return;
          // 上書き確認後に再実行（Python側にforce引数はないため、既存を先に削除してリネーム）
          BridgeClient.deleteFile(newPath, (delRes) => {
            if (!delRes.success) { StatusBar.showError(_errorMessage(delRes.error)); return; }
            BridgeClient.renameFile(oldPath, newPath, (res2) => {
              if (res2.success) { refresh(); StatusBar.showSuccess(`リネームしました`); }
              else { StatusBar.showError(_errorMessage(res2.error)); }
            });
          });
        } else {
          StatusBar.showError(_errorMessage(res.error));
        }
      }
    });
  }

  function _onDelete() {
    _hideContextMenu();
    if (!_contextTarget) return;

    const targetPath = _contextTarget.path;
    const name = targetPath.split("/").pop();
    if (!window.confirm(`"${name}" を削除しますか？\nこの操作は元に戻せません。`)) return;

    BridgeClient.deleteFile(targetPath, (res) => {
      if (res.success) {
        // 削除対象が現在開いているファイルの場合はエディタをクリア
        if (_selectedPath === targetPath) {
          _selectedPath = null;
          EditorView.clear();
          PreviewView.clear();
        }
        refresh();
        StatusBar.showSuccess(`"${name}" を削除しました`);
      } else {
        StatusBar.showError(_errorMessage(res.error));
      }
    });
  }

  // ------------------------------------------------------------------
  // リサイザー（左右ペイン幅調整）
  // ------------------------------------------------------------------
  function _initResizer() {
    const resizer  = document.getElementById("resizer");
    const leftPane = document.getElementById("left-pane");
    let _dragging  = false;
    let _startX    = 0;
    let _startW    = 0;

    resizer.addEventListener("mousedown", (e) => {
      _dragging = true;
      _startX   = e.clientX;
      _startW   = leftPane.offsetWidth;
      resizer.classList.add("dragging");
      document.body.style.cursor = "col-resize";
      document.body.style.userSelect = "none";
    });

    document.addEventListener("mousemove", (e) => {
      if (!_dragging) return;
      const newW = Math.max(120, Math.min(600, _startW + (e.clientX - _startX)));
      leftPane.style.width = `${newW}px`;
      EditorView.refresh();
    });

    document.addEventListener("mouseup", () => {
      if (!_dragging) return;
      _dragging = false;
      resizer.classList.remove("dragging");
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    });
  }

  return { init, render, refresh };
})();


/* ============================================================
   エラーコード → メッセージ変換
   ============================================================ */
function _errorMessage(code) {
  const map = {
    FOLDER_NOT_FOUND:  "フォルダが見つかりません",
    FILE_NOT_FOUND:    "ファイルが見つかりません",
    PERMISSION_DENIED: "アクセスが拒否されました",
    PATH_TRAVERSAL:    "フォルダ外へのアクセスは禁止されています",
    ENCODING_ERROR:    "文字コードを判定できませんでした",
    FILE_EXISTS:       "同名のファイルが既に存在します",
    BASE_NOT_SET:      "フォルダが選択されていません",
    BRIDGE_NOT_READY:  "バックエンドと接続できていません",
    UNKNOWN_ERROR:     "予期しないエラーが発生しました",
  };
  return map[code] || `エラー: ${code}`;
}


/* ============================================================
   App - 全体初期化
   ============================================================ */
const App = (() => {
  function init() {
    StatusBar.init();
    PreviewView.init();
    EditorView.init();
    TreeView.init();
    _bindToolbar();
    StatusBar.showSuccess("mdFileReader が起動しました");
  }

  function _bindToolbar() {
    // フォルダ選択ボタン
    document.getElementById("btn-select-folder").addEventListener("click", () => {
      BridgeClient.selectFolder((path) => {
        if (!path) return;
        BridgeClient.getTree(path, (res) => {
          if (res.success) {
            TreeView.render(res.data);
            StatusBar.showSuccess(`フォルダを開きました: ${path}`);
          } else {
            StatusBar.showError(_errorMessage(res.error));
          }
        });
      });
    });

    // 保存ボタン
    document.getElementById("btn-save").addEventListener("click", () => EditorView.save());

    // エディタトグル
    document.getElementById("btn-toggle-editor").addEventListener("click", () => {
      EditorView.toggle();
      EditorView.refresh();
    });

    // プレビュートグル
    document.getElementById("btn-toggle-preview").addEventListener("click", () => {
      PreviewView.toggle();
      EditorView.refresh();
    });

    // Ctrl+S (CodeMirror の extraKeys で処理済みだが document レベルでもカバー)
    document.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "s") {
        e.preventDefault();
        EditorView.save();
      }
    });
  }

  return { init };
})();


/* ============================================================
   QWebChannel 接続後にアプリを起動
   ============================================================ */
document.addEventListener("DOMContentLoaded", () => {
  if (typeof QWebChannel === "undefined") {
    console.error("qwebchannel.js が読み込まれていません");
    return;
  }
  new QWebChannel(qt.webChannelTransport, (channel) => {
    BridgeClient.init(channel.objects.backend);
    App.init();
  });
});
