# JSON Schema と JSON-LD の役割分担ガイド

このドキュメントは、get-a-grip プロジェクトで使用しているデータ形式（JSON, JSON Schema, JSON-LD）の関係性と、それぞれの役割について解説します。

## 概要

| 技術 | 役割 | 答える問い |
|------|------|-----------|
| **JSON** | データの形式 | 「データをどう書くか？」 |
| **JSON Schema** | 構造の検証 | 「データの形は正しいか？」 |
| **JSON-LD** | 意味の定義 | 「このデータは何を意味するか？」 |

これら3つは**補完関係**にあり、すべてを組み合わせることで「構造的に正しく、意味的にも明確なデータ」を実現できます。

## JSON Schema でできること・できないこと

### できること（構造的制約）

```json
{
  "patternProperties": {
    "^[^/\\\\:*?\"<>|]+$": { "$ref": "#/definitions/treeNode" }
  }
}
```

- キーが特定のパターン（正規表現）に一致するか検証
- 値が特定の型（string, number, object等）であるか検証
- 必須項目の存在確認
- 配列の長さや数値の範囲の制限

### できないこと（意味的制約）

- 「このキーは**パスセグメント**である」という**概念**の定義
- 「このオブジェクトは**ファイルシステムの構造**を表す」という**意図**の表現
- 「キーを連結すると**フルパス**になる」という**解釈ルール**の記述

## JSON-LD でできること・できないこと

### できること（意味の定義）

```json
{
  "@context": {
    "gag": "https://purl.org/gag/schema/vocab#",
    "pathSegment": "gag:pathSegment"
  }
}
```

- プロパティ名が何を意味するかの定義
- 標準語彙（schema.org等）との紐付け
- RDFグラフとしての解釈・変換

### できないこと

- データの構造検証
- 型チェックや必須項目の確認
- 正規表現によるパターンマッチング

## よくある誤解

### 誤解1: JSON-LDドキュメントは自分のスキーマを指し示せる

**事実**: JSON-LD の標準機能には、「このデータはこの JSON Schema で検証できる」と記述する仕組みはありません。

`@context` は意味の定義のためのもので、構造検証のためのものではありません。

### 誤解2: `$schema` をデータに書けばスキーマが適用される

**事実**: JSON Schema 仕様において `$schema` は**スキーマ文書自身**に書くもので、「このスキーマはどのバージョンの JSON Schema 仕様に従うか」を示すためのものです。

```json
// これは「スキーマ文書」に書く
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object"
}
```

データ（インスタンス）に `$schema` を書くのは：

- ❌ JSON Schema 仕様で定義された動作ではない
- ⚠️ 一部のツール（VS Code, JetBrains IDE等）が独自に認識する
- ⚠️ 相互運用性は保証されない

これは**事実上の慣習（de facto convention）**であり、標準ではありません。

### 誤解3: XMLのようにデータがスキーマを自己記述できる

**事実**: XML には `DOCTYPE` や `xsi:schemaLocation` のような標準的な仕組みがありますが、JSON にはありません。

```xml
<!-- XMLでは標準的 -->
<root xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://example.com/ns http://example.com/schema.xsd">
```

これは設計思想の違いによるものです：

| 形式 | 設計思想 |
|------|---------|
| XML | 重厚で自己完結 |
| JSON | 軽量で外部依存 |

## このプロジェクトでの対応方法

get-a-grip では、以下の方法でスキーマとデータの関連付けを行っています：

### 1. ファイル命名規則

```
schema/
├── filelist.json      # JSON Schema
├── filelist.jsonld    # JSON-LD Context
├── dirtree.json       # JSON Schema
├── dirtree.jsonld     # JSON-LD Context
└── vocab.jsonld       # 語彙定義
```

同じベース名で `.json`（スキーマ）と `.jsonld`（コンテキスト）を並べることで、対応関係を明示しています。

### 2. 語彙の統一

すべてのプロパティ定義は `vocab.jsonld` に集約し、各コンテキストから参照しています。

### 3. ドキュメントによる明示

このドキュメントや `AGENTS.md` で、どのスキーマがどのデータ形式に対応するかを記載しています。

## まとめ

| やりたいこと | 使う技術 |
|------------|---------|
| データの構造を検証したい | JSON Schema |
| データに意味を持たせたい | JSON-LD |
| スキーマとデータを関連付けたい | 命名規則 + ドキュメント |
| 両方を兼ね備えたデータを作りたい | JSON Schema + JSON-LD を併用 |

**重要**: JSON Schema と JSON-LD は「別々の世界」に住んでおり、標準的な橋渡しの仕組みは存在しません。プロジェクトごとに慣習を決め、ドキュメント化することが重要です。

## 参考リンク

- [JSON Schema 仕様](https://json-schema.org/)
- [JSON-LD 仕様](https://www.w3.org/TR/json-ld11/)
- [Schema.org](https://schema.org/)
