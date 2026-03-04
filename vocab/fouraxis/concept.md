# 四軸文書分類モデル（Provenance / Activity / Genre / Subject）

## 1. 概要

本モデルは、個人研究アーカイブ、研究室文書管理、大学事務文書整理など、多様な文書集合を体系的に整理することを想定している。

本ドキュメントは、研究・教育・事務・財務など多様な文書を統一的に整理・検索・分析するための **四軸文書分類モデル**を定義する。

本モデルは次の4つの直交的な観点から文書を記述する。

| 軸  | カラム名       | 意味           |
| -- | ---------- | ------------ |
| 来歴 | provenance | 文書の作成主体または出所 |
| 活動 | activity   | 文書が関係する人間活動  |
| 形式 | genre      | 文書の慣習的形式     |
| 主題 | subject    | 文書の内容領域      |

この4軸は次の4つの独立した問いに対応する。

* **provenance** : 誰が作った文書か
* **activity** : どの活動に関係する文書か
* **genre** : どのような形式の文書か
* **subject** : 何について書かれている文書か

---

## 2. モデルの基本構造

ここでいう「直交」とは、各軸が異なる観点を表し、互いに独立して組み合わせ可能であることを意味する。

四軸は概念的には次のような関係で理解できる。

文書は次のメタデータ構造で表現される。

```
provenance
activity
genre
subject
```

概念的には次の分類空間を形成する。

```
                subject
                   ↑
                   │
provenance ─ activity ─ genre
```

各軸は異なる観点を表すため、実務上は直交する分類ファセットとして扱うことができる。

---

## 3. provenance（来歴）

### 定義

```
provenance = 文書を作成または提供した主体
```

アーカイブ学では **provenance（来歴の原則）** が基本原則とされる。

以下は代表的な genre の例であり、実際の語彙は組織の文書集合に応じて調整される。

### 典型値

| 値                     | 意味      |
| --------------------- | ------- |
| self                  | 本人が作成   |
| student               | 学生が作成   |
| lab_member            | 研究室メンバー |
| university_admin      | 大学事務    |
| vendor                | 業者      |
| publisher             | 出版社     |
| external_collaborator | 外部共同研究者 |

### 特徴

* 通常は単一値
* 文書の文脈理解に重要

---

## 4. activity（活動）

### 定義

```
activity = 文書が関係する人間活動
```

これは records management の **function / activity** 概念に対応する。

### 典型値

| 値              | 意味     |
| -------------- | ------ |
| research       | 研究活動   |
| teaching       | 教育活動   |
| administration | 組織運営   |
| finance        | 財務活動   |
| event          | イベント運営 |
| communication  | 連絡・広報  |

### 例

| 文書        | activity       |
| --------- | -------------- |
| 論文        | research       |
| 講義スライド    | teaching       |
| 議事録       | administration |
| 領収書       | finance        |
| ワークショップ案内 | event          |

---

## 5. genre（文書形式）

### 定義

※ `genre` は文書の社会的・慣習的な形式（例: journal_article, report, receipt など）を指す。一方 `file format`（PDF, DOCX, CSV など）はファイルの技術的保存形式を指すため、両者は別の概念である。

```
genre = 社会的に確立した文書形式
```

この概念は図書館メタデータの **MODS <genre>** に近い。

### 典型値

| 値                  |
| ------------------ |
| journal_article    |
| conference_paper   |
| technical_report   |
| presentation_slide |
| poster             |
| meeting_minutes    |
| report             |
| dataset            |
| software           |
| receipt            |
| invoice            |
| quotation          |
| budget_sheet       |

### 特徴

* 文書構造
* 文書フォーマット
* 社会的慣習

によって識別される。

---

## 6. subject（主題）

### 定義

```
subject = 文書の内容分野
```

図書館メタデータでは **MODS subject / Dublin Core subject** に対応する。

### 例

| subject            |
| ------------------ |
| machine_learning   |
| computer_science   |
| biology            |
| education          |
| workshop           |
| project_management |

### 特徴

* 複数値を許容
* 階層構造を持つことが多い

例

```
computer_science
  └ machine_learning
      └ transformer_models
```

---

## 7. メタデータ例

### 研究論文

```
provenance = self
activity = research
genre = journal_article
subject = machine_learning
```

### 学生レポート

```
provenance = student
activity = teaching
genre = report
subject = machine_learning
```

### 見積書

```
provenance = vendor
activity = finance
genre = quotation
subject = microscope
```

---

## 8. LLM分類

LLMは文書内のさまざまなシグナルを利用して分類を行う。典型的には次のような情報が判断材料となる。

典型的には次の軸が自動推定可能である。

* 文書構造（例: abstract, introduction, references などのセクション）
* キーワードや専門用語
* レイアウトや表形式・スライド形式などの構造
* タイトルや見出し
* ファイル名やディレクトリ構造
* 埋め込まれたメタデータ（作成者、日時など）

文書から以下をLLMで抽出できる。

```
activity
genre
subject
```

またメタデータやファイル位置から

```
provenance
```

を推定できる。

LLM出力例

```
{
  "provenance": "vendor",
  "activity": "finance",
  "genre": "quotation",
  "subject": ["microscope"]
}
```

---

## 9. スプレッドシート実装

Google Sheets でのカラム例

| file | provenance | activity | genre | subject | keywords |
| ---- | ---------- | -------- | ----- | ------- | -------- |

例

| file         | provenance | activity | genre              | subject          | keywords    |
| ------------ | ---------- | -------- | ------------------ | ---------------- | ----------- |
| paper1.pdf   | self       | research | journal_article    | machine_learning | transformer |
| slides1.pdf  | self       | teaching | presentation_slide | machine_learning | attention   |
| receipt1.pdf | vendor     | finance  | receipt            | equipment        | microscope  |

---

## 10. 利点

この四軸モデルは次の利点を持つ。

* 分類観点が明確
* LLMによる分類が容易
* フォルダ構造に変換可能
* メタデータ検索に強い

分類観点

```
provenance  = 出所
activity    = 活動
genre       = 文書形式
subject     = 内容
```

---

## 11. フォルダ構造への応用

すべての軸をディレクトリ構造にする必要はなく、subject のような多値属性はタグとして管理する方が適切な場合が多い。

例

```
research/
    journal_article/
    conference_paper/

finance/
    receipt/
    invoice/
    quotation/
```

subject は通常タグとして扱う。

---

## 12. 今後の設計課題

四軸モデルを安定させるためには次が重要。

1. activity 語彙の定義
2. genre 語彙の管理
3. subject 階層設計
4. provenance の分類粒度

特に **genre の語彙爆発**を防ぐ設計が重要である。

---

## 13. まとめ

このモデルは次のような問題を解決する。

* 文書集合の検索性を向上させる
* 分類の一貫性を確保する
* LLMによる文書整理・分類を容易にする

本モデルは次の四軸で文書を記述する。

```
provenance
activity
genre
subject
```

それぞれ

```
出所
活動
形式
内容
```

を表し、多様な文書コレクションを整理するための基盤となる。
