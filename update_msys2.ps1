$pacmanPath = "C:\msys64\usr\bin\pacman.exe"

if (-not (Test-Path $pacmanPath)) {
    Write-Error "pacman.exe found at $pacmanPath"
    exit 1
}

Write-Host "Updating MSYS2 packages..."
& $pacmanPath -Syu --noconfirm

if ($LASTEXITCODE -ne 0) {
    Write-Error "Update failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}

Write-Host "Update completed successfully."
