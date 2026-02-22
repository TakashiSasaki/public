# Web Development Guide (for Python Developers)

このプロジェクトのフロントエンド（`pictogram`）は、**Bun**, **Vite**, **React**, **Tailwind CSS** という現代的なウェブ技術スタックを使用して構築されています。Python 開発者向けに、これらのツールの役割と開発フローを解説します。

---

## 1. ツール セットアップ (Python との比較)

Python エコシステムに慣れている方向けに、ウェブ開発ツールの役割をマッピングしました。

| ウェブ技術 | Python での相当ツール | 役割 |
| :--- | :--- | :--- |
| **Bun** | `python` + `pip` + `venv` | JavaScript 実行環境、パッケージ管理、最速のランタイム |
| **Vite** | (該当なし) | 開発サーバの提供、JSX のリアルタイムコンパイル |
| **React** | (UI フレームワーク) | コンポーネントベースの UI ライブラリ |
| **Tailwind CSS** | (スタイルシート) | クラス名だけでデザインを完結させる CSS フレームワーク |
| **package.json** | `pyproject.toml` | プロジェクト設定、依存ライブラリの定義 |
| **node_modules/** | `.venv/` | インストールされたパッケージの実体（`.gitignore` 推奨） |

---

## 2. 基本的な開発フロー

### 依存関係のインストール
新しい開発環境で作業を始める際は、まずライブラリをインストールします。
```bash
cd pictogram
bun install
```
*Python で言う `pip install .` や `uv sync` に相当します。*

### 開発サーバの起動
ウェブブラウザで動作を確認しながら開発するには、開発サーバを起動します。
```bash
bun run dev
```
起動すると `http://localhost:5173` などの URL が表示されます。ブラウザでこの URL を開いてください。

---

## 3. なぜ `index.html` を直接開いても動かないのか？

ウェブブラウザは、React 特有の構文（**JSX**）や、外部ファイルの `import` をそのまま実行することが苦手です。

- **JSX コンパイル**: `App.jsx` 内の HTML のようなコード（`<div className="...">`）は、Vite がリアルタイムで標準的な JavaScript 関数に変換しています。
- **モジュール解決**: `import { useState } from "react"` などの記述を、ブラウザが理解できるファイルパスに Vite が紐付けています。

このため、ブラウザで閲覧するには常に `bun run dev` で起動したサーバを経由する必要があります。

---

## 4. プロジェクト構成

`pictogram/` 以下の主要ファイル：

- **`src/App.jsx`**: アプリケーションのメインロジック。UI コンポーネントや状態（State）を記述します。
- **`src/main.jsx`**: React を起動し、`index.html` の `root` 要素に流し込むエントリーポイント。
- **`src/index.css`**: Tailwind CSS の基本設定。
- **`vite.config.js`**: Vite の設定ファイル（Tailwind プラグイン等の有効化）。

---

## 5. 本番用ビルド

開発が完了し、サーバなしで動作する静的なファイルを生成したい場合はビルドを行います。

```bash
bun run build
```
実行後、`dist/` フォルダが生成されます。この中のファイルは標準的な HTML/JS/CSS なので、一般的なウェブサーバ（Nginx, S3, GitHub Pages 等）に置くだけで全世界に公開できます。

---

## 6. ヒント

- **Hot Module Replacement (HMR)**: `App.jsx` を保存すると、ブラウザをリロードしなくても画面が即座に更新されます。
- **エディタ**: VS Code を使用している場合、`ESLint` や `Tailwind CSS IntelliSense` 拡張機能をインストールすると、入力補完が効いて開発が非常に楽になります。
