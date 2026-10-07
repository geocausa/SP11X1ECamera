$ErrorActionPreference='Stop'
if($env:COMPUTERNAME -ne 'DESKTOP-AQ4SMTC'){throw 'SP11 Windows only'}
$root=Split-Path -Parent $MyInvocation.MyCommand.Path
$task='SP11-Native-Rear-Screen-20261007-01'
if(Test-Path -LiteralPath (Join-Path $root 'CONSUMED.txt')){throw 'identity consumed; never rerun'}
if(Test-Path -LiteralPath (Join-Path $root 'RESULT.json')){throw 'unexpected existing result'}
if(Get-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue){throw 'unexpected existing task'}
if(-not (Get-Acl -LiteralPath $root).AreAccessRulesProtected){throw 'private ACL not protected'}
$user=(Get-CimInstance Win32_ComputerSystem).UserName
if(-not $user -or $user -notmatch '\\Geoca$'){throw 'Geoca must already be signed in'}
$manifest=Get-Content -LiteralPath (Join-Path $root 'SOURCE.json') -Raw|ConvertFrom-Json
foreach($name in @('measure-rear.ps1','run-once.ps1')){
 $p=Join-Path $root $name
 if((Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant() -ne $manifest.files.$name){throw ('script hash drift '+$name)}
 $tokens=$null;$errors=$null
 [void][Management.Automation.Language.Parser]::ParseFile($p,[ref]$tokens,[ref]$errors)
 if($errors.Count){throw ($errors|Out-String)}
}
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root 'measure-rear.ps1') -OfflineTest
if($LASTEXITCODE -ne 0){throw 'SP11 offline test failed; no start'}
$action=New-ScheduledTaskAction -Execute 'powershell.exe' -Argument ('-NoProfile -ExecutionPolicy Bypass -File "'+(Join-Path $root 'run-once.ps1')+'"') -WorkingDirectory $root
$principal=New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Highest
$settings=New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Seconds 180) -MultipleInstances IgnoreNew
$definition=New-ScheduledTask -Action $action -Principal $principal -Settings $settings
Register-ScheduledTask -TaskName $task -InputObject $definition|Out-Null
try{
 [xml]$xml=Export-ScheduledTask -TaskName $task
 $children=@($xml.SelectNodes('/*[local-name()="Task"]/*[local-name()="Triggers"]/*'))
 if($children.Count -ne 0){throw 'task has scheduled trigger'}
 if(Test-Path -LiteralPath (Join-Path $root 'CONSUMED.txt')){throw 'consumed during preparation'}
 [IO.File]::WriteAllText((Join-Path $root 'TASK-PREPARED.json'),(@{task=$task;user=$user;trigger_children=0;started_once_utc=[DateTime]::UtcNow.ToString('o')}|ConvertTo-Json),[Text.Encoding]::UTF8)
 Start-ScheduledTask -TaskName $task
 Write-Output 'REAR_SCREEN_01_TASK_STARTED_ONCE=YES TRIGGERS=0'
}catch{
 Unregister-ScheduledTask -TaskName $task -Confirm:$false -ErrorAction SilentlyContinue
 throw
}
