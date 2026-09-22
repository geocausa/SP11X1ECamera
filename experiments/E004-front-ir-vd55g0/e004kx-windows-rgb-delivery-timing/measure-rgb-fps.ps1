param([switch]$OfflineTest)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[void][Windows.Graphics.Imaging.SoftwareBitmap,Windows.Graphics.Imaging,ContentType=WindowsRuntime]
[void][Windows.Graphics.Imaging.BitmapPixelFormat,Windows.Graphics.Imaging,ContentType=WindowsRuntime]
[void][Windows.Graphics.Imaging.BitmapBufferAccessMode,Windows.Graphics.Imaging,ContentType=WindowsRuntime]
[void][Windows.Storage.Streams.Buffer,Windows.Storage.Streams,ContentType=WindowsRuntime]
[void][Windows.Storage.Streams.DataReader,Windows.Storage.Streams,ContentType=WindowsRuntime]

$script:Hasher=[Security.Cryptography.SHA256]::Create()
function Frame-Fingerprint($sb) {
 if($sb.BitmapPixelFormat.ToString() -ne 'Nv12'){throw 'expected native NV12'}
 $w=[int]$sb.PixelWidth;$h=[int]$sb.PixelHeight
 $lock=$sb.LockBuffer([Windows.Graphics.Imaging.BitmapBufferAccessMode]::Read)
 try {
  $y=$lock.GetPlaneDescription(0);$uv=$lock.GetPlaneDescription(1)
  if($lock.GetPlaneCount() -ne 2 -or $y.StartIndex -ne 0 -or $y.Stride -ne $w -or $uv.Stride -ne $w -or $uv.StartIndex -ne $w*$h){throw 'unsupported layout'}
 }finally{$lock.Dispose()}
 $buffer=New-Object Windows.Storage.Streams.Buffer ([uint32]($w*$h*3/2))
 $sb.CopyToBuffer($buffer)
 if($buffer.Length -ne $w*$h*3/2){throw 'short NV12 payload'}
 $bytes=New-Object byte[] ([int]$buffer.Length)
 $dr=[Windows.Storage.Streams.DataReader]::FromBuffer($buffer)
 try {$dr.ReadBytes($bytes)}finally{$dr.Dispose()}
 try {return [Convert]::ToBase64String($script:Hasher.ComputeHash($bytes))}finally{[Array]::Clear($bytes,0,$bytes.Length)}
}
if($OfflineTest) {
 $sb=New-Object Windows.Graphics.Imaging.SoftwareBitmap ([Windows.Graphics.Imaging.BitmapPixelFormat]::Nv12),1920,1080
 try {$a=Frame-Fingerprint $sb;$b=Frame-Fingerprint $sb;if($a -ne $b -or $a.Length -ne 44){throw 'fingerprint regression'}}finally{$sb.Dispose()}
 Write-Output 'E004KX_OFFLINE_TEST=PASS CAMERA_ACTIVATED=NO'
 exit 0
}
if($env:COMPUTERNAME -ne 'DESKTOP-AQ4SMTC'){throw 'E004kx only authorized SP11 Windows host'}
$root=Split-Path -Parent $MyInvocation.MyCommand.Path
$marker=Join-Path $root 'CONSUMED.txt'
$fh=[IO.File]::Open($marker,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
try {$b=[Text.Encoding]::UTF8.GetBytes('E004kx single attempt; never rerun');$fh.Write($b,0,$b.Length)}finally{$fh.Dispose()}
& shutdown.exe /r /t 240 /c 'SP11 E004kx bounded RGB reference; return to protected Golden Linux'
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
  $row=[ordered]@{camera=$name;status='FAIL';measurement=$null;advertised_formats=@();exposure_auto=$null;exposure_ticks=$null;white_balance_auto=$null;white_balance_kelvin=$null;error=$null}
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
   foreach($fmt in $src.SupportedFormats) {
    $row.advertised_formats+=[pscustomobject]@{subtype=$fmt.Subtype;width=$fmt.VideoFormat.Width;height=$fmt.VideoFormat.Height;fps_numerator=$fmt.FrameRate.Numerator;fps_denominator=$fmt.FrameRate.Denominator}
   }
   $row.selected_format=[pscustomobject]@{width=$vf.Width;height=$vf.Height;subtype=$src.CurrentFormat.Subtype;fps_numerator=$src.CurrentFormat.FrameRate.Numerator;fps_denominator=$src.CurrentFormat.FrameRate.Denominator}
   $reader=Await-Result ($mc.CreateFrameReaderAsync($src)) ([Windows.Media.Capture.Frames.MediaFrameReader])
   $status=Await-Result ($reader.StartAsync()) ([Windows.Media.Capture.Frames.MediaFrameReaderStartStatus])
   if($status.ToString() -ne 'Success'){throw 'RGB reader start failed'}
   Start-Sleep -Seconds 2
   $seen=New-Object 'System.Collections.Generic.HashSet[string]'
   $arrivals=New-Object 'System.Collections.Generic.List[double]'
   $work=New-Object 'System.Collections.Generic.List[double]'
   $sourceTicks=New-Object 'System.Collections.Generic.HashSet[long]'
   $attempts=0;$duplicates=0;$nulls=0;$nullTimestamps=0
   $proc=[Diagnostics.Process]::GetCurrentProcess();$cpu0=$proc.TotalProcessorTime.TotalSeconds
   $sw=[Diagnostics.Stopwatch]::StartNew()
   while($sw.Elapsed.TotalSeconds -lt 30) {
    $f=$reader.TryAcquireLatestFrame();$attempts++
    if(-not $f){$nulls++;Start-Sleep -Milliseconds 1;continue}
    $arrival=$sw.Elapsed.TotalMilliseconds
    try {
     $sb=$f.VideoMediaFrame.SoftwareBitmap
     if(-not $sb -or $sb.PixelWidth -ne $expectedW -or $sb.PixelHeight -ne $expectedH){throw 'frame bitmap/dimensions drift'}
     $fingerprint=Frame-Fingerprint $sb
     if($seen.Add($fingerprint)){$arrivals.Add($arrival)}else{$duplicates++}
     if($null -eq $f.SystemRelativeTime){$nullTimestamps++}else{[void]$sourceTicks.Add([long]$f.SystemRelativeTime.Ticks)}
    }finally{$f.Dispose()}
    $work.Add($sw.Elapsed.TotalMilliseconds-$arrival)
    Start-Sleep -Milliseconds 1
   }
   $sw.Stop();$proc.Refresh();$cpu=$proc.TotalProcessorTime.TotalSeconds-$cpu0
   if($arrivals.Count -lt 2){throw 'insufficient distinct frame payloads'}
   $gaps=@();for($i=1;$i -lt $arrivals.Count;$i++){$gaps+=($arrivals[$i]-$arrivals[$i-1])}
   $sorted=@($gaps|Sort-Object);$wm=($work|Measure-Object -Average -Maximum)
   $row.measurement=[pscustomobject]@{
    requested_window_s=30;elapsed_s=$sw.Elapsed.TotalSeconds;poll_attempts=$attempts
    complete_distinct_payloads=$arrivals.Count;duplicate_payload_acquisitions=$duplicates;null_acquisitions=$nulls
    unique_payload_arrival_fps=($arrivals.Count-1)*1000/($arrivals[$arrivals.Count-1]-$arrivals[0])
    unique_payload_span_s=($arrivals[$arrivals.Count-1]-$arrivals[0])/1000
    p95_arrival_gap_ms=$sorted[[int][Math]::Floor(($sorted.Count-1)*0.95)];max_arrival_gap_ms=$sorted[-1]
    observer_copy_hash_mean_ms=$wm.Average;observer_copy_hash_max_ms=$wm.Maximum
    observer_process_cpu_seconds=$cpu;unique_system_timestamps=$sourceTicks.Count;null_system_timestamps=$nullTimestamps
    full_nv12_bytes_per_payload=$expectedW*$expectedH*3/2
    sensor_sequence_gaps_proven=$false;driver_cpu_usage_measured=$false
   }
   $seen.Clear();$sourceTicks.Clear();$fingerprint=$null
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
 $out=[pscustomobject]@{experiment='E004kx';kind='Windows RGB advertised modes and distinct-payload delivery timing';pixel_files_or_hashes_exported=$false;ir_activated=$false;controls_modified=$false;scene_controlled_or_matched=$false;frame_uniqueness='full NV12 SHA256 deduplicated in RAM, hashes never exported';fps_semantics='distinct payload arrival rate; polling observer may miss frames, not sensor sequence or physical sensor maximum';results=@($records.ToArray());automatic_return_reboot_scheduled=$true}
 $json=$out|ConvertTo-Json -Depth 10
 [IO.File]::WriteAllText((Join-Path $root 'RESULT.json'),$json,[Text.Encoding]::UTF8)
 Write-Output $json
}
