# Mouse Pointer Generator

Windows用のマウスポインタ（.cur / .aniファイル）をカスタマイズして生成できるツールです。

## 特徴

- **GUIモード**: Tkinterを使用した視覚的なインターフェースで、形状、色、枠線、文字などをリアルタイムに調整できます。
- **カスタマイズ要素**:
  - 形状（矢印、三角形、十字、リンク選択用の手、テキスト選択用のIビーム、砂時計）
  - 塗りつぶしの色と枠線の色
  - 枠線の太さ
  - 内部への1文字描画やSVGバッジの合成
  - アニメーション効果（強度調整可能なグラデーションウェーブ、キャプションのスクロール等）
  - ホットスポットの自動計算と手動保存
  - Export Set タブからの標準カーソルセット一括生成
- **CLIモード**: コマンドラインから素早くカーソルを自動生成できます。
- **アプリケーションアイコン**: Tk 実行時のウィンドウ/タスクバーと、PyInstaller でビルドした `.exe` に専用アイコンを適用します。

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

```bash
uv run mouse-pointer generate --color "#800080" --shape arrow --anim-gradient --anim-gradient-intensity 128 --output demo.ani
```

```bash
uv run mouse-pointer generate --color "#cc00ff" --shape hand --output link_select.cur
```

### サンプルファイルの生成

機能を確認するための様々な静的・動的カーソル（.cur / .ani）を `examples/` フォルダ配下に一括生成できます。

```bash
uv run generate-examples
```

### 実行ファイル（.exe）の作成

PythonがインストールされていないWidnows環境でも動作する、単一の実行ファイル（.exe）をビルドできます。

```bash
uv run build-exe
```

ビルドが完了すると、`dist/MousePointerGenerator_vX.Y.Z.exe` （例: `MousePointerGenerator_v0.3.1.exe`）が生成されます。このファイル単体で配布・実行が可能です。

アプリケーションアイコン素材は `assets/app_icon.png` と `assets/app_icon.ico` に配置しています。アイコンを差し替える場合は、この 2 ファイルを揃えて更新してください。

## 開発

- `src/mouse_pointer/gui.py`: GUIの実装
- `src/mouse_pointer/generators/basic.py`: 画像生成ロジック
- `src/mouse_pointer/core/cursor.py`: `.cur` 形式のバイナリ構築
- `src/mouse_pointer/cli.py`: エントリポイント
