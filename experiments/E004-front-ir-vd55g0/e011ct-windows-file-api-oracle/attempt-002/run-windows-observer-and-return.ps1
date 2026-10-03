[CmdletBinding()]
param([string]$ExpectedObserverSha)
$ErrorActionPreference='Stop'
if(-not $ExpectedObserverSha -or $ExpectedObserverSha -notmatch '^[0-9a-f]{64}$'){throw 'Explicit prepared observer digest required'}
if([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT){throw 'Windows required'}
$armed=$false
$createdMount=$false
$drive=$null
$phase='entry'
try {
 & "$env:windir\System32\shutdown.exe" /r /t 600 /f /c 'E011CT OS dependency Golden fallback'
 if($LASTEXITCODE -ne 0){throw 'Failed to arm dedicated Golden watchdog'}
 $armed=$true
 $phase='watchdog_armed'
 $partition=Get-Partition -DiskNumber 0 -PartitionNumber 1
 if(([string]$partition.GptType).Trim('{}').ToLowerInvariant() -ne 'c12a7328-f81f-11d2-ba4b-00a0c93ec93b' -or
    ([string]$partition.Guid).Trim('{}').ToLowerInvariant() -ne '5b4f74dc-b427-4828-bc1d-ab024feeb313' -or
    $partition.Size -ne 209715200){throw 'Pinned SP11 EFI partition mismatch'}
 $preexistingMount=[bool]$partition.DriveLetter
 if($preexistingMount){
  $drive=[string]$partition.DriveLetter
  if($drive -notmatch '^[A-Za-z]$'){throw 'Existing ESP letter mismatch'}
 }else{
  $used=[IO.Directory]::GetLogicalDrives()
  $drive=@('S','T','U','V','W','X','Y','Z')|Where-Object{($used -notcontains ($_+':\')) -and (-not (Get-PSDrive -Name $_ -ErrorAction SilentlyContinue))}|Select-Object -First 1
  if(-not $drive){throw 'No unused temporary ESP letter'}
  & "$env:windir\System32\mountvol.exe" ($drive+':') /S
  if($LASTEXITCODE -ne 0){throw 'ESP mount failed'}
  $createdMount=$true
 }
 $mount=$drive+':\'
 $root=[IO.Path]::Combine($mount,'EFI\SP11CameraPrivate\E011CT-OS-002')
 $script=Join-Path $root 'windows-file-api-observer.ps1'
 $actual=(Get-FileHash -LiteralPath $script -Algorithm SHA256).Hash.ToLowerInvariant()
 if($actual -ne $ExpectedObserverSha){throw 'Prepared observer digest mismatch'}
 $phase='prepared_source_verified'
 [ordered]@{identity='E011CT-OS-002';phase=$phase;UTC=[DateTime]::UtcNow.ToString('o');watchdog_armed=$true;observer_sha256=$actual;new_camera_Starts=0;scheduled_task_registered=$false;preexisting_ESP_mount_preserved=$preexistingMount;temporary_mount_owned_by_runner=$createdMount;ESP_partition_guid_verified=$true}|ConvertTo-Json -Compress|Set-Content -LiteralPath (Join-Path $root 'WINDOWS-PARENT-GUARD-SAFE.json') -Encoding UTF8
 & $script -Root $root -WatchdogAlreadyArmed
 $phase='observer_completed'
} catch {
 [ordered]@{identity='E011CT-OS-002';status='ABORT';phase=$phase;exception_type=$_.Exception.GetType().FullName;watchdog_armed=$armed;new_camera_Starts=0}|ConvertTo-Json -Compress
 throw
} finally {
 if($createdMount){ & "$env:windir\System32\mountvol.exe" ($drive+':\') /D | Out-Null }
 if($armed){
  & "$env:windir\System32\shutdown.exe" /a | Out-Null
  & "$env:windir\System32\shutdown.exe" /r /t 15 /f /c 'E011CT observer retired; normal return to Golden'
 }
}
