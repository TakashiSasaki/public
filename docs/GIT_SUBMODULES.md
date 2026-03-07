# Git Submodule の構造とコマンド

## 1. 概要

Git submodule は、ある Git リポジトリの中で別の Git リポジトリを参照する仕組みである。サブモジュールは通常のディレクトリとは異なり、親リポジトリの tree 内では "gitlink" と呼ばれる特殊エントリとして保存される。

この設計により、親リポジトリはサブモジュールの特定の commit を固定して参照する。

## 2. Git tree における表現

Git の tree オブジェクトではサブモジュールは次の形式で保存される。

```
mode 160000 commit <hash> <path>
```

mode 160000 は "gitlink" を意味する。

これは通常のファイルやディレクトリではなく、外部リポジトリの commit を参照するポインタである。

## 3. 設定ファイルの構造

### 3.1 .gitmodules

`.gitmodules` はリポジトリにコミットされる設定ファイルである。

例

```
[submodule "lib"]
    path = lib
    url = https://example.com/lib.git
```

ここにはサブモジュールの

* path
* url
* branch (任意)

などが記述される。

### 3.2 .git/config

`.git/config` はローカルリポジトリ固有の設定である。

`.gitmodules` の内容は `git submodule init` によりここへコピーされる。

例

```
[submodule "lib"]
    url = https://example.com/lib.git
```

この設定はユーザーが変更できる。

## 4. 設定階層

Git submodule の設定は次の階層で管理される。

```
.gitmodules   (共有設定)
      ↓
.git/config   (ローカル設定)
```

`.git/config` は `.gitmodules` を上書きする。

## 5. 主なサブコマンド

### 5.1 add

新しいサブモジュールを追加する。

```
git submodule add <repo> <path>
```

このコマンドは次の処理を行う。

1. リポジトリを clone
2. `.gitmodules` を更新
3. gitlink を index に追加

### 5.2 init

`.gitmodules` の設定を `.git/config` にコピーする。

既に設定が存在する場合は上書きされない。

### 5.3 update

サブモジュールを checkout する。

```
git submodule update
```

処理内容

1. clone (必要な場合)
2. 指定 commit checkout

### 5.4 sync

`.gitmodules` と `.git/config` の URL を同期する。

同期対象

```
submodule.<name>.url
```

### 5.5 status

サブモジュールの状態を表示する。

```
git submodule status
```

### 5.6 summary

サブモジュールの差分概要を表示する。

### 5.7 foreach

全サブモジュールでコマンドを実行する。

### 5.8 set-url

サブモジュールの URL を変更する。

### 5.9 set-branch

追跡ブランチを設定する。

### 5.10 deinit

サブモジュールのローカル設定を削除する。

## 6. init と sync の設計理由

Git は `.git/config` をユーザーのローカル設定として扱う。

そのため `.gitmodules` の変更を自動反映するとローカル設定が破壊される可能性がある。

このため

```
init  = 初期コピー
sync  = URL再同期
```

として分離されている。

## 7. init の挙動

### 冪等性

`git submodule init` を複数回実行しても設定は変更されない。

### 新しいサブモジュール

`.gitmodules` に新しいサブモジュールが追加された場合のみ `.git/config` に設定が追加される。

## 8. sync の同期範囲

`git submodule sync` が同期するのは URL のみである。

同期されない設定例

* branch
* update
* ignore
* fetchRecurseSubmodules

## 9. 差異検出

Git には `.gitmodules` と `.git/config` の差異を検出する専用コマンドは存在しない。

比較する場合は `git config` を利用する。

例

```
git config -f .gitmodules --get-regexp ^submodule
git config --get-regexp ^submodule
```

## 10. 運用上の典型コマンド

クローン後

```
git submodule update --init --recursive
```

URL変更後

```
git submodule sync
git submodule update
```

## 11. 重要な概念

サブモジュールの本質は URL ではなく commit pointer である。

親リポジトリは

```
path → commit
```

という参照のみを保持する。

URL はその commit を取得するための transport 情報に過ぎない。

## 12. サブモジュールのコミットが最新かどうかを調査する方法

親リポジトリが参照しているサブモジュールの commit が upstream の最新 commit かどうかを確認する方法はいくつかある。

### 12.1 `git submodule status`

```
git submodule status
```

出力例

```
 3f2a1c libA
+92a8bc libB
```

記号の意味

* 空白: 親リポジトリが指す commit と一致
* `+` : 作業ツリーの submodule commit が親リポジトリの index と異なる
* `-` : submodule 未初期化

ただしこのコマンドは upstream の最新 commit との比較は行わない。

### 12.2 `git submodule update --remote --dry-run`

```
git submodule update --remote --dry-run
```

このコマンドは remote の最新 commit を取得した場合に変更が発生するかを確認できる。

### 12.3 サブモジュール内で fetch して比較

最も確実な方法はサブモジュール内部で remote の commit を取得して比較する方法である。

```
cd <submodule>

git fetch

git status
```

または

```
git log HEAD..origin/main
```

これにより upstream に存在する commit を確認できる。

### 12.4 全サブモジュールを一括確認

```
git submodule foreach 'git fetch && git status'
```

これにより全サブモジュールの状態を一括確認できる。

### 12.5 親リポジトリの記録 commit を確認

親リポジトリが指している commit は次の方法で確認できる。

```
git ls-tree HEAD <submodule-path>
```

出力例

```
160000 commit 3f2a1c... libA
```

ここに表示される commit が親リポジトリが固定しているサブモジュール commit である。

### 12.6 upstream の最新 commit を確認

```
cd <submodule>

git ls-remote origin
```

または

```
git rev-parse origin/main
```

これを親リポジトリの commit と比較することで

* 親リポジトリが古い commit を固定している
* 最新 commit と一致している

かを判断できる。

### 12.7 実務的な確認手順

一般的な手順

```
git submodule foreach 'git fetch'

git submodule foreach 'git log HEAD..origin/main --oneline'
```

出力が存在する場合、親リポジトリが固定している commit は upstream より古い。

この状態でサブモジュールを最新に更新するには

```
git submodule update --remote
```

を使用する。
