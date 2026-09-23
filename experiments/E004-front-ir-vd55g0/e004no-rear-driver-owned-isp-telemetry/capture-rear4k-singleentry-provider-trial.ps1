# E004no NEW source-only guid-candidate driver telemetry correlation; ONE camera acquisition; no image bytes read or saved.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[void][Windows.Media.Capture.Frames.MediaFrameSourceGroup,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameReader,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCapture,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCaptureInitializationSettings,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCaptureMemoryPreference,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.StreamingCaptureMode,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameReaderStartStatus,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$marker=Join-Path $root 'E004NO-rear4k-driver-etw-single-entry.consumed'
$marker_stream=$null
try {
  $marker_stream=[IO.File]::Open($marker,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
  $marker_bytes=[Text.Encoding]::UTF8.GetBytes('E004NO-REAR4K-ENTRY-UTC='+[DateTimeOffset]::UtcNow.ToString('o')+[Environment]::NewLine)
  $marker_stream.Write($marker_bytes,0,$marker_bytes.Length)
  $marker_stream.Flush($true)
} catch {
  throw 'E004NO_CAMERA_EXPERIMENT_ALREADY_CONSUMED_OR_UNCERTAIN'
} finally { if($marker_stream){$marker_stream.Dispose()} }

$stamp = (Get-Date -Format 'yyyyMMdd-HHmmss')
$path = Join-Path $root ('E004NO-rear-video4k-' + $stamp + '.json')
$records = New-Object 'System.Collections.Generic.List[object]'
function Await-Result($op,[Type]$type) {
  $meth = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 } | Select-Object -First 1
  $task = $meth.MakeGenericMethod($type).Invoke($null,@($op))
  if (-not $task.Wait(30000)) { throw 'WinRT operation timed out at 30 seconds' }
  return $task.Result
}
function Await-Action($op) {
  $meth = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and -not $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 } | Select-Object -First 1
  $task = $meth.Invoke($null,@($op))
  if (-not $task.Wait(30000)) { throw 'WinRT action timed out at 30 seconds' }
}
$groups = Await-Result ([Windows.Media.Capture.Frames.MediaFrameSourceGroup]::FindAllAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Media.Capture.Frames.MediaFrameSourceGroup]])
foreach ($name in @('Surface Camera Rear')) {
  $group = $groups | Where-Object { $_.DisplayName -eq $name } | Select-Object -First 1
  if (-not $group) { $records.Add([pscustomobject]@{group=$name; error='missing camera group'}); continue }
  $mc=$null
  try {
    $settings = New-Object Windows.Media.Capture.MediaCaptureInitializationSettings
    $settings.SourceGroup = $group
    $settings.StreamingCaptureMode = [Windows.Media.Capture.StreamingCaptureMode]::Video
    $settings.MemoryPreference = [Windows.Media.Capture.MediaCaptureMemoryPreference]::Cpu
    $mc = New-Object Windows.Media.Capture.MediaCapture
    Await-Action ($mc.InitializeAsync($settings))
    Write-Output ('OPENED_GROUP=' + $name)
    $sources=@(); foreach($entry in $mc.FrameSources){ $v=$entry.Value; if($null -ne $v -and $null -ne $v.Info -and $v.Info.SourceKind.ToString() -eq 'Color' -and $v.Info.MediaStreamType.ToString() -eq 'VideoRecord'){ $sources += $v } }; Write-Output ('RGB_SOURCE_COUNT=' + $name + ' ' + $sources.Count)
    foreach($src in $sources){
      $formats=@()
      foreach($fmt in $src.SupportedFormats){
        $vf=$fmt.VideoFormat
        $formats+= [pscustomobject]@{
          subtype=[string]$fmt.Subtype; width=[int]$vf.Width; height=[int]$vf.Height
          fps_num=[uint32]$fmt.FrameRate.Numerator; fps_den=[uint32]$fmt.FrameRate.Denominator
        }
      }
      $vf=$src.CurrentFormat.VideoFormat
      if ([int]$vf.Width -ne 3840 -or [int]$vf.Height -ne 2160 -or [string]$src.CurrentFormat.Subtype -ne 'NV12') { throw 'E004NM fail closed: rear VideoRecord is not native NV12 3840x2160' }
      $base=[ordered]@{
        group=$name; source_kind=[string]$src.Info.SourceKind; stream=[string]$src.Info.MediaStreamType
        default_subtype=[string]$src.CurrentFormat.Subtype; default_width=[int]$vf.Width; default_height=[int]$vf.Height
        supported_formats=$formats; start_status=$null; samples=@(); error=$null
      }
      $reader=$null
      try {
        $reader=Await-Result ($mc.CreateFrameReaderAsync($src)) ([Windows.Media.Capture.Frames.MediaFrameReader])
        $status=Await-Result ($reader.StartAsync()) ([Windows.Media.Capture.Frames.MediaFrameReaderStartStatus])
        $base.start_status=[string]$status
        if ($status.ToString() -eq 'Success') {
          Set-Content -LiteralPath (Join-Path $root 'E004NO-REAR4K-LIVE.txt') -Value ('REAR_VIDEORECORD_NV12_3840x2160_LIVE=' + (Get-Date -Format o)) -Encoding Ascii
          $clock=[Diagnostics.Stopwatch]::StartNew()
          $seen=0
          while($clock.Elapsed.TotalSeconds -lt 15 -and $seen -lt 350) {
            $f=$reader.TryAcquireLatestFrame()
            if($null -ne $f) {
              try{
                $seen++
                $vmf=$f.VideoMediaFrame
                $vfmt=$vmf.VideoFormat
                $sb=$vmf.SoftwareBitmap
                $base.samples+= [pscustomobject]@{
                  elapsed_ms=[int]$clock.ElapsedMilliseconds; system_time_ticks=if($f.SystemRelativeTime.HasValue){[int64]$f.SystemRelativeTime.Value.Ticks}else{$null}
                  duration_ticks=if($f.Duration.HasValue){[int64]$f.Duration.Value.Ticks}else{$null}
                  width=if($vfmt){[int]$vfmt.Width}else{$null};height=if($vfmt){[int]$vfmt.Height}else{$null}
                  software_bitmap=($null -ne $sb); bitmap_format=if($sb){[string]$sb.BitmapPixelFormat}else{$null}
                  bitmap_width=if($sb){[int]$sb.PixelWidth}else{$null}; bitmap_height=if($sb){[int]$sb.PixelHeight}else{$null}
                }
              } finally { $f.Dispose() }
            }
            Start-Sleep -Milliseconds 30
          }
        }
      } catch { $base.error=$_.Exception.ToString(); Write-Output ('STREAM_ERROR='+$name+' '+$base.stream+' '+$_.Exception.Message) }
      finally {
        if($reader) {
          try{Await-Action ($reader.StopAsync())}catch{}
          try{$reader.Dispose()}catch{}
        }
      }
      $records.Add([pscustomobject]$base)
      Write-Output ('RGB_RESULT={0} STREAM={1} DEFAULT={2} {3}x{4} FORMATS={5} START={6} SAMPLES={7}' -f $name,$base.stream,$base.default_subtype,$base.default_width,$base.default_height,$formats.Count,$base.start_status,$base.samples.Count)
      foreach ($a in $formats) { Write-Output ('RGB_FORMAT={0} STREAM={1} {2} {3}x{4} {5}/{6}' -f $name,$base.stream,$a.subtype,$a.width,$a.height,$a.fps_num,$a.fps_den) }
    }
  } catch { $records.Add([pscustomobject]@{group=$name;error=$_.Exception.ToString()}); Write-Output ('GROUP_ERROR='+$name+' '+$_.Exception.Message) }
  finally {if($mc){try{$mc.Dispose()}catch{}}}
}
$out=[pscustomobject]@{created=(Get-Date -Format o);machine=$env:COMPUTERNAME;kind='Windows RGB-only MediaFrameSource inventory and frame metadata, no image saved';results=@($records.ToArray())}
$out | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $path -Encoding UTF8
Set-Content -LiteralPath (Join-Path $root 'E004NO-REAR4K-DONE.txt') -Value ('E004NO_REAR4K_DONE=' + $path) -Encoding Ascii
Write-Output ('E004NO_REAR4K_METADATA_JSON='+$path)
