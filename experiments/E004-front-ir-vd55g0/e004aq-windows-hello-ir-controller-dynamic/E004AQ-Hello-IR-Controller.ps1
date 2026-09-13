$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[void][Windows.Media.Capture.MediaCapture,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCaptureInitializationSettings,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.StreamingCaptureMode,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.MediaCaptureMemoryPreference,Windows.Media.Capture,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameSourceGroup,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameReader,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameReaderStartStatus,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameSourceGetPropertyResult,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Media.Capture.Frames.MediaFrameSourceSetPropertyStatus,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
[void][Windows.Foundation.PropertyValue,Windows.Foundation,ContentType=WindowsRuntime]

function Await-Op($op,[Type]$type){
    $m=[System.WindowsRuntimeSystemExtensions].GetMethods()|?{$_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1}|select -First 1
    $t=$m.MakeGenericMethod($type).Invoke($null,@($op)); $t.Wait(); $t.Result
}
function Await-Action($op){
    $m=[System.WindowsRuntimeSystemExtensions].GetMethods()|?{$_.Name -eq 'AsTask' -and -not $_.IsGenericMethod -and $_.GetParameters().Count -eq 1}|select -First 1
    $t=$m.Invoke($null,@($op)); $t.Wait()
}
function Hex-Bytes([byte[]]$a){ if($null -eq $a){return '<null>'}; (($a|%{$_.ToString('x2')}) -join '') }
function Put-U64([byte[]]$b,[int]$o,[uint64]$v){ [Array]::Copy([BitConverter]::GetBytes($v),0,$b,$o,8) }
function Clone-Bytes([byte[]]$a){ $b=New-Object byte[] $a.Length; [Array]::Copy($a,0,$b,0,$a.Length); return $b }
function To-Bytes($v){
    if($null -eq $v){ return $null }
    try { return [byte[]]$v } catch {}
    try {
        [byte[]]$out=$null
        $v.GetUInt8Array([ref]$out)
        return $out
    } catch {
        Write-Host ("E004AQ_VALUE_CAST_ERROR type={0} message={1}" -f $v.GetType().FullName,$_.Exception.Message)
        return $null
    }
}
function Parse-Extended([byte[]]$a,[string]$tag){
    if($null -eq $a -or $a.Length -lt 40){
        Write-Host ("E004AQ_PARSE tag={0} len={1} INVALID" -f $tag,($(if($null -eq $a){0}else{$a.Length})))
        return $null
    }
    $o=[pscustomobject]@{
        Version=[BitConverter]::ToUInt32($a,0)
        PinId=[BitConverter]::ToUInt32($a,4)
        Size=[BitConverter]::ToUInt32($a,8)
        Result=[BitConverter]::ToUInt32($a,12)
        Flags=[BitConverter]::ToUInt64($a,16)
        Capability=[BitConverter]::ToUInt64($a,24)
        Tail=[BitConverter]::ToUInt64($a,32)
    }
    Write-Host ("E004AQ_PARSE tag={0} version={1} pin=0x{2:x8} size={3} result=0x{4:x8} flags=0x{5:x} capability=0x{6:x} tail=0x{7:x}" -f $tag,$o.Version,$o.PinId,$o.Size,$o.Result,$o.Flags,$o.Capability,$o.Tail)
    return $o
}
function Get-Prop($controller,[string]$id,[string]$tag){
    $r=Await-Op ($controller.GetPropertyAsync($id)) ([Windows.Media.Capture.Frames.MediaFrameSourceGetPropertyResult])
    $a=To-Bytes $r.Value
    Write-Host ("E004AQ_GET tag={0} id={1} status={2} len={3} value={4}" -f $tag,$id,$r.Status,($(if($null -eq $a){0}else{$a.Length})),($(if($null -eq $a){'<null>'}else{Hex-Bytes $a})))
    $p=Parse-Extended $a $tag
    return [pscustomobject]@{Result=$r;Bytes=$a;Parsed=$p}
}
function Set-Flags($controller,[string]$id,[byte[]]$from,[uint64]$flags,[string]$tag){
    if($null -eq $from -or $from.Length -lt 40){ throw "No valid 40-byte GET buffer for $tag" }
    [byte[]]$b=New-Object byte[] $from.Length; [Array]::Copy($from,0,$b,0,$from.Length)
    $before=Hex-Bytes $b
    [Array]::Copy([BitConverter]::GetBytes($flags),0,$b,16,8)
    $boxed=[Windows.Foundation.PropertyValue]::CreateUInt8Array($b)
    $s=Await-Op ($controller.SetPropertyAsync($id,$boxed)) ([Windows.Media.Capture.Frames.MediaFrameSourceSetPropertyStatus])
    Write-Host ("E004AQ_SET tag={0} id={1} requested_flags=0x{2:x} status={3} before={4} after={5}" -f $tag,$id,$flags,$s,$before,(Hex-Bytes $b))
    return $s
}

$FaceId='{1CB79112-C0D2-4213-9CA6-CD4FDB927972},35'
$SecureId='{1CB79112-C0D2-4213-9CA6-CD4FDB927972},36'
$mc=$null; $reader=$null; $controller=$null; $faceEnabled=$false; $secureEnabled=$false
Write-Output 'E004AQ_BEGIN'
try {
    $groups=Await-Op ([Windows.Media.Capture.Frames.MediaFrameSourceGroup]::FindAllAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Media.Capture.Frames.MediaFrameSourceGroup]])
    $g=$groups|? DisplayName -eq 'Surface IR Camera Front'|select -First 1
    if(-not $g){throw 'Surface IR Camera Front source group missing'}
    $profiles=[Windows.Media.Capture.MediaCapture]::FindAllVideoProfiles($g.Id)
    $face=$profiles|?{$_.Id -like '{81361B22-700B-4546-A2D4-C52E907BFC27},0'}|select -First 1
    if(-not $face){throw 'FaceAuth profile missing'}
    $desc=$face.SupportedPreviewMediaDescription|?{$_.Subtype -eq 'NV12' -and $_.Width -eq 644 -and $_.Height -eq 604}|select -First 1
    if(-not $desc){$desc=$face.SupportedPreviewMediaDescription|select -First 1}
    Write-Output ("E004AQ_PROFILE id={0} subtype={1} dims={2}x{3} fps={4}" -f $face.Id,$desc.Subtype,$desc.Width,$desc.Height,$desc.FrameRate)

    $settings=New-Object Windows.Media.Capture.MediaCaptureInitializationSettings
    $settings.VideoDeviceId=$face.VideoDeviceId
    $settings.VideoProfile=$face
    $settings.PreviewMediaDescription=$desc
    $settings.StreamingCaptureMode=[Windows.Media.Capture.StreamingCaptureMode]::Video
    $settings.MemoryPreference=[Windows.Media.Capture.MediaCaptureMemoryPreference]::Cpu
    $mc=New-Object Windows.Media.Capture.MediaCapture
    Write-Output 'E004AQ_INIT_BEGIN'
    Await-Action ($mc.InitializeAsync($settings))
    Write-Output 'E004AQ_INIT_PASS'

    $sources=@(); foreach($kv in $mc.FrameSources){$sources+=$kv.Value}
    $src=$sources|?{$_.Info.DeviceInformation.Name -eq 'Surface IR Camera Front' -and $_.Info.SourceKind.ToString() -eq 'Infrared' -and $_.Info.MediaStreamType.ToString() -eq 'VideoPreview'}|select -First 1
    if(-not $src){$src=$sources|?{$_.Info.SourceKind.ToString() -eq 'Infrared'}|select -First 1}
    if(-not $src){throw 'IR source missing'}
    Write-Output ("E004AQ_SOURCE kind={0} stream={1} subtype={2} dims={3}x{4} fps={5}/{6}" -f $src.Info.SourceKind,$src.Info.MediaStreamType,$src.CurrentFormat.Subtype,$src.CurrentFormat.VideoFormat.Width,$src.CurrentFormat.VideoFormat.Height,$src.CurrentFormat.FrameRate.Numerator,$src.CurrentFormat.FrameRate.Denominator)
    $controller=$src.Controller
    if($null -eq $controller){throw 'IR MediaFrameSource.Controller is null'}
    Write-Output ("E004AQ_CONTROLLER type={0}" -f $controller.GetType().FullName)

    $fg=Get-Prop $controller $FaceId 'face-before'
    if($null -eq $fg.Parsed){throw 'FaceAuthMode GET did not return 40-byte payload'}
    if(($fg.Parsed.Capability -band 2) -ne 0){$faceFlag=[uint64]2}
    elseif(($fg.Parsed.Capability -band 4) -ne 0){$faceFlag=[uint64]4}
    else{throw ("FaceAuthMode capability lacks supported enable bit: 0x{0:x}" -f $fg.Parsed.Capability)}
    $fs=Set-Flags $controller $FaceId $fg.Bytes $faceFlag 'face-enable'
    if($fs.ToString() -ne 'Success'){throw "FaceAuthMode enable failed: $fs"}
    $faceEnabled=$true
    Start-Sleep -Milliseconds 100
    [void](Get-Prop $controller $FaceId 'face-after-enable')

    $sg=Get-Prop $controller $SecureId 'secure-before'
    if($null -eq $sg.Parsed){throw 'SecureMode GET did not return 40-byte payload'}
    if(($sg.Parsed.Capability -band 2) -eq 0){throw ("SecureMode capability bit 1 absent: 0x{0:x}" -f $sg.Parsed.Capability)}
    $ss=Set-Flags $controller $SecureId $sg.Bytes ([uint64]2) 'secure-enable'
    if($ss.ToString() -ne 'Success'){throw "SecureMode enable failed: $ss"}
    $secureEnabled=$true
    Start-Sleep -Milliseconds 150
    [void](Get-Prop $controller $SecureId 'secure-after-enable')

    $reader=Await-Op ($mc.CreateFrameReaderAsync($src)) ([Windows.Media.Capture.Frames.MediaFrameReader])
    $start=Await-Op ($reader.StartAsync()) ([Windows.Media.Capture.Frames.MediaFrameReaderStartStatus])
    Write-Output ("E004AQ_START={0}" -f $start)
    if($start.ToString() -ne 'Success'){throw "StartAsync failed: $start"}
    $frames=0; $deadline=[DateTime]::UtcNow.AddSeconds(5)
    while([DateTime]::UtcNow -lt $deadline -and $frames -lt 12){
        $f=$reader.TryAcquireLatestFrame()
        if($null -ne $f){$frames++; Write-Output ("E004AQ_FRAME n={0} time={1}" -f $frames,$f.SystemRelativeTime); $f.Dispose()}
        Start-Sleep -Milliseconds 25
    }
    Write-Output ("E004AQ_ACQUIRED={0}" -f $frames)
    if($frames -lt 3){throw "Insufficient frames: $frames"}
    [void](Get-Prop $controller $SecureId 'secure-during-stream')
    Write-Output 'E004AQ_LIVE_GATE'
    $gate=[Console]::ReadLine()
    Write-Output ("E004AQ_GATE_RELEASE={0}" -f $gate)
}
finally {
    if($null -ne $reader){
        try { Await-Action ($reader.StopAsync()); Write-Output 'E004AQ_STOP_PASS' } catch { Write-Output ("E004AQ_STOP_ERROR="+$_.Exception.Message) }
        try { $reader.Dispose() } catch {}
    }
    if($null -ne $controller){
        if($secureEnabled){
            try {
                $g=Get-Prop $controller $SecureId 'secure-pre-disable'
                if($null -ne $g.Parsed){ $s=Set-Flags $controller $SecureId $g.Bytes ([uint64]1) 'secure-disable'; Write-Output ("E004AQ_SECURE_DISABLE={0}" -f $s); Start-Sleep -Milliseconds 100; [void](Get-Prop $controller $SecureId 'secure-after-disable') }
            } catch { Write-Output ("E004AQ_SECURE_DISABLE_ERROR="+$_.Exception.Message) }
        }
        if($faceEnabled){
            try {
                $g=Get-Prop $controller $FaceId 'face-pre-disable'
                if($null -ne $g.Parsed){ $s=Set-Flags $controller $FaceId $g.Bytes ([uint64]1) 'face-disable'; Write-Output ("E004AQ_FACE_DISABLE={0}" -f $s); Start-Sleep -Milliseconds 100; [void](Get-Prop $controller $FaceId 'face-after-disable') }
            } catch { Write-Output ("E004AQ_FACE_DISABLE_ERROR="+$_.Exception.Message) }
        }
    }
    if($null -ne $mc){ try{$mc.Dispose()}catch{} }
    Write-Output 'E004AQ_END'
}




