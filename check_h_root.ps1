$path = "H:\"

Write-Host "=== Connection Information ==="
Get-SmbMapping | Where-Object { $_.LocalPath -eq 'H:' } | Format-List -Property LocalPath, RemotePath, Status, ConnectionType, RemoteHost, UserName, Protocol, TransportType

Write-Host "`n=== Local User Information ==="
whoami /user /fo list

if (!(Test-Path $path)) {
    Write-Host "Path $path does not exist."
    exit
}

$acl = Get-Acl $path

Write-Host "`n=== File Permissions: $path ==="
Write-Host "Owner Identity: $($acl.Owner)"
# Try to resolve owner if it looks like a SID, or opposite
try {
    $obj = New-Object System.Security.Principal.SecurityIdentifier($acl.Owner)
    Write-Host "Owner is valid SID: $($obj.Value)"
    try {
        $name = $obj.Translate([System.Security.Principal.NTAccount]).Value
        Write-Host "Resolved Owner Name: $name"
    } catch {
        Write-Host "Could not resolve Owner SID to Name."
    }
} catch {
    # It might be a name already
    Write-Host "Owner might be a name, trying to get SID..."
    try {
        $sid = (New-Object System.Security.Principal.NTAccount($acl.Owner)).Translate([System.Security.Principal.SecurityIdentifier]).Value
        Write-Host "Resolved Owner SID: $sid"
    } catch {
        Write-Host "Could not resolve Owner Name to SID."
    }
}

Write-Host "`n--- Access Rules ---"
foreach ($rule in $acl.Access) {
    Write-Host "Identity: $($rule.IdentityReference)"
    $sidStr = $null
    
    # Check if IdentityReference is already a SID
    if ($rule.IdentityReference -is [System.Security.Principal.SecurityIdentifier]) {
        $sidStr = $rule.IdentityReference.Value
        Write-Host "  Type: SecurityIdentifier"
        Write-Host "  SID: $sidStr"
        try {
            $name = $rule.IdentityReference.Translate([System.Security.Principal.NTAccount]).Value
            Write-Host "  Resolved Name: $name"
        } catch {
            Write-Host "  Name: <Unresolvable>"
        }
    } else {
        Write-Host "  Type: NTAccount"
        try {
            $sidStr = $rule.IdentityReference.Translate([System.Security.Principal.SecurityIdentifier]).Value
            Write-Host "  Resolved SID: $sidStr"
        } catch {
            Write-Host "  SID: <Unresolvable>"
        }
    }

    Write-Host "  Rights: $($rule.FileSystemRights)"
    Write-Host "  Type: $($rule.AccessControlType)"
    Write-Host "  Inheritance: $($rule.IsInherited) ($($rule.InheritanceFlags), $($rule.PropagationFlags))"
    Write-Host "--------------------"
}
