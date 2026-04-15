---
name: repository_landscape_analyzer
description: Analyze the overall landscape of repositories in a worktree, including nested repos, submodules, and their relationships.
---

# Repository Landscape Analyzer

このスキルは、ワークツリー内に散在するリポジトリ群（サブモジュール、リポジトリ内リポジトリ、ネストされた `.git` ディレクトリなど）を横断的に解析し、全体像と個々のリポジトリの位置づけをわかりやすく報告します。

## ユースケース

- 「このリポジトリはどんなものですかね？」という質問に答える
- ワークツリー内のリポジトリ構造を俯瞰して把握する
- サブモジュールと独立クローンが混在している状況を整理する
- 任意のパスのリポジトリが、上位のリポジトリとどういう関係にあるかを説明する

## Usage

```powershell
pwsh .agent/skills/repository_landscape_analyzer/scripts/analyze_repository_landscape.ps1 [-TargetPath <path>] [-RootPath <path>] [-OutputFormat <text|json|markdown>]
```

## Options

- `-TargetPath`: 詳細を調べたい特定のリポジトリパス（省略時はカレントディレクトリ）。
- `-RootPath`: スキャンを開始する起点ディレクトリ（省略時はカレントディレクトリ）。
- `-OutputFormat`: 出力フォーマット。`text`（デフォルト）、`json`、`markdown` から選択。
- `-MaxDepth`: ディレクトリ探索の最大深度（デフォルト: 5）。

## 実行手順（エージェント向け）

ユーザーから「このリポジトリはどんなものですか？」と問われた場合、以下のステップで回答を構築してください。

### Step 1: 全体スキャン

スクリプトを実行してワークツリー全体のリポジトリ一覧を取得します。

```powershell
pwsh .agent/skills/repository_landscape_analyzer/scripts/analyze_repository_landscape.ps1 -RootPath . -OutputFormat json
```

### Step 2: 対象リポジトリの特定

ユーザーが指定したパス（またはカレントディレクトリ）のリポジトリをスキャン結果から特定します。

### Step 3: 位置づけの説明

以下の観点から、ワークツリー全体における当該リポジトリの位置づけをまとめます。

1. **分類**: サブモジュール / 独立クローン（リポジトリ内リポジトリ）/ 親リポジトリ自体
2. **上位リポジトリ**: 当該リポジトリを参照・包含している上位リポジトリの有無
3. **下位リポジトリ**: 当該リポジトリ内にさらに含まれるサブモジュール・ネストリポジトリの有無
4. **リモートURL**: `origin` その他のリモート設定
5. **ブランチ**: 現在チェックアウトされているブランチ・コミット
6. **同一リモートを共有する兄弟リポジトリ**: 同じリモートURLを参照する他のサブモジュール

## Output

スクリプトは以下の情報を出力します。

- **ランドスケープマップ**: ワークツリー内のすべてのリポジトリをツリー形式で表示
- **対象リポジトリ詳細**: 分類・上位/下位リポジトリ・リモートURL・現在のブランチ
- **関係グラフ（Markdown）**: Mermaid 形式のリポジトリ関係図（`-OutputFormat markdown` 時）

## Output Example

```
[Repository Landscape]

Workspace Root: C:\Users\takashi\Documents\GitHub\public
│
├── [PARENT REPO] public (branch: public.moukaeritai.work)
│   ├── [SUBMODULE] pictogram  → origin/pictogram
│   ├── [SUBMODULE] mcp        → origin/mcp
│   └── [NESTED CLONE] some-other-repo  ← not registered as submodule
│
└── ...

[Target Repository: ./mcp]
  Classification : Submodule
  Registered in  : public (via .gitmodules)
  Remote (origin): https://github.com/TakashiSasaki/public
  Branch         : mcp
  HEAD commit    : abc1234
  Children       : (none)
```

## 注意事項

- `.git` ディレクトリが存在するディレクトリをリポジトリとして検出します。
- `git worktree` によるワークツリーも検出対象です。
- `.gitmodules` に登録されていない独立クローン（リポジトリ内リポジトリ）は `[NESTED CLONE]` として明示します。
- スキャン対象が広い場合は `-MaxDepth` で深度を制限してください。

## 実装ステータス

> **[TODO]** スクリプト本体 `scripts/analyze_repository_landscape.ps1` は未実装です。
> このスキルのひな型を作成した段階です。実装が必要な場合はユーザーに確認してから進めてください。
