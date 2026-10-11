# SPDX-License-Identifier: MIT
$ErrorActionPreference='Stop'
if($env:COMPUTERNAME -ne 'DESKTOP-AQ4SMTC'){throw 'SP11 Windows only'}
$root='C:\Users\Geoca\Documents\SP11-Camera-WindowsDaylight-20261011-01'
$task='SP11-Daylight-Both-20261011-01'
if(Test-Path -LiteralPath (Join-Path $root 'CONSUMED.txt')){throw 'identity consumed; never rerun'}
if(Get-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue){throw 'unexpected existing task'}
$user=(Get-CimInstance Win32_ComputerSystem).UserName
if(-not $user -or $user -notmatch '\\Geoca$'){throw 'Geoca must already be signed in'}
$p=Join-Path $root 'capture-daylight-01.ps1'
$tokens=$null;$errors=$null
[void][Management.Automation.Language.Parser]::ParseFile($p,[ref]$tokens,[ref]$errors)
if($errors.Count){throw ($errors|Out-String)}
$action=New-ScheduledTaskAction -Execute 'powershell.exe' -Argument ('-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "'+$p+'"') -WorkingDirectory $root
$principal=New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Highest
$settings=New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Seconds 240) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName $task -InputObject (New-ScheduledTask -Action $action -Principal $principal -Settings $settings)|Out-Null
Start-ScheduledTask -TaskName $task
Write-Output 'DAYLIGHT_01_TASK_STARTED_ONCE=YES'
