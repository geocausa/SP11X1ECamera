$ErrorActionPreference='Stop'
$root=Split-Path -Parent $MyInvocation.MyCommand.Path
$exit=1
try{
 & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root 'measure-rear.ps1') *> (Join-Path $root 'RUN.log')
 $exit=$LASTEXITCODE
}finally{
 try{
  Unregister-ScheduledTask -TaskName 'SP11-Native-Rear-Screen-20261007-01' -Confirm:$false -ErrorAction Stop
  [IO.File]::WriteAllText((Join-Path $root 'TASK-RETIRED.txt'),[DateTime]::UtcNow.ToString('o'),[Text.Encoding]::UTF8)
 }catch{[IO.File]::WriteAllText((Join-Path $root 'TASK-RETIRE-ERROR.txt'),$_.Exception.Message,[Text.Encoding]::UTF8)}
 [IO.File]::WriteAllText((Join-Path $root 'WRAPPER-EXIT.txt'),[string]$exit,[Text.Encoding]::UTF8)
}
exit $exit
