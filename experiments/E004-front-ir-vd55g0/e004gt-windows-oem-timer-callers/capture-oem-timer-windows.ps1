# E004gt only: new bounded normal OEM IR preview to correlate timer-caller KD hooks.
# Never invoke old E004gb capture or write PMIC, LED, exposure, face template or image files.
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[void][Windows.Media.Capture.Frames.MediaFrameSourceGroup,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCapture,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCaptureInitializationSettings,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.StreamingCaptureMode,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCaptureMemoryPreference,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameReader,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameReaderStartStatus,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]

function Await-Result($op,[Type]$type) {
    $method=[System.WindowsRuntimeSystemExtensions].GetMethods() |
        Where-Object { $_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 } |
        Select-Object -First 1
    $task=$method.MakeGenericMethod($type).Invoke($null,@($op))
    if(-not $task.Wait(30000)){ throw 'E004GT_OperationTimedOut' }
    return $task.Result
}
function Await-Task($op) {
    $method=[System.WindowsRuntimeSystemExtensions].GetMethods() |
        Where-Object { $_.Name -eq 'AsTask' -and -not $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 } |
        Select-Object -First 1
    $task=$method.Invoke($null,@($op))
    if(-not $task.Wait(30000)){ throw 'E004GT_ActionTimedOut' }
}
$mc=$null
$reader=$null
$frames=0
$started=$false
$stopped=$false
Write-Output ('E004GT_BEGIN '+[DateTime]::UtcNow.ToString('o'))
try {
    $groups=Await-Result ([Windows.Media.Capture.Frames.MediaFrameSourceGroup]::FindAllAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Media.Capture.Frames.MediaFrameSourceGroup]])
    $matching=@($groups | Where-Object DisplayName -eq 'Surface IR Camera Front')
    if($matching.Count -ne 1){ throw 'E004GT_ExactSurfaceIRGroupUnavailable' }
    $settings=New-Object Windows.Media.Capture.MediaCaptureInitializationSettings
    $settings.SourceGroup=$matching[0]
    $settings.StreamingCaptureMode=[Windows.Media.Capture.StreamingCaptureMode]::Video
    $settings.MemoryPreference=[Windows.Media.Capture.MediaCaptureMemoryPreference]::Cpu
    $mc=New-Object Windows.Media.Capture.MediaCapture
    Await-Task ($mc.InitializeAsync($settings))
    Write-Output 'E004GT_INITIALIZE_PASS'
    $sources=@()
    foreach($item in $mc.FrameSources){ $sources += $item.Value }
    $matchingSources=@($sources | Where-Object {
        $_.Info.DeviceInformation.Name -eq 'Surface IR Camera Front' -and
        $_.Info.SourceKind.ToString() -eq 'Infrared' -and
        $_.Info.MediaStreamType.ToString() -eq 'VideoPreview'
    })
    if($matchingSources.Count -ne 1){ throw 'E004GT_ExactIRPreviewSourceUnavailable' }
    $src=$matchingSources[0]
    $fmt=$src.CurrentFormat
    if($fmt.VideoFormat.Width -ne 644 -or $fmt.VideoFormat.Height -ne 604){
        throw 'E004GT_UnapprovedIRVideoGeometry'
    }
    Write-Output ('E004GT_SOURCE subtype={0} width={1} height={2} fps={3}/{4}' -f $fmt.Subtype,$fmt.VideoFormat.Width,$fmt.VideoFormat.Height,$fmt.FrameRate.Numerator,$fmt.FrameRate.Denominator)
    $reader=Await-Result ($mc.CreateFrameReaderAsync($src)) ([Windows.Media.Capture.Frames.MediaFrameReader])
    $state=Await-Result ($reader.StartAsync()) ([Windows.Media.Capture.Frames.MediaFrameReaderStartStatus])
    if($state.ToString() -ne 'Success'){ throw ('E004GT_ReaderStartFailed_'+$state.ToString()) }
    $started=$true
    Write-Output 'E004GT_READER_STARTED'
    $deadline=[DateTime]::UtcNow.AddSeconds(4)
    while([DateTime]::UtcNow -lt $deadline -and $frames -lt 8){
        $frame=$reader.TryAcquireLatestFrame()
        if($null -ne $frame){
            try {
                $frames++
                Write-Output ('E004GT_FRAME_METADATA n={0}' -f $frames)
                # Do NOT read VideoMediaFrame, SoftwareBitmap, planes or pixel data.
            } finally { $frame.Dispose() }
        }
        if($frames -lt 8){ Start-Sleep -Milliseconds 25 }
    }
    Write-Output ('E004GT_ACQUIRED_METADATA_ONLY={0}' -f $frames)
    if($frames -lt 3){ throw 'E004GT_FewerThanThreeNormalFrames' }
} finally {
    if($null -ne $reader){
        try {
            if($started) { Await-Task ($reader.StopAsync()) }
            $stopped=$true
            Write-Output 'E004GT_STOP_PASS'
        } catch {
            Write-Output ('E004GT_STOP_ERROR '+$_.Exception.Message)
        } finally { $reader.Dispose() }
    }
    if($null -ne $mc){ $mc.Dispose() }
    Write-Output ('E004GT_END '+[DateTime]::UtcNow.ToString('o'))
}
if(-not $stopped){ throw 'E004GT_CannotVerifyNormalReaderStop' }
if($frames -lt 3 -or $frames -gt 8){ throw 'E004GT_InvalidNormalFrameCount' }
Write-Output 'E004GT_BOUNDED_OEM_PREVIEW_COMPLETE_NO_PIXEL_SAVE'
