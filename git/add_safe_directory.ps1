param (
    [string]$Path = "."
)

$targetPath = Convert-Path $Path
if (-not $targetPath) {
    Write-Host "Error: Path not found."
    exit 1
}

# Get-Item to handle simple paths
$item = Get-Item $targetPath

# Check if it's a mapped drive and resolve UNC if possible
# Git for Windows often sees the UNC path for network drives
$driveLetter = $item.PSDrive.Name
if ($driveLetter -and ($item.PSDrive.Provider.Name -eq 'FileSystem')) {
    $mapping = Get-SmbMapping | Where-Object { $_.LocalPath -eq "$($driveLetter):" }
    if ($mapping) {
        # Construct UNC path
        $relativePath = $targetPath.Substring(3) # Remove 'H:\'
        $uncStart = $mapping.RemotePath
        if ($relativePath) {
            $fullUnc = "$uncStart\$relativePath"
        } else {
            $fullUnc = $uncStart
        }
        
        # Format for git config: %(prefix)///server/share/path
        # Note: git safe.directory checks are case sensitive and path format sensitive.
        # The observed error suggested: %(prefix)///133.71.3.4/home/server-certification
        
        # Convert backslashes to forward slashes
        $uncGitPath = "%(prefix)/" + $fullUnc.Replace("\", "/")
        
        Write-Host "Detected network drive. Adding UNC path to safe.directory:"
        Write-Host "  $uncGitPath"
        git config --global --add safe.directory "$uncGitPath"
        
        # ALSO add the drive letter path, just in case git sees it that way in some shells (like cmd)
        $driveGitPath = $targetPath.Replace("\", "/")
        Write-Host "Adding drive path to safe.directory (for robustness):"
        Write-Host "  $driveGitPath"
        git config --global --add safe.directory "$driveGitPath"
        
        Write-Host "Done."
        exit 0
    }
}

# Fallback for local paths
$gitPath = $targetPath.Replace("\", "/")
Write-Host "Adding local path to safe.directory:"
Write-Host "  $gitPath"
git config --global --add safe.directory "$gitPath"
Write-Host "Done."
