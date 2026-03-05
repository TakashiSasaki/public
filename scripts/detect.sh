#!/bin/bash
# 現在のブランチ名を取得
CURRENT_BRANCH=$(git branch --show-current)

if [ -z "$CURRENT_BRANCH" ]; then
    echo "Error: Not on any branch or not in a git repository."
    exit 1
fi

echo "Branches sharing history with '$CURRENT_BRANCH':"

# ローカルおよびリモートの全てのブランチをループ
# --format='%(refname:short)' でブランチ名のみ取得
git for-each-ref --format='%(refname:short)' refs/heads refs/remotes | while read branch; do
    # 自分自身との比較をスキップしたい場合はコメントアウトを外す
    # [ "$branch" == "$CURRENT_BRANCH" ] && continue

    # merge-base が正常終了すれば履歴を共有している
    if git merge-base "$CURRENT_BRANCH" "$branch" >/dev/null 2>&1; then
        echo "  $branch"
    fi
done
