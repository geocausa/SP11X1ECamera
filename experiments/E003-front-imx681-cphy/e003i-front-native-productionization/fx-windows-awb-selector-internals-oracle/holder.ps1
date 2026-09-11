$ErrorActionPreference = 'Stop'
$Base = 'C:\Users\Geoca\Documents\E003I-FX'
$Go = "$Base-START.GO"
$Ready = "$Base-READY"
$Done = "$Base-DONE"
Remove-Item $Go,$Ready,$Done -Force -ErrorAction SilentlyContinue
Write-Output "$(Get-Date -Format o) FX_HOLDER_BEGIN"
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null=[Windows.Media.Capture.MediaCapture,Windows.Media.Capture,ContentType=WindowsRuntime]
$null=[Windows.Media.Capture.MediaCaptureInitializationSettings,Windows.Media.Capture,ContentType=WindowsRuntime]
$null=[Windows.Media.Capture.StreamingCaptureMode,Windows.Media.Capture,ContentType=WindowsRuntime]
$null=[Windows.Media.Capture.MediaStreamType,Windows.Media.Capture,ContentType=WindowsRuntime]
$null=[Windows.Media.Capture.MediaFrameSourceKind,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
$null=[Windows.Media.Capture.Frames.MediaFrameReader,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
function Await($op,[Type]$t){$asTask=[System.WindowsRuntimeSystemExtensions].GetMethods()|?{$_.Name-eq'AsTask'-and$_.IsGenericMethod-and$_.GetParameters().Count-eq1}|select -First 1;$task=$asTask.MakeGenericMethod($t).Invoke($null,@($op));$task.Wait();$task.Result}
function AwaitAction($op){$task=[System.WindowsRuntimeSystemExtensions]::AsTask($op);$task.Wait()}
Write-Output "$(Get-Date -Format o) INIT_BEGIN"
$mc=[Windows.Media.Capture.MediaCapture]::new()
$settings=[Windows.Media.Capture.MediaCaptureInitializationSettings]::new()
$settings.StreamingCaptureMode=[Windows.Media.Capture.StreamingCaptureMode]::Video
$settings.SharingMode=[Windows.Media.Capture.MediaCaptureSharingMode]::ExclusiveControl
AwaitAction ($mc.InitializeAsync($settings))
$src=$mc.FrameSources.Values|?{$_.Info.SourceKind -eq [Windows.Media.Capture.MediaFrameSourceKind]::Color -and $_.Info.DeviceInformation.Name -like '*Surface Camera Front*'}|select -First 1
if(-not $src){throw 'Surface Camera Front source missing'}
Write-Output "$(Get-Date -Format o) INIT_PASS"
$reader=Await ($mc.CreateFrameReaderAsync($src)) ([Windows.Media.Capture.Frames.MediaFrameReader])
Write-Output "$(Get-Date -Format o) READER_CREATED"
New-Item -ItemType File -Path $Ready -Force|Out-Null
Write-Output "$(Get-Date -Format o) WAIT_START"
$deadline=(Get-Date).AddMinutes(5)
while(-not(Test-Path $Go)){if((Get-Date)-gt$deadline){throw 'START.GO timeout'};Start-Sleep -Milliseconds 100}
Write-Output "$(Get-Date -Format o) START_BEGIN"
$status=Await ($reader.StartAsync()) ([Windows.Media.Capture.Frames.MediaFrameReaderStartStatus])
Write-Output "$(Get-Date -Format o) START_STATUS=$status"
Start-Sleep -Seconds 5
Write-Output "$(Get-Date -Format o) STOP_BEGIN"
AwaitAction ($reader.StopAsync())
Write-Output "$(Get-Date -Format o) STOP_PASS"
$reader.Dispose();$mc.Dispose()
New-Item -ItemType File -Path $Done -Force|Out-Null
Write-Output "$(Get-Date -Format o) FX_HOLDER_END"
