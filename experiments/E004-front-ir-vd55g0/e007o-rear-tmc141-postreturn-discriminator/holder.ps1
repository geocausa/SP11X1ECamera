$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[void][Windows.Media.Capture.Frames.MediaFrameSourceGroup,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCapture,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCaptureInitializationSettings,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCaptureMemoryPreference,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.StreamingCaptureMode,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameReader,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameReaderStartStatus,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]

function Await-Op($op,[Type]$type){
  $m=[System.WindowsRuntimeSystemExtensions].GetMethods() |
    Where-Object{$_.Name-eq'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count-eq1} |
    Select-Object -First 1
  $t=$m.MakeGenericMethod($type).Invoke($null,@($op))
  if(-not $t.Wait(30000)){throw 'E007O WinRT generic operation timeout'}
  $t.Result
}
function Await-Action($op){
  $m=[System.WindowsRuntimeSystemExtensions].GetMethods() |
    Where-Object{$_.Name-eq'AsTask' -and -not $_.IsGenericMethod -and $_.GetParameters().Count-eq1} |
    Select-Object -First 1
  $t=$m.Invoke($null,@($op))
  if(-not $t.Wait(30000)){throw 'E007O WinRT action timeout'}
}
function Stamp($s){"{0:O} {1}" -f [DateTime]::UtcNow,$s}

$base='C:\Users\Geoca\Documents\E007O'
$go="$base-START.GO"
$ready="$base-READY"
$done="$base-DONE"
$log="$base-holder.log"
New-Item $base -ItemType Directory -Force | Out-Null

$entry=Join-Path $base 'SCRIPT-ENTRY-CONSUMED.marker'
$fh=$null
try {
  $fh=[IO.File]::Open($entry,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
  $b=[Text.Encoding]::UTF8.GetBytes('E007O_ATOMIC_ENTRY_UTC='+[DateTimeOffset]::UtcNow.ToString('o')+[Environment]::NewLine)
  $fh.Write($b,0,$b.Length);$fh.Flush($true)
} catch { throw 'E007O_SCRIPT_ENTRY_ALREADY_CONSUMED_OR_UNCERTAIN' }
finally {if($fh){$fh.Dispose()}}

Remove-Item $go,$ready,$done -Force -ErrorAction SilentlyContinue
$mc=$null;$reader=$null;$valid=0
try {
  Stamp 'E007O_HOLDER_BEGIN' | Tee-Object -FilePath $log -Append
  $groups=Await-Op ([Windows.Media.Capture.Frames.MediaFrameSourceGroup]::FindAllAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Media.Capture.Frames.MediaFrameSourceGroup]])
  $rear=@($groups|Where-Object DisplayName -eq 'Surface Camera Rear')
  if($rear.Count-ne1){throw 'E007O unique Surface Camera Rear group absent'}
  $settings=New-Object Windows.Media.Capture.MediaCaptureInitializationSettings
  $settings.SourceGroup=$rear[0]
  $settings.StreamingCaptureMode=[Windows.Media.Capture.StreamingCaptureMode]::Video
  $settings.MemoryPreference=[Windows.Media.Capture.MediaCaptureMemoryPreference]::Cpu
  $mc=New-Object Windows.Media.Capture.MediaCapture
  Stamp 'INIT_BEGIN' | Tee-Object -FilePath $log -Append
  Await-Action ($mc.InitializeAsync($settings))
  Stamp 'INIT_PASS' | Tee-Object -FilePath $log -Append

  $sources=@()
  foreach($kv in $mc.FrameSources){
    $s=$kv.Value
    if($null-ne$s -and $null-ne$s.Info -and
       $s.Info.SourceKind.ToString()-eq'Color' -and
       $s.Info.MediaStreamType.ToString()-eq'VideoRecord'){$sources+=$s}
  }
  if($sources.Count-ne1){throw 'E007O unique rear Color VideoRecord source absent'}
  $src=$sources[0]
  $fmt=$src.CurrentFormat
  if([string]$fmt.Subtype-ne'NV12' -or
     [int]$fmt.VideoFormat.Width-ne3840 -or [int]$fmt.VideoFormat.Height-ne2160){
    throw 'E007O rear source is not OEM NV12 3840x2160'
  }

  $reader=Await-Op ($mc.CreateFrameReaderAsync($src)) ([Windows.Media.Capture.Frames.MediaFrameReader])
  New-Item $ready -ItemType File -Force|Out-Null
  Stamp 'WAIT_START REAR_COLOR_VIDEORECORD_NV12_3840x2160' | Tee-Object -FilePath $log -Append

  $wait=[Diagnostics.Stopwatch]::StartNew()
  while(-not(Test-Path $go)){
    if($wait.Elapsed.TotalSeconds-gt300){throw 'E007O START.GO timeout'}
    Start-Sleep -Milliseconds 10
  }

  Stamp 'START_BEGIN' | Tee-Object -FilePath $log -Append
  $st=Await-Op ($reader.StartAsync()) ([Windows.Media.Capture.Frames.MediaFrameReaderStartStatus])
  Stamp ("START_STATUS=$st") | Tee-Object -FilePath $log -Append
  if($st.ToString()-ne'Success'){throw 'E007O rear reader start failed'}

  $clock=[Diagnostics.Stopwatch]::StartNew()
  while($clock.Elapsed.TotalSeconds-lt5){
    $f=$reader.TryAcquireLatestFrame()
    if($null-ne$f){
      try{
        $v=$f.VideoMediaFrame
        if($null-ne$v -and $null-ne$v.VideoFormat -and
           [int]$v.VideoFormat.Width-eq3840 -and [int]$v.VideoFormat.Height-eq2160){$valid++}
      } finally {$f.Dispose()}
    }
    Start-Sleep -Milliseconds 15
  }
  if($valid-lt10){throw "E007O insufficient rear4k handles: $valid"}

  Stamp 'STOP_BEGIN' | Tee-Object -FilePath $log -Append
  Await-Action ($reader.StopAsync())
  Stamp ("STOP_PASS valid_4k_handles=$valid") | Tee-Object -FilePath $log -Append
  $reader.Dispose();$reader=$null
  $mc.Dispose();$mc=$null
  New-Item $done -ItemType File -Force|Out-Null
  Stamp 'E007O_HOLDER_END' | Tee-Object -FilePath $log -Append
} finally {
  if($reader){try{Await-Action ($reader.StopAsync())}catch{};try{$reader.Dispose()}catch{}}
  if($mc){try{$mc.Dispose()}catch{}}
}