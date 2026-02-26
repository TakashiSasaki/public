# file-catalog: Agent and Developer Guidelines

大量のファイルやフォルダが散らかってしまったデスクトップの整理を支援するPythonアプリケーションです。
この `AGENTS.md` は、開発者やコーディングエージェントが従うべき指示、試行錯誤の結果、および共有情報を記録するリビングドキュメントです。

## プロジェクト概要

1.  **デスクトップ場所の特定**: 整理対象となるデスクトップのパスを自動で特定します。
2.  **アイテムの列挙と分類**: デスクトップ直下のアイテムを移動前に列挙・分類します。
    - **ファイル情報**: フルパス、更新日付、パーミッション、サイズ。
    - **フォルダ情報**: フルパス、更新日付、パーミッション。
    - **容量計算**: フォルダ配下の全ファイルの合計容量。
3.  **データの永続化**: 取得情報はSQLiteデータベースに保存し、再利用可能にします。

## 技術仕様

- **ランタイム**: Python (実行環境管理には `uv` を使用)
- **GUIライブラリ**: `tkinter` (`ttk`)
- **データベース**: SQLite
- **データ保存先**: [`platformdirs`](https://pypi.org/project/platformdirs/) を使用
  - `app_name`: `file_catalog`
  - `appauthor`: `work.moukaeritai`

## 設計原則

- **コアとUIの分離**: コアコンポーネント（ロジック、データアクセス）とユーザーインターフェイス（Tkinter）を厳格に分離します。
- **再利用性**: コアコンポーネントは、GUI以外のインターフェイス（CLIなど）からも利用可能なよう、再利用可能性を重視して設計します。

## 開発・エージェント方針

- **環境**: 主に Windows 環境で開発を行います。
- **ドキュメント管理**:
  - `AGENTS.md` には、他の開発者やエージェントが従うべき指示や共有情報を記述します。
  - 試行錯誤の結果は `AGENTS.md` で積極的に共有してください。
- **バージョン管理とコミット**:
  - コミットのたびに、バージョンのパッチレベルをバンプアップしてください。
  - コミットの際には、詳細なコミットメッセージ（英語）を記述してください。

## 試行錯誤メモ

- 2026-02-25: 初期実装として、`src/desktop_seiri` にコア（`paths.py`, `scanner.py`, `db.py`, `service.py`）とUI（`gui.py`）を分離して追加。
- 2026-02-25: デスクトップ直下を列挙し、ファイル情報（パス・更新日時・パーミッション・サイズ）とフォルダ情報（パス・更新日時・パーミッション・配下総容量）をSQLiteに保存する構成を導入。
- 2026-02-25: `tkinter/ttk` のGUIで、検索文字列とタイプ（all/file/folder）によるDB検索を可能にした。
- 2026-02-25: スキャンを再帰走査に変更し、探索で見つかった全ファイル・全フォルダをDBに保存する方式へ拡張。
- 2026-02-25: `scanned_at` を廃止し、`first_seen` / `last_seen` を導入。未検出になったアイテムは削除せず、`last_seen` が更新されない履歴保持型に変更。
- 2026-02-25: `path` はリンク自体のパスを保持する方針に変更し、リパースポイント向けに `target_path`（NULL許容）カラムを追加。
- 2026-02-25: Tk `Treeview` の描画負荷を下げるため、検索結果表示をページング（既定 200件/ページ）に変更。
- 2026-02-25: GUIにカラム表示ON/OFFチェックボックスを追加し、`displaycolumns` の切替で描画負荷を調整可能にした。
- 2026-02-25: `last_seen` の最新値が現在時刻から1時間以内の場合は再スキャンをスキップする判定を追加。
- 2026-02-25: 将来の多様なパス体系に対応するため `root` カラムを追加し、`path` はフルパス、`root` はドライブ/UNC共有/URLのスキーム+オーソリティ相当を保持する設計に変更。
- 2026-02-25: 重複情報を減らすため保存形式を `root` + `path` + `name` に再設計し、`path` は中間パスのみ保持する方式へ変更。あわせて `target_path` カラム名を `target` にリネーム。
- 2026-02-25: DB保存インターフェイスで `root/path/name` 形式のバリデーションを実施し、`path` が区切り文字で始まり区切り文字で終わるルール違反時は例外を送出するように変更。
- 2026-02-25: 保存前バリデーションを追加強化し、`name` は区切り文字で開始不可、`root` は区切り文字で終了不可（ただし `root='.'` は許容）とした。
- 2026-02-25: 日時保存をISO8601文字列からWindows FILETIME 64-bit整数へ統一し、Windows/Linuxの両環境で同一フォーマットで記録する方式に変更。
- 2026-02-26: パッケージ名を `desktop_seiri` から `file_catalog`、プロジェクト名を `desktop-seiri` から `file-catalog` へ変更。
- 2026-02-26: 起動時の自動スキャンを廃止し、GUI上の明示的な `Refresh Desktop Scan` 操作でのみスキャンを実行する方式に変更。
- 2026-02-26: GUIにデータ保存ディレクトリをエクスプローラーで開く `Open Data Folder` ボタンを追加。

## 現在のデータベース設計

- DBファイル: `platformdirs.user_data_dir(appname="file_catalog", appauthor="work.moukaeritai")` 配下の `desktop_items.sqlite3`
- テーブル: `items`
- カラム:
  - `id` (`INTEGER PRIMARY KEY AUTOINCREMENT`)
  - `item_type` (`TEXT NOT NULL`, `file` / `folder` 制約)
  - `name` (`TEXT NOT NULL`): ファイル名またはフォルダ名（末尾要素）
  - `root` (`TEXT NOT NULL`): ルート要素（例: `C:`, `\\server\share`, `https://host`）。相対パスは `.` を使用
  - `path` (`TEXT NOT NULL`): 中間パス（`root` と `name` を除いた部分）
  - `target` (`TEXT NULL`): シンボリックリンク/ジャンクションのリンク先。通常は `NULL`
  - `modified_filetime` (`INTEGER NOT NULL`): 対象の更新日時（Windows FILETIME 64-bit, 100ns刻み）
  - `permissions` (`TEXT NOT NULL`): パーミッション表現
  - `size_bytes` (`INTEGER NULL`): ファイルサイズ（ファイルのみ）
  - `folder_total_size_bytes` (`INTEGER NULL`): フォルダ配下合計サイズ（フォルダのみ）
  - `first_seen_filetime` (`INTEGER NOT NULL`): 初回発見日時（Windows FILETIME 64-bit）
  - `last_seen_filetime` (`INTEGER NOT NULL`): 最終発見日時（Windows FILETIME 64-bit）
- 論理パス再構成: `root + path + name`
- 正規化ルール:
  - `path` は必ず先頭文字が区切り文字（`/` または `\`）
  - `path` は必ず末尾文字も区切り文字（`/` または `\`）
  - ディレクトリを含まない相対ファイルでも `path` は区切り文字1文字（例: `\`）
  - `name` は区切り文字で始めない
  - `root` は区切り文字で終えない（相対パスの `.` は例外的に許容）
- 一意制約: `UNIQUE(root, path, name)`
- CHECK制約:
  - `name` は空文字不可かつ先頭区切り文字不可
  - `root` は空文字不可かつ末尾区切り文字不可（相対パスの `.` は許容）
  - `path` は空文字不可かつ先頭/末尾が区切り文字
- インデックス:
  - `idx_items_name` (`name`)
  - `idx_items_type` (`item_type`)
  - `idx_items_last_seen` (`last_seen_filetime`)
- 更新方針:
  - スキャン時は `ON CONFLICT(root, path, name)` でアップサート
  - 既存行は `last_seen_filetime` のみ更新され、`first_seen_filetime` は保持
  - スキャンで見つからなかった行は削除しない（履歴として残す）
