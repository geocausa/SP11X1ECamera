# SPDX-License-Identifier: MIT
# One-use Windows daylight reference: front and rear cameras, OEM defaults, private NV12 frames.
$ErrorActionPreference='Stop'
$root=$PSScriptRoot
$identity='E-WINDOWS-DAYLIGHT-BOTH-20261011-01'
if($env:COMPUTERNAME -ne 'DESKTOP-AQ4SMTC'){throw 'exact SP11 Windows required'}
if($root -ne 'C:\Users\Geoca\Documents\SP11-Camera-WindowsDaylight-20261011-01'){throw 'exact fresh private root required'}
$marker=Join-Path $root 'CONSUMED.txt'
$fh=[IO.File]::Open($marker,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
try{$b=[Text.Encoding]::UTF8.GetBytes($identity+' '+[DateTimeOffset]::UtcNow.ToString('o'));$fh.Write($b,0,$b.Length);$fh.Flush($true)}finally{$fh.Dispose()}
& shutdown.exe /r /t 300 /c 'SP11 one-use daylight reference; return to Golden Linux'
if($LASTEXITCODE -ne 0){throw 'camera refused without return reboot watchdog'}
Add-Type -AssemblyName System.Runtime.WindowsRuntime
Add-Type -TypeDefinition @'
using System.IO;
public static class SP11DaylightSave01 {
 public static void SaveNew(byte[] d,string path){using(var f=new FileStream(path,FileMode.CreateNew,FileAccess.Write,FileShare.None)){f.Write(d,0,d.Length);f.Flush(true);}}
}
'@
foreach($type in @(
 'Windows.Graphics.Imaging.SoftwareBitmap,Windows.Graphics.Imaging,ContentType=WindowsRuntime',
 'Windows.Graphics.Imaging.BitmapPixelFormat,Windows.Graphics.Imaging,ContentType=WindowsRuntime',
 'Windows.Graphics.Imaging.BitmapBufferAccessMode,Windows.Graphics.Imaging,ContentType=WindowsRuntime',
 'Windows.Storage.Streams.Buffer,Windows.Storage.Streams,ContentType=WindowsRuntime',
 'Windows.Storage.Streams.DataReader,Windows.Storage.Streams,ContentType=WindowsRuntime',
 'Windows.Media.Capture.Frames.MediaFrameSourceGroup,Windows.Media.Capture.Frames,ContentType=WindowsRuntime',
 'Windows.Media.Capture.Frames.MediaFrameReader,Windows.Media.Capture.Frames,ContentType=WindowsRuntime',
 'Windows.Media.Capture.MediaCapture,Windows.Media.Capture,ContentType=WindowsRuntime',
 'Windows.Media.Capture.MediaCaptureInitializationSettings,Windows.Media.Capture,ContentType=WindowsRuntime',
 'Windows.Media.Capture.MediaCaptureMemoryPreference,Windows.Media.Capture,ContentType=WindowsRuntime',
 'Windows.Media.Capture.StreamingCaptureMode,Windows.Media.Capture,ContentType=WindowsRuntime',
 'Windows.Media.Capture.Frames.MediaFrameReaderStartStatus,Windows.Media.Capture.Frames,ContentType=WindowsRuntime')){[void][Type]::GetType($type,$true)}
function Await-Result($op,[Type]$type) {
 $m=[System.WindowsRuntimeSystemExtensions].GetMethods()|Where-Object {$_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1}|Select-Object -First 1
 $t=$m.MakeGenericMethod($type).Invoke($null,@($op));if(-not $t.Wait(30000)){throw 'WinRT result timeout'};return $t.Result
}
function Await-Action($op) {
 $m=[System.WindowsRuntimeSystemExtensions].GetMethods()|Where-Object {$_.Name -eq 'AsTask' -and -not $_.IsGenericMethod -and $_.GetParameters().Count -eq 1}|Select-Object -First 1
 $t=$m.Invoke($null,@($op));if(-not $t.Wait(30000)){throw 'WinRT action timeout'}
}
function Copy-Nv12($sb,[int]$w,[int]$h) {
 if($sb.BitmapPixelFormat.ToString() -ne 'Nv12' -or $sb.PixelWidth -ne $w -or $sb.PixelHeight -ne $h){throw "native ${w}x${h} NV12 geometry required"}
 $lock=$sb.LockBuffer([Windows.Graphics.Imaging.BitmapBufferAccessMode]::Read)
 try {
  $y=$lock.GetPlaneDescription(0);$uv=$lock.GetPlaneDescription(1)
  if($lock.GetPlaneCount() -ne 2 -or $y.StartIndex -ne 0 -or $y.Stride -ne $w -or $uv.StartIndex -ne $w*$h -or $uv.Stride -ne $w){throw 'NV12 exact plane layout mismatch'}
 }finally{$lock.Dispose()}
 $n=[uint32]($w*$h*3/2)
 $buffer=New-Object Windows.Storage.Streams.Buffer $n
 $sb.CopyToBuffer($buffer)
 if($buffer.Length -ne $n){throw 'exact copied NV12 extent required'}
 $bytes=New-Object byte[] $n
 $dr=[Windows.Storage.Streams.DataReader]::FromBuffer($buffer)
 try{$dr.ReadBytes($bytes)}finally{$dr.Dispose()}
 return $bytes
}
function Capture-Camera([string]$name,[string]$tag,[int]$w,[int]$h,[int]$keep) {
 $r=[ordered]@{camera=$name;width=$w;height=$h;status='STARTED';controls=@();saved=0;error=$null}
 $mc=$null;$reader=$null
 try {
  $groups=Await-Result ([Windows.Media.Capture.Frames.MediaFrameSourceGroup]::FindAllAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Media.Capture.Frames.MediaFrameSourceGroup]])
  $group=@($groups|Where-Object {$_.DisplayName -eq $name})
  if($group.Count -ne 1){throw "one exact source group required: $name"}
  $settings=New-Object Windows.Media.Capture.MediaCaptureInitializationSettings
  $settings.SourceGroup=$group[0];$settings.StreamingCaptureMode=[Windows.Media.Capture.StreamingCaptureMode]::Video;$settings.MemoryPreference=[Windows.Media.Capture.MediaCaptureMemoryPreference]::Cpu
  $mc=New-Object Windows.Media.Capture.MediaCapture;Await-Action ($mc.InitializeAsync($settings))
  $sources=@();foreach($entry in $mc.FrameSources){$v=$entry.Value;if($v -and $v.Info.SourceKind.ToString() -eq 'Color' -and $v.Info.MediaStreamType.ToString() -eq 'VideoRecord'){$sources+=$v}}
  if($sources.Count -ne 1){throw 'one recording source required'}
  $src=$sources[0]
  $formats=@($src.SupportedFormats | Where-Object {$_.Subtype -eq 'NV12' -and $_.VideoFormat.Width -eq $w -and $_.VideoFormat.Height -eq $h} | Sort-Object {[double]$_.FrameRate.Numerator/[double]$_.FrameRate.Denominator} -Descending)
  if($formats.Count -lt 1){throw "no ${w}x${h} NV12 format"}
  Await-Action ($src.SetFormatAsync($formats[0]))
  $vf=$src.CurrentFormat.VideoFormat
  if($src.CurrentFormat.Subtype -ne 'NV12' -or $vf.Width -ne $w -or $vf.Height -ne $h){throw 'format drift'}
  $r.fps_num=$src.CurrentFormat.FrameRate.Numerator;$r.fps_den=$src.CurrentFormat.FrameRate.Denominator
  $reader=Await-Result ($mc.CreateFrameReaderAsync($src)) ([Windows.Media.Capture.Frames.MediaFrameReader])
  $status=Await-Result ($reader.StartAsync()) ([Windows.Media.Capture.Frames.MediaFrameReaderStartStatus])
  if($status.ToString() -ne 'Success'){throw 'reader start failed'}
  Start-Sleep -Seconds 6
  $seen=New-Object 'System.Collections.Generic.HashSet[long]';$clock=[Diagnostics.Stopwatch]::StartNew()
  while($r.saved -lt $keep -and $clock.Elapsed.TotalSeconds -lt 30) {
   $f=$reader.TryAcquireLatestFrame()
   if($f) {
    $sb=$null
    try {
     $t=$f.SystemRelativeTime
     $ticks=if($null -ne $t.Ticks){[long]$t.Ticks}else{[long]$t.Value.Ticks}
     if($seen.Add($ticks)) {
      $sb=$f.VideoMediaFrame.SoftwareBitmap;if(-not $sb){throw 'CPU SoftwareBitmap missing'}
      $bytes=Copy-Nv12 $sb $w $h
      [SP11DaylightSave01]::SaveNew($bytes,(Join-Path $root ($tag+'-frame-'+$r.saved+'.nv12')))
      [Array]::Clear($bytes,0,$bytes.Length)
      $ctl=[ordered]@{sample=$r.saved;ticks=$ticks;utc=[DateTimeOffset]::UtcNow.ToString('o')}
      $ec=$mc.VideoDeviceController.ExposureControl
      if($ec.Supported){$ctl.exposure_auto=$ec.Auto;$ctl.exposure_ticks=$ec.Value.Ticks}
      $ic=$mc.VideoDeviceController.IsoSpeedControl
      if($ic.Supported){$ctl.iso_auto=$ic.Auto;$ctl.iso=$ic.Value}
      $wc=$mc.VideoDeviceController.WhiteBalanceControl
      if($wc.Supported){$ctl.wb_auto=$wc.Auto;$ctl.wb_kelvin=$wc.Value}
      $r.controls+=[pscustomobject]$ctl
      $r.saved++
     }
    }finally{if($sb){$sb.Dispose()};$f.Dispose()}
   }
   Start-Sleep -Milliseconds 300
  }
  if($r.saved -ne $keep){throw "only $($r.saved) of $keep frames"}
  Await-Action ($reader.StopAsync());$reader.Dispose();$reader=$null;$mc.Dispose();$mc=$null
  $r.status='PASS'
 }catch{$r.status='FAIL';$r.error=$_.Exception.Message}
 finally{
  if($reader){try{Await-Action ($reader.StopAsync())}catch{};try{$reader.Dispose()}catch{}}
  if($mc){try{$mc.Dispose()}catch{}}
 }
 return [pscustomobject]$r
}
$out=[ordered]@{identity=$identity;started_utc=[DateTimeOffset]::UtcNow.ToString('o');cameras=@()}
$out.cameras+=Capture-Camera 'Surface Camera Front' 'front' 2560 1440 6
Start-Sleep -Seconds 2
$out.cameras+=Capture-Camera 'Surface Camera Rear' 'rear' 3840 2160 6
Start-Sleep -Seconds 2
$out.cameras+=Capture-Camera 'Surface Camera Front' 'front2' 2560 1440 3
$out.finished_utc=[DateTimeOffset]::UtcNow.ToString('o')
$json=$out|ConvertTo-Json -Depth 10
$path=Join-Path $root 'RESULT.json';$fh=[IO.File]::Open($path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
try{$b=[Text.Encoding]::UTF8.GetBytes($json);$fh.Write($b,0,$b.Length);$fh.Flush($true)}finally{$fh.Dispose()}
Write-Output $json
