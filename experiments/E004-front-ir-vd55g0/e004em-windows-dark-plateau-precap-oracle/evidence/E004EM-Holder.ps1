$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[void][Windows.Media.Capture.Frames.MediaFrameSourceGroup,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCapture,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCaptureInitializationSettings,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.StreamingCaptureMode,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameReader,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameReaderStartStatus,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
function Await-Op($op,[Type]$type){$m=[System.WindowsRuntimeSystemExtensions].GetMethods()|Where-Object{$_.Name-eq'AsTask'-and$_.IsGenericMethod-and$_.GetParameters().Count-eq1}|Select-Object -First 1;$t=$m.MakeGenericMethod($type).Invoke($null,@($op));$t.Wait();$t.Result}
function Await-Action($op){$m=[System.WindowsRuntimeSystemExtensions].GetMethods()|Where-Object{$_.Name-eq'AsTask'-and-not$_.IsGenericMethod-and$_.GetParameters().Count-eq1}|Select-Object -First 1;$t=$m.Invoke($null,@($op));$t.Wait()}
$base='C:\Users\Geoca\Documents\E004EM';$go="$base-START.GO";$ready="$base-READY";$done="$base-DONE"
$groups=Await-Op ([Windows.Media.Capture.Frames.MediaFrameSourceGroup]::FindAllAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Media.Capture.Frames.MediaFrameSourceGroup]])
$group=$groups|Where-Object DisplayName -eq 'Surface Camera Front'|Select-Object -First 1;if(-not $group){throw 'front group missing'}
$settings=New-Object Windows.Media.Capture.MediaCaptureInitializationSettings;$settings.SourceGroup=$group;$settings.StreamingCaptureMode=[Windows.Media.Capture.StreamingCaptureMode]::Video;$settings.MemoryPreference=[Windows.Media.Capture.MediaCaptureMemoryPreference]::Cpu
$mc=New-Object Windows.Media.Capture.MediaCapture; Await-Action ($mc.InitializeAsync($settings))
$sources=@();foreach($kv in $mc.FrameSources){$sources+=$kv.Value};$src=$sources|Where-Object{$_.Info.DeviceInformation.Name-eq'Surface Camera Front'-and$_.Info.SourceKind.ToString()-eq'Color'}|Select-Object -First 1;if(-not $src){throw 'front color missing'}
$reader=Await-Op ($mc.CreateFrameReaderAsync($src)) ([Windows.Media.Capture.Frames.MediaFrameReader]); New-Item $ready -ItemType File -Force|Out-Null
while(-not(Test-Path $go)){Start-Sleep -Milliseconds 5}
$st=Await-Op ($reader.StartAsync()) ([Windows.Media.Capture.Frames.MediaFrameReaderStartStatus]); if($st.ToString()-ne'Success'){throw 'start failed'}
Start-Sleep -Milliseconds 7000
Await-Action ($reader.StopAsync());$reader.Dispose();$mc.Dispose();New-Item $done -ItemType File -Force|Out-Null
