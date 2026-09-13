$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[void][Windows.Media.Capture.Frames.MediaFrameSourceGroup,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCapture,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCaptureInitializationSettings,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.StreamingCaptureMode,Windows.Media.Capture,ContentType=WindowsRuntime]
function Await-Op($op,[Type]$type){$m=[System.WindowsRuntimeSystemExtensions].GetMethods()|?{$_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1}|select -First 1;$t=$m.MakeGenericMethod($type).Invoke($null,@($op));$t.Wait();$t.Result}
function Await-Action($op){$m=[System.WindowsRuntimeSystemExtensions].GetMethods()|?{$_.Name -eq 'AsTask' -and -not $_.IsGenericMethod -and $_.GetParameters().Count -eq 1}|select -First 1;$t=$m.Invoke($null,@($op));$t.Wait()}
function Put-U32([byte[]]$b,[int]$o,[uint32]$v){[Array]::Copy([BitConverter]::GetBytes($v),0,$b,$o,4)}
function New-KsProperty([uint32]$id,[uint32]$flags){$b=New-Object byte[] 24;$g=([Guid]'1CB79112-C0D2-4213-9CA6-CD4FDB927972').ToByteArray();[Array]::Copy($g,0,$b,0,16);Put-U32 $b 16 $id;Put-U32 $b 20 $flags;return $b}
$groups=Await-Op ([Windows.Media.Capture.Frames.MediaFrameSourceGroup]::FindAllAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Media.Capture.Frames.MediaFrameSourceGroup]])
$idx=0
foreach($g in $groups){
  Write-Output ("E004AJ_GROUP_ENUM idx={0} name={1} id={2}" -f $idx,$g.DisplayName,$g.Id)
  foreach($si in $g.SourceInfos){ Write-Output ("  SOURCE kind={0} stream={1} dev={2} id={3}" -f $si.SourceKind,$si.MediaStreamType,$si.DeviceInformation.Name,$si.Id) }
  $settings=New-Object Windows.Media.Capture.MediaCaptureInitializationSettings
  $settings.SourceGroup=$g
  $settings.StreamingCaptureMode=[Windows.Media.Capture.StreamingCaptureMode]::Video
  $mc=New-Object Windows.Media.Capture.MediaCapture
  try {
    Await-Action ($mc.InitializeAsync($settings))
    $ctl=$mc.VideoDeviceController
    $p=New-KsProperty 36 1
    [Nullable[uint32]]$max=128
    try {
      $r=$ctl.GetDevicePropertyByExtendedId($p,$max)
      $hex=''
      if($null -ne $r.Value){try{$a=[byte[]]$r.Value;$hex=(($a|%{$_.ToString('x2')}) -join '')}catch{$hex='<'+$r.Value.GetType().FullName+'>'}}
      Write-Output ("  SECURE36 controller={0} status={1} value={2}" -f $ctl.Id,$r.Status,$hex)
    } catch { Write-Output ("  SECURE36 controller={0} EX={1}" -f $ctl.Id,$_.Exception.Message) }
  } catch { Write-Output ("  INIT_FAIL {0}" -f $_.Exception.Message) }
  finally { if($null -ne $mc){$mc.Dispose()} }
  $idx++
}
