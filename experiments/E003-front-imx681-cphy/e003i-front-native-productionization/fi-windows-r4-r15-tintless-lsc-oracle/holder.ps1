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
function Stamp($s){"{0:O} {1}" -f [DateTime]::UtcNow,$s}
$base='C:\Users\Geoca\Documents\E003I-FI';$go="$base-START.GO";$ready="$base-READY";$done="$base-DONE"
New-Item $base -ItemType Directory -Force|Out-Null
Remove-Item $ready,$done -Force -ErrorAction SilentlyContinue
Stamp 'FI_HOLDER_BEGIN'
$groups=Await-Op ([Windows.Media.Capture.Frames.MediaFrameSourceGroup]::FindAllAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Media.Capture.Frames.MediaFrameSourceGroup]])
$group=$groups|Where-Object DisplayName -eq 'Surface Camera Front'|Select-Object -First 1;if(-not $group){throw 'front group missing'}
$settings=New-Object Windows.Media.Capture.MediaCaptureInitializationSettings;$settings.SourceGroup=$group;$settings.StreamingCaptureMode=[Windows.Media.Capture.StreamingCaptureMode]::Video;$settings.MemoryPreference=[Windows.Media.Capture.MediaCaptureMemoryPreference]::Cpu
$mc=New-Object Windows.Media.Capture.MediaCapture;Stamp 'INIT_BEGIN';Await-Action ($mc.InitializeAsync($settings));Stamp 'INIT_PASS'
$sources=@();foreach($kv in $mc.FrameSources){$sources+=$kv.Value};$src=$sources|Where-Object{$_.Info.DeviceInformation.Name-eq'Surface Camera Front'-and$_.Info.SourceKind.ToString()-eq'Color'}|Select-Object -First 1;if(-not $src){throw 'front color missing'}
$reader=Await-Op ($mc.CreateFrameReaderAsync($src)) ([Windows.Media.Capture.Frames.MediaFrameReader]);Stamp 'READER_CREATED';New-Item $ready -ItemType File -Force|Out-Null
Stamp 'WAIT_START';while(-not(Test-Path $go)){Start-Sleep -Milliseconds 5}
Stamp 'START_BEGIN';$st=Await-Op ($reader.StartAsync()) ([Windows.Media.Capture.Frames.MediaFrameReaderStartStatus]);Stamp ("START_STATUS=$st");if($st.ToString()-ne'Success'){throw 'start failed'}
Start-Sleep -Milliseconds 5000
Stamp 'STOP_BEGIN';Await-Action ($reader.StopAsync());Stamp 'STOP_PASS';$reader.Dispose();$mc.Dispose();New-Item $done -ItemType File -Force|Out-Null;Stamp 'FI_HOLDER_END'
