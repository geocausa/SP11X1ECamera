$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[void][Windows.Media.Capture.Frames.MediaFrameSourceGroup,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCapture,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCaptureInitializationSettings,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.StreamingCaptureMode,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameReader,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameReaderStartStatus,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
function Await-Op($op,[Type]$type){$m=[System.WindowsRuntimeSystemExtensions].GetMethods()|?{$_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1}|select -First 1;$t=$m.MakeGenericMethod($type).Invoke($null,@($op));$t.Wait();$t.Result}
function Await-Action($op){$m=[System.WindowsRuntimeSystemExtensions].GetMethods()|?{$_.Name -eq 'AsTask' -and -not $_.IsGenericMethod -and $_.GetParameters().Count -eq 1}|select -First 1;$t=$m.Invoke($null,@($op));$t.Wait()}
Write-Output 'E004_IR_ROUTE_HOLDER_BEGIN'
$groups=Await-Op ([Windows.Media.Capture.Frames.MediaFrameSourceGroup]::FindAllAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Media.Capture.Frames.MediaFrameSourceGroup]])
$group=$groups|? DisplayName -eq 'Surface IR Camera Front'|select -First 1
if(-not $group){throw 'Surface IR Camera Front source group not found'}
$settings=New-Object Windows.Media.Capture.MediaCaptureInitializationSettings
$settings.SourceGroup=$group
$settings.StreamingCaptureMode=[Windows.Media.Capture.StreamingCaptureMode]::Video
$settings.MemoryPreference=[Windows.Media.Capture.MediaCaptureMemoryPreference]::Cpu
$mc=New-Object Windows.Media.Capture.MediaCapture
Write-Output 'E004_IR_ROUTE_INITIALIZE_BEGIN'
Await-Action ($mc.InitializeAsync($settings))
Write-Output 'E004_IR_ROUTE_INITIALIZE_PASS'
$sources=@(); foreach($kv in $mc.FrameSources){$sources+=$kv.Value}
$src=$sources|?{$_.Info.DeviceInformation.Name -eq 'Surface IR Camera Front' -and $_.Info.SourceKind.ToString() -eq 'Infrared' -and $_.Info.MediaStreamType.ToString() -eq 'VideoPreview'}|select -First 1
if(-not $src){$src=$sources|?{$_.Info.DeviceInformation.Name -eq 'Surface IR Camera Front' -and $_.Info.SourceKind.ToString() -eq 'Infrared'}|select -First 1}
if(-not $src){throw 'No IR source'}
Write-Output ("E004_IR_ROUTE_SELECTED kind={0} stream={1} subtype={2} dims={3}x{4} fps={5}/{6}" -f $src.Info.SourceKind,$src.Info.MediaStreamType,$src.CurrentFormat.Subtype,$src.CurrentFormat.VideoFormat.Width,$src.CurrentFormat.VideoFormat.Height,$src.CurrentFormat.FrameRate.Numerator,$src.CurrentFormat.FrameRate.Denominator)
$reader=Await-Op ($mc.CreateFrameReaderAsync($src)) ([Windows.Media.Capture.Frames.MediaFrameReader])
$status=Await-Op ($reader.StartAsync()) ([Windows.Media.Capture.Frames.MediaFrameReaderStartStatus])
Write-Output ("E004_IR_ROUTE_START_STATUS={0}" -f $status)
if($status.ToString() -ne 'Success'){throw "StartAsync failed: $status"}
$frames=0
$deadline=[DateTime]::UtcNow.AddSeconds(5)
while([DateTime]::UtcNow -lt $deadline -and $frames -lt 12){
    $f=$reader.TryAcquireLatestFrame()
    if($null -ne $f){
        $frames++
        $rt=$f.SystemRelativeTime
        Write-Output ("E004_IR_ROUTE_FRAME n={0} system_relative_time={1}" -f $frames,$rt)
        $f.Dispose()
    }
    Start-Sleep -Milliseconds 25
}
Write-Output ("E004_IR_ROUTE_ACQUIRED={0}" -f $frames)
if($frames -lt 3){ throw "Insufficient acquired frames: $frames" }
Write-Output 'E004_IR_ROUTE_LIVE_GATE'
$gate=[Console]::ReadLine()
Write-Output ("E004_IR_ROUTE_GATE_RELEASE={0}" -f $gate)
Await-Action ($reader.StopAsync())
Write-Output 'E004_IR_ROUTE_STOP_PASS'
$reader.Dispose(); $mc.Dispose()
Write-Output 'E004_IR_ROUTE_HOLDER_END'
