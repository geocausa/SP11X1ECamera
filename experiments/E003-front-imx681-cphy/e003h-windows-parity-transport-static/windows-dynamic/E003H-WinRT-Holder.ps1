$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[void][Windows.Media.Capture.Frames.MediaFrameSourceGroup,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCapture,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCaptureInitializationSettings,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.StreamingCaptureMode,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameReader,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameReaderStartStatus,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]

function Await-Op($op, [Type]$type) {
  $m=[System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 } | Select-Object -First 1
  $t=$m.MakeGenericMethod($type).Invoke($null,@($op)); $t.Wait(); return $t.Result
}
function Await-Action($op) {
  $m=[System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and -not $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 } | Select-Object -First 1
  $t=$m.Invoke($null,@($op)); $t.Wait()
}

Write-Output 'E003H_HOLDER_BEGIN'
$groups=Await-Op ([Windows.Media.Capture.Frames.MediaFrameSourceGroup]::FindAllAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Media.Capture.Frames.MediaFrameSourceGroup]])
$group=$groups | Where-Object DisplayName -eq 'Surface Camera Front' | Select-Object -First 1
if(-not $group){ throw 'Surface Camera Front source group not found' }
Write-Output ("E003H_GROUP={0}" -f $group.DisplayName)
$settings=New-Object Windows.Media.Capture.MediaCaptureInitializationSettings
$settings.SourceGroup=$group
$settings.StreamingCaptureMode=[Windows.Media.Capture.StreamingCaptureMode]::Video
$settings.MemoryPreference=[Windows.Media.Capture.MediaCaptureMemoryPreference]::Cpu
$mc=New-Object Windows.Media.Capture.MediaCapture
Write-Output 'E003H_INITIALIZE_BEGIN'
Await-Action ($mc.InitializeAsync($settings))
Write-Output 'E003H_INITIALIZE_PASS'
$sources=@()
foreach($kv in $mc.FrameSources){
  $s=$kv.Value
  $sources += $s
  $dn = if($s.Info.DeviceInformation){$s.Info.DeviceInformation.Name}else{'<none>'}
  $vf=$s.CurrentFormat.VideoFormat
  $dims=if($vf){"$($vf.Width)x$($vf.Height)"}else{'n/a'}
  Write-Output ("E003H_SOURCE device={0} kind={1} stream={2} fmt={3} dims={4} id={5}" -f $dn,$s.Info.SourceKind,$s.Info.MediaStreamType,$s.CurrentFormat.Subtype,$dims,$s.Info.Id)
}
$src=$sources | Where-Object { $_.Info.DeviceInformation.Name -eq 'Surface Camera Front' -and $_.Info.SourceKind.ToString() -eq 'Color' } | Select-Object -First 1
if(-not $src){ throw 'No Surface Camera Front color MediaFrameSource' }
if($src.Info.DeviceInformation.Name -ne 'Surface Camera Front'){ throw 'Front-source assertion failed' }
Write-Output ("E003H_SELECTED_SOURCE device={0} kind={1} stream={2} fmt={3} dims={4}" -f $src.Info.DeviceInformation.Name,$src.Info.SourceKind,$src.Info.MediaStreamType,$src.CurrentFormat.Subtype,("$($src.CurrentFormat.VideoFormat.Width)x$($src.CurrentFormat.VideoFormat.Height)"))
$reader=Await-Op ($mc.CreateFrameReaderAsync($src)) ([Windows.Media.Capture.Frames.MediaFrameReader])
Write-Output 'E003H_READER_CREATED'
$status=Await-Op ($reader.StartAsync()) ([Windows.Media.Capture.Frames.MediaFrameReaderStartStatus])
Write-Output ("E003H_START_STATUS={0}" -f $status)
if($status.ToString() -ne 'Success'){ throw "StartAsync did not succeed: $status" }
Start-Sleep -Seconds 3
Write-Output 'E003H_STOP_BEGIN'
Await-Action ($reader.StopAsync())
Write-Output 'E003H_STOP_PASS'
$reader.Dispose(); $mc.Dispose()
Write-Output 'E003H_HOLDER_END'
