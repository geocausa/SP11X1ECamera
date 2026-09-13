$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[void][Windows.Media.Capture.Frames.MediaFrameSourceGroup,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
function Await-Op($op,[Type]$type){$m=[System.WindowsRuntimeSystemExtensions].GetMethods()|?{$_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1}|select -First 1;$t=$m.MakeGenericMethod($type).Invoke($null,@($op));$t.Wait();$t.Result}
Add-Type @'
using System;
using System.Runtime.InteropServices;
using Microsoft.Win32.SafeHandles;
public static class KSRawGet {
  [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
  public static extern SafeFileHandle CreateFile(string name, uint access, uint share, IntPtr sa, uint creation, uint flags, IntPtr template);
  [DllImport("kernel32.dll", SetLastError=true)]
  public static extern bool DeviceIoControl(SafeFileHandle h, uint code, byte[] inBuf, uint inLen, byte[] outBuf, uint outLen, out uint returned, IntPtr overlapped);
}
'@
function Put-U32([byte[]]$b,[int]$o,[uint32]$v){[Array]::Copy([BitConverter]::GetBytes($v),0,$b,$o,4)}
function Put-U64([byte[]]$b,[int]$o,[uint64]$v){[Array]::Copy([BitConverter]::GetBytes($v),0,$b,$o,8)}
function New-KsProperty([uint32]$id,[uint32]$flags){$b=New-Object byte[] 24;$g=([Guid]'1CB79112-C0D2-4213-9CA6-CD4FDB927972').ToByteArray();[Array]::Copy($g,0,$b,0,16);Put-U32 $b 16 $id;Put-U32 $b 20 $flags;return $b}
function New-Out([uint32]$pin){$b=New-Object byte[] 128;Put-U32 $b 0 1;Put-U32 $b 4 $pin;Put-U32 $b 8 56;Put-U32 $b 12 0;Put-U64 $b 16 0;Put-U64 $b 24 0;return $b}
$groups=Await-Op ([Windows.Media.Capture.Frames.MediaFrameSourceGroup]::FindAllAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Media.Capture.Frames.MediaFrameSourceGroup]])
foreach($g in $groups | ?{$_.Id -like '\\?\DISPLAY#QCOM_AVStream_8380*'}){
  $h=[KSRawGet]::CreateFile($g.Id,[Convert]::ToUInt32("C0000000",16),3,[IntPtr]::Zero,3,0,[IntPtr]::Zero)
  if($h.IsInvalid){Write-Output ("E004AJ_RAWGET name={0} OPEN_FAIL err={1}" -f $g.DisplayName,[Runtime.InteropServices.Marshal]::GetLastWin32Error());continue}
  $in=New-KsProperty 36 1
  $pins=@([uint32]0,[Convert]::ToUInt32("FFFFFFFF",16)); foreach($pin in $pins){
    $out=New-Out $pin
    [uint32]$ret=0
    $ok=[KSRawGet]::DeviceIoControl($h,0x002F0003,$in,$in.Length,$out,$out.Length,[ref]$ret,[IntPtr]::Zero)
    $err=[Runtime.InteropServices.Marshal]::GetLastWin32Error()
    $hex=if($ret -gt 0){(($out[0..([Math]::Min([int]$ret-1,95))]|%{$_.ToString('x2')}) -join '')}else{''}
    $v=[BitConverter]::ToUInt32($out,0);$p=[BitConverter]::ToUInt32($out,4);$sz=[BitConverter]::ToUInt32($out,8);$res=[BitConverter]::ToUInt32($out,12);$fl=[BitConverter]::ToUInt64($out,16);$cap=[BitConverter]::ToUInt64($out,24)
    Write-Output ("E004AJ_RAWGET name={0} inpin=0x{1:x8} ok={2} ret={3} err={4} version={5} outpin=0x{6:x8} size={7} result=0x{8:x8} flags=0x{9:x} cap=0x{10:x} hex={11}" -f $g.DisplayName,$pin,$ok,$ret,$err,$v,$p,$sz,$res,$fl,$cap,$hex)
  }
  $h.Dispose()
}

