$ErrorActionPreference='Stop'
if($env:COMPUTERNAME -ne 'DESKTOP-AQ4SMTC'){throw 'SP11 only'}
$root=Split-Path -Parent $MyInvocation.MyCommand.Path
if(-not (Get-Acl $root).AreAccessRulesProtected){throw 'private ACL required'}
$f=[IO.File]::Open((Join-Path $root 'CONSUMED.txt'),[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
try{$b=[Text.Encoding]::UTF8.GetBytes([DateTime]::UtcNow.ToString('o'));$f.Write($b,0,$b.Length);$f.Flush($true)}finally{$f.Dispose()}
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[void][Windows.Media.Capture.Frames.MediaFrameSourceGroup,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCapture,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCaptureInitializationSettings,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCaptureMemoryPreference,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.StreamingCaptureMode,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameReader,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameReaderStartStatus,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
function Await-Op($op,[Type]$type){
 $m=[System.WindowsRuntimeSystemExtensions].GetMethods()|Where-Object{$_.Name-eq'AsTask'-and $_.IsGenericMethod-and $_.GetParameters().Count-eq1}|Select-Object -First 1
 $t=$m.MakeGenericMethod($type).Invoke($null,@($op));if(-not $t.Wait(120000)){throw 'WinRT operation timeout'};$t.Result
}
function Await-Action($op){
 $m=[System.WindowsRuntimeSystemExtensions].GetMethods()|Where-Object{$_.Name-eq'AsTask'-and -not $_.IsGenericMethod-and $_.GetParameters().Count-eq1}|Select-Object -First 1
 $t=$m.Invoke($null,@($op));if(-not $t.Wait(120000)){throw 'WinRT action timeout'}
}
function Phase($name){[IO.File]::WriteAllText((Join-Path $root 'PHASE.txt'),$name)}
$mc=$null;$reader=$null;$valid=0;$distinct=0;$last=$null;$ok=$false;$err=''
try{
 Phase 'INITIALIZING_REAR_ONLY'
 $groups=Await-Op ([Windows.Media.Capture.Frames.MediaFrameSourceGroup]::FindAllAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Media.Capture.Frames.MediaFrameSourceGroup]])
 $rear=@($groups|Where-Object DisplayName -eq 'Surface Camera Rear');if($rear.Count-ne1){throw 'unique rear required'}
 $settings=New-Object Windows.Media.Capture.MediaCaptureInitializationSettings
 $settings.SourceGroup=$rear[0];$settings.StreamingCaptureMode=[Windows.Media.Capture.StreamingCaptureMode]::Video;$settings.MemoryPreference=[Windows.Media.Capture.MediaCaptureMemoryPreference]::Cpu
 $mc=New-Object Windows.Media.Capture.MediaCapture;Await-Action ($mc.InitializeAsync($settings))
 $sources=@();foreach($kv in $mc.FrameSources){$s=$kv.Value;if($s.Info.SourceKind.ToString()-eq'Color'-and $s.Info.MediaStreamType.ToString()-eq'VideoRecord'){$sources+=$s}}
 if($sources.Count-ne1){throw 'unique Color VideoRecord required'};$src=$sources[0];$fmt=$src.CurrentFormat
 if([string]$fmt.Subtype-ne'NV12'-or [int]$fmt.VideoFormat.Width-ne3840-or [int]$fmt.VideoFormat.Height-ne2160){throw 'exact rear4K NV12 required'}
 $reader=Await-Op ($mc.CreateFrameReaderAsync($src)) ([Windows.Media.Capture.Frames.MediaFrameReader])
 Phase 'READY';
 $deadline=[DateTime]::UtcNow.AddSeconds(120);while(-not(Test-Path (Join-Path $root 'START.GO'))){if([DateTime]::UtcNow -gt $deadline){throw 'start coordination timeout'};Start-Sleep -Milliseconds 100}
 Phase 'STARTING'
 $st=Await-Op ($reader.StartAsync()) ([Windows.Media.Capture.Frames.MediaFrameReaderStartStatus]);if($st.ToString()-ne'Success'){throw 'reader start failed'}
 Phase 'RUNNING'
 $clock=[Diagnostics.Stopwatch]::StartNew()
 while($clock.Elapsed.TotalSeconds-lt60){
  $frame=$reader.TryAcquireLatestFrame()
  if($null-ne$frame){try{
   $v=$frame.VideoMediaFrame
   if($v -and $v.VideoFormat.Width-eq3840-and $v.VideoFormat.Height-eq2160){$valid++;$ts=$frame.SystemRelativeTime;if($ts -and ($null-eq$last-or $ts.Ticks-gt$last)){$distinct++;$last=$ts.Ticks}}
  }finally{$frame.Dispose()}}
  Start-Sleep -Milliseconds 30
 }
 Phase 'STOPPING';Await-Action ($reader.StopAsync());$reader.Dispose();$reader=$null;$mc.Dispose();$mc=$null
 if($distinct-lt10){throw 'insufficient distinct timestamps'};$ok=$true;Phase 'STOPPED'
}catch{$err=$_.Exception.Message;Phase 'FAILED'}
finally{
 if($reader){try{Await-Action ($reader.StopAsync())}catch{};try{$reader.Dispose()}catch{}}
 if($mc){try{$mc.Dispose()}catch{}}
 $result=@{identity='E-NATIVE-REAR-CAMIF-WINDOWS-01';passed=$ok;valid_4k_handles=$valid;distinct_timestamps=$distinct;pixels_read=$false;pixel_files_saved=0;front_opened=$false;error=$err;finished_utc=[DateTime]::UtcNow.ToString('o')}
 [IO.File]::WriteAllText((Join-Path $root 'RESULT.json'),($result|ConvertTo-Json),[Text.Encoding]::UTF8)
 try{Unregister-ScheduledTask -TaskName 'SP11-Native-Rear-CAMIF-Windows-20261008-01' -Confirm:$false -ErrorAction Stop}catch{}
}
if(-not $ok){exit 1}
