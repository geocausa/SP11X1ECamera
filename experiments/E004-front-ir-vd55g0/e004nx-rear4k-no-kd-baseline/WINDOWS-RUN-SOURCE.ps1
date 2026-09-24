# E004nx fresh, one-use Windows Surface Camera Rear NV12 3840x2160 holder
# for physical-only SP7 KD "dd /p" IDLE/LIVE1/POST/LIVE2/POST2 comparisons.
# No pixels, RAW, thumbnail, photo or image hash is read or serialized.
# No future ScheduledTask trigger. Must run in logged-on Geoca session.
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $MyInvocation.MyCommand.Path
$entry=Join-Path $root 'E004NX-SCRIPT-ENTRY-CONSUMED.marker'
$handle=$null
try {
  $handle=[IO.File]::Open($entry,[IO.FileMode]::CreateNew,
    [IO.FileAccess]::Write,[IO.FileShare]::None)
  $bytes=[Text.Encoding]::UTF8.GetBytes(
    ('E004NX_ATOMIC_ENTRY_UTC='+[DateTimeOffset]::UtcNow.ToString('o')+[Environment]::NewLine))
  $handle.Write($bytes,0,$bytes.Length)
  $handle.Flush($true)
} catch { throw 'E004NX_ENTRY_ALREADY_CONSUMED_OR_UNCERTAIN' }
finally { if($handle){$handle.Dispose()} }
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[void][Windows.Media.Capture.Frames.MediaFrameSourceGroup,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameReader,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameReaderStartStatus,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCapture,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCaptureInitializationSettings,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCaptureMemoryPreference,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.StreamingCaptureMode,Windows.Media.Capture,ContentType=WindowsRuntime]
$log=Join-Path $root 'E004NX-WINDOWS-SCALAR-PHASES.txt'
function Mark([string]$name,[string]$message) {
  $now=Get-Date -Format o
  $line='E004NX_'+$name+' '+$now+' '+$message
  Add-Content -LiteralPath $log -Value $line -Encoding UTF8
  $path=Join-Path $root ('E004NX-'+$name+'.txt')
  if(Test-Path -LiteralPath $path){throw ('E004NX_PHASE_MARKER_ALREADY_EXISTS: '+$name)}
  Set-Content -LiteralPath $path -Value $line -Encoding Ascii -NoNewline
  Write-Output $line
}
function Await-Result($op,[Type]$type) {
  $m=[System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 } | Select-Object -First 1
  $task=$m.MakeGenericMethod($type).Invoke($null,@($op))
  if(-not $task.Wait(30000)){throw 'E004NX WinRT generic action timed out'}
  return $task.Result
}
function Await-Action($op) {
  $m=[System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and -not $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 } | Select-Object -First 1
  $task=$m.Invoke($null,@($op))
  if(-not $task.Wait(30000)){throw 'E004NX WinRT action timed out'}
}
function Hold([string]$phase,[int]$maxSeconds,$reader) {
  $clock=[Diagnostics.Stopwatch]::StartNew()
  $count=0
  while($clock.Elapsed.TotalSeconds -lt $maxSeconds) {
    $f=$reader.TryAcquireLatestFrame()
    if($null -ne $f) {
      try {
        $vm=$f.VideoMediaFrame
        if($null -ne $vm -and $null -ne $vm.VideoFormat -and
           [int]$vm.VideoFormat.Width -eq 3840 -and
           [int]$vm.VideoFormat.Height -eq 2160) { $count++ }
      } finally { $f.Dispose() }
    }
    Start-Sleep -Milliseconds 80
  }
  Mark ($phase+'-HOLD-END') ('elapsed_ms='+$clock.ElapsedMilliseconds+
          ' color_3840x2160_frame_handles='+$count) | Out-Null
  return $count
}
$mc=$null
$reader=$null
$counts=@()
try {
  $groups=Await-Result ([Windows.Media.Capture.Frames.MediaFrameSourceGroup]::FindAllAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Media.Capture.Frames.MediaFrameSourceGroup]])
  $groups=@($groups | Where-Object {$_.DisplayName -eq 'Surface Camera Rear'})
  if($groups.Count -ne 1){throw 'E004NX rear group not uniquely found'}
  $settings=New-Object Windows.Media.Capture.MediaCaptureInitializationSettings
  $settings.SourceGroup=$groups[0]
  $settings.StreamingCaptureMode=[Windows.Media.Capture.StreamingCaptureMode]::Video
  $settings.MemoryPreference=[Windows.Media.Capture.MediaCaptureMemoryPreference]::Cpu
  $mc=New-Object Windows.Media.Capture.MediaCapture
  Await-Action ($mc.InitializeAsync($settings))
  $sources=@()
  foreach($kv in $mc.FrameSources) {
    $s=$kv.Value
    if($null -ne $s -and $null -ne $s.Info -and
       $s.Info.SourceKind.ToString() -eq 'Color' -and
       $s.Info.MediaStreamType.ToString() -eq 'VideoRecord'){$sources+= $s}
  }
  if($sources.Count -ne 1){throw 'E004NX rear VideoRecord source count not one'}
  $src=$sources[0]
  $fmt=$src.CurrentFormat
  if([string]$fmt.Subtype -ne 'NV12' -or
     [int]$fmt.VideoFormat.Width -ne 3840 -or [int]$fmt.VideoFormat.Height -ne 2160){
    throw 'E004NX unexpected WinRT rear source media type'
  }
  Mark 'READY' 'Surface Camera Rear Color VideoRecord NV12 3840x2160; no reader started'
  for($pass=1;$pass -le 2;$pass++){
    $reader=Await-Result ($mc.CreateFrameReaderAsync($src)) ([Windows.Media.Capture.Frames.MediaFrameReader])
    $status=Await-Result ($reader.StartAsync()) ([Windows.Media.Capture.Frames.MediaFrameReaderStartStatus])
    if([string]$status -ne 'Success'){throw ('E004NX StartAsync pass '+$pass+' status '+$status)}
    Mark ('LIVE'+$pass) 'StartAsync=Success; NO_KD baseline sampler running'
    $counts+=Hold ('LIVE'+$pass) 35 $reader
    Await-Action ($reader.StopAsync())
    $reader.Dispose()
    $reader=$null
    Mark ('POST'+$pass) 'StopAsync=Success and reader disposed'
    if($pass -eq 1){ Start-Sleep -Seconds 3 }
  }
  if($counts.Count -ne 2 -or $counts[0] -lt 10 -or $counts[1] -lt 10){
    throw 'E004NX rear live client delivery insufficient for trusted KD phases'
  }
  Mark 'DONE' ('passes=2 frame_handles1='+$counts[0]+' frame_handles2='+$counts[1])
} catch {
  Add-Content -LiteralPath $log -Value ('E004NX_ERROR '+(Get-Date -Format o)+' '+$_.Exception.Message) -Encoding UTF8
  throw
} finally {
  if($reader){try{Await-Action ($reader.StopAsync())}catch{};try{$reader.Dispose()}catch{}}
  if($mc){try{$mc.Dispose()}catch{}}
}
