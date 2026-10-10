
# SPDX-License-Identifier: MIT
param([switch]$OfflineTest)
$ErrorActionPreference='Stop'
$root=$PSScriptRoot
$identity='E-WINDOWS-FRONT-QUALITY-20261010-08'
if(-not $OfflineTest) {
 if($env:COMPUTERNAME -ne 'DESKTOP-AQ4SMTC'){throw 'exact SP11 Windows required'}
 if($root -ne 'C:\Users\Geoca\Documents\SP11-Camera-WindowsFrontQuality-20261010-08'){throw 'exact fresh private root required'}
 $marker=Join-Path $root 'CONSUMED.txt'
 $fh=[IO.File]::Open($marker,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
 try{$b=[Text.Encoding]::UTF8.GetBytes($identity+' '+[DateTimeOffset]::UtcNow.ToString('o'));$fh.Write($b,0,$b.Length);$fh.Flush($true)}finally{$fh.Dispose()}
 & shutdown.exe /r /t 300 /c 'SP11 one-use front quality oracle; return to protected Golden Linux'
 if($LASTEXITCODE -ne 0){throw 'camera refused without return reboot watchdog'}
}
Add-Type -AssemblyName System.Runtime.WindowsRuntime
foreach($type in @(
 'Windows.Graphics.Imaging.SoftwareBitmap,Windows.Graphics.Imaging,ContentType=WindowsRuntime',
 'Windows.Graphics.Imaging.BitmapPixelFormat,Windows.Graphics.Imaging,ContentType=WindowsRuntime',
 'Windows.Graphics.Imaging.BitmapBufferAccessMode,Windows.Graphics.Imaging,ContentType=WindowsRuntime',
 'Windows.Storage.Streams.Buffer,Windows.Storage.Streams,ContentType=WindowsRuntime',
 'Windows.Storage.Streams.DataReader,Windows.Storage.Streams,ContentType=WindowsRuntime')){[void][Type]::GetType($type,$true)}
Add-Type -Path (Join-Path $root 'native-metrics.cs')
function Copy-NativeNv12($sb) {
 if($sb.BitmapPixelFormat.ToString() -ne 'Nv12' -or $sb.PixelWidth -ne 2560 -or $sb.PixelHeight -ne 1440){throw 'native 2560x1440 NV12 geometry required'}
 $lock=$sb.LockBuffer([Windows.Graphics.Imaging.BitmapBufferAccessMode]::Read)
 try {
  if($lock.GetPlaneCount() -ne 2){throw 'exact NV12 two planes required'}
  $y=$lock.GetPlaneDescription(0);$uv=$lock.GetPlaneDescription(1)
  if($y.StartIndex -ne 0 -or $y.Stride -ne 2560 -or $y.Width -ne 2560 -or $y.Height -ne 1440 -or $uv.StartIndex -ne 3686400 -or $uv.Stride -ne 2560 -or $uv.Width -ne 1280 -or $uv.Height -ne 720){throw 'NV12 exact plane layout mismatch'}
 }finally{$lock.Dispose()}
 $buffer=New-Object Windows.Storage.Streams.Buffer ([uint32]5529600)
 $sb.CopyToBuffer($buffer)
 if($buffer.Length -ne 5529600){throw 'exact copied NV12 extent required'}
 $bytes=New-Object byte[] 5529600
 $dr=[Windows.Storage.Streams.DataReader]::FromBuffer($buffer)
 try{$dr.ReadBytes($bytes)}finally{$dr.Dispose()}
 return [pscustomobject]@{bytes=$bytes;stats=[SP11WindowsFrontQualityStats02]::Summarize($bytes,2560,1440)}
}
function Scalar-Stats($a) {
 $r=[ordered]@{}
 foreach($pair in @(@('Y',0),@('U',7),@('V',14))) {
  $off=[int]$pair[1]
  $r[$pair[0]]=[ordered]@{min=$a[$off];max=$a[$off+1];mean=$a[$off+2];std=$a[$off+3];p01=$a[$off+4];p50=$a[$off+5];p99=$a[$off+6]}
 }
 $r.at_or_below_video_black_fraction=$a[21];$r.at_or_above_video_white_fraction=$a[22]
 $r.horizontal_adjacent_luma_difference_mean=$a[23];$r.vertical_adjacent_luma_difference_mean=$a[24]
 return $r
}
if($OfflineTest) {
 [SP11WindowsFrontQualityStats02]::SelfTest()
 $sb=New-Object Windows.Graphics.Imaging.SoftwareBitmap ([Windows.Graphics.Imaging.BitmapPixelFormat]::Nv12),2560,1440
 try{$v=Copy-NativeNv12 $sb;if($v.bytes.Length -ne 5529600){throw 'synthetic WinRT copy'};[Array]::Clear($v.bytes,0,$v.bytes.Length)}finally{$sb.Dispose()}
 $e=$null;$tokens=$null
 [void][System.Management.Automation.Language.Parser]::ParseFile($PSCommandPath,[ref]$tokens,[ref]$e)
 if($e.Count -ne 0){throw 'PowerShell syntax errors'}
 Write-Output 'PASS_WINDOWS_NATIVE_NV12_SYNTHETIC_WINRT_COPY_NO_CAMERA'
 exit 0
}
function Await-Result($op,[Type]$type) {
 $m=[System.WindowsRuntimeSystemExtensions].GetMethods()|Where-Object {$_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1}|Select-Object -First 1
 $t=$m.MakeGenericMethod($type).Invoke($null,@($op));if(-not $t.Wait(30000)){throw 'WinRT result timeout'};return $t.Result
}
function Await-Action($op) {
 $m=[System.WindowsRuntimeSystemExtensions].GetMethods()|Where-Object {$_.Name -eq 'AsTask' -and -not $_.IsGenericMethod -and $_.GetParameters().Count -eq 1}|Select-Object -First 1
 $t=$m.Invoke($null,@($op));if(-not $t.Wait(30000)){throw 'WinRT action timeout'}
}
foreach($type in @(
 'Windows.Media.Capture.Frames.MediaFrameSourceGroup,Windows.Media.Capture.Frames,ContentType=WindowsRuntime',
 'Windows.Media.Capture.Frames.MediaFrameReader,Windows.Media.Capture.Frames,ContentType=WindowsRuntime',
 'Windows.Media.Capture.MediaCapture,Windows.Media.Capture,ContentType=WindowsRuntime',
 'Windows.Media.Capture.MediaCaptureInitializationSettings,Windows.Media.Capture,ContentType=WindowsRuntime',
 'Windows.Media.Capture.MediaCaptureMemoryPreference,Windows.Media.Capture,ContentType=WindowsRuntime',
 'Windows.Media.Capture.StreamingCaptureMode,Windows.Media.Capture,ContentType=WindowsRuntime',
 'Windows.Media.Capture.Frames.MediaFrameReaderStartStatus,Windows.Media.Capture.Frames,ContentType=WindowsRuntime')){[void][Type]::GetType($type,$true)}
$mc=$null;$reader=$null;$saved=New-Object 'System.Collections.Generic.List[object]'
$out=[ordered]@{identity=$identity;status='STARTED';camera='Surface Camera Front';width=2560;height=1440;format='native_NV12';samples=@();controls=@();captured_utc=$null;error=$null;clean_stop_release=$false;private_native_frames_saved=0;pixel_bytes_or_hashes_exported=$false;controls_modified=$false;ir_activated=$false;automatic_return_reboot_scheduled=$true;scene_stability_or_ambient_lux_verified=$false;visual_or_Windows_Linux_parity_qualified=$false;percentile_method='full_frame_histogram_floor_rank';color_space='unspecified'}
try {
 $groups=Await-Result ([Windows.Media.Capture.Frames.MediaFrameSourceGroup]::FindAllAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Media.Capture.Frames.MediaFrameSourceGroup]])
 $group=@($groups|Where-Object {$_.DisplayName -eq 'Surface Camera Front'})
 if($group.Count -ne 1){throw 'one exact front source group required'}
 $settings=New-Object Windows.Media.Capture.MediaCaptureInitializationSettings
 $settings.SourceGroup=$group[0];$settings.StreamingCaptureMode=[Windows.Media.Capture.StreamingCaptureMode]::Video;$settings.MemoryPreference=[Windows.Media.Capture.MediaCaptureMemoryPreference]::Cpu
 $mc=New-Object Windows.Media.Capture.MediaCapture;Await-Action ($mc.InitializeAsync($settings))
 $sources=@();foreach($entry in $mc.FrameSources){$v=$entry.Value;if($v -and $v.Info.SourceKind.ToString() -eq 'Color' -and $v.Info.MediaStreamType.ToString() -eq 'VideoRecord'){$sources+=$v}}
 if($sources.Count -ne 1){throw 'one front recording source required'}
 $src=$sources[0]
 $formats=@($src.SupportedFormats | Where-Object {
   $_.Subtype -eq 'NV12' -and $_.VideoFormat.Width -eq 2560 -and
   $_.VideoFormat.Height -eq 1440 -and $_.FrameRate.Numerator -eq 30 -and
   $_.FrameRate.Denominator -eq 1 })
 if($formats.Count -ne 1){throw 'one exact front2560x1440 NV12 30/1 format required'}
 Await-Action ($src.SetFormatAsync($formats[0]))
 $vf=$src.CurrentFormat.VideoFormat
 if($src.CurrentFormat.Subtype -ne 'NV12' -or $vf.Width -ne 2560 -or $vf.Height -ne 1440){throw 'OEM default 2560x1440 NV12 drift'}
 $out.fps_num=$src.CurrentFormat.FrameRate.Numerator;$out.fps_den=$src.CurrentFormat.FrameRate.Denominator
 $reader=Await-Result ($mc.CreateFrameReaderAsync($src)) ([Windows.Media.Capture.Frames.MediaFrameReader])
 $status=Await-Result ($reader.StartAsync()) ([Windows.Media.Capture.Frames.MediaFrameReaderStartStatus])
 if($status.ToString() -ne 'Success'){throw 'OEM front reader start failed'}
 Start-Sleep -Seconds 5
 $seen=New-Object 'System.Collections.Generic.HashSet[long]';$clock=[Diagnostics.Stopwatch]::StartNew()
 while($out.samples.Count -lt 8 -and $clock.Elapsed.TotalSeconds -lt 25) {
  $f=$reader.TryAcquireLatestFrame()
  if($f) {
   $sb=$null;$capture=$null
   try {
    $t=$f.SystemRelativeTime
    if($null -eq $t){throw 'unique frame timestamp required'}
    $ticks=if($null -ne $t.Ticks){[long]$t.Ticks}else{[long]$t.Value.Ticks}
    if($seen.Add($ticks)) {
     $sb=$f.VideoMediaFrame.SoftwareBitmap;if(-not $sb){throw 'OEM CPU SoftwareBitmap missing'}
     $capture=Copy-NativeNv12 $sb
     $index=$out.samples.Count
     $row=Scalar-Stats $capture.stats;$row.sequence=$index;$row.system_relative_ticks=$ticks;$row.captured_utc=[DateTimeOffset]::UtcNow.ToString('o')
     $out.samples+= [pscustomobject]$row
     $ctl=[ordered]@{sample=$index;exposure_supported=$false;iso_supported=$false;white_balance_supported=$false}
     $ec=$mc.VideoDeviceController.ExposureControl
     if($ec.Supported){$ctl.exposure_supported=$true;$ctl.exposure_auto=$ec.Auto;$ctl.exposure_nominal_ticks=$ec.Value.Ticks}
     $ic=$mc.VideoDeviceController.IsoSpeedControl
     if($ic.Supported){$ctl.iso_supported=$true;$ctl.iso_auto=$ic.Auto;$ctl.iso_nominal_value=$ic.Value}
     $wc=$mc.VideoDeviceController.WhiteBalanceControl
     if($wc.Supported){$ctl.white_balance_supported=$true;$ctl.white_balance_auto=$wc.Auto;$ctl.white_balance_nominal_kelvin=$wc.Value}
     $out.controls+=[pscustomobject]$ctl
     if($index -in @(1,4,7)){$saved.Add([pscustomobject]@{sequence=$index;bytes=$capture.bytes});$capture=$null}
    }
   }finally{if($capture){[Array]::Clear($capture.bytes,0,$capture.bytes.Length)};if($sb){$sb.Dispose()};$f.Dispose()}
  }
  Start-Sleep -Milliseconds 500
 }
 if($out.samples.Count -ne 8 -or $saved.Count -ne 3){throw 'eight unique samples and three private snapshots required'}
 Await-Action ($reader.StopAsync());$reader.Dispose();$reader=$null;$mc.Dispose();$mc=$null;$out.clean_stop_release=$true
 foreach($frame in $saved){[SP11WindowsFrontQualityStats02]::SaveNew($frame.bytes,(Join-Path $root ('frame-'+$frame.sequence+'.nv12')))}
 $out.private_native_frames_saved=3;$out.captured_utc=[DateTimeOffset]::UtcNow.ToString('o');$out.status='PASS_WINDOWS_FRONT_NATIVE_NV12_PRIVATE_CAPTURE'
}catch{$out.status='FAIL_WINDOWS_FRONT_NATIVE_NV12_PRIVATE_CAPTURE';$out.error=$_.Exception.Message}
finally {
 if($reader){try{Await-Action ($reader.StopAsync())}catch{};try{$reader.Dispose()}catch{}}
 if($mc){try{$mc.Dispose()}catch{}}
 foreach($frame in $saved){[Array]::Clear($frame.bytes,0,$frame.bytes.Length)}
 $json=$out|ConvertTo-Json -Depth 10
 $path=Join-Path $root 'RESULT.json';$fh=[IO.File]::Open($path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
 try{$b=[Text.Encoding]::UTF8.GetBytes($json);$fh.Write($b,0,$b.Length);$fh.Flush($true)}finally{$fh.Dispose()}
 Write-Output $json
}
if($out.status -ne 'PASS_WINDOWS_FRONT_NATIVE_NV12_PRIVATE_CAPTURE'){exit 1}
