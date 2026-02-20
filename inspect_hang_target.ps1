$targetPath = "H:\server-certification"

Write-Host "=== Inspecting Target Directory: $targetPath ==="

# 1. Check Existence and Basic Attributes
if (!(Test-Path $targetPath)) {
    Write-Host "Error: Path does not exist or is inaccessible."
    exit
}

try {
    $item = Get-Item $targetPath -ErrorAction Stop
    Write-Host "Attributes: $($item.Attributes)"
    Write-Host "Is Reparse Point: $([bool]($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint))"
    
    if ($item.LinkType) {
        Write-Host "LinkType: $($item.LinkType)"
        Write-Host "Target: $($item.Target)"
    }
} catch {
    Write-Host "Failed to get item attributes: $_"
}

# 2. Check ACLs
Write-Host "`n=== ACL Check ==="
try {
    $acl = Get-Acl $targetPath
    Write-Host "Owner: $($acl.Owner)"
    foreach ($rule in $acl.Access) {
        Write-Host "  $($rule.IdentityReference) | Rights: $($rule.FileSystemRights) | Type: $($rule.AccessControlType)"
    }
} catch {
    Write-Host "Failed to read ACL: $_"
}

# 3. List Content Count (with timeout protection logic simulation)
Write-Host "`n=== Content Enumeration ==="
Write-Host "Counting items (first 100)..."

try {
    $measure = Measure-Command {
        $items = Get-ChildItem -Path $targetPath -Force -ErrorAction SilentlyContinue | Select-Object -First 100
        $count = $items.Count
        Write-Host "Found $count items (limit 100)."
        if ($count -eq 100) {
            Write-Host "WARNING: Directory has at least 100 items. It might have many more."
            # Attempt a full count only if user wants, but here we just try a slightly larger batch to see speed
            Write-Host "Attempting to count up to 5000..."
            $fullCount = (Get-ChildItem -Path $targetPath -Force -ErrorAction SilentlyContinue | Select-Object -First 5000).Count
            Write-Host "Count result: $fullCount"
            if ($fullCount -eq 5000) {
                 Write-Host "CRITICAL: Directory has over 5000 items. Git Bash status check might hang here."
            }
        }
    }
    Write-Host "Time taken to list: $($measure.TotalMilliseconds) ms"
} catch {
    Write-Host "Failed to enumerate items: $_"
}
