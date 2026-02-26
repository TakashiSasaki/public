# mdns-inspector

LAN内のmDNSトラフィックをキャプチャし、表示し、必要に応じて他ネットワークへ転送するPython製ツールのプロトタイプです。

## 方針
- コア機能は `asyncio` で実装
- GUIは `Tk/ttk` で実装
- GUIとコアは分離
- 実行は `uv run` を前提

## ディレクトリ構成
```text
mdns-inspector/
  pyproject.toml
  README.md
  githooks/
    pre-commit
    bump-version.py
    setup-hooks.ps1
    setup-hooks.sh
  src/
    my_mdns/
      __init__.py
      __main__.py
      core/
        __init__.py
        capture.py
        dns_packet.py
        events.py
        forwarder.py
        interfaces.py
        query.py
        runtime.py
      gui/
        __init__.py
        app.py
```

## プロトタイプ機能
- mDNS multicast 受信
  - IPv4: `224.0.0.251:5353`
  - IPv6: `ff02::fb:5353`
  - いずれもインターフェイスごとにjoinして受信
- GUIで受信パケットを一覧表示
- 指定した転送先（host:port）へ受信パケットをUDP転送
- サービス問い合わせ送信
  - Mainタブから全IFへ一括送信
  - Listeningタブから選択IFへ IPv4/IPv6 別送信
- 手動名前解決クエリ送信
  - Resolveタブで `.local.` 前の名前入力 + QTYPE選択
  - IP付与済みIFごとに IPv4/IPv6 送信ボタン
- 個別のDNSレコード収集とリアルタイムソート表示
  - A, AAAA, SRV, PTR, TXT レコードをタブ別に表示
  - 受信時刻（Last Seen）、送信元IP、宛先種別（Multicast/Unicast）を記録
- 統計表示（Statsタブ）
  - Packet direction counts（Query/Response/Other）
  - Query QTYPE counts
  - Response RR TYPE counts
  - 各行に `last received` を表示
- Listeningタブでインターフェイスごとの送信カウンタ表示
  - `tx4`, `tx6`（受信パケットは単一ソケット化の都合上 `* (All Interfaces)` 行にて全IFの合計値を表示）
- カラム幅と手動クエリの入力内容の永続化（自動保存・復元）

## GUIタブ
- Main: 実行トグル、サービス問い合わせ一括送信、転送先設定、受信パケット全体表示
- Listening: インターフェイス一覧、IF選択問い合わせ、送受信カウンタ
- Queries: ネットワーク上で観測されたmDNSクエリの一覧とリクエスト回数
- A / AAAA / SRV / PTR / TXT: 各レコードの収集結果（最新受信順）
- Stats: 受信パケット種別の集計表3種
- Resolve: 手動クエリ送信（IFごと、前回入力値を記憶）
- Logs: ログ表示

## 起動方法
```bash
uv run mdns-inspector
```

バージョン確認:
```bash
uv run mdns-inspector --version
```

## バージョン運用（プロトタイプ）
- バージョンは `pyproject.toml` に保持
- `githooks/bump-version.py` で `pyproject.toml` / `package.json` / `manifest.webmanifest` の `version` をバンプ
- `githooks/pre-commit` でコミット前に自動実行

hooksPath設定:
```bash
pwsh -File githooks/setup-hooks.ps1
```

## その他
- 開発者やコーディングエージェント向けの情報は AGENTS.md に記載する。
- README.md は利用者向けのドキュメントである。
- ライセンスは MIT ライセンス。

## 作者
- Takashi Sasaki
- https://x.com/TakashiSasaki
