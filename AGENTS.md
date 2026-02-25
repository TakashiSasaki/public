# AGENTS Guide for `git-lfs-lite`

このファイルは、このリポジトリで作業する開発者/コーディングエージェント向けの共通ガイドです。

## 1. プロジェクト概要

- 目的: 最小構成の Git LFS サーバ実装（Python 標準ライブラリベース）
- 主要実装: `lfs_server.py`
- 対応API:
  - Batch API: `POST /info/lfs/objects/batch`
  - Basic transfer:
    - `PUT /info/lfs/objects/{oid}`
    - `POST /info/lfs/objects/{oid}/verify`
    - `GET /info/lfs/objects/{oid}`
  - Locking API:
    - `POST /info/lfs/locks`
    - `GET /info/lfs/locks`
    - `POST /info/lfs/locks/verify`
    - `POST /info/lfs/locks/{id}/unlock`

## 2. 実行環境ルール

- Python は `uv` で管理する前提。
- 直接 `python` が使えない環境があるため、実行コマンドは原則 `uv run python ...` を使う。
- 例:
  - サーバ起動: `uv run python .\lfs_server.py --host 127.0.0.1 --port 8080 --storage-dir .\data`
  - テスト実行: `pwsh -NoLogo -NoProfile -File .\scripts\test_lfs_server.ps1`

## 3. 仕様準拠の重点ポイント

- Batch API は `/{base-path}/objects/batch` に実装する（既定 `base-path=/info/lfs`）。
- Batch request:
  - `transfers`（複数形）を受ける。未指定時は `basic` を仮定。
  - `Accept` は `application/vnd.git-lfs+json` を受理（`*/*` も許容）。
  - `Content-Type` は `application/vnd.git-lfs+json`（`charset=utf-8` 付き許容）。
  - `size` は `>= 0`。
- Batch response:
  - 正常系は原則 HTTP 200 で `objects` 内に個別エラーを返す。
  - `hash_algo != sha256` は個別オブジェクトエラー `409`。
  - バリデーション不正は `422`（実装方針に従う）。
- 401 応答時は `LFS-Authenticate` ヘッダを返す（`WWW-Authenticate` も返す）。

## 4. 認証・アクセス制御

- 認証モード:
  - `none`
  - `basic`（単一ユーザー/パスワード）
- IP 制限:
  - `--allow-net`（複数指定）
  - `--allow-nets`（カンマ区切り）
  - `LFS_ALLOW_NETS`（環境変数）

## 5. データ配置

- オブジェクト: `<storage-dir>/objects/<oid-prefix>/.../<oid>`
- lock DB: `<storage-dir>/locks.json`

## 6. 変更時のチェックリスト

- `README.md` と実装内容が一致していること（エンドポイント/ヘッダ/挙動）。
- Batch API のパスとペイロードキー（`transfers`）を崩していないこと。
- Basic auth 時の 401 ヘッダ（`LFS-Authenticate`）を維持すること。
- テストスクリプト（`scripts/test_lfs_server.ps1`）で主要フローを確認すること。

## 7. 参考仕様

- Batch API:
  - https://raw.githubusercontent.com/git-lfs/git-lfs/main/docs/api/batch.md
- Basic transfer adapter:
  - https://raw.githubusercontent.com/git-lfs/git-lfs/main/docs/api/basic-transfers.md
- Locking API:
  - https://raw.githubusercontent.com/git-lfs/git-lfs/main/docs/api/locking.md
