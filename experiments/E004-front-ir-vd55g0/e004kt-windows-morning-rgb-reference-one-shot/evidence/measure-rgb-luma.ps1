param([switch]$OfflineTest)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[void][Windows.Graphics.Imaging.SoftwareBitmap,Windows.Graphics.Imaging,ContentType=WindowsRuntime]
[void][Windows.Graphics.Imaging.BitmapPixelFormat,Windows.Graphics.Imaging,ContentType=WindowsRuntime]
[void][Windows.Graphics.Imaging.BitmapBufferAccessMode,Windows.Graphics.Imaging,ContentType=WindowsRuntime]
[void][Windows.Storage.Streams.Buffer,Windows.Storage.Streams,ContentType=WindowsRuntime]
[void][Windows.Storage.Streams.DataReader,Windows.Storage.Streams,ContentType=WindowsRuntime]
Add-Type -TypeDefinition @'
public static class E004ktYStats {
 public static double[] Summarize(byte[] data,int width,int height) {
  if(width<=0 || height<=0 || (long)width*height>data.Length) throw new System.ArgumentException("invalid luma geometry");
  long sum=0,n=0,zero=0,white=0;int min=255,max=0;
  for(int y=0;y<height;y++) for(int x=0;x<width;x+=64) {
   int v=data[y*width+x];sum+=v;n++;if(v<min)min=v;if(v>max)max=v;if(v==0)zero++;if(v==255)white++;
  }
  return new double[]{(double)sum/n,min,max,(double)zero/n,(double)white/n,n};
 }
}
'@
function Measure-Luma($sb) {
 if($sb.BitmapPixelFormat.ToString() -ne 'Nv12'){throw 'expected native NV12'}
 $w=[int]$sb.PixelWidth;$h=[int]$sb.PixelHeight
 $lock=$sb.LockBuffer([Windows.Graphics.Imaging.BitmapBufferAccessMode]::Read)
 try {
  if($lock.GetPlaneCount() -ne 2){throw 'expected two NV12 planes'}
  $y=$lock.GetPlaneDescription(0);$uv=$lock.GetPlaneDescription(1)
  if($y.StartIndex -ne 0 -or $y.Stride -ne $w -or $y.Width -ne $w -or $y.Height -ne $h){throw 'unsupported luma layout; no guessed stride'}
  $capacity=[uint32][Math]::Max($w*$h*3/2,$uv.StartIndex+$uv.Stride*$uv.Height)
 } finally {$lock.Dispose()}
 $buffer=New-Object Windows.Storage.Streams.Buffer $capacity
 $sb.CopyToBuffer($buffer)
 if($buffer.Length -lt ($w*$h)){throw 'short CPU buffer'}
 $bytes=New-Object byte[] ([int]$buffer.Length)
 $dr=[Windows.Storage.Streams.DataReader]::FromBuffer($buffer)
 try {$dr.ReadBytes($bytes)} finally {$dr.Dispose()}
 $a=[E004ktYStats]::Summarize($bytes,$w,$h)
 [Array]::Clear($bytes,0,$bytes.Length)
 return [pscustomobject]@{width=$w;height=$h;format='NV12';y_mean=$a[0];y_min=$a[1];y_max=$a[2];y_zero_fraction=$a[3];y_255_fraction=$a[4];sampled_values=$a[5];horizontal_stride=64;all_rows=$true}
}
if($OfflineTest) {
 $bytes=New-Object byte[] 128
 for($i=0;$i -lt $bytes.Length;$i++){$bytes[$i]=37}
 $a=[E004ktYStats]::Summarize($bytes,64,2)
 if($a[0] -ne 37 -or $a[1] -ne 37 -or $a[2] -ne 37 -or $a[5] -ne 2){throw 'numeric test failed'}
 $sb=New-Object Windows.Graphics.Imaging.SoftwareBitmap ([Windows.Graphics.Imaging.BitmapPixelFormat]::Nv12),1920,1080
 try {$v=Measure-Luma $sb;if($v.width -ne 1920 -or $v.sampled_values -ne 32400){throw 'synthetic WinRT layout test failed'}} finally {$sb.Dispose()}
 Write-Output 'E004KT_OFFLINE_TEST=PASS CAMERA_ACTIVATED=NO'
 exit 0
}
if($env:COMPUTERNAME -ne 'DESKTOP-AQ4SMTC'){throw 'E004kt only authorized SP11 Windows host'}
$root=Split-Path -Parent $MyInvocation.MyCommand.Path
$marker=Join-Path $root 'CONSUMED.txt'
$fh=[IO.File]::Open($marker,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
try {$b=[Text.Encoding]::UTF8.GetBytes('E004kt single attempt; never rerun');$fh.Write($b,0,$b.Length)}finally{$fh.Dispose()}
& shutdown.exe /r /t 240 /c 'SP11 E004kt bounded RGB reference; return to protected Golden Linux'
if($LASTEXITCODE -ne 0){throw 'could not establish bounded return reboot; refusing cameras'}
function Await-Result($op,[Type]$type) {
 $m=[System.WindowsRuntimeSystemExtensions].GetMethods()|Where-Object {$_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1}|Select-Object -First 1
 $t=$m.MakeGenericMethod($type).Invoke($null,@($op));if(-not $t.Wait(30000)){throw 'WinRT result timeout'};return $t.Result
}
function Await-Action($op) {
 $m=[System.WindowsRuntimeSystemExtensions].GetMethods()|Where-Object {$_.Name -eq 'AsTask' -and -not $_.IsGenericMethod -and $_.GetParameters().Count -eq 1}|Select-Object -First 1
 $t=$m.Invoke($null,@($op));if(-not $t.Wait(30000)){throw 'WinRT action timeout'}
}
[void][Windows.Media.Capture.Frames.MediaFrameSourceGroup,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameReader,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCapture,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCaptureInitializationSettings,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCaptureMemoryPreference,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.StreamingCaptureMode,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameReaderStartStatus,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
$records=New-Object 'System.Collections.Generic.List[object]'
try {
 $groups=Await-Result ([Windows.Media.Capture.Frames.MediaFrameSourceGroup]::FindAllAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Media.Capture.Frames.MediaFrameSourceGroup]])
 foreach($name in @('Surface Camera Front','Surface Camera Rear')) {
  $mc=$null;$reader=$null
  $row=[ordered]@{camera=$name;status='FAIL';samples=@();exposure_auto=$null;exposure_ticks=$null;white_balance_auto=$null;white_balance_kelvin=$null;error=$null}
  try {
   $group=$groups|Where-Object {$_.DisplayName -eq $name}|Select-Object -First 1
   if(-not $group){throw 'missing exact RGB source group'}
   $settings=New-Object Windows.Media.Capture.MediaCaptureInitializationSettings
   $settings.SourceGroup=$group;$settings.StreamingCaptureMode=[Windows.Media.Capture.StreamingCaptureMode]::Video;$settings.MemoryPreference=[Windows.Media.Capture.MediaCaptureMemoryPreference]::Cpu
   $mc=New-Object Windows.Media.Capture.MediaCapture;Await-Action ($mc.InitializeAsync($settings))
   $sources=@();foreach($entry in $mc.FrameSources){$v=$entry.Value;if($v -and $v.Info.SourceKind.ToString() -eq 'Color' -and $v.Info.MediaStreamType.ToString() -eq 'VideoRecord'){$sources+=$v}}
   if($sources.Count -ne 1){throw 'expected one RGB recording source'}
   $src=$sources[0];$vf=$src.CurrentFormat.VideoFormat
   $expectedW=if($name -eq 'Surface Camera Front'){1920}else{3840};$expectedH=if($expectedW -eq 1920){1080}else{2160}
   if($src.CurrentFormat.Subtype -ne 'NV12' -or $vf.Width -ne $expectedW -or $vf.Height -ne $expectedH){throw 'default RGB recording format drift'}
   $reader=Await-Result ($mc.CreateFrameReaderAsync($src)) ([Windows.Media.Capture.Frames.MediaFrameReader])
   $status=Await-Result ($reader.StartAsync()) ([Windows.Media.Capture.Frames.MediaFrameReaderStartStatus])
   if($status.ToString() -ne 'Success'){throw 'RGB reader start failed'}
   Start-Sleep -Seconds 2
   for($i=0;$i -lt 8;$i++) {
    $f=$reader.TryAcquireLatestFrame()
    if(-not $f){throw 'missing RGB frame'}
    try {
     $sb=$f.VideoMediaFrame.SoftwareBitmap;if(-not $sb){throw 'missing CPU SoftwareBitmap'}
     $row.samples+=Measure-Luma $sb
    }finally{$f.Dispose()}
    Start-Sleep -Milliseconds 500
   }
   $ec=$mc.VideoDeviceController.ExposureControl
   if($ec.Supported){$row.exposure_auto=$ec.Auto;$row.exposure_ticks=$ec.Value.Ticks}
   $wc=$mc.VideoDeviceController.WhiteBalanceControl
   if($wc.Supported){$row.white_balance_auto=$wc.Auto;$row.white_balance_kelvin=$wc.Value}
   $row.status='PASS'
  }catch{$row.error=$_.Exception.Message}
  finally {
   if($reader){try{Await-Action ($reader.StopAsync())}catch{};try{$reader.Dispose()}catch{}}
   if($mc){try{$mc.Dispose()}catch{}}
  }
  $records.Add([pscustomobject]$row)
 }
}finally {
 $out=[pscustomobject]@{experiment='E004kt';kind='Windows RGB numeric luminance only';pixel_files_or_hashes_exported=$false;ir_activated=$false;controls_modified=$false;scene_controlled_or_matched=$false;frame_uniqueness_or_fps_proven=$false;results=@($records.ToArray());automatic_return_reboot_scheduled=$true}
 $json=$out|ConvertTo-Json -Depth 10
 [IO.File]::WriteAllText((Join-Path $root 'RESULT.json'),$json,[Text.Encoding]::UTF8)
 Write-Output $json
}
