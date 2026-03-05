# 現在のブランチ名を取得
$currentBranch = git branch --show-current

if ([string]::IsNullOrWhiteSpace($currentBranch)) {
    Write-Error "Not on any branch or not in a git repository."
    exit 1
}

Write-Host "Branches sharing history with '$currentBranch':"

# ローカルおよびリモートの全ての参照を取得
$branches = git for-each-ref --format='%(refname:short)' refs/heads refs/remotes

foreach ($branch in $branches) {
    if ([string]::IsNullOrWhiteSpace($branch)) { continue }
    
    # merge-base を実行し、終了コードを確認
    $null = git merge-base $currentBranch $branch 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  $branch"
    }
}
