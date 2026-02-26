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
- mDNS受信実装では `0.0.0.0` / ifindex `0` の単発JOINに依存せず、IPv4/IPv6ともインターフェイスごとに multicast group join を優先する（取りこぼし防止）。
- インターフェイス向けソケットオプションは以下を基本方針とする。
- 受信ソケット: `SO_REUSEADDR`（可能なら `SO_REUSEPORT` も）を設定し、IPv4は `IP_ADD_MEMBERSHIP`、IPv6は `IPV6_JOIN_GROUP` をインターフェイス単位で適用する。
- 送信ソケット: IPv4は `IP_MULTICAST_IF`、IPv6は `IPV6_MULTICAST_IF` を明示して送信元インターフェイスを固定する。
- `Listening` タブのインターフェイス表示は、各IFの `rx4/tx4/rx6/tx6` カウンタを扱う前提で実装・保守する。

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

# その他（このセクションは削除せず、このセクションの内容は他の適切なセクションに構造化することを強く推奨する）
- このセクションの内容は上記セクションへ順次移管済み。新規ルールは該当セクションへ追加する。
- コミットメッセージは英語で記述する。
- AGENTS.md README.md は日本語で記述する。
