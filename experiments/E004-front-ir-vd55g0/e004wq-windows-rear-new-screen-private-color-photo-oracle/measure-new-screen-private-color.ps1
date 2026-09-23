param([switch]$OfflineTest)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[void][Windows.Graphics.Imaging.SoftwareBitmap,Windows.Graphics.Imaging,ContentType=WindowsRuntime]
[void][Windows.Graphics.Imaging.BitmapPixelFormat,Windows.Graphics.Imaging,ContentType=WindowsRuntime]
[void][Windows.Graphics.Imaging.BitmapBufferAccessMode,Windows.Graphics.Imaging,ContentType=WindowsRuntime]
[void][Windows.Storage.Streams.Buffer,Windows.Storage.Streams,ContentType=WindowsRuntime]
[void][Windows.Storage.Streams.DataReader,Windows.Storage.Streams,ContentType=WindowsRuntime]
Add-Type -ReferencedAssemblies 'System.Drawing' -TypeDefinition @'
public static class E004wqYStats {
 public static void SavePrivateRearGray(byte[] data,int width,int height,string path) {
  if(width!=3840 || height!=2160 || data==null || data.Length<(long)width*height*3/2)
   throw new System.ArgumentException("unexpected private rear NV12 layout");
  if(System.IO.File.Exists(path)) throw new System.IO.IOException("private image exists");
  using(var bitmap=new System.Drawing.Bitmap(width/4,height/4,
          System.Drawing.Imaging.PixelFormat.Format24bppRgb)) {
   var rect=new System.Drawing.Rectangle(0,0,bitmap.Width,bitmap.Height);
   var locked=bitmap.LockBits(rect,System.Drawing.Imaging.ImageLockMode.WriteOnly,
                System.Drawing.Imaging.PixelFormat.Format24bppRgb);
   try {
    byte[] output=new byte[locked.Stride*bitmap.Height];
    for(int y=0;y<bitmap.Height;y++) for(int x=0;x<bitmap.Width;x++) {
     int v=data[(4*y)*width+4*x];
     int rgb=System.Math.Max(0,System.Math.Min(255,(v-16)*255/219));
     int off=y*locked.Stride+x*3;
     output[off]=output[off+1]=output[off+2]=(byte)rgb;
    }
    System.Runtime.InteropServices.Marshal.Copy(output,0,locked.Scan0,output.Length);
    System.Array.Clear(output,0,output.Length);
   } finally {bitmap.UnlockBits(locked);}
   bitmap.Save(path,System.Drawing.Imaging.ImageFormat.Png);
  }
 }
 public static void SavePrivateRearColor(byte[] data,int width,int height,string path) {
  if(width!=3840 || height!=2160 || data==null || data.Length<(long)width*height*3/2)
   throw new System.ArgumentException("unexpected private rear NV12 color geometry");
  if(System.IO.File.Exists(path)) throw new System.IO.IOException("private color image already exists");
  int uvBase=width*height;
  using(var bitmap=new System.Drawing.Bitmap(width/4,height/4,
       System.Drawing.Imaging.PixelFormat.Format24bppRgb)) {
   var rect=new System.Drawing.Rectangle(0,0,bitmap.Width,bitmap.Height);
   var bits=bitmap.LockBits(rect,System.Drawing.Imaging.ImageLockMode.WriteOnly,
       System.Drawing.Imaging.PixelFormat.Format24bppRgb);
   try {
    byte[] output=new byte[bits.Stride*bitmap.Height];
    for(int y=0;y<bitmap.Height;y++) for(int x=0;x<bitmap.Width;x++) {
     int sx=x*4,sy=y*4;
     int yv=data[sy*width+sx];
     int uvIndex=uvBase+(sy/2)*width+sx;
     double cb=(int)data[uvIndex]-128,cr=(int)data[uvIndex+1]-128;
     double l=System.Math.Max(0,yv-16)*255.0/219.0;
     // Approximate BT709 NV12 studio RGB PRIVATE display render only.
     // Not calibrated sensor true colour or verified native YUV matrix.
     int red=(int)System.Math.Round(l+1.793*cr);
     int green=(int)System.Math.Round(l-0.213*cb-0.533*cr);
     int blue=(int)System.Math.Round(l+2.112*cb);
     int off=y*bits.Stride+x*3;
     output[off]=(byte)System.Math.Max(0,System.Math.Min(255,blue));
     output[off+1]=(byte)System.Math.Max(0,System.Math.Min(255,green));
     output[off+2]=(byte)System.Math.Max(0,System.Math.Min(255,red));
    }
    System.Runtime.InteropServices.Marshal.Copy(output,0,bits.Scan0,output.Length);
    System.Array.Clear(output,0,output.Length);
   } finally {bitmap.UnlockBits(bits);}
   bitmap.Save(path,System.Drawing.Imaging.ImageFormat.Png);
  }
 }
 public static double[] Summarize(byte[] data,int width,int height) {
  if(width<=0 || height<=0 || (long)width*height>data.Length ||
      width%64!=0 || height%8!=0) throw new System.ArgumentException("invalid luma geometry");
  long sum=0,n=0;int min=255,max=0;long[] hist=new long[256];
  long[] tileSum=new long[64],tileN=new long[64];
  for(int y=0;y<height;y++) for(int x=0;x<width;x+=64) {
   int v=data[y*width+x];sum+=v;n++;hist[v]++;if(v<min)min=v;if(v>max)max=v;
   int ix=System.Math.Min(7,(8*x)/width),iy=System.Math.Min(7,(8*y)/height);
   int tile=iy*8+ix;tileSum[tile]+=v;tileN[tile]++;
  }
  if(n<128) throw new System.ArgumentException("too few luma samples");
  double tileMean=0,tileSq=0;
  for(int t=0;t<64;t++){
   if(tileN[t]==0) throw new System.ArgumentException("missing spatial tile");
   double tm=(double)tileSum[t]/tileN[t];tileMean+=tm;tileSq+=tm*tm;
  }
  tileMean/=64.0;tileSq/=64.0;
  double[] ps=new double[4];int[] ranks=new int[]{1,50,95,99};
  for(int i=0;i<4;i++){
   long target=(long)System.Math.Floor((double)(n-1)*ranks[i]/100.0),cum=0;
   for(int v=0;v<256;v++) {cum+=hist[v];if(cum>target){ps[i]=v;break;}}
  }
  double hDiff=0,vDiff=0;long hN=0,vN=0;
  for(int y=32;y<height;y+=4) for(int x=64;x<width;x+=64) {
   int i=y*width+x;hDiff+=System.Math.Abs((int)data[i]-(int)data[i-64]);hN++;
   vDiff+=System.Math.Abs((int)data[i]-(int)data[i-32*width]);vN++;
  }
  long below20=0,below32=0,above64=0;
  for(int v=0;v<256;v++){
   if(v<20)below20+=hist[v];if(v<32)below32+=hist[v];if(v>64)above64+=hist[v];
  }
  return new double[]{(double)sum/n,min,max,(double)hist[0]/n,
   (double)hist[255]/n,n,ps[0],ps[1],ps[2],ps[3],
   (double)below20/n,(double)below32/n,(double)above64/n,
   System.Math.Sqrt(System.Math.Max(0.0,tileSq-tileMean*tileMean)),
   hN>0?hDiff/hN:0.0,vN>0?vDiff/vN:0.0};
 }
}
'@
function Measure-Luma($sb,[string]$privatePreviewPath=$null) {
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
 $a=[E004wqYStats]::Summarize($bytes,$w,$h)
 if($privatePreviewPath) {
  [E004wqYStats]::SavePrivateRearGray($bytes,$w,$h,$privatePreviewPath)
  [E004wqYStats]::SavePrivateRearColor($bytes,$w,$h,$script:privateColorPreview)
 }

 [Array]::Clear($bytes,0,$bytes.Length)
 return [pscustomobject]@{width=$w;height=$h;format='NV12';y_mean=$a[0];y_min=$a[1];y_max=$a[2];y_zero_fraction=$a[3];y_255_fraction=$a[4];sampled_values=$a[5];y_p01=$a[6];y_p50=$a[7];y_p95=$a[8];y_p99=$a[9];y_fraction_below20=$a[10];y_fraction_below32=$a[11];y_fraction_above64=$a[12];spatial_8x8_tile_mean_std_y=$a[13];horizontal_64pixel_abs_diff_mean_y=$a[14];vertical_32pixel_abs_diff_mean_y=$a[15];horizontal_stride=64;all_rows=$true}
}
if($OfflineTest) {
 $bytes=New-Object byte[] (512*16)
 for($i=0;$i -lt $bytes.Length;$i++){$bytes[$i]=37}
 $a=[E004wqYStats]::Summarize($bytes,512,16)
 if($a[0] -ne 37 -or $a[1] -ne 37 -or $a[2] -ne 37 -or $a[5] -ne 128 -or $a[9] -ne 37 -or $a[13] -ne 0 -or $a[14] -ne 0 -or $a[15] -ne 0){throw 'numeric test failed'}
 $dummy=New-Object byte[] (3840*2160*3/2)
 $dummyPreview=Join-Path $env:TEMP 'SP11-E004wq-OFFLINE-SYNTHETIC-GRAY.png'
 $dummyColor=Join-Path $env:TEMP 'SP11-E004wq-OFFLINE-SYNTHETIC-COLOR.png'
 if(Test-Path $dummyPreview){Remove-Item -LiteralPath $dummyPreview -Force}
 try {
  [E004wqYStats]::SavePrivateRearGray($dummy,3840,2160,$dummyPreview)
  [E004wqYStats]::SavePrivateRearColor($dummy,3840,2160,$dummyColor)
  if(-not (Test-Path -LiteralPath $dummyColor)){throw 'offline synthetic color photo failed'}
  if(-not (Test-Path $dummyPreview)){throw 'offline synthetic preview failed'}
 }finally{if(Test-Path $dummyPreview){Remove-Item -LiteralPath $dummyPreview -Force};if(Test-Path $dummyColor){Remove-Item -LiteralPath $dummyColor -Force}}
 $sb=New-Object Windows.Graphics.Imaging.SoftwareBitmap ([Windows.Graphics.Imaging.BitmapPixelFormat]::Nv12),1920,1080
 try {$v=Measure-Luma $sb;if($v.width -ne 1920 -or $v.sampled_values -ne 32400){throw 'synthetic WinRT layout test failed'}} finally {$sb.Dispose()}
 Write-Output 'E004WQ_OFFLINE_TEST=PASS CAMERA_ACTIVATED=NO'
 exit 0
}
if($env:COMPUTERNAME -ne 'DESKTOP-AQ4SMTC'){throw 'E004wq only authorized SP11 Windows host'}
$root=Split-Path -Parent $MyInvocation.MyCommand.Path
$marker=Join-Path $root 'CONSUMED.txt'
$fh=[IO.File]::Open($marker,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
try {$b=[Text.Encoding]::UTF8.GetBytes('E004wq single attempt; never rerun');$fh.Write($b,0,$b.Length)}finally{$fh.Dispose()}
& shutdown.exe /r /t 300 /c 'SP11 E004wq bounded colour camera optical brightness; return to protected Golden Linux'
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
$rearPreview=Join-Path $root 'REAR-WINDOWS-PRIVATE-GRAYSCALE-960x540.png'
$script:privateColorPreview=Join-Path $root 'REAR-WINDOWS-PRIVATE-COLOR-960x540.png'
$rearPreviewCreated=$false
$records=New-Object 'System.Collections.Generic.List[object]'
try {
 $groups=Await-Result ([Windows.Media.Capture.Frames.MediaFrameSourceGroup]::FindAllAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Media.Capture.Frames.MediaFrameSourceGroup]])
 foreach($name in @('Surface Camera Front','Surface Camera Rear')) {
  $mc=$null;$reader=$null
  $row=[ordered]@{camera=$name;status='FAIL';samples=@();exposure_auto=$null;exposure_ticks=$null;white_balance_auto=$null;white_balance_kelvin=$null;captured_local_time=$null;error=$null}
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
     if($name -eq 'Surface Camera Rear' -and $i -eq 6) {
      $row.samples+=Measure-Luma $sb $rearPreview
      $rearPreviewCreated=((Test-Path -LiteralPath $rearPreview) -and (Test-Path -LiteralPath $script:privateColorPreview))
      if(-not $rearPreviewCreated){throw 'private rear gray/color capture missing'}
     }else{$row.samples+=Measure-Luma $sb}
    }finally{$f.Dispose()}
    Start-Sleep -Milliseconds 500
   }
   $ec=$mc.VideoDeviceController.ExposureControl
   if($ec.Supported){$row.exposure_auto=$ec.Auto;$row.exposure_ticks=$ec.Value.Ticks}
   $wc=$mc.VideoDeviceController.WhiteBalanceControl
   if($wc.Supported){$row.white_balance_auto=$wc.Auto;$row.white_balance_kelvin=$wc.Value}
   $row.captured_local_time=(Get-Date).ToString('o');$row.status='PASS'
  }catch{$row.error=$_.Exception.Message}
  finally {
   if($reader){try{Await-Action ($reader.StopAsync())}catch{};try{$reader.Dispose()}catch{}}
   if($mc){try{$mc.Dispose()}catch{}}
  }
  $records.Add([pscustomobject]$row)
 }
}finally {
 $out=[pscustomobject]@{experiment='E004wq';kind='Windows fresh rear-corner Color NV12 numeric luminance, spatial contrast, and one strictly local private grayscale preview';private_rear_grayscale_png_captured_locally_only=$rearPreviewCreated;private_rear_color_png_captured_locally_only=$rearPreviewCreated;private_rear_color_dimensions=@(960,540);private_rear_color_render='provisional_BT709_local_only_NV12_RGB';private_rear_grayscale_dimensions=@(960,540);private_rear_grayscale_is_color_or_semantic_detail_proof=$false;private_rear_color_png_proves_sensor_color_calibration_or_semantic_detail=$false;pixel_files_or_hashes_exported=$false;ir_activated=$false;controls_modified=$false;camera_orientation_verified=$false;scene_illumination_measured_or_matched=$false;frame_uniqueness_or_fps_proven=$false;results=@($records.ToArray());automatic_return_reboot_scheduled=$true;local_windows_time=(Get-Date).ToString('o')}
 $json=$out|ConvertTo-Json -Depth 10
 [IO.File]::WriteAllText((Join-Path $root 'RESULT.json'),$json,[Text.Encoding]::UTF8)
 Write-Output $json
}
