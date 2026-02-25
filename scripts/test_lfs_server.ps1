Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-PythonCommand {
  $uv = Get-Command uv -ErrorAction SilentlyContinue
  if ($uv) {
    $uvPy = & $uv.Source python find 2>$null
    if ($LASTEXITCODE -eq 0 -and $uvPy) {
      $uvPyPath = ($uvPy | Select-Object -First 1).Trim()
      if ($uvPyPath -and (Test-Path $uvPyPath)) {
        return @{
          Executable = $uvPyPath
          PrefixArgs = @()
        }
      }
    }

    return @{
      Executable = $uv.Source
      PrefixArgs = @("run", "python")
    }
  }

  $cmd = Get-Command python -ErrorAction SilentlyContinue
  if ($cmd) {
    return @{
      Executable = $cmd.Source
      PrefixArgs = @()
    }
  }

  $py = Get-Command py -ErrorAction SilentlyContinue
  if ($py) {
    return @{
      Executable = $py.Source
      PrefixArgs = @("-3")
    }
  }

  throw "uv/python/py command was not found in PATH."
}

function Invoke-Http {
  param(
    [Parameter(Mandatory = $true)][string]$Method,
    [Parameter(Mandatory = $true)][string]$Url,
    [hashtable]$Headers,
    [object]$Body,
    [string]$ContentType = "",
    [switch]$Raw
  )

  $params = @{
    Method = $Method
    Uri = $Url
    Headers = $Headers
    SkipHttpErrorCheck = $true
  }
  if ($Body -ne $null) {
    $params["Body"] = $Body
  }
  if ($ContentType) {
    $params["ContentType"] = $ContentType
  }

  $resp = Invoke-WebRequest @params
  if ($Raw) {
    return $resp
  }

  $parsed = $null
  if ($resp.Content) {
    $contentText = $resp.Content
    if ($resp.Content -is [byte[]]) {
      $contentText = [Text.Encoding]::UTF8.GetString($resp.Content)
    }
    try {
      $parsed = $contentText | ConvertFrom-Json
    }
    catch {
      $parsed = $contentText
    }
  }

  return @{
    Status = [int]$resp.StatusCode
    Body = $parsed
    Raw = $resp
  }
}

function Wait-ServerReady {
  param(
    [Parameter(Mandatory = $true)][string]$BaseUrl,
    [int]$TimeoutSec = 10
  )

  $deadline = (Get-Date).AddSeconds($TimeoutSec)
  while ((Get-Date) -lt $deadline) {
    try {
      $resp = Invoke-Http -Method GET -Url "$BaseUrl/locks"
      if ($resp.Status -in @(200, 401, 403)) {
        return
      }
    }
    catch {
      Start-Sleep -Milliseconds 200
    }
  }
  throw "Server did not become ready in ${TimeoutSec}s: $BaseUrl"
}

function Start-LfsServer {
  param(
    [Parameter(Mandatory = $true)][string]$RepoRoot,
    [Parameter(Mandatory = $true)][string]$StorageDir,
    [Parameter(Mandatory = $true)][int]$Port,
    [string[]]$ExtraArgs = @()
  )

  $py = Get-PythonCommand
  $script = Join-Path $RepoRoot "lfs_server.py"
  $args = @() + $py.PrefixArgs + @(
    $script,
    "--host", "127.0.0.1",
    "--port", "$Port",
    "--storage-dir", $StorageDir
  ) + $ExtraArgs

  $proc = Start-Process -FilePath $py.Executable -ArgumentList $args -PassThru -NoNewWindow -WorkingDirectory $RepoRoot
  Wait-ServerReady -BaseUrl "http://127.0.0.1:$Port/info/lfs"
  return $proc
}

function Get-FreePort {
  $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, 0)
  $listener.Start()
  try {
    return $listener.LocalEndpoint.Port
  }
  finally {
    $listener.Stop()
  }
}

function Stop-ProcessTree {
  param([int]$TargetPid)
  $children = @(Get-CimInstance Win32_Process -Filter "ParentProcessId=$TargetPid" -ErrorAction SilentlyContinue)
  foreach ($child in $children) {
    Stop-ProcessTree -TargetPid $child.ProcessId
  }
  try {
    Stop-Process -Id $TargetPid -Force -ErrorAction Stop
  }
  catch {
  }
}

function Stop-ProcIfRunning {
  param([System.Diagnostics.Process]$Proc)
  if ($null -ne $Proc -and -not $Proc.HasExited) {
    Stop-ProcessTree -TargetPid $Proc.Id
    try {
      $Proc.WaitForExit(3000) | Out-Null
    }
    catch {
    }
  }
}

function Assert-True {
  param(
    [Parameter(Mandatory = $true)][bool]$Condition,
    [Parameter(Mandatory = $true)][string]$Message
  )
  if (-not $Condition) {
    throw "Assertion failed: $Message"
  }
}

function Make-BasicAuthHeader {
  param([string]$User, [string]$Password)
  $token = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes("$User`:$Password"))
  return @{ Authorization = "Basic $token" }
}

function Get-LfsHeaders {
  param([hashtable]$Extra = @{})
  $h = @{
    Accept = "application/vnd.git-lfs+json"
  }
  foreach ($k in $Extra.Keys) {
    $h[$k] = $Extra[$k]
  }
  return $h
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$baseMedia = "application/vnd.git-lfs+json"
$tmpRoot = Join-Path $env:TEMP ("git-lfs-lite-test-" + [Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $tmpRoot | Out-Null

$port1 = Get-FreePort
$port2 = Get-FreePort
$port3 = Get-FreePort

$proc1 = $null
$proc2 = $null
$proc3 = $null

try {
  Write-Host "[1/3] no-auth mode basic flow test"
  $storage1 = Join-Path $tmpRoot "store1"
  New-Item -ItemType Directory -Path $storage1 | Out-Null
  $proc1 = Start-LfsServer -RepoRoot $repoRoot -StorageDir $storage1 -Port $port1 -ExtraArgs @("--auth-mode", "none")
  $base1 = "http://127.0.0.1:$port1/info/lfs"

  $payload = [Text.Encoding]::UTF8.GetBytes("git-lfs-lite-test-" + [Guid]::NewGuid().ToString("N"))
  $oid = ([System.Security.Cryptography.SHA256]::HashData($payload) | ForEach-Object { $_.ToString("x2") }) -join ""
  $size = $payload.Length

  $batchReq = @{
    operation = "upload"
    transfers = @("basic")
    objects = @(@{ oid = $oid; size = $size })
  } | ConvertTo-Json -Depth 8

  $batchUpload = Invoke-Http -Method POST -Url "$base1/objects/batch" -Headers (Get-LfsHeaders) -ContentType $baseMedia -Body $batchReq
  Assert-True ($batchUpload.Status -eq 200) "upload batch status should be 200"
  Assert-True ($null -ne $batchUpload.Body) "upload batch body should exist"
  $hasObjects = $batchUpload.Body.PSObject.Properties.Name -contains "objects"
  Assert-True $hasObjects ("upload batch objects missing. body=" + ($batchUpload.Raw.Content))
  $uploadHref = $batchUpload.Body.objects[0].actions.upload.href
  $verifyHref = $batchUpload.Body.objects[0].actions.verify.href
  Assert-True ([string]::IsNullOrEmpty($uploadHref) -eq $false) "upload href is required"
  Assert-True ([string]::IsNullOrEmpty($verifyHref) -eq $false) "verify href is required"

  $putResp = Invoke-Http -Method PUT -Url $uploadHref -Body $payload -ContentType "application/octet-stream"
  Assert-True ($putResp.Status -eq 200) "upload object status should be 200"

  $verifyReq = @{ oid = $oid; size = $size } | ConvertTo-Json
  $verifyResp = Invoke-Http -Method POST -Url $verifyHref -ContentType $baseMedia -Body $verifyReq
  Assert-True ($verifyResp.Status -eq 200) "verify status should be 200"

  $batchDlReq = @{
    operation = "download"
    transfers = @("basic")
    objects = @(@{ oid = $oid; size = $size })
  } | ConvertTo-Json -Depth 8
  $batchDownload = Invoke-Http -Method POST -Url "$base1/objects/batch" -Headers (Get-LfsHeaders) -ContentType $baseMedia -Body $batchDlReq
  Assert-True ($batchDownload.Status -eq 200) "download batch status should be 200"
  $downloadHref = $batchDownload.Body.objects[0].actions.download.href
  Assert-True ([string]::IsNullOrEmpty($downloadHref) -eq $false) "download href is required"

  $downloadPath = Join-Path $tmpRoot "download.bin"
  $dlResp = Invoke-WebRequest -Method GET -Uri $downloadHref -OutFile $downloadPath -SkipHttpErrorCheck -PassThru
  Assert-True ([int]$dlResp.StatusCode -eq 200) "download status should be 200"
  $downloadBytes = [IO.File]::ReadAllBytes($downloadPath)
  Assert-True ($downloadBytes.Length -eq $payload.Length) "downloaded payload length should match"
  Assert-True ([System.Linq.Enumerable]::SequenceEqual($downloadBytes, $payload)) "downloaded payload should match uploaded data"

  $lockCreateReq = @{ path = "large.bin" } | ConvertTo-Json
  $lockCreate = Invoke-Http -Method POST -Url "$base1/locks" -ContentType $baseMedia -Body $lockCreateReq
  Assert-True ($lockCreate.Status -eq 201) "lock create should be 201"
  $lockId = $lockCreate.Body.lock.id
  Assert-True ([string]::IsNullOrEmpty($lockId) -eq $false) "lock id is required"

  $lockList = Invoke-Http -Method GET -Url "$base1/locks"
  Assert-True ($lockList.Status -eq 200) "lock list should be 200"
  Assert-True ($lockList.Body.locks.Count -ge 1) "lock list should include created lock"

  $lockVerifyReq = @{ limit = 100 } | ConvertTo-Json
  $lockVerify = Invoke-Http -Method POST -Url "$base1/locks/verify" -ContentType $baseMedia -Body $lockVerifyReq
  Assert-True ($lockVerify.Status -eq 200) "lock verify should be 200"
  Assert-True ($lockVerify.Body.ours.Count -ge 1) "ours should include created lock"

  $unlockReq = @{ force = $false } | ConvertTo-Json
  $unlockResp = Invoke-Http -Method POST -Url "$base1/locks/$lockId/unlock" -ContentType $baseMedia -Body $unlockReq
  Assert-True ($unlockResp.Status -eq 200) "unlock should be 200"
  Stop-ProcIfRunning -Proc $proc1

  Write-Host "[2/3] basic auth test"
  $storage2 = Join-Path $tmpRoot "store2"
  New-Item -ItemType Directory -Path $storage2 | Out-Null
  $proc2 = Start-LfsServer -RepoRoot $repoRoot -StorageDir $storage2 -Port $port2 -ExtraArgs @(
    "--auth-mode", "basic",
    "--basic-user", "lfs",
    "--basic-pass", "secret"
  )
  $base2 = "http://127.0.0.1:$port2/info/lfs"

  $unauthResp = Invoke-Http -Method GET -Url "$base2/locks"
  Assert-True ($unauthResp.Status -eq 401) "without auth should be 401"

  $authHeaders = Make-BasicAuthHeader -User "lfs" -Password "secret"
  $authResp = Invoke-Http -Method GET -Url "$base2/locks" -Headers $authHeaders
  Assert-True ($authResp.Status -eq 200) "with basic auth should be 200"
  Stop-ProcIfRunning -Proc $proc2

  Write-Host "[3/3] CIDR allow-list test"
  $storage3 = Join-Path $tmpRoot "store3"
  New-Item -ItemType Directory -Path $storage3 | Out-Null
  $proc3 = Start-LfsServer -RepoRoot $repoRoot -StorageDir $storage3 -Port $port3 -ExtraArgs @("--auth-mode", "none", "--allow-net", "10.0.0.0/8")
  $base3 = "http://127.0.0.1:$port3/info/lfs"
  $forbiddenResp = Invoke-Http -Method GET -Url "$base3/locks"
  Assert-True ($forbiddenResp.Status -eq 403) "localhost should be blocked when only 10.0.0.0/8 is allowed"
  Stop-ProcIfRunning -Proc $proc3

  Write-Host "All tests passed."
}
finally {
  Stop-ProcIfRunning -Proc $proc1
  Stop-ProcIfRunning -Proc $proc2
  Stop-ProcIfRunning -Proc $proc3
  if (Test-Path $tmpRoot) {
    Remove-Item -Recurse -Force $tmpRoot
  }
}
