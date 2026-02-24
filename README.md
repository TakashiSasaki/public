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

## スクリプト呼び出し関係
コミット時の実行起点は `pre-commit` です。

```text
git commit
  -> githooks/pre-commit
     -> githooks/bump-version.py
        -> pyproject.toml / package.json / manifest.webmanifest を更新
        -> git add (変更ファイル)
```

互換ラッパー経由の呼び出しは次の通りです。

```text
githooks/pre-commit-pyproject.sh
  -> (環境変数を設定)
  -> githooks/pre-commit
     -> githooks/bump-version.py

githooks/pre-commit-packagejson.sh
  -> (環境変数を設定)
  -> githooks/pre-commit
     -> githooks/bump-version.py

githooks/pre-commit-manifest-version.ps1
  -> githooks/bump-version.py (--type manifest --no-discover --stage)
```

`setup-hooks.sh` / `setup-hooks.ps1` は `core.hooksPath` を `githooks` に設定するためのセットアップスクリプトであり、バンプ処理自体は実行しません。
