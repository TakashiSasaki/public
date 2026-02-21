# Mouse Pointer Generator

Windows用のマウスポインタ（.curファイル）をカスタマイズして生成できるツールです。

## 特徴

- **GUIモード**: Tkinterを使用した視覚的なインターフェースで、形状、色、枠線、文字などをリアルタイムに調整できます。
- **カスタマイズ要素**:
  - 形状（矢印、三角形、十字）
  - 塗りつぶしの色と枠線の色
  - 枠線の太さ
  - 内部への1文字描画（モードの識別などに便利）
  - ホットスポットの自動計算と手動保存
- **CLIモード**: コマンドラインから素早くカーソルを生成できます。

## セットアップ

このプロジェクトは `uv` を使用して管理されています。

```bash
# 依存関係のインストール
uv sync
```

## 使い方

### GUIを起動する（推奨）

```bash
uv run mouse-pointer gui
# または単に
uv run mouse-pointer
```

### コマンドラインから生成する

```bash
uv run mouse-pointer generate --color red --size 48 --shape triangle --output my_cursor.cur
```

## 開発

- `src/mouse_pointer/gui.py`: GUIの実装
- `src/mouse_pointer/generators/basic.py`: 画像生成ロジック
- `src/mouse_pointer/core/cursor.py`: `.cur` 形式のバイナリ構築
- `src/mouse_pointer/cli.py`: エントリポイント
