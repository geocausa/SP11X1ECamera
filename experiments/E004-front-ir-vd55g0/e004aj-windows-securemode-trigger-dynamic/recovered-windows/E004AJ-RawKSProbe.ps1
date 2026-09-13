$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[void][Windows.Media.Capture.Frames.MediaFrameSourceGroup,Windows.Media.Capture.Frames,ContentType=WindowsRuntime]
function Await-Op($op,[Type]$type){$m=[System.WindowsRuntimeSystemExtensions].GetMethods()|?{$_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1}|select -First 1;$t=$m.MakeGenericMethod($type).Invoke($null,@($op));$t.Wait();$t.Result}
Add-Type @'
using System;
using System.Runtime.InteropServices;
using Microsoft.Win32.SafeHandles;
public static class KSRaw {
  [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
  public static extern SafeFileHandle CreateFile(string name, uint access, uint share, IntPtr sa, uint creation, uint flags, IntPtr template);
  [DllImport("kernel32.dll", SetLastError=true)]
  public static extern bool DeviceIoControl(SafeFileHandle h, uint code, byte[] inBuf, uint inLen, byte[] outBuf, uint outLen, out uint returned, IntPtr overlapped);
}
'@
function Put-U32([byte[]]$b,[int]$o,[uint32]$v){[Array]::Copy([BitConverter]::GetBytes($v),0,$b,$o,4)}
function New-KsProperty([uint32]$id,[uint32]$flags){$b=New-Object byte[] 24;$g=([Guid]'1CB79112-C0D2-4213-9CA6-CD4FDB927972').ToByteArray();[Array]::Copy($g,0,$b,0,16);Put-U32 $b 16 $id;Put-U32 $b 20 $flags;return $b}
$groups=Await-Op ([Windows.Media.Capture.Frames.MediaFrameSourceGroup]::FindAllAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Media.Capture.Frames.MediaFrameSourceGroup]])
foreach($g in $groups | ?{$_.Id -like '\\?\DISPLAY#QCOM_AVStream_8380*'}){
  Write-Output ("E004AJ_RAW_OPEN name={0} id={1}" -f $g.DisplayName,$g.Id)
  foreach($access in @([Convert]::ToUInt32("C0000000",16),[uint32]0)){
    $h=[KSRaw]::CreateFile($g.Id,$access,3,[IntPtr]::Zero,3,0,[IntPtr]::Zero)
    $err=[Runtime.InteropServices.Marshal]::GetLastWin32Error()
    Write-Output ("  OPEN access=0x{0:x8} invalid={1} err={2}" -f $access,$h.IsInvalid,$err)
    if(-not $h.IsInvalid){
      $in=New-KsProperty 36 0x200
      $out=New-Object byte[] 512
      [uint32]$ret=0
      $ok=[KSRaw]::DeviceIoControl($h,0x002F0003,$in,$in.Length,$out,$out.Length,[ref]$ret,[IntPtr]::Zero)
      $ioerr=[Runtime.InteropServices.Marshal]::GetLastWin32Error()
      $hex=if($ret -gt 0){(($out[0..([Math]::Min([int]$ret-1,127))]|%{$_.ToString('x2')}) -join '')}else{''}
      Write-Output ("  BASIC36 ok={0} ret={1} err={2} out={3}" -f $ok,$ret,$ioerr,$hex)
      $h.Dispose()
      break
    }
  }
}

