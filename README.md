# my-mdns

LAN内のmDNSトラフィックをキャプチャし、表示し、必要に応じて他ネットワークへ転送するPython製ツールのプロトタイプです。

## 方針
- コア機能は `asyncio` で実装
- GUIは `Tk/ttk` で実装
- GUIとコアは分離
- 実行は `uv run` を前提

## ディレクトリ構成
```text
my-mdns/
  pyproject.toml
  README.md
  githooks/
    pre-commit
  scripts/
    bump_patch.py
    setup-hooks.ps1
    setup-hooks.sh
  src/
    my_mdns/
      __init__.py
      __main__.py
      core/
        __init__.py
        capture.py
        events.py
        forwarder.py
        runtime.py
      gui/
        __init__.py
        app.py
```

## プロトタイプ機能
- mDNS multicast (`224.0.0.251:5353`) を受信
- GUIで受信パケットを一覧表示
- 指定した転送先（host:port）へ受信パケットをUDP転送

## 起動方法
```bash
uv run my-mdns
```

バージョン確認:
```bash
uv run my-mdns --version
```

## バージョン運用（プロトタイプ）
- バージョンは `pyproject.toml` に保持
- `scripts/bump_patch.py` でパッチバージョンを1つ上げる
- `githooks/pre-commit` でコミット前に自動実行する想定

hooksPath設定:
```bash
pwsh -File scripts/setup-hooks.ps1
```

## 作者
- Takashi Sasaki
- https://x.com/TakashiSasaki
AGENTS.mdは他の開発者やコーディングエージェントが共通して参照する指示であるので、コーディング上の注意点や試行錯誤の結果を積極的にAGENTS.mdに記載して他の開発者やエージェントと共有すること。
