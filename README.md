# githooks

このディレクトリは、複数プロジェクトで再利用する Git hook と補助スクリプトを置く場所です。

## 現在このブランチで有効なフック
- `pre-commit`
- `pre-commit.ps1`
  
`manifest.webmanifest` の `version` をコミット時に自動バンプします。

## Python プロジェクト向けテンプレート（このブランチでは未使用）
- `pre-commit-pyproject.sh`
- `bump-pyproject-version.py`

これらは `pyproject.toml` の `version` をバンプするための再利用テンプレートです。
このブランチには `pyproject.toml` がないため、デフォルトでは実行されません。

## 使い方（Python プロジェクトで利用する場合）
1. `githooks/pre-commit-pyproject.sh` を `pre-commit` として使用する。
2. 必要に応じて環境変数を設定する。
   - `PYPROJECT_PATH`（既定: `pyproject.toml`）
   - `BUMP_PART`（既定: `patch`）
   - `BUMP_SCRIPT`（既定: `githooks/bump-pyproject-version.py`）
