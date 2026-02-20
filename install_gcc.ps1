$pacmanPath = "C:\msys64\usr\bin\pacman.exe"

if (-not (Test-Path $pacmanPath)) {
    Write-Error "pacman.exe found at $pacmanPath"
    exit 1
}

Write-Host "Syncing database and installing mingw-w64-x86_64-gcc..."
& $pacmanPath -Sy --noconfirm mingw-w64-x86_64-gcc

if ($LASTEXITCODE -ne 0) {
    Write-Error "Installation failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}

Write-Host "Installation completed successfully."
