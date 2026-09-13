$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[void][Windows.Media.Capture.Frames.MediaFrameSourceGroup,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCapture,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCaptureInitializationSettings,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.StreamingCaptureMode,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameReader,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameReaderStartStatus,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]

function Await-Op($op,[Type]$type){
    $m=[System.WindowsRuntimeSystemExtensions].GetMethods()|?{$_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1}|select -First 1
    $t=$m.MakeGenericMethod($type).Invoke($null,@($op)); $t.Wait(); $t.Result
}
function Await-Action($op){
    $m=[System.WindowsRuntimeSystemExtensions].GetMethods()|?{$_.Name -eq 'AsTask' -and -not $_.IsGenericMethod -and $_.GetParameters().Count -eq 1}|select -First 1
    $t=$m.Invoke($null,@($op)); $t.Wait()
}
function Put-U32([byte[]]$b,[int]$o,[uint32]$v){ [Array]::Copy([BitConverter]::GetBytes($v),0,$b,$o,4) }
function Put-U64([byte[]]$b,[int]$o,[uint64]$v){ [Array]::Copy([BitConverter]::GetBytes($v),0,$b,$o,8) }
function New-KsProperty([uint32]$id,[uint32]$flags){
    $b=New-Object byte[] 24
    $g=([Guid]'1CB79112-C0D2-4213-9CA6-CD4FDB927972').ToByteArray()
    [Array]::Copy($g,0,$b,0,16)
    Put-U32 $b 16 $id
    Put-U32 $b 20 $flags
    return $b
}
function New-ExtendedHeader([uint64]$flags){
    $b=New-Object byte[] 40
    Put-U32 $b 0 1
    Put-U32 $b 4 ([uint32]::MaxValue)
    Put-U32 $b 8 40
    Put-U32 $b 12 0
    Put-U64 $b 16 $flags
    Put-U64 $b 24 0
    Put-U64 $b 32 0
    return $b
}
function Hex-Bytes($v){
    if($null -eq $v){ return '<null>' }
    try {
        $a=[byte[]]$v
        return (($a|%{$_.ToString('x2')}) -join '')
    } catch {
        return ('<type='+$v.GetType().FullName+'>')
    }
}
function Get-SecureMode($ctl,[string]$tag){
    $id=New-KsProperty 36 1
    [Nullable[uint32]]$max=40
    $r=$ctl.GetDevicePropertyByExtendedId($id,$max)
    $type=if($null -eq $r.Value){'<null>'}else{$r.Value.GetType().FullName}
    $hex=Hex-Bytes $r.Value
    Write-Output ("E004AJ_SECUREMODE_GET tag={0} status={1} type={2} value={3}" -f $tag,$r.Status,$type,$hex)
    if($null -ne $r.Value){
        try {
            $a=[byte[]]$r.Value
            if($a.Length -ge 32){
                $version=[BitConverter]::ToUInt32($a,0)
                $pin=[BitConverter]::ToUInt32($a,4)
                $size=[BitConverter]::ToUInt32($a,8)
                $result=[BitConverter]::ToUInt32($a,12)
                $flags=[BitConverter]::ToUInt64($a,16)
                $cap=[BitConverter]::ToUInt64($a,24)
                Write-Output ("E004AJ_SECUREMODE_GET_PARSED tag={0} version={1} pin=0x{2:x8} size={3} result=0x{4:x8} flags=0x{5:x} capability=0x{6:x}" -f $tag,$version,$pin,$size,$result,$flags,$cap)
            }
        } catch {}
    }
    return $r
}
function Set-SecureMode($ctl,[uint64]$mode,[string]$tag){
    $id=New-KsProperty 36 2
    $payload=New-ExtendedHeader $mode
    $s=$ctl.SetDevicePropertyByExtendedId($id,$payload)
    Write-Output ("E004AJ_SECUREMODE_SET tag={0} requested=0x{1:x} status={2} payload={3}" -f $tag,$mode,$s,(Hex-Bytes $payload))
    return $s
}

