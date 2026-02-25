# Project Notes

- Git hook and version bump scripts are centralized in the `githooks` submodule so they can be reused across repositories.
- Use `githooks/setup-hooks.ps1` on Windows or `githooks/setup-hooks.sh` on Linux/macOS to set `core.hooksPath`.
- `githooks/pre-commit` supports `pyproject.toml`, `package.json`, and `manifest.webmanifest` with auto discovery.
- Repository-local `scripts/` hook helpers were removed to avoid duplication with the shared submodule.
- Keep core application logic under `src/my_mdns/core/` as reusable modules, and keep GUI code in `src/my_mdns/gui/`.
- mDNS受信実装では `0.0.0.0` / ifindex `0` の単発JOINに依存せず、IPv4/IPv6ともインターフェイスごとに multicast group join する方針を優先する（LAN内ホストの取りこぼし防止）。

# その他（このセクションは削除せず、このセクションの内容は他の適切なセクションに構造化することを強く推奨する）
- AGENTS.md は他のコーディングエージェントや開発者も参照する指示なので、プロジェクト全体の方針にかかわることは積極的にAGENTS.mdに追記する
- 特にWindows環境でうまくいかなかった作業を試行錯誤で成功させたときにはそのベストプラクティスをAGENTS.mdに記録する。
- バージョンのパッチレベルはコミットの際に必ずバンプアップする。これはgitのフックによって実現することが好ましい。そのためのフック関係のスクリプトやそれを補助するスクリプトは githooks サブモジュールに格納している。 githooks サブモジュールは他のプロジェクトとも共有している。
- このリポジトリにおける開発作業は Linux 環境と Windows 環境のどちらでも行う可能性がある。
- Pythonの環境は uv で管理している。
- コミットメッセージは常に詳細なコミットメッセージを書くこと。
- README.md はユーザーが参照するドキュメントである。AGENTS.mdは他の開発者やコーディングエージェントが参照するドキュメントである。
