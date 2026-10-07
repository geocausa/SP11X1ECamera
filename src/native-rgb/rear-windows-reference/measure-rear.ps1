param([switch]$OfflineTest)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[void][Windows.Graphics.Imaging.SoftwareBitmap,Windows.Graphics.Imaging,ContentType=WindowsRuntime]
[void][Windows.Graphics.Imaging.BitmapPixelFormat,Windows.Graphics.Imaging,ContentType=WindowsRuntime]
[void][Windows.Graphics.Imaging.BitmapBufferAccessMode,Windows.Graphics.Imaging,ContentType=WindowsRuntime]
[void][Windows.Storage.Streams.Buffer,Windows.Storage.Streams,ContentType=WindowsRuntime]
[void][Windows.Storage.Streams.DataReader,Windows.Storage.Streams,ContentType=WindowsRuntime]
Add-Type -TypeDefinition @'
public static class NativeRearScreen01YStats {
 public static double[] Summarize(byte[] data,int width,int height) {
  if(width<=0 || height<=0 || (long)width*height>data.Length) throw new System.ArgumentException("invalid luma geometry");
  long sum=0,n=0,zero=0,white=0;int min=255,max=0;long[] hist=new long[256];
  for(int y=0;y<height;y++) for(int x=0;x<width;x+=64) {
   int v=data[y*width+x];sum+=v;n++;hist[v]++;if(v<min)min=v;if(v>max)max=v;if(v==0)zero++;if(v==255)white++;
  }
  double[] p=new double[3];int[] ranks=new int[]{50,95,99};
  for(int k=0;k<3;k++){long acc=0,target=(n*ranks[k]+99)/100;for(int v=0;v<256;v++){acc+=hist[v];if(acc>=target){p[k]=v;break;}}}
  return new double[]{(double)sum/n,min,max,(double)zero/n,(double)white/n,n,p[0],p[1],p[2]};
 }
 public static void SavePrivate(byte[] data,int width,int height,string path) {
  if(data.Length!=(long)width*height*3/2)throw new System.ArgumentException("unexpected NV12 extent");
  using(var f=new System.IO.FileStream(path,System.IO.FileMode.CreateNew,System.IO.FileAccess.Write,System.IO.FileShare.None)){f.Write(data,0,data.Length);f.Flush(true);}
 }
 public static void SaveNativeY(byte[] data,int width,int height,string path) {
  using(var f=new System.IO.FileStream(path,System.IO.FileMode.CreateNew,System.IO.FileAccess.Write,System.IO.FileShare.None)){
   byte[] hdr=System.Text.Encoding.ASCII.GetBytes("P5\n"+width+" "+height+"\n255\n");f.Write(hdr,0,hdr.Length);f.Write(data,0,width*height);f.Flush(true);
  }
 }
}
'@
function Measure-Luma($sb,[string]$PrivateRawPath=$null,[string]$PrivateYPath=$null) {
 if($sb.BitmapPixelFormat.ToString() -ne 'Nv12'){throw 'expected native NV12'}
 $w=[int]$sb.PixelWidth;$h=[int]$sb.PixelHeight
 $lock=$sb.LockBuffer([Windows.Graphics.Imaging.BitmapBufferAccessMode]::Read)
 try {
  if($lock.GetPlaneCount() -ne 2){throw 'expected two NV12 planes'}
  $y=$lock.GetPlaneDescription(0);$uv=$lock.GetPlaneDescription(1)
  if($uv.StartIndex -ne ($w*$h) -or $uv.Stride -ne $w -or $uv.Height -ne ($h/2)){throw 'unsupported UV layout; no guessed chroma geometry'}
  if($y.StartIndex -ne 0 -or $y.Stride -ne $w -or $y.Width -ne $w -or $y.Height -ne $h){throw 'unsupported luma layout; no guessed stride'}
  $capacity=[uint32][Math]::Max($w*$h*3/2,$uv.StartIndex+$uv.Stride*$uv.Height)
 } finally {$lock.Dispose()}
 $buffer=New-Object Windows.Storage.Streams.Buffer $capacity
 $sb.CopyToBuffer($buffer)
 if($buffer.Length -ne ($w*$h*3/2)){throw 'unexpected native NV12 buffer extent'}
 $bytes=New-Object byte[] ([int]$buffer.Length)
 $dr=[Windows.Storage.Streams.DataReader]::FromBuffer($buffer)
 try {$dr.ReadBytes($bytes)} finally {$dr.Dispose()}
 try {
  $a=[NativeRearScreen01YStats]::Summarize($bytes,$w,$h)
  if($PrivateRawPath){[NativeRearScreen01YStats]::SavePrivate($bytes,$w,$h,$PrivateRawPath)}
  if($PrivateYPath){[NativeRearScreen01YStats]::SaveNativeY($bytes,$w,$h,$PrivateYPath)}
 }finally{[Array]::Clear($bytes,0,$bytes.Length)}
 return [pscustomobject]@{width=$w;height=$h;format='NV12';y_mean=$a[0];y_min=$a[1];y_max=$a[2];y_zero_fraction=$a[3];y_255_fraction=$a[4];sampled_values=$a[5];y_p50=$a[6];y_p95=$a[7];y_p99=$a[8];buffer_bytes=[int]$buffer.Length;y_start=$y.StartIndex;y_stride=$y.Stride;uv_start=$uv.StartIndex;uv_stride=$uv.Stride;uv_width=$uv.Width;uv_height=$uv.Height;horizontal_stride=64;all_rows=$true}
}
if($OfflineTest) {
 $bytes=New-Object byte[] 128
 for($i=0;$i -lt $bytes.Length;$i++){$bytes[$i]=37}
 $a=[NativeRearScreen01YStats]::Summarize($bytes,64,2)
 if($a[6] -ne 37 -or $a[7] -ne 37 -or $a[8] -ne 37 -or $a[0] -ne 37 -or $a[1] -ne 37 -or $a[2] -ne 37 -or $a[5] -ne 2){throw 'numeric test failed'}
 $sb=New-Object Windows.Graphics.Imaging.SoftwareBitmap ([Windows.Graphics.Imaging.BitmapPixelFormat]::Nv12),1920,1080
 try {$v=Measure-Luma $sb;if($v.width -ne 1920 -or $v.sampled_values -ne 32400){throw 'synthetic WinRT layout test failed'}} finally {$sb.Dispose()}
 $dummy=New-Object byte[] (3840*2160*3/2)
 $raw=Join-Path $env:TEMP ('SP11-REAR-SYNTHETIC-'+[guid]::NewGuid()+'.nv12')
 $pgm=$raw+'.pgm'
 try{
  [NativeRearScreen01YStats]::SavePrivate($dummy,3840,2160,$raw)
  [NativeRearScreen01YStats]::SaveNativeY($dummy,3840,2160,$pgm)
  if((Get-Item -LiteralPath $raw).Length -ne 12441600){throw 'private raw size test failed'}
  if((Get-Item -LiteralPath $pgm).Length -ne (8294400+17)){throw 'native Y size test failed'}
  $duplicateRejected=$false
  try{[NativeRearScreen01YStats]::SavePrivate($dummy,3840,2160,$raw)}catch{$duplicateRejected=$true}
  if(-not $duplicateRejected){throw 'duplicate private file accepted'}
 }finally{Remove-Item -LiteralPath $raw,$pgm -Force -ErrorAction SilentlyContinue;[Array]::Clear($dummy,0,$dummy.Length)}
 Write-Output 'NATIVE_REAR_SCREEN_01_OFFLINE_TEST=PASS CAMERA_ACTIVATED=NO'
 exit 0
}
if($env:COMPUTERNAME -ne 'DESKTOP-AQ4SMTC'){throw 'NativeRearScreen01 only authorized SP11 Windows host'}
$root=Split-Path -Parent $MyInvocation.MyCommand.Path
if(-not (Get-Acl -LiteralPath $root).AreAccessRulesProtected){throw 'private root ACL inheritance not disabled'}
$marker=Join-Path $root 'CONSUMED.txt'
$fh=[IO.File]::Open($marker,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
try {$b=[Text.Encoding]::UTF8.GetBytes('NativeRearScreen01 single attempt; never rerun');$fh.Write($b,0,$b.Length)}finally{$fh.Dispose()}
& shutdown.exe /r /t 240 /c 'SP11 NativeRearScreen01 bounded RGB reference; return to protected Golden Linux'
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
 foreach($name in @('Surface Camera Rear')) {
  $mc=$null;$reader=$null
  $row=[ordered]@{camera=$name;status='FAIL';samples=@();exposure_auto=$null;exposure_ticks=$null;white_balance_auto=$null;white_balance_kelvin=$null;reader_started=$false;reader_stopped=$false;capture_disposed=$false;private_frame_indices=@();error=$null}
  try {
   $matching=@($groups|Where-Object {$_.DisplayName -eq $name})
   if($matching.Count -ne 1){throw 'expected one exact rear RGB group'}
   $group=$matching[0]
   $settings=New-Object Windows.Media.Capture.MediaCaptureInitializationSettings
   $settings.SourceGroup=$group;$settings.StreamingCaptureMode=[Windows.Media.Capture.StreamingCaptureMode]::Video;$settings.MemoryPreference=[Windows.Media.Capture.MediaCaptureMemoryPreference]::Cpu
   $mc=New-Object Windows.Media.Capture.MediaCapture;Await-Action ($mc.InitializeAsync($settings))
   $sources=@();foreach($entry in $mc.FrameSources){$v=$entry.Value;if($v -and $v.Info.SourceKind.ToString() -eq 'Color' -and $v.Info.MediaStreamType.ToString() -eq 'VideoRecord'){$sources+=$v}}
   if($sources.Count -ne 1){throw 'expected one RGB recording source'}
   $src=$sources[0]
   $formats=@($src.SupportedFormats | Where-Object {
       $_.Subtype -eq 'NV12' -and $_.VideoFormat.Width -eq 3840 -and
       $_.VideoFormat.Height -eq 2160 -and $_.FrameRate.Numerator -eq 30 -and
       $_.FrameRate.Denominator -eq 1 })
   if($formats.Count -ne 1){throw 'one exact3840x2160 NV12 30/1 format required'}
   Await-Action ($src.SetFormatAsync($formats[0]))
   $vf=$src.CurrentFormat.VideoFormat
   if($src.CurrentFormat.Subtype -ne 'NV12' -or $vf.Width -ne 3840 -or $vf.Height -ne 2160){throw 'rear format selection drift'}
   $row.selected_format=[ordered]@{width=3840;height=2160;subtype='NV12';advertised_fps_num=30;advertised_fps_den=1}
   $row.started_utc=[DateTime]::UtcNow.ToString('o')
   $row.media_format_scalar_properties=@()
   foreach($pair in $src.CurrentFormat.Properties){
       $value=$pair.Value
       if($value -is [int] -or $value -is [uint32] -or $value -is [long] -or $value -is [uint64] -or $value -is [string]){
           $row.media_format_scalar_properties+=@{key=[string]$pair.Key;value=$value}
       }
   }
   $reader=Await-Result ($mc.CreateFrameReaderAsync($src)) ([Windows.Media.Capture.Frames.MediaFrameReader])
   $status=Await-Result ($reader.StartAsync()) ([Windows.Media.Capture.Frames.MediaFrameReaderStartStatus])
   if($status.ToString() -ne 'Success'){throw 'RGB reader start failed'}
   $row.reader_started=$true
   Start-Sleep -Seconds 5
   for($i=0;$i -lt 16;$i++) {
    $f=$reader.TryAcquireLatestFrame()
    if(-not $f){throw 'missing RGB frame'}
    try {
     $sb=$f.VideoMediaFrame.SoftwareBitmap;if(-not $sb){throw 'missing CPU SoftwareBitmap'}
     $rawPath=$null;$yPath=$null
     if($i -in @(8,12,15)){$rawPath=Join-Path $root ('PRIVATE-REAR-FRAME-'+$i+'.nv12')}
     if($i -eq 12){$yPath=Join-Path $root 'PRIVATE-REAR-NATIVE-Y-3840x2160.pgm'}
     $sample=Measure-Luma $sb $rawPath $yPath
     if($sb.PixelWidth -ne 3840 -or $sb.PixelHeight -ne 2160){throw 'delivered rear geometry drift'}
     if($rawPath){$row.private_frame_indices+=$i}
     $sample|Add-Member -NotePropertyName acquired_utc -NotePropertyValue ([DateTime]::UtcNow.ToString('o'))
     $sample|Add-Member -NotePropertyName exposure_auto -NotePropertyValue $null
     $sample|Add-Member -NotePropertyName exposure_ticks -NotePropertyValue $null
     $ec=$mc.VideoDeviceController.ExposureControl
     if($ec.Supported){$sample.exposure_auto=$ec.Auto;$sample.exposure_ticks=$ec.Value.Ticks}
     $sample|Add-Member -NotePropertyName iso_supported -NotePropertyValue $false
     $sample|Add-Member -NotePropertyName iso_speed -NotePropertyValue $null
     try{$iso=$mc.VideoDeviceController.IsoSpeedControl;if($iso.Supported){$sample.iso_supported=$true;$sample.iso_speed=$iso.Value}}catch{}
     $sample|Add-Member -NotePropertyName system_relative_ticks -NotePropertyValue $null
     if($null -ne $f.SystemRelativeTime){
         if($f.SystemRelativeTime -is [TimeSpan]){$sample.system_relative_ticks=$f.SystemRelativeTime.Ticks}
         elseif($f.SystemRelativeTime.HasValue){$sample.system_relative_ticks=$f.SystemRelativeTime.Value.Ticks}
     }
     $row.samples+=$sample
    }finally{$f.Dispose()}
    Start-Sleep -Milliseconds 500
   }
   $ec=$mc.VideoDeviceController.ExposureControl
   if($ec.Supported){$row.exposure_auto=$ec.Auto;$row.exposure_ticks=$ec.Value.Ticks}
   $wc=$mc.VideoDeviceController.WhiteBalanceControl
   if($wc.Supported){$row.white_balance_auto=$wc.Auto;$row.white_balance_kelvin=$wc.Value}
   $ticks=@($row.samples|ForEach-Object {$_.system_relative_ticks})
   if($ticks.Count -ne 16 -or @($ticks|Where-Object {$null -eq $_}).Count -ne 0){throw 'missing source timestamps'}
   for($k=1;$k -lt $ticks.Count;$k++){if($ticks[$k] -le $ticks[$k-1]){throw 'nonadvancing source frame timestamp'}}
   if($row.private_frame_indices.Count -ne 3){throw 'private full-resolution baseline incomplete'}
   $row.distinct_advancing_timestamp_samples=16
   $row.completed_utc=[DateTime]::UtcNow.ToString('o')
   $row.status='PASS'
  }catch{$row.error=$_.Exception.Message}
  finally {
   if($reader){
    try{Await-Action ($reader.StopAsync());$row.reader_stopped=$true}catch{$row.status='FAIL';$row.error='reader stop: '+$_.Exception.Message}
    try{$reader.Dispose()}catch{$row.status='FAIL';$row.error='reader dispose: '+$_.Exception.Message}
   }
   if($mc){try{$mc.Dispose();$row.capture_disposed=$true}catch{$row.status='FAIL';$row.error='capture dispose: '+$_.Exception.Message}}
  }
  $records.Add([pscustomobject]$row)
 }
}finally {
 $out=[pscustomobject]@{experiment='E-NATIVE-REAR-WINDOWS-SCREEN-01';comparison_session='rear-SP7-screen-light-off-20261007-01';lights_off_user_report_utc='2026-10-07T20:37:51Z';scene='user reports rear pointed at SP7 screen';SP7_brightness_readback=26;SP7_brightness_readback_utc='2026-10-07T20:38:32.7020979Z';SP7_damaged_lower_LCD_band=$true;healthy_upper_screen_ROI_registered=$false;kind='Windows rear-only native3840x2160 NV12 baseline';private_full_resolution_nv12_frames_requested=3;private_native_Y_PGM_requested=1;pixel_files_or_hashes_exported=$false;front_activated=$false;ir_activated=$false;controls_modified=$false;format_selection_modified=$true;scene_controlled_or_matched=$false;measured_hardware_fps_proven=$false;results=@($records.ToArray());automatic_return_reboot_scheduled=$true}
 $json=$out|ConvertTo-Json -Depth 10
 [IO.File]::WriteAllText((Join-Path $root 'RESULT.json'),$json,[Text.Encoding]::UTF8)
 Write-Output 'NATIVE_REAR_WINDOWS_REFERENCE_RESULT_WRITTEN'
}
