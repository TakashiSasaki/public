# Githooks プロジェクトノート (開発エージェント・開発者向け)

この `githooks` プロジェクトは、独立したサブモジュールとして様々なリポジトリで再利用されることを前提に設計されています。
特に Windows、macOS、Linux といったクロスプラットフォームで安定して稼働させるため、各種スクリプトへの変更・追加を行う際は以下の制約と知見（ハマりどころ）を厳守してください。

## 1. PowerShell スクリプトの制約と機能制限 (.ps1)

Windows環境向けのセットアップスクリプト等では、利用者の PowerShell のバージョン（多くは Windows 10/11 に標準搭載されている古い Windows PowerShell 5.1）に依存します。
- `[System.IO.Path]::GetRelativePath` のような **.NET Core (PowerShell 6.0+) 以降で追加された便利なAPIは絶対に使用しないでください**。PowerShell 5.1 では `MethodInvocationException` が発生します。
- パスの相対解決やディレクトリ操作は、`StartsWith`増や `Substring` などのクラシックな文字列操作、あるいは `$PSScriptRoot` (もしくは `$MyInvocation.MyCommand.Path` と `Split-Path`) の基本的なコマンドレットのみを使って実装してください。
- エラーハンドリングは `$ErrorActionPreference = "Stop"` を宣言し、異常系の際（リポジトリのルートが見つからない等）はただちに `throw` で停止させてください。

## 2. Shell スクリプトと Python の探索順位 (.sh / pre-commit)

`pre-commit` などのフックシェルスクリプトから Python 実行環境を起動する際、コマンドの優先順位には重大な罠があります。

- **Windows + Git Bash の最大の罠**: Git for Windows などの環境で、`command -v python` や `which python` が **Microsoft Storeのダミー実行ファイル（`python.exe`）** を見つけてしまうことがあります。このダミーが実行されると、コマンドラインが対話モードストールするか、Microsoft Store がポップアップしてしまい、コミット処理がハングアップします。
- **対処法**: もしリポジトリでパッケージマネージャー `uv` などが利用可能である（または利用できる可能性が高い）場合は、**`uv`（または `py -3` のランチャー）を必ず `python` 単体よりも優先してチェックするロジックを組んでください**。
  - 推奨する優先順位例: `uv` -> `python3` -> `python` -> `py`

## 3. ファイル操作時の 改行コード 問題 (Python)

`bump-version.py` などのように、ファイル (例: `pyproject.toml`, `package.json`) の内容を読み込んで正規表現で置換し上書き保存するスクリプトではエンコーディングと改行コードの保持に注意が必要です。
- **読み書きは `open(..., newline="")` を必須とする**: Windows環境とLinux環境で Git リポジトリの改行コード（CRLF / LF）が混在していると、`read_text()` や単純な `open()` で書き直した際に全ての改行コードが環境依存（WindowsならCRLF）に統一されてしまい、意図しない巨大な Git の差分（ノイズ）を生み出します。
- 文字コードも常に `encoding="utf-8"` を明示し、CP932などによる文字化けを防ぐようにしてください。

## 4. 全般的な設計方針
- 各リポジトリで一元管理できるようにするため、プロジェクト固有の設定（どのファイルをバンプするか等）は極力環境変数（`BUMP_TYPES` など）や引数として外部から注入・上書きできる設計を維持してください。
- 可能な限り、開発者のローカル環境を汚さない（依存ライブラリを追加インストールさせない）ように、`uv run` や標準モジュール（`re`, `subprocess`, `argparse`）のみで完結するツールチェインを構成してください。

## このリポジトリのコードの使い方
- このリポジトリは https://github.com/TakashiSasaki/public リポジトリの githooks ブランチとして公開されている。
- このリポジトリは他のリポジトリのルート直下に githooks という名前のディレクトリでサブモジュールとして設置されることを想定している。
- githooks ディレクトリそのものを core.hooksPath として設定されることを想定している。
- サブモジュールとして設置された場合、親リポジトリにはバージョン情報を持つファイルが存在し、pre-commit ではbump-versions.py を使用してコミット直前にバージョンのパッチレベルをバンプアップしリポジトリに追加する動作を行う。