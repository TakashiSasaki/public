$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$bumpScript = Join-Path $scriptDir "bump-version.py"
$manifestPath = $env:MANIFEST_PATH
if ([string]::IsNullOrWhiteSpace($manifestPath)) {
  $manifestPath = "manifest.webmanifest"
}
$part = $env:BUMP_PART
if ([string]::IsNullOrWhiteSpace($part)) {
  $part = "patch"
}

if (-not (Test-Path $bumpScript)) {
  throw "pre-commit: bump script not found: $bumpScript"
}

if (Get-Command python -ErrorAction SilentlyContinue) {
  & python $bumpScript --part $part --type manifest --manifest-path $manifestPath --no-discover --stage
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
  & py -3 $bumpScript --part $part --type manifest --manifest-path $manifestPath --no-discover --stage
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
  & python3 $bumpScript --part $part --type manifest --manifest-path $manifestPath --no-discover --stage
} elseif (Get-Command uv -ErrorAction SilentlyContinue) {
  & uv run --no-sync python $bumpScript --part $part --type manifest --manifest-path $manifestPath --no-discover --stage
} else {
  throw "pre-commit: python runtime not found (python/py/python3/uv)."
}
