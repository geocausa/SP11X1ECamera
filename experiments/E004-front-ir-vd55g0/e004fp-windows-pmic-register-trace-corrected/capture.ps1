$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[void][Windows.Media.Capture.Frames.MediaFrameSourceGroup,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCapture,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCaptureInitializationSettings,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.StreamingCaptureMode,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameReader,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameReaderStartStatus,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
function Await-Op($op,[Type]$type){$m=[System.WindowsRuntimeSystemExtensions].GetMethods()|?{$_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1}|select -First 1;$t=$m.MakeGenericMethod($type).Invoke($null,@($op));if(-not $t.Wait(30000)){throw 'WinRT action exceeded 30 seconds'};$t.Result}
function Await-Action($op){$m=[System.WindowsRuntimeSystemExtensions].GetMethods()|?{$_.Name -eq 'AsTask' -and -not $_.IsGenericMethod -and $_.GetParameters().Count -eq 1}|select -First 1;$t=$m.Invoke($null,@($op));if(-not $t.Wait(30000)){throw 'WinRT action exceeded 30 seconds'}}

function Report-Exposure($mc, [string]$phase) {
    try {
        $e=$mc.VideoDeviceController.ExposureControl
        if($e.Supported){
            Write-Output ("E004FP_EXPOSURE phase={0} auto={1} min_ticks={2} max_ticks={3} step_ticks={4} value_ticks={5}" -f $phase,$e.Auto,$e.Min.Ticks,$e.Max.Ticks,$e.Step.Ticks,$e.Value.Ticks)
        } else { Write-Output ("E004FP_EXPOSURE phase={0} supported=false" -f $phase) }
    } catch { Write-Output ("E004FP_EXPOSURE phase={0} error={1}" -f $phase,$_.Exception.Message) }
}
$mc=$null; $reader=$null; $frames=0
Write-Output ('E004FP_BEGIN '+[DateTime]::UtcNow.ToString('o'))
try {
    $groups=Await-Op ([Windows.Media.Capture.Frames.MediaFrameSourceGroup]::FindAllAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Media.Capture.Frames.MediaFrameSourceGroup]])
    $group=$groups|Where-Object DisplayName -eq 'Surface IR Camera Front'|Select-Object -First 1
    if(-not $group){throw 'Surface IR Camera Front missing'}
    $settings=New-Object Windows.Media.Capture.MediaCaptureInitializationSettings
    $settings.SourceGroup=$group
    $settings.StreamingCaptureMode=[Windows.Media.Capture.StreamingCaptureMode]::Video
    $settings.MemoryPreference=[Windows.Media.Capture.MediaCaptureMemoryPreference]::Cpu
    $mc=New-Object Windows.Media.Capture.MediaCapture
    Await-Action ($mc.InitializeAsync($settings))
    Write-Output 'E004FP_INIT_PASS'
    $sources=@(); foreach($kv in $mc.FrameSources){$sources+=$kv.Value}
    $src=$sources|Where-Object {$_.Info.DeviceInformation.Name -eq 'Surface IR Camera Front' -and $_.Info.SourceKind.ToString() -eq 'Infrared' -and $_.Info.MediaStreamType.ToString() -eq 'VideoPreview'}|Select-Object -First 1
    if(-not $src){throw 'Exact IR preview source missing'}
    if($src.CurrentFormat.VideoFormat.Width -ne 644 -or $src.CurrentFormat.VideoFormat.Height -ne 604){throw 'Unexpected format'}
    Write-Output ("E004FP_SOURCE subtype={0} width={1} height={2} fps={3}/{4}" -f $src.CurrentFormat.Subtype,$src.CurrentFormat.VideoFormat.Width,$src.CurrentFormat.VideoFormat.Height,$src.CurrentFormat.FrameRate.Numerator,$src.CurrentFormat.FrameRate.Denominator)
    Report-Exposure $mc 'initialized'
    $reader=Await-Op ($mc.CreateFrameReaderAsync($src)) ([Windows.Media.Capture.Frames.MediaFrameReader])
    $status=Await-Op ($reader.StartAsync()) ([Windows.Media.Capture.Frames.MediaFrameReaderStartStatus])
    Write-Output ("E004FP_START={0}" -f $status)
    if($status.ToString() -ne 'Success'){throw "Start failed: $status"}
    $deadline=[DateTime]::UtcNow.AddSeconds(5)
    while([DateTime]::UtcNow -lt $deadline -and $frames -lt 12){
        $f=$reader.TryAcquireLatestFrame()
        if($null -ne $f){
            try {
                $frames++
                Write-Output ("E004FP_FRAME n={0} timestamp={1}" -f $frames,$f.SystemRelativeTime)
                Report-Exposure $mc ('frame-'+$frames)
            } finally { $f.Dispose() }
        }
        Start-Sleep -Milliseconds 25
    }
    Write-Output ("E004FP_ACQUIRED={0}" -f $frames)
    if($frames -lt 3){throw 'Fewer than three frames'}
} finally {
    if($null -ne $reader){
        try { Await-Action ($reader.StopAsync()); Write-Output 'E004FP_STOP_PASS' }
        catch { Write-Output ('E004FP_STOP_ERROR '+$_.Exception.Message) }
        finally { $reader.Dispose() }
    }
    if($null -ne $mc){ $mc.Dispose() }
    Write-Output ('E004FP_END '+[DateTime]::UtcNow.ToString('o'))
}
