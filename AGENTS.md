# AGENTS

## リポジトリ概要
- このリポジトリは、GitHub Pages で `public.moukaeritai.work` を公開するためのものです。
- GitHub リポジトリ URL は `https://github.com/TakashiSasaki/public` です。

## 公開ブランチ
- 公開対象は、ドメイン名と同じブランチ `public.moukaeritai.work` です。

## サブモジュール構成
- `public.moukaeritai.work` ブランチには、このブランチ以外の各ブランチをサブモジュールとして配置します。
- サブモジュールの配置先は、対象ブランチ名と同名のサブディレクトリです。
- 例: `pictogram` ブランチは `./pictogram` サブモジュールとして配置します。
- サブモジュール URL は同一リポジトリ `git@github.com:TakashiSasaki/public` を使用し、`.gitmodules` の `branch` に対象ブランチ名を設定します。

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
- pre-commit フック（`githooks/pre-commit`）で `manifest.webmanifest` の `version` を自動バンプし、同ファイルを自動 `git add` します。
- フックは `git config core.hooksPath githooks` で有効化します。
- 別のチェックアウト先でも同じ挙動にするため、チェックアウト後に `githooks/setup-hooks.ps1` または `githooks/setup-hooks.sh` を実行してください。

## 新規クローン時の必須手順
- このブランチを新しくクローンまたはチェックアウトした直後は、必ずフック設定を行ってください。
- Windows (PowerShell): `./githooks/setup-hooks.ps1`
- sh 環境: `./githooks/setup-hooks.sh`
- この設定をしないと、コミット時の `manifest.webmanifest` バージョン自動バンプが動作しません。

## 運用ルール
- 今後もプロジェクト運用に有効な知見は、継続的に `AGENTS.md` へ反映してください。
- コミットメッセージは常に詳細な内容（変更目的・主な変更点が分かる内容）を優先してください。
