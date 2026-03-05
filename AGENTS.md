# AGENTS

## リポジトリ概要
- このリポジトリは、GitHub Pages で `public.moukaeritai.work` を公開するためのものです。
- GitHub リポジトリ URL は `https://github.com/TakashiSasaki/public` です。

## 公開ブランチ
- 公開対象は、ドメイン名と同じブランチ `public.moukaeritai.work` です。

## サブモジュール構成
- `public.moukaeritai.work` ブランチには、このブランチ以外の各ブランチ（`master` 等の一部例外を除く）をサブモジュールとして配置します。
- サブモジュールの配置先は、対象ブランチ名と同名のディレクトリ（リポジトリのルート直下）です。
- 例: `pictogram` ブランチは `./pictogram` サブモジュールとして配置します。
- サブモジュール URL は同一リポジトリ `git@github.com:TakashiSasaki/public` を使用し、`.gitmodules` の `branch` に対象ブランチ名を設定します。
- 新しく追加されたリモートブランチを自動でサブモジュールとして取り込むため、`.agent/skills/remaining_branches_submodule_adder/scripts/add_remaining_branches_as_submodules.ps1` スクリプトを用意しています。必要に応じてこのスクリプトを実行し、サブモジュール構成を同期してください。

## 別リモートブランチの取り込み手順
- `windows-moukaeritai-work` リモートの全ブランチを、このリポジトリのローカルブランチとして履歴ごと取り込む場合は追跡ブランチを作成します。
- まず最新を取得します: `git fetch windows-moukaeritai-work --prune`
- 1ブランチずつ作る場合: `git branch --track <branch-name> windows-moukaeritai-work/<branch-name>`
- 例: `git branch --track mcp windows-moukaeritai-work/mcp`
- 既存ブランチがある場合は作成をスキップしてください（重複作成は失敗します）。
- 取り込み後は `git branch -vv` で upstream が `windows-moukaeritai-work/<branch-name>` になっていることを確認してください。

## AGENTS.md の目的
- `AGENTS.md` は、他の開発者やコーディングエージェントも参照する共通指示ファイルです。

## 記載方針
- 他の開発者やコーディングエージェントが参照すべき情報は、積極的に `AGENTS.md` に追記してください。

## 開発環境メモ（Windows）
- 現在の作業環境は Windows（PowerShell）です。
- Windows 環境特有の実行エラー（例: `CreateProcessWithLogonW failed: 1056`）により、通常実行のコマンドが失敗する場合があります。
- コマンドが失敗した場合は、実行権限やサンドボックス制約を確認し、必要に応じて昇格実行で再試行してください。
- Git 操作時に改行コード関連の警告（`LF will be replaced by CRLF`）が表示されることがあります。必要ならリポジトリで改行コード方針を明示してください。

## バージョン運用（Manifest）
- `manifest.webmanifest` の `version` はセマンティックバージョン（`major.minor.patch`）を使用します。
- コミット時は少なくともパッチ番号を `+1` します。
- pre-commit フック（`githooks/pre-commit`）は `githooks/pre-commit-manifest-version.ps1` を呼び出し、`manifest.webmanifest` の `version` を自動バンプして同ファイルを自動 `git add` します。
- フックは `git config core.hooksPath githooks` で有効化します。
- 別のチェックアウト先でも同じ挙動にするため、チェックアウト後に `githooks/setup-hooks.ps1` または `githooks/setup-hooks.sh` を実行してください。
- `githooks` には Python プロジェクト再利用用のテンプレート（`githooks/pre-commit-pyproject.sh`, `githooks/bump-pyproject-version.py`）と JavaScript/TypeScript プロジェクト再利用用のテンプレート（`githooks/pre-commit-packagejson.sh`, `githooks/bump-packagejson-version.py`）も保管します。
- このブランチでは `pyproject.toml` を対象とするテンプレートは実行しません。
- このブランチでは `package.json` を対象とするテンプレートも実行しません。
- プロジェクトごとにバージョンを管理するファイルは1つだけにし、同一コミットで複数ファイルを同時バンプしません。複数バージョン管理が必要な場合は別プロジェクトとして扱います。

## 新規クローン時の必須手順
- このブランチを新しくクローンまたはチェックアウトした直後は、必ずフック設定を行ってください。
- Windows (PowerShell): `./.agent/skills/remaining_branches_submodule_adder/scripts/add_remaining_branches_as_submodules.ps1`
- sh 環境: (必要に応じて sh 用スクリプトを作成してください)
- この設定をしないと、コミット時の `manifest.webmanifest` バージョン自動バンプが動作しません。

## 運用ルール
- 今後もプロジェクト運用に有効な知見は、継続的に `AGENTS.md` へ反映してください。
- コミットメッセージは常に詳細な内容（変更目的・主な変更点が分かる内容）を優先してください。

## 知見: ローカル作業とプッシュの管理
- **事例 (2026-03-05)**: 以前作成したエージェント用スキル（Submodule Adder 等）が、新しくクローンした環境で消失していることが判明。
- **原因**: 3月3日の作業時、コミットは作成されたがリモート（GitHub）に `git push` されていなかった。その後、デスクトップ上の古いクローンが完全に削除（または消失）され、3月4日にドキュメントフォルダへ新しくクローンしたため、未プッシュの履歴が失われた。
- **対策**:
  - 作業完了時、特にマニフェストのバージョンをバンプした後は、必ず `git push` を行いリモートと同期させること。
  - 環境を移行（再クローン）する際は、古い環境に未プッシュのコミットや stash が残っていないか必ず確認すること。
