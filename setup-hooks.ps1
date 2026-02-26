$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (& git -C $scriptDir rev-parse --show-toplevel).Trim()
if ([string]::IsNullOrWhiteSpace($repoRoot)) {
  throw "setup-hooks: failed to resolve repository root"
}

if ($scriptDir.StartsWith($repoRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    $hooksPath = $scriptDir.Substring($repoRoot.Length).TrimStart("\", "/").Replace("\", "/")
} else {
    throw "setup-hooks: script is not inside the repo root"
}

if ([string]::IsNullOrWhiteSpace($hooksPath) -or $hooksPath -eq ".") {
  throw "setup-hooks: hooks path resolution failed"
}

& git -C $repoRoot config core.hooksPath $hooksPath
Write-Host "Configured core.hooksPath=$hooksPath (repo: $repoRoot)"
