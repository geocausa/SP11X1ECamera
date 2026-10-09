param([switch]$OfflineTest,[string]$Root='C:\Users\Geoca\Documents\SP11-Camera-Pattern62')
# SPDX-License-Identifier: GPL-2.0-only
# SP11 Windows rear reference capture against the SP7 pattern loop (run 62).
# Phase 0: Windows automatic controls. Phases 1-4: manual exposure 33.25 ms with
# an ISO ladder (or an exposure ladder if ISO is not controllable). Every frame
# is reduced to a 16x9 Y/U/V grid with UTC acquire time. Pixels stay on SP11.
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[void][Windows.Graphics.Imaging.SoftwareBitmap,Windows.Graphics.Imaging,ContentType=WindowsRuntime]
[void][Windows.Graphics.Imaging.BitmapPixelFormat,Windows.Graphics.Imaging,ContentType=WindowsRuntime]
[void][Windows.Graphics.Imaging.BitmapBufferAccessMode,Windows.Graphics.Imaging,ContentType=WindowsRuntime]
[void][Windows.Storage.Streams.Buffer,Windows.Storage.Streams,ContentType=WindowsRuntime]
[void][Windows.Storage.Streams.DataReader,Windows.Storage.Streams,ContentType=WindowsRuntime]
Add-Type -TypeDefinition @'
public static class Pattern62Grid {
 public static string Line(byte[] d,int w,int h) {
  const int GX=16,GY=9; int cw=w/GX, ch=h/GY;
  var sb=new System.Text.StringBuilder(4096);
  for(int plane=0;plane<3;plane++)
   for(int gy=0;gy<GY;gy++) for(int gx=0;gx<GX;gx++) {
    long s=0,n=0;
    if(plane==0){
     for(int y=gy*ch+2;y<(gy+1)*ch;y+=4) for(int x=gx*cw+2;x<(gx+1)*cw;x+=4){s+=d[y*w+x];n++;}
    } else {
     int off=w*h, o=plane-1;
     for(int y=gy*ch/2+1;y<(gy+1)*ch/2;y+=2) for(int x=gx*cw/2+1;x<(gx+1)*cw/2;x+=2){s+=d[off+y*w+2*x+o];n++;}
    }
    sb.Append(',').Append(((double)s/n).ToString("F3",System.Globalization.CultureInfo.InvariantCulture));
   }
  return sb.ToString();
 }
 public static void SavePrivate(byte[] d,string path){
  using(var f=new System.IO.FileStream(path,System.IO.FileMode.CreateNew)){f.Write(d,0,d.Length);f.Flush(true);}
 }
}
'@
function Get-Bytes($sb) {
 if($sb.BitmapPixelFormat.ToString() -ne 'Nv12'){throw 'expected NV12'}
 $w=[int]$sb.PixelWidth;$h=[int]$sb.PixelHeight
 $lock=$sb.LockBuffer([Windows.Graphics.Imaging.BitmapBufferAccessMode]::Read)
 try{
  $y=$lock.GetPlaneDescription(0);$uv=$lock.GetPlaneDescription(1)
  if($y.Stride -ne $w -or $uv.StartIndex -ne ($w*$h) -or $uv.Stride -ne $w){throw 'unsupported NV12 layout'}
 }finally{$lock.Dispose()}
 $buf=New-Object Windows.Storage.Streams.Buffer ([uint32]($w*$h*3/2))
 $sb.CopyToBuffer($buf)
 $bytes=New-Object byte[] ([int]$buf.Length)
 $dr=[Windows.Storage.Streams.DataReader]::FromBuffer($buf);try{$dr.ReadBytes($bytes)}finally{$dr.Dispose()}
 return ,$bytes
}
if($OfflineTest){
 $d=New-Object byte[] (64*36*3/2);for($i=0;$i -lt $d.Length;$i++){$d[$i]=50}
 $l=[Pattern62Grid]::Line($d,64,36)
 if(($l.Split(',').Count) -ne 433){throw 'grid width'}
 $sb=New-Object Windows.Graphics.Imaging.SoftwareBitmap ([Windows.Graphics.Imaging.BitmapPixelFormat]::Nv12),1920,1080
 try{$b=Get-Bytes $sb;if($b.Length -ne 1920*1080*3/2){throw 'bytes'}}finally{$sb.Dispose()}
 'PATTERN62_OFFLINE_TEST=PASS CAMERA_ACTIVATED=NO';exit 0
}
function Await-Result($op,[Type]$type){
 $m=[System.WindowsRuntimeSystemExtensions].GetMethods()|Where-Object{$_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1}|Select-Object -First 1
 $t=$m.MakeGenericMethod($type).Invoke($null,@($op));if(-not $t.Wait(30000)){throw 'WinRT result timeout'};return $t.Result
}
function Await-Action($op){
 $m=[System.WindowsRuntimeSystemExtensions].GetMethods()|Where-Object{$_.Name -eq 'AsTask' -and -not $_.IsGenericMethod -and $_.GetParameters().Count -eq 1}|Select-Object -First 1
 $t=$m.Invoke($null,@($op));if(-not $t.Wait(30000)){throw 'WinRT action timeout'}
}
New-Item -ItemType Directory -Force $Root|Out-Null
$marker=Join-Path $Root 'CONSUMED.txt'
$fh=[IO.File]::Open($marker,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None);$fh.Dispose()
& shutdown.exe /r /t 900 /c 'SP11 pattern62 Windows reference: bounded return to Linux'
$log=Join-Path $Root 'run.log'
function L($m){Add-Content $log ("{0} {1}" -f [DateTime]::UtcNow.ToString('o'),$m)}
[void][Windows.Media.Capture.Frames.MediaFrameSourceGroup,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameReader,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCapture,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCaptureInitializationSettings,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCaptureMemoryPreference,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.StreamingCaptureMode,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameReaderStartStatus,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
$result=[ordered]@{run='E-REAR-PATTERN-62-WINDOWS';status='FAIL';phases=@();frames=0;error=$null;controls=[ordered]@{}}
$mc=$null;$reader=$null;$wr=$null
try{
 $groups=Await-Result ([Windows.Media.Capture.Frames.MediaFrameSourceGroup]::FindAllAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Media.Capture.Frames.MediaFrameSourceGroup]])
 $group=@($groups|Where-Object{$_.DisplayName -eq 'Surface Camera Rear'})
 if($group.Count -ne 1){throw 'expected one Surface Camera Rear group'}
 $settings=New-Object Windows.Media.Capture.MediaCaptureInitializationSettings
 $settings.SourceGroup=$group[0];$settings.StreamingCaptureMode=[Windows.Media.Capture.StreamingCaptureMode]::Video;$settings.MemoryPreference=[Windows.Media.Capture.MediaCaptureMemoryPreference]::Cpu
 $mc=New-Object Windows.Media.Capture.MediaCapture;Await-Action ($mc.InitializeAsync($settings))
 $src=$null;foreach($e in $mc.FrameSources){$v=$e.Value;if($v.Info.SourceKind.ToString() -eq 'Color' -and $v.Info.MediaStreamType.ToString() -eq 'VideoRecord'){$src=$v}}
 if(-not $src){throw 'no RGB record source'}
 $fmt=@($src.SupportedFormats|Where-Object{$_.Subtype -eq 'NV12' -and $_.VideoFormat.Width -eq 3840 -and $_.VideoFormat.Height -eq 2160 -and $_.FrameRate.Numerator -eq 30 -and $_.FrameRate.Denominator -eq 1})
 if($fmt.Count -lt 1){throw 'no 3840x2160 NV12 30fps format'}
 Await-Action ($src.SetFormatAsync($fmt[0]))
 $vdc=$mc.VideoDeviceController;$ec=$vdc.ExposureControl;$iso=$vdc.IsoSpeedControl
 $result.controls.exposure_supported=$ec.Supported
 if($ec.Supported){$result.controls.exposure_min_ticks=$ec.Min.Ticks;$result.controls.exposure_max_ticks=$ec.Max.Ticks;$result.controls.exposure_step_ticks=$ec.Step.Ticks}
 $result.controls.iso_supported=$iso.Supported
 if($iso.Supported){try{$result.controls.iso_min=$iso.Min;$result.controls.iso_max=$iso.Max;$result.controls.iso_step=$iso.Step}catch{};try{$result.controls.iso_presets=@($iso.SupportedPresets|ForEach-Object{$_.ToString()})}catch{}}
 L ('controls '+($result.controls|ConvertTo-Json -Compress))
 $isoLadder=$null
 if($iso.Supported -and $iso.Max -gt $iso.Min){$b=[Math]::Max([uint32]$iso.Min,[uint32]100);$isoLadder=@($b,($b*2),($b*4),($b*8))|ForEach-Object{[uint32][Math]::Min($_,$iso.Max)}}
 $plan=@(@{name='auto';auto=$true;seconds=70})
 if($ec.Supported){
  if($isoLadder){foreach($v in $isoLadder){$plan+=@{name="manual_33ms_iso$v";auto=$false;exp=332500;iso=$v;seconds=58}}}
  else{foreach($t in 332500,166250,83125,41563){$plan+=@{name="manual_exp$t";auto=$false;exp=$t;iso=$null;seconds=58}}}
 }
 $reader=Await-Result ($mc.CreateFrameReaderAsync($src)) ([Windows.Media.Capture.Frames.MediaFrameReader])
 $st=Await-Result ($reader.StartAsync()) ([Windows.Media.Capture.Frames.MediaFrameReaderStartStatus])
 if($st.ToString() -ne 'Success'){throw 'reader start failed'}
 $wr=New-Object IO.StreamWriter (Join-Path $Root 'records.csv')
 $wr.WriteLine('phase,utc_unix,sys_ticks,exposure_ticks,exposure_auto,iso,grid432')
 $saved=0
 for($p=0;$p -lt $plan.Count;$p++){
  $ph=$plan[$p];$pr=[ordered]@{name=$ph.name;frames=0;set_error=$null}
  try{
   if($ph.auto){if($ec.Supported){Await-Action ($ec.SetAutoAsync($true))};if($iso.Supported){try{Await-Action ($iso.SetAutoAsync())}catch{}}}
   else{Await-Action ($ec.SetAutoAsync($false));Await-Action ($ec.SetValueAsync([TimeSpan]::FromTicks($ph.exp)));if($ph.iso){Await-Action ($iso.SetValueAsync([uint32]$ph.iso))}}
  }catch{$pr.set_error=$_.Exception.Message;L ("set $($ph.name) failed: "+$_.Exception.Message)}
  $end=[DateTime]::UtcNow.AddSeconds($ph.seconds);$last=-1
  while([DateTime]::UtcNow -lt $end){
   $f=$reader.TryAcquireLatestFrame()
   if($f){
    try{
     $ticks=-1;if($null -ne $f.SystemRelativeTime){$ticks=$f.SystemRelativeTime.Ticks}
     if($ticks -ne $last){
      $last=$ticks;$utc=([DateTime]::UtcNow-[DateTime]'1970-01-01').TotalSeconds
      $bytes=Get-Bytes $f.VideoMediaFrame.SoftwareBitmap
      $line=[Pattern62Grid]::Line($bytes,3840,2160)
      if($saved -lt 2 -and $p -eq 1 -and $pr.frames -in 30,200){[Pattern62Grid]::SavePrivate($bytes,(Join-Path $Root ("frame-p1-"+$pr.frames+".nv12")));$saved++}
      $et='';$ea='';$iv=''
      if($ec.Supported){$et=$ec.Value.Ticks;$ea=$ec.Auto};if($iso.Supported){try{$iv=$iso.Value}catch{}}
      $wr.WriteLine(("{0},{1:F6},{2},{3},{4},{5}{6}" -f $p,$utc,$ticks,$et,$ea,$iv,$line))
      $pr.frames++
     }
    }finally{$f.Dispose()}
   } else {Start-Sleep -Milliseconds 10}
  }
  $result.phases+=$pr;$result.frames+=$pr.frames;L ("phase $($ph.name) frames $($pr.frames)")
 }
 $result.status='PASS'
}catch{$result.error=$_.Exception.Message;L ('error '+$_.Exception.Message)}
finally{
 if($wr){$wr.Dispose()}
 if($reader){try{Await-Action ($reader.StopAsync())}catch{};try{$reader.Dispose()}catch{}}
 if($mc){try{$mc.Dispose()}catch{}}
 [IO.File]::WriteAllText((Join-Path $Root 'RESULT.json'),($result|ConvertTo-Json -Depth 6),[Text.Encoding]::UTF8)
 L 'done; returning to Linux'
 & shutdown.exe /a 2>$null
 & shutdown.exe /r /t 20 /c 'SP11 pattern62 complete: return to Linux'
}
