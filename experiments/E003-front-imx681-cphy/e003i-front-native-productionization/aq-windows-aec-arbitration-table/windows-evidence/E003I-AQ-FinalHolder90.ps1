$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[void][Windows.Media.Capture.Frames.MediaFrameSourceGroup,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCapture,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCaptureInitializationSettings,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.StreamingCaptureMode,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameReader,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameReaderStartStatus,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
function Await-Op($op, [Type]$type) { $m=[System.WindowsRuntimeSystemExtensions].GetMethods() | ? { $_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 } | select -First 1; $t=$m.MakeGenericMethod($type).Invoke($null,@($op)); $t.Wait(); $t.Result }
function Await-Action($op) { $m=[System.WindowsRuntimeSystemExtensions].GetMethods() | ? { $_.Name -eq 'AsTask' -and -not $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 } | select -First 1; $t=$m.Invoke($null,@($op)); $t.Wait() }
$gate='C:\Users\Geoca\Documents\E003I-AC53.GO'
Remove-Item $gate -Force -ErrorAction SilentlyContinue
Write-Output 'E003I_AC53_BEGIN'
$groups=Await-Op ([Windows.Media.Capture.Frames.MediaFrameSourceGroup]::FindAllAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Media.Capture.Frames.MediaFrameSourceGroup]])
$group=$groups | ? DisplayName -eq 'Surface Camera Front' | select -First 1
if(-not $group){throw 'front group missing'}
$settings=New-Object Windows.Media.Capture.MediaCaptureInitializationSettings
$settings.SourceGroup=$group; $settings.StreamingCaptureMode=[Windows.Media.Capture.StreamingCaptureMode]::Video; $settings.MemoryPreference=[Windows.Media.Capture.MediaCaptureMemoryPreference]::Cpu
Write-Output 'E003I_AC53_FILE_GATE_WAIT'
while(-not (Test-Path $gate)){ Start-Sleep -Milliseconds 50 }
Remove-Item $gate -Force -ErrorAction SilentlyContinue
Write-Output 'E003I_AC53_FILE_GATE_RELEASE'
$mc=New-Object Windows.Media.Capture.MediaCapture; Await-Action ($mc.InitializeAsync($settings))
$sources=@(); foreach($kv in $mc.FrameSources){ $sources += $kv.Value }
$src=$sources | ? { $_.Info.DeviceInformation.Name -eq 'Surface Camera Front' -and $_.Info.SourceKind.ToString() -eq 'Color' } | select -First 1
if(-not $src){throw 'front color source missing'}
$reader=Await-Op ($mc.CreateFrameReaderAsync($src)) ([Windows.Media.Capture.Frames.MediaFrameReader])
$s=Await-Op ($reader.StartAsync()) ([Windows.Media.Capture.Frames.MediaFrameReaderStartStatus]); Write-Output "E003I_AC53_STATUS=$s"; if($s.ToString() -ne 'Success'){throw 'start failed'}
Start-Sleep -Seconds 90
Await-Action ($reader.StopAsync()); $reader.Dispose(); $mc.Dispose(); Write-Output 'E003I_AC53_END'












