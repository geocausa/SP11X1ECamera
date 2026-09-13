$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[void][Windows.Media.Capture.MediaCapture,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCaptureInitializationSettings,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.StreamingCaptureMode,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCaptureMemoryPreference,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameSourceGroup,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameReader,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameReaderStartStatus,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
function Await-Op($op,[Type]$type){$m=[System.WindowsRuntimeSystemExtensions].GetMethods()|?{$_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1}|select -First 1;$t=$m.MakeGenericMethod($type).Invoke($null,@($op));$t.Wait();$t.Result}
function Await-Action($op){$m=[System.WindowsRuntimeSystemExtensions].GetMethods()|?{$_.Name -eq 'AsTask' -and -not $_.IsGenericMethod -and $_.GetParameters().Count -eq 1}|select -First 1;$t=$m.Invoke($null,@($op));$t.Wait()}
function Put-U32([byte[]]$b,[int]$o,[uint32]$v){[Array]::Copy([BitConverter]::GetBytes($v),0,$b,$o,4)}
function New-KsPropertyGet(){ $b=New-Object byte[] 24; $g=([Guid]'1CB79112-C0D2-4213-9CA6-CD4FDB927972').ToByteArray(); [Array]::Copy($g,0,$b,0,16); Put-U32 $b 16 36; Put-U32 $b 20 1; return $b }
function Get-SM($ctl,[string]$tag){ try{[Nullable[uint32]]$max=40;$r=$ctl.GetDevicePropertyByExtendedId((New-KsPropertyGet),$max);$a=[byte[]]$r.Value;if($a.Length -ge 32){$pin=[BitConverter]::ToUInt32($a,4);$fl=[BitConverter]::ToUInt64($a,16);$cap=[BitConverter]::ToUInt64($a,24);Write-Output ("E004AJ_FACEAUTH_SM tag={0} status={1} pin=0x{2:x8} flags=0x{3:x} cap=0x{4:x}" -f $tag,$r.Status,$pin,$fl,$cap)}else{Write-Output ("E004AJ_FACEAUTH_SM tag={0} status={1} len={2}" -f $tag,$r.Status,$a.Length)}} catch{Write-Output ("E004AJ_FACEAUTH_SM tag={0} ERROR={1}" -f $tag,$_.Exception.Message)}}
Write-Output 'E004AJ_FACEAUTH_BEGIN'
$groups=Await-Op ([Windows.Media.Capture.Frames.MediaFrameSourceGroup]::FindAllAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Media.Capture.Frames.MediaFrameSourceGroup]])
$g=$groups|? DisplayName -eq 'Surface IR Camera Front'|select -First 1
if(-not $g){throw 'IR group missing'}
$profiles=[Windows.Media.Capture.MediaCapture]::FindAllVideoProfiles($g.Id)
$face=$profiles|?{$_.Id -like '{81361B22-700B-4546-A2D4-C52E907BFC27},0'}|select -First 1
if(-not $face){throw 'FaceAuth profile missing'}
$desc=$face.SupportedPreviewMediaDescription|select -First 1
Write-Output ("E004AJ_FACEAUTH_PROFILE id={0} subtype={1} dims={2}x{3} fps={4}" -f $face.Id,$desc.Subtype,$desc.Width,$desc.Height,$desc.FrameRate)
$settings=New-Object Windows.Media.Capture.MediaCaptureInitializationSettings
$settings.VideoDeviceId=$face.VideoDeviceId
$settings.VideoProfile=$face
$settings.PreviewMediaDescription=$desc
$settings.StreamingCaptureMode=[Windows.Media.Capture.StreamingCaptureMode]::Video
$settings.MemoryPreference=[Windows.Media.Capture.MediaCaptureMemoryPreference]::Cpu
$mc=New-Object Windows.Media.Capture.MediaCapture
Write-Output 'E004AJ_FACEAUTH_INIT_BEGIN'
Await-Action ($mc.InitializeAsync($settings))
Write-Output 'E004AJ_FACEAUTH_INIT_PASS'
$ctl=$mc.VideoDeviceController
Get-SM $ctl 'after-init'
$sources=@();foreach($kv in $mc.FrameSources){$sources+=$kv.Value}
$src=$sources|?{$_.Info.SourceKind.ToString() -eq 'Infrared' -and $_.Info.MediaStreamType.ToString() -eq 'VideoPreview'}|select -First 1
if(-not $src){throw 'FaceAuth IR preview source missing'}
Write-Output ("E004AJ_FACEAUTH_SOURCE profile={0} kind={1} stream={2} subtype={3} dims={4}x{5} fps={6}/{7}" -f $src.Info.ProfileId,$src.Info.SourceKind,$src.Info.MediaStreamType,$src.CurrentFormat.Subtype,$src.CurrentFormat.VideoFormat.Width,$src.CurrentFormat.VideoFormat.Height,$src.CurrentFormat.FrameRate.Numerator,$src.CurrentFormat.FrameRate.Denominator)
$reader=Await-Op ($mc.CreateFrameReaderAsync($src)) ([Windows.Media.Capture.Frames.MediaFrameReader])
$status=Await-Op ($reader.StartAsync()) ([Windows.Media.Capture.Frames.MediaFrameReaderStartStatus])
Write-Output ("E004AJ_FACEAUTH_START={0}" -f $status)
Get-SM $ctl 'after-start'
$frames=0;$deadline=[DateTime]::UtcNow.AddSeconds(4)
while([DateTime]::UtcNow -lt $deadline -and $frames -lt 12){$f=$reader.TryAcquireLatestFrame();if($null -ne $f){$frames++;Write-Output ("E004AJ_FACEAUTH_FRAME n={0} time={1}" -f $frames,$f.SystemRelativeTime);$f.Dispose()};Start-Sleep -Milliseconds 25}
Write-Output ("E004AJ_FACEAUTH_ACQUIRED={0}" -f $frames)
Get-SM $ctl 'during-stream'
Await-Action ($reader.StopAsync())
Write-Output 'E004AJ_FACEAUTH_STOP_PASS'
Get-SM $ctl 'after-stop'
$reader.Dispose();$mc.Dispose()
Write-Output 'E004AJ_FACEAUTH_END'
