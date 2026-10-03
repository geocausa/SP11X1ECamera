[CmdletBinding()]
param([switch]$CompileOnly,[string]$Root,[switch]$ReturnGolden,[switch]$WatchdogAlreadyArmed)
$ErrorActionPreference='Stop'
$definition=@'
using System;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
namespace E011CTOracle {
 [StructLayout(LayoutKind.Sequential)]
 public struct SecurityAttributes { public uint Length; public IntPtr Descriptor; public int Inherit; }
 public sealed class FileResult {
  public bool ValidHandle, HandleClosed; public uint LastError, NativeLastError, NtStatus, NtdllLastError;
  public int SecurityAttributesBytes; public bool ContentRead; public bool FileCreated;
 }
 public static class Native {
  [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
  private static extern IntPtr CreateFileW(string filename, uint access, uint share, ref SecurityAttributes sa, uint disposition, uint attrs, IntPtr template);
  [DllImport("kernel32.dll", SetLastError=false)] private static extern uint GetLastError();
  [DllImport("kernel32.dll", SetLastError=false)] private static extern void SetLastError(uint value);
  [DllImport("kernel32.dll", SetLastError=false)] private static extern bool CloseHandle(IntPtr handle);
  [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=false)] private static extern IntPtr GetModuleHandleW(string name);
  [DllImport("ntdll.dll", SetLastError=false)] private static extern uint RtlGetLastNtStatus();
  [DllImport("ntdll.dll", SetLastError=false)] private static extern uint RtlGetLastWin32Error();
  public static int Layout() {
   if (IntPtr.Size!=8 || Marshal.SizeOf(typeof(SecurityAttributes))!=24
    || Marshal.OffsetOf(typeof(SecurityAttributes),"Descriptor").ToInt32()!=8
    || Marshal.OffsetOf(typeof(SecurityAttributes),"Inherit").ToInt32()!=16) throw new InvalidOperationException("Win64 ABI layout mismatch");
   return 24;
  }
  public static string Sha(byte[] b) { using (SHA256 h=SHA256.Create()) return BitConverter.ToString(h.ComputeHash(b)).Replace("-","").ToLowerInvariant(); }
  public static uint[] ErrorRoundTrip(uint value) {
   GetLastError(); RtlGetLastWin32Error(); SetLastError(value);
   uint a=GetLastError(),b=RtlGetLastWin32Error(); return new uint[]{value,a,b};
  }
  public static FileResult OpenReadonly(string filename) {
   Layout(); GetLastError(); RtlGetLastWin32Error(); RtlGetLastNtStatus();
   FileResult result=new FileResult();
   SecurityAttributes sa=new SecurityAttributes {Length=24,Descriptor=IntPtr.Zero,Inherit=1};
   SetLastError(0);
   IntPtr handle=CreateFileW(filename,0x80000000u,1u,ref sa,3u,128u,IntPtr.Zero);
   uint lastError=unchecked((uint)Marshal.GetLastWin32Error());
   uint ntStatus=RtlGetLastNtStatus();
   uint nativeError=GetLastError();
   uint ntdllError=RtlGetLastWin32Error();
   bool valid=handle!=new IntPtr(-1) && handle!=IntPtr.Zero;
   bool closed=!valid;
   if (valid) closed=CloseHandle(handle);
   result.ValidHandle=valid;result.HandleClosed=closed;result.LastError=lastError;
   result.NtStatus=ntStatus;result.NativeLastError=nativeError;result.NtdllLastError=ntdllError;
   result.SecurityAttributesBytes=24;result.ContentRead=false;result.FileCreated=false;
   return result;
  }
  public static byte[] SharedPage() {
   byte[] b=new byte[4096];Marshal.Copy(new IntPtr(0x7ffe0000L),b,0,b.Length);return b;
  }
  public static byte[] NtdllInitializationCell() {
   IntPtr at=GetModuleHandleW("ntdll.dll");
   if(at==IntPtr.Zero || Marshal.ReadInt16(at)!=0x5a4d) throw new InvalidOperationException("Loaded NTDLL header mismatch");
   int pe=Marshal.ReadInt32(at,0x3c);int size=Marshal.ReadInt32(at,pe+24+56);
   if(size<=0x3933f0) throw new InvalidOperationException("NTDLL cell outside loaded image");
   byte[] b=new byte[8];Marshal.Copy(IntPtr.Add(at,0x3933e8),b,0,8);return b;
  }
 }
}
'@
Add-Type -TypeDefinition $definition -Language CSharp
$layout=[E011CTOracle.Native]::Layout()
if($CompileOnly){
 [pscustomobject]@{compile_only=$true;security_attributes_bytes=$layout;descriptor_offset=8;inherit_offset=16;target_CreateFileW_call_count=0;shared_memory_read_count=0;marker_written=$false}|ConvertTo-Json -Compress
 return
}
if([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT){throw 'Windows-only observation'}
if(-not $Root){throw 'Explicit prepared private root required'}
$resolved=[IO.Path]::GetFullPath($Root).TrimEnd([char]92)
if(-not [IO.Directory]::Exists($resolved)){throw 'Prepared private directory missing'}
if($resolved -notmatch '^[A-Za-z]:\\EFI\\SP11CameraPrivate\\E011CT-OS-001$'){throw 'Prepared ESP root mismatch'}
if(Test-Path -LiteralPath (Join-Path $resolved 'CONSUMED.marker')){throw 'Consumed observation identity'}
$inputPath=Join-Path $resolved 'api-input-private.json'
$inputRaw=[IO.File]::ReadAllText($inputPath)
$inputData=$inputRaw|ConvertFrom-Json
if($inputData.identity -ne 'E011CT-OS-001'){throw 'Input identity mismatch'}
$path=[string]$inputData.selected_path
if($path -notmatch '^[Cc]:\\' -or $path.Length -ne 36){throw 'Owned path scope mismatch'}
foreach($ch in $path.ToCharArray()){if([int]$ch -gt 127 -or [int]$ch -eq 0){throw 'ASCII path scope mismatch'}}
$bytes=[Text.Encoding]::ASCII.GetBytes($path+[char]0)
if([E011CTOracle.Native]::Sha($bytes) -ne '4cbd98d9784913d9111d301111dba46a1ec9d90e9545d450fc616bca635c432d'){throw 'Owned path digest mismatch'}
$pins=@{
 'kernelbase.dll'='26be64c26bac33368a650372cb5fb1e3235f1bd7883471bd3291dbf6372ae274'
 'ntdll.dll'='60ef561645b50dce71ad0919dbbef3ad334a0489432cde718e75b73b558c7997'
 'kernel32.dll'='6a7bd4daff9c0c4cc8b9478ecd9828c3f19be257a4a18db9559cae929197fffa'
}
foreach($key in $pins.Keys){
 $p=Join-Path $env:windir ('System32\'+$key)
 if((Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant() -ne $pins[$key]){throw ('Pinned system input changed: '+$key)}
}
$marker=Join-Path $resolved 'CONSUMED.marker'
$stream=[IO.File]::Open($marker,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
try{
 $b=[Text.Encoding]::UTF8.GetBytes('E011CT-OS-001 '+[DateTime]::UtcNow.ToString('o'))
 $stream.Write($b,0,$b.Length);$stream.Flush($true)
}finally{$stream.Dispose()}
$watchdogArmed=[bool]$WatchdogAlreadyArmed
try{
 if($ReturnGolden -and -not $watchdogArmed){
  & "$env:windir\System32\shutdown.exe" /r /t 600 /f /c 'E011CT OS dependency observer Golden fallback'
  if($LASTEXITCODE -ne 0){throw 'Golden return watchdog not armed'}
  $watchdogArmed=$true
 }
 $shared=[E011CTOracle.Native]::SharedPage()
 $before=[E011CTOracle.Native]::NtdllInitializationCell()
 $result=[E011CTOracle.Native]::OpenReadonly($path)
 $after=[E011CTOracle.Native]::NtdllInitializationCell()
 $roundTrip=[E011CTOracle.Native]::ErrorRoundTrip(0x13572468)
 [IO.File]::WriteAllBytes((Join-Path $resolved 'shared-user-data-private.bin'),$shared)
 [IO.File]::WriteAllBytes((Join-Path $resolved 'ntdll-initialization-before-private.bin'),$before)
 [IO.File]::WriteAllBytes((Join-Path $resolved 'ntdll-initialization-after-private.bin'),$after)
 $safe=[ordered]@{
  experiment='E011CT';identity='E011CT-OS-001';status='OBSERVED_WINDOWS_FILE_API_DEPENDENCY'
  UTC=[DateTime]::UtcNow.ToString('o');machine=$env:COMPUTERNAME;process_architecture=$env:PROCESSOR_ARCHITECTURE
  source_filename_bytes_including_NUL=37;source_filename_sha256=[E011CTOracle.Native]::Sha($bytes)
  system_DLL_pins=$pins;native_standard_Win32_API_observation=$true;proprietary_OEM_DLL_loaded_by_observer=$false
  target_CreateFileW_call_count=1;valid_handle=$result.ValidHandle;handle_closed=$result.HandleClosed
  Win32_last_error=$result.LastError;native_thread_last_error=$result.NativeLastError;NTDLL_thread_last_error=$result.NtdllLastError
  NTSTATUS=[uint32]$result.NtStatus;NTSTATUS_hex=('0x{0:x8}' -f $result.NtStatus)
  security_attributes_bytes=$result.SecurityAttributesBytes;input_desired_access=2147483648;input_share_mode=1
  input_creation_disposition=3;input_attributes=128;template_null=$true;security_descriptor_null=$true;inherit_handle=$true
  target_file_content_read=$false;target_file_created=$false;filename_content_exported=$false
  shared_page_private_bytes=$shared.Length;shared_page_private_sha256=[E011CTOracle.Native]::Sha($shared)
  ntdll_initialization_cell_RVA='0x3933e8';initialization_before_private_sha256=[E011CTOracle.Native]::Sha($before)
  initialization_after_private_sha256=[E011CTOracle.Native]::Sha($after)
  error_round_trip_requested=$roundTrip[0];error_round_trip_Kernel32=$roundTrip[1];error_round_trip_NTDLL=$roundTrip[2]
  new_camera_Starts=0;new_camera_streams=0;camera_or_optical_API_used=$false;Golden_return_watchdog_armed=$watchdogArmed
  single_use_atomic_marker=$true;original_CRT_CFE600_not_executed=$true;live_Default_filename_producer_qualified=$false
 }
 $safe|ConvertTo-Json -Depth 8|Set-Content -LiteralPath (Join-Path $resolved 'WINDOWS-FILE-API-SAFE.json') -Encoding UTF8
 $safe|ConvertTo-Json -Depth 8 -Compress
}catch{
 [ordered]@{identity='E011CT-OS-001';status='CONSUMED_ABORT';exception_type=$_.Exception.GetType().FullName;new_camera_Starts=0;watchdog_armed=$watchdogArmed}|ConvertTo-Json -Compress
 throw
}finally{
 if($ReturnGolden -and $watchdogArmed){
  & "$env:windir\System32\shutdown.exe" /a | Out-Null
  & "$env:windir\System32\shutdown.exe" /r /t 15 /f /c 'E011CT observer complete; normal reboot to Golden'
 }
}
