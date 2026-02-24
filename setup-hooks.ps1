$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (& git -C $scriptDir rev-parse --show-toplevel).Trim()
if ([string]::IsNullOrWhiteSpace($repoRoot)) {
  throw "setup-hooks: failed to resolve repository root"
}

$hooksPath = [System.IO.Path]::GetRelativePath($repoRoot, $scriptDir)
if ([string]::IsNullOrWhiteSpace($hooksPath) -or $hooksPath -eq ".") {
  throw "setup-hooks: hooks path resolution failed"
}

& git -C $repoRoot config core.hooksPath $hooksPath
Write-Host "Configured core.hooksPath=$hooksPath (repo: $repoRoot)"
