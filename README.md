# githooks

複数プロジェクトで再利用する Git hooks とバージョンバンプ用スクリプトです。

## 対応対象
- `pyproject.toml`
- `package.json`
- `manifest.webmanifest`

`pre-commit` は上記ファイルを自動検出して `version` をバンプします。

## セットアップ
Linux/macOS:
```sh
sh githooks/setup-hooks.sh
```

Windows (PowerShell):
```powershell
pwsh -File githooks/setup-hooks.ps1
```

どちらも `core.hooksPath` をこのサブモジュールに設定します。

## デフォルト動作
- `BUMP_PART=patch`
- `BUMP_TYPES=pyproject,packagejson,manifest`
- 自動検出有効 (`BUMP_DISCOVER=1`)
- 変更対象は自動で `git add` されます

## 環境変数での制御
- `BUMP_PART`
  - `patch` / `minor` / `major`
- `BUMP_TYPES`
  - 例: `pyproject,packagejson`
- `BUMP_DISCOVER`
  - `1`: 自動検出
  - `0`: 自動検出しない
- `BUMP_PYPROJECT_PATHS`
  - カンマ/セミコロン区切りで `pyproject.toml` パス指定
- `BUMP_PACKAGE_JSON_PATHS`
  - カンマ/セミコロン区切りで `package.json` パス指定
- `BUMP_MANIFEST_PATHS`
  - カンマ/セミコロン区切りで `manifest.webmanifest` パス指定

## 互換ラッパー
- `pre-commit-pyproject.sh`
- `pre-commit-packagejson.sh`
- `pre-commit-manifest-version.ps1`

上記は既存運用向けの互換ラッパーで、内部的には統合 `pre-commit` / `bump-version.py` を利用します。
