Pythonスクリプトが、自身が実行されている環境を内省的に調査する際に利用できる、`sys` と `site` モジュールについて記載する。
以下では、**「実行環境の把握・診断」に有用なものだけ**を厳選し、
**読み取り専用の観点**で `sys` と `site` を整理する。
（副作用を持つ API は除外、または注意書きを付ける）

---

# 1. `sys` モジュール

## 1.1 実行ファイル・環境同一性（最重要）

### モジュール変数

| 変数                     | 意味                                       |
| ---------------------- | ---------------------------------------- |
| `sys.executable`       | **実際に起動されている Python インタープリタの実行ファイルパス**   |
| `sys.prefix`           | 現在の実行環境の prefix（pip / site-packages の基準） |
| `sys.base_prefix`      | venv の元となったベース Python の prefix           |
| `sys.exec_prefix`      | プラットフォーム依存バイナリの prefix（通常は `prefix` と同一） |
| `sys.base_exec_prefix` | base 側の exec prefix                      |

---

## 1.2 import・ロード構造（診断用）

### モジュール変数

| 変数                        | 意味                      |
| ------------------------- | ----------------------- |
| `sys.path`                | import 探索パス（**最終的な真実**） |
| `sys.meta_path`           | import フック（Finder 群）    |
| `sys.path_hooks`          | path-based import hooks |
| `sys.path_importer_cache` | path → importer のキャッシュ  |

※ 読み取りのみなら安全

---

## 1.3 実行コンテキスト

| 変数                   | 意味                      |
| -------------------- | ----------------------- |
| `sys.argv`           | コマンドライン引数               |
| `sys.platform`       | プラットフォーム識別子（例: `win32`） |
| `sys.version`        | Python バージョン文字列         |
| `sys.version_info`   | バージョン構造体                |
| `sys.implementation` | 実装情報（CPython / PyPy 等）  |

---

## 1.4 I/O・ランタイム補助（参照のみ）

| 変数                            | 意味               |
| ----------------------------- | ---------------- |
| `sys.stdin / stdout / stderr` | 標準入出力            |
| `sys.getfilesystemencoding()` | ファイルシステムエンコーディング |
| `sys.getdefaultencoding()`    | デフォルト文字エンコーディング  |

---

## 1.5 情報取得関数（安全）

| 関数                        | 意味        |
| ------------------------- | --------- |
| `sys.getsizeof(obj)`      | オブジェクトサイズ |
| `sys.getrecursionlimit()` | 再帰上限      |
| `sys.getswitchinterval()` | スレッド切替間隔  |

---

# 2. `site` モジュール

## 2.1 site-packages / インストール先（最重要）

### 情報取得関数

| 関数                           | 意味                               |
| ---------------------------- | -------------------------------- |
| `site.getsitepackages()`     | system / venv の site-packages 一覧 |
| `site.getusersitepackages()` | user site-packages のパス           |

---

### モジュール変数

| 変数                      | 意味                      |
| ----------------------- | ----------------------- |
| `site.ENABLE_USER_SITE` | user site-packages が有効か |
| `site.USER_SITE`        | user site-packages（文字列） |
| `site.USER_BASE`        | user install の基準ディレクトリ  |

---

## 2.2 prefix・探索構造

| 変数              | 意味                             |
| --------------- | ------------------------------ |
| `site.PREFIXES` | site-packages 探索に使われる prefix 群 |

---

## 2.3 起動時フックの存在確認（間接）

※ 関数はないが、**調査対象として重要**

* `sitecustomize.py`
* `usercustomize.py`

存在確認例（読み取りのみ）：

```python
import importlib.util

for name in ("sitecustomize", "usercustomize"):
    print(name, bool(importlib.util.find_spec(name)))
```

---

## 2.4 注意：読み取り目的では使わないもの

以下は **環境を変更するため**、本件の目的では除外：

* `site.addsitedir()`
* `site.removeduppaths()`
* `site.main()`

---

# 3. 実務向け：最小・安全な環境ダンプ

```python
import sys, site

print("=== sys ===")
print("executable :", sys.executable)
print("prefix     :", sys.prefix)
print("base_prefix:", sys.base_prefix)
print("version    :", sys.version)
print("platform   :", sys.platform)

print("\n=== site ===")
print("ENABLE_USER_SITE:", site.ENABLE_USER_SITE)
print("USER_SITE        :", site.getusersitepackages())
print("SYSTEM_SITE:")
for p in site.getsitepackages():
    print(" ", p)
```

---

# 4. まとめ（観点別対応）

| 観点            | 参照先                                     |
| ------------- | --------------------------------------- |
| 実体の Python    | `sys.executable`                        |
| venv 判定       | `sys.prefix != sys.base_prefix`         |
| import の真実    | `sys.path`                              |
| pip install 先 | `sys.prefix` + `site.getsitepackages()` |
| user install  | `site.getusersitepackages()`            |
| user site 有効？ | `site.ENABLE_USER_SITE`                 |

---

## 最終結論

* `sys` は **「この Python プロセスは何者か」**を示す
* `site` は **「どこからモジュールを読む構成か」**を示す
* 両者は **完全に補完関係**
* **読み取り専用で使う限り、副作用はない**

この一覧を基準にすれば、
**外部コマンドに依存しない自己診断用 Python スクリプト**を安定して構築できます。
