$path = "H:\_perm_test.txt"

Write-Host "=== Analysis of Effective Identity & Permissions ==="

Write-Host "`n1. Network Connection (net use)"
net use "H:"

Write-Host "`n2. SMB Mapping Info"
Get-SmbMapping | Where-Object { $_.LocalPath -eq 'H:' } | Select-Object *

Write-Host "`n3. Creating Test File on H: ($path)"
$ownerSid = $null
if (Test-Path $path) {
    Remove-Item $path -Force -ErrorAction SilentlyContinue
}

try {
    New-Item -Path $path -ItemType File -Value "Permission Test" -Force | Out-Null
    Write-Host "File created successfully."

    $acl = Get-Acl $path
    $ownerString = $acl.Owner
    if ($ownerString.StartsWith("O:")) {
        $ownerString = $ownerString.Substring(2)
    }
    
    try {
        $ownerSid = (New-Object System.Security.Principal.NTAccount($ownerString)).Translate([System.Security.Principal.SecurityIdentifier]).Value
        Write-Host "Effective SID (Resolved from Name): $ownerSid"
    } catch {
        # Maybe it's already a SID
        try {
            $sidObj = New-Object System.Security.Principal.SecurityIdentifier($ownerString)
            $ownerSid = $sidObj.Value
            Write-Host "Effective SID (Direct): $ownerSid"
        } catch {
            Write-Host "Could not resolve owner '$ownerString' to strict SID."
        }
    }
    
    Remove-Item $path -Force
    Write-Host "Test file removed."
} catch {
    Write-Host "FAILED to create test file. Error: $_"
    Write-Host "This confirms you do NOT have write permission at the root of H: with your current credentials."
}

Write-Host "`n4. Comparing with Local User"
$localUser = whoami /user /fo csv | ConvertFrom-Csv
$localUserSid = $localUser.SID
Write-Host "Local User: $($localUser.User_Name)"
Write-Host "Local SID:  $localUserSid"

Write-Host "`n=== Conclusion ==="
if ($ownerSid) {
    if ($ownerSid -eq $localUserSid) {
        Write-Host "Match: You are authenticated as your local Windows user."
    } else {
        Write-Host "MISMATCH: You are authenticated as a DIFFERENT user on the server."
        Write-Host "Server User SID: $ownerSid"
        Write-Host "Local User SID:  $localUserSid"
        Write-Host "This explains why permissions might seem different. You are accessing H: as the Server User."
    }
} else {
    Write-Host "Could not determine effective SID to compare."
}
