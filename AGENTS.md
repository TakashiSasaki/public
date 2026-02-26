# Project Notes

## ドキュメント運用
- `README.md` はユーザー向けドキュメント、`AGENTS.md` は開発者/コーディングエージェント向け指示として運用する。
- プロジェクト全体の方針・設計判断・試行錯誤の結果は、必要に応じて `AGENTS.md` に追記して共有する。
- 特に Windows 環境でハマりやすい点と対処法は積極的に残す。

## 開発環境
- Python環境は `uv` で管理する。
- Linux / Windows の両環境で開発される前提で実装・検証する。

## 構成方針
- コアロジックは `src/my_mdns/core/` に集約し、GUIロジックは `src/my_mdns/gui/` に分離する。
- mDNS受信実装では、OS（特にWindows）の挙動を安定させるため、IPv4/IPv6それぞれで `0.0.0.0` または `::` にバインドした**単一のUDPソケット**を利用し、そこからすべてのネットワークインターフェイスのマルチキャストグループへ JOIN する方式を採用している。
- インターフェイス向けソケットオプションは以下を基本方針とする。
  - 受信ソケット: `SO_REUSEADDR`（可能なら `SO_REUSEPORT` も）を設定し、IPv4は `IP_ADD_MEMBERSHIP`、IPv6は `IPV6_JOIN_GROUP` を適用する。
  - 送信ソケット: 
    - IPv4は `IP_MULTICAST_IF`、IPv6は `IPV6_MULTICAST_IF` を明示して送信元インターフェイスを固定する。
    - mDNSの規格 (RFC 6762) およびローカルループバックの安定した観測のため、マルチキャストの TTL/HOPS は `255` を指定し、ループバック (`IP_MULTICAST_LOOP` / `IPV6_MULTICAST_LOOP`) を有効にする。
- `Listening` タブの表示について、パケット送信 (`tx4`/`tx6`) は各IFごとに計測可能だが、上記の単一ソケット化の都合上、パケット受信 (`rx4`/`rx6`) は個別のIFごとの追跡が困難なため、UI上では `* (All Interfaces)` というグローバル行で合計値を集計して表示する設計とする。

## GUI・データ保存と復元の方針
- 設定情報（カラム幅など）や直近の入力情報（手動クエリのName/Typeなど）は、`user_data_dir` 配下の SQLite データベース内 `ui_settings` テーブルを用いてKVS形式で随時永続化し、次回の起動時に自動復元する。
- 収集したDNSレコードはDB上で記録し、UIでは常に最新のレコード（Last Seen で降順）が先頭に来るようにソート・更新する。

## フックとバージョン運用
- バージョンのパッチレベルはコミット時に必ずバンプする。
- Git hook とバンプ補助スクリプトは `githooks` サブモジュールに集約し、他プロジェクトと共有する。
- `githooks/pre-commit` は `pyproject.toml` / `package.json` / `manifest.webmanifest` を自動検出してバンプ可能。
- フック有効化は `githooks/setup-hooks.ps1`（Windows）または `githooks/setup-hooks.sh`（Linux/macOS）を使って `core.hooksPath` を設定する。
- リポジトリ直下の旧 `scripts/` フック補助は使わず、`githooks` 側に一本化する。

## コミット運用
- コミットメッセージは常に具体的で、変更意図が分かる内容にする。

## データ・設定の保存方針
- ユーザーの設定情報やデータは基本的に `platformdirs` の `user_data_dir` を使って保存場所を決める。
- mdns-inspectorでは `user_data_dir(appname="work.moukaeritai.mdns-inspector", appauthor=None)` を使う。
- このアプリケーションの主要な開発者は moukaeritai.work ドメインを所有しているので、ドメイン名の逆順にアプリケーション名を連接している。

## OS-specific Notes (Windows)
- Windows 上の Python (`asyncio` + `DatagramProtocol`) では、UDPパケットの宛先IP（Unicast か Multicast か）を標準機能で取得するための `recvmsg` がサポートされていない。
- 代替案として、mDNSレスポンスパケット内の **Cache-flushビット**（RRのクラスフィールドの最高ビット）を流用して判定する。
  - Cache-flushビットが `1`: マルチキャスト（またはブロードキャスト）配信を想定。
  - Cache-flushビットが `0`: ユニキャストレスポンスを想定。
- この判定ロジックにより、A/AAAAレコードの「宛先タイプ」を擬似的に表現する。

# その他（このセクションは削除せず、このセクションの内容は他の適切なセクションに構造化することを強く推奨する）
- このセクションの内容は上記セクションへ順次移管済み。新規ルールは該当セクションへ追加する。
- コミットメッセージは英語で記述する。
- AGENTS.md README.md は日本語で記述する。
- Python 環境は uv で管理していることをわすれずに。もし uv を使っていないなら uv を使うように促してほしい。