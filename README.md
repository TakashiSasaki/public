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
- 統計表示（Statsタブ）
  - Packet direction counts（Query/Response/Other）
  - Query QTYPE counts
  - Response RR TYPE counts
  - 各行に `last received` を表示
- ListeningタブでIFごとのカウンタ表示
  - `rx4`, `tx4`, `rx6`, `tx6`

## GUIタブ
- Main: 実行トグル、サービス問い合わせ一括送信、転送先設定、受信パケット表示
- Listening: インターフェイス一覧、IF選択問い合わせ、IF別送受信カウンタ
- Stats: 受信パケット種別の集計表3種
- Resolve: 手動クエリ送信（IFごと）
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

## 作者
- Takashi Sasaki
- https://x.com/TakashiSasaki
