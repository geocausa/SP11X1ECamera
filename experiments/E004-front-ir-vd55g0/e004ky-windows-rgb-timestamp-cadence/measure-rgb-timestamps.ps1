param([switch]$OfflineTest)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[void][Windows.Graphics.Imaging.SoftwareBitmap,Windows.Graphics.Imaging,ContentType=WindowsRuntime]
[void][Windows.Graphics.Imaging.BitmapPixelFormat,Windows.Graphics.Imaging,ContentType=WindowsRuntime]
[void][Windows.Graphics.Imaging.BitmapBufferAccessMode,Windows.Graphics.Imaging,ContentType=WindowsRuntime]
[void][Windows.Storage.Streams.Buffer,Windows.Storage.Streams,ContentType=WindowsRuntime]
[void][Windows.Storage.Streams.DataReader,Windows.Storage.Streams,ContentType=WindowsRuntime]

if($OfflineTest) { Write-Output 'E004KY_SOURCE_LOAD=PASS CAMERA_ACTIVATED=NO'; exit 0 }
if($env:COMPUTERNAME -ne 'DESKTOP-AQ4SMTC'){throw 'E004ky only authorized SP11 Windows host'}
$root=Split-Path -Parent $MyInvocation.MyCommand.Path
$marker=Join-Path $root 'CONSUMED.txt'
$fh=[IO.File]::Open($marker,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
try {$b=[Text.Encoding]::UTF8.GetBytes('E004ky single attempt; never rerun');$fh.Write($b,0,$b.Length)}finally{$fh.Dispose()}
& shutdown.exe /r /t 240 /c 'SP11 E004ky bounded RGB reference; return to protected Golden Linux'
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
   $sourceArrivals=New-Object 'System.Collections.Generic.List[long]'
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
     if($null -eq $f.SystemRelativeTime){throw 'missing timestamp; cannot measure without copying pixels'}
     $ticks=[long]$f.SystemRelativeTime.Ticks
     if($sourceTicks.Add($ticks)){
      if($sourceArrivals.Count -gt 0 -and $ticks -le $sourceArrivals[$sourceArrivals.Count-1]){throw 'nonmonotonic source timestamp'}
      $arrivals.Add($arrival);$sourceArrivals.Add($ticks)
     }else{$duplicates++}
    }finally{$f.Dispose()}
    $work.Add($sw.Elapsed.TotalMilliseconds-$arrival)
    Start-Sleep -Milliseconds 1
   }
   $sw.Stop();$proc.Refresh();$cpu=$proc.TotalProcessorTime.TotalSeconds-$cpu0
   if($arrivals.Count -lt 2){throw 'insufficient distinct source timestamps'}
   $gaps=@();for($i=1;$i -lt $arrivals.Count;$i++){$gaps+=($arrivals[$i]-$arrivals[$i-1])}
   $sorted=@($gaps|Sort-Object);$wm=($work|Measure-Object -Average -Maximum)
   $row.measurement=[pscustomobject]@{
    requested_window_s=30;elapsed_s=$sw.Elapsed.TotalSeconds;poll_attempts=$attempts
    distinct_timestamp_frames=$arrivals.Count;duplicate_timestamp_acquisitions=$duplicates;null_acquisitions=$nulls
    unique_timestamp_arrival_fps=($arrivals.Count-1)*1000/($arrivals[$arrivals.Count-1]-$arrivals[0])
    unique_timestamp_arrival_span_s=($arrivals[$arrivals.Count-1]-$arrivals[0])/1000
    p95_arrival_gap_ms=$sorted[[int][Math]::Floor(($sorted.Count-1)*0.95)];max_arrival_gap_ms=$sorted[-1]
    observer_metadata_mean_ms=$wm.Average;observer_metadata_max_ms=$wm.Maximum
    observer_process_cpu_seconds=$cpu;unique_system_timestamps=$sourceTicks.Count;null_system_timestamps=$nullTimestamps
    source_timestamp_fps=($sourceArrivals.Count-1)*10000000/($sourceArrivals[$sourceArrivals.Count-1]-$sourceArrivals[0])
    source_timestamp_span_s=($sourceArrivals[$sourceArrivals.Count-1]-$sourceArrivals[0])/10000000
    full_payload_copied_or_hashed=$false;pixel_content_uniqueness_tested=$false
    sensor_sequence_gaps_proven=$false;driver_cpu_usage_measured=$false
   }
   $sourceArrivals.Clear();$sourceTicks.Clear()
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
 $out=[pscustomobject]@{experiment='E004ky';kind='Windows RGB low-overhead source-timestamp delivery timing';pixel_files_or_hashes_exported=$false;ir_activated=$false;controls_modified=$false;scene_controlled_or_matched=$false;frame_uniqueness='monotonic unique system timestamps; no pixel-content uniqueness claim';fps_semantics='source timestamp cadence and monotonic arrival rate; not physical sensor maximum';results=@($records.ToArray());automatic_return_reboot_scheduled=$true}
 $json=$out|ConvertTo-Json -Depth 10
 [IO.File]::WriteAllText((Join-Path $root 'RESULT.json'),$json,[Text.Encoding]::UTF8)
 Write-Output $json
}