Write-Output 'E004AJ_BEGIN'
$groups=Await-Op ([Windows.Media.Capture.Frames.MediaFrameSourceGroup]::FindAllAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Media.Capture.Frames.MediaFrameSourceGroup]])
$group=$groups|? DisplayName -eq 'Surface IR Camera Front'|select -First 1
if(-not $group){throw 'Surface IR Camera Front source group not found'}
Write-Output ("E004AJ_GROUP id={0} name={1}" -f $group.Id,$group.DisplayName)

$settings=New-Object Windows.Media.Capture.MediaCaptureInitializationSettings
$settings.SourceGroup=$group
$settings.StreamingCaptureMode=[Windows.Media.Capture.StreamingCaptureMode]::Video
$settings.MemoryPreference=[Windows.Media.Capture.MediaCaptureMemoryPreference]::Cpu
$mc=New-Object Windows.Media.Capture.MediaCapture

Write-Output 'E004AJ_INITIALIZE_BEGIN'
Await-Action ($mc.InitializeAsync($settings))
Write-Output 'E004AJ_INITIALIZE_PASS'
Start-Sleep -Milliseconds 350

$ctl=$mc.VideoDeviceController
Write-Output ("E004AJ_CONTROLLER_ID={0}" -f $ctl.Id)
[void](Get-SecureMode $ctl 'before')
$set=Set-SecureMode $ctl 2 'enable'
Start-Sleep -Milliseconds 150
[void](Get-SecureMode $ctl 'after-enable')

if($set.ToString() -ne 'Success'){ throw "SecureMode enable failed: $set" }

$sources=@(); foreach($kv in $mc.FrameSources){$sources+=$kv.Value}
$src=$sources|?{$_.Info.DeviceInformation.Name -eq 'Surface IR Camera Front' -and $_.Info.SourceKind.ToString() -eq 'Infrared' -and $_.Info.MediaStreamType.ToString() -eq 'VideoPreview'}|select -First 1
if(-not $src){$src=$sources|?{$_.Info.DeviceInformation.Name -eq 'Surface IR Camera Front' -and $_.Info.SourceKind.ToString() -eq 'Infrared'}|select -First 1}
if(-not $src){throw 'No IR source'}

Write-Output ("E004AJ_SELECTED kind={0} stream={1} subtype={2} dims={3}x{4} fps={5}/{6}" -f $src.Info.SourceKind,$src.Info.MediaStreamType,$src.CurrentFormat.Subtype,$src.CurrentFormat.VideoFormat.Width,$src.CurrentFormat.VideoFormat.Height,$src.CurrentFormat.FrameRate.Numerator,$src.CurrentFormat.FrameRate.Denominator)

$reader=Await-Op ($mc.CreateFrameReaderAsync($src)) ([Windows.Media.Capture.Frames.MediaFrameReader])
$status=Await-Op ($reader.StartAsync()) ([Windows.Media.Capture.Frames.MediaFrameReaderStartStatus])
Write-Output ("E004AJ_START_STATUS={0}" -f $status)
if($status.ToString() -ne 'Success'){throw "StartAsync failed: $status"}

$frames=0
$deadline=[DateTime]::UtcNow.AddSeconds(5)
while([DateTime]::UtcNow -lt $deadline -and $frames -lt 12){
    $f=$reader.TryAcquireLatestFrame()
    if($null -ne $f){
        $frames++
        Write-Output ("E004AJ_FRAME n={0} system_relative_time={1}" -f $frames,$f.SystemRelativeTime)
        $f.Dispose()
    }
    Start-Sleep -Milliseconds 25
}
Write-Output ("E004AJ_ACQUIRED={0}" -f $frames)
if($frames -lt 3){ throw "Insufficient acquired frames: $frames" }

Write-Output 'E004AJ_LIVE_GATE'
$gate=[Console]::ReadLine()
Write-Output ("E004AJ_GATE_RELEASE={0}" -f $gate)

Await-Action ($reader.StopAsync())
Write-Output 'E004AJ_STOP_PASS'
$reader.Dispose()

$disable=Set-SecureMode $ctl 1 'disable'
Start-Sleep -Milliseconds 100
[void](Get-SecureMode $ctl 'after-disable')
Write-Output ("E004AJ_DISABLE_STATUS={0}" -f $disable)

$mc.Dispose()
Write-Output 'E004AJ_END'
