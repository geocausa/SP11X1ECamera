$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[void][Windows.Media.Capture.Frames.MediaFrameSourceGroup,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
function Await-Op($op,[Type]$type){$m=[System.WindowsRuntimeSystemExtensions].GetMethods()|?{$_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1}|select -First 1;$t=$m.MakeGenericMethod($type).Invoke($null,@($op));$t.Wait();$t.Result}
Add-Type @'
using System;
using System.Runtime.InteropServices;
using Microsoft.Win32.SafeHandles;
public static class KSScope {
  [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
  public static extern SafeFileHandle CreateFile(string name, uint access, uint share, IntPtr sa, uint creation, uint flags, IntPtr template);
  [DllImport("kernel32.dll", SetLastError=true)]
  public static extern bool DeviceIoControl(SafeFileHandle h, uint code, [In] byte[] inBuf, uint inLen, [In,Out] byte[] outBuf, uint outLen, out uint returned, IntPtr overlapped);
}
'@
function Put-U32([byte[]]$b,[int]$o,[uint32]$v){[Array]::Copy([BitConverter]::GetBytes($v),0,$b,$o,4)}
function Put-U64([byte[]]$b,[int]$o,[uint64]$v){[Array]::Copy([BitConverter]::GetBytes($v),0,$b,$o,8)}
function New-KsProperty([uint32]$flags){$b=New-Object byte[] 24;$g=([Guid]'1CB79112-C0D2-4213-9CA6-CD4FDB927972').ToByteArray();[Array]::Copy($g,0,$b,0,16);Put-U32 $b 16 36;Put-U32 $b 20 $flags;return $b}
function New-Data([uint64]$flags){$b=New-Object byte[] 40;Put-U32 $b 0 1;Put-U32 $b 4 0;Put-U32 $b 8 40;Put-U32 $b 12 0;Put-U64 $b 16 $flags;Put-U64 $b 24 0;Put-U64 $b 32 0;return $b}
function Do-Set($h,[uint64]$flags,[string]$tag){
  $p=New-KsProperty 2;$d=New-Data $flags;[uint32]$ret=0
  $ok=[KSScope]::DeviceIoControl($h,0x002F0003,$p,$p.Length,$d,$d.Length,[ref]$ret,[IntPtr]::Zero);$err=[Runtime.InteropServices.Marshal]::GetLastWin32Error()
  Write-Output ("E004AJ_SCOPE_SET tag={0} flags=0x{1:x} ok={2} ret={3} err={4} data={5}" -f $tag,$flags,$ok,$ret,$err,(($d|%{$_.ToString('x2')}) -join ''))
  return $ok
}
function Do-Get($h,[string]$tag){
  $p=New-KsProperty 1;$d=New-Data 0;[uint32]$ret=0
  $ok=[KSScope]::DeviceIoControl($h,0x002F0003,$p,$p.Length,$d,$d.Length,[ref]$ret,[IntPtr]::Zero);$err=[Runtime.InteropServices.Marshal]::GetLastWin32Error()
  $v=[BitConverter]::ToUInt32($d,0);$pin=[BitConverter]::ToUInt32($d,4);$sz=[BitConverter]::ToUInt32($d,8);$res=[BitConverter]::ToUInt32($d,12);$fl=[BitConverter]::ToUInt64($d,16);$cap=[BitConverter]::ToUInt64($d,24)
  Write-Output ("E004AJ_SCOPE_GET tag={0} ok={1} ret={2} err={3} version={4} pin={5} size={6} result=0x{7:x8} flags=0x{8:x} cap=0x{9:x} data={10}" -f $tag,$ok,$ret,$err,$v,$pin,$sz,$res,$fl,$cap,(($d|%{$_.ToString('x2')}) -join ''))
  return $fl
}
$groups=Await-Op ([Windows.Media.Capture.Frames.MediaFrameSourceGroup]::FindAllAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Media.Capture.Frames.MediaFrameSourceGroup]])
$g=$groups|? DisplayName -eq 'Surface IR Camera Front'|select -First 1
if(-not $g){throw 'IR group missing'}
$access=[Convert]::ToUInt32("C0000000",16)
$a=[KSScope]::CreateFile($g.Id,$access,3,[IntPtr]::Zero,3,0,[IntPtr]::Zero)
if($a.IsInvalid){throw "open A failed $([Runtime.InteropServices.Marshal]::GetLastWin32Error())"}
$b=$null
$enabled=$false
try {
  [void](Do-Get $a 'A-before')
  $enabled=Do-Set $a 2 'A-enable'
  [void](Do-Get $a 'A-after-enable')
  $b=[KSScope]::CreateFile($g.Id,$access,3,[IntPtr]::Zero,3,0,[IntPtr]::Zero)
  if($b.IsInvalid){throw "open B failed $([Runtime.InteropServices.Marshal]::GetLastWin32Error())"}
  [void](Do-Get $b 'B-while-A-enabled')
} finally {
  if($enabled){[void](Do-Set $a 1 'A-disable')}
  [void](Do-Get $a 'A-after-disable')
  if($null -ne $b -and -not $b.IsInvalid){[void](Do-Get $b 'B-after-A-disable');$b.Dispose()}
  $a.Dispose()
}
