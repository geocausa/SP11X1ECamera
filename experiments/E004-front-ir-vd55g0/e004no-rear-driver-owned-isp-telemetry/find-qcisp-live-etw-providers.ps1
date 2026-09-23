# E004no read-only: compare Windows live ETW provider GUIDs with GUID bytes
# embedded in the local installed qcISP PE. Does not start ETW or touch camera.
# Zero OEM driver bytes leave SP11. GUID matches are only CANDIDATES until
# independently attributed to qcISP at an actual rear recording session.
$ErrorActionPreference='Stop'
$source=@'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
namespace E004noProviderAudit {
public static class TraceApi {
  [DllImport("advapi32.dll", EntryPoint="EnumerateTraceGuidsEx",
             CallingConvention=CallingConvention.Winapi)]
  public static extern uint EnumerateTraceGuidsEx(uint which, IntPtr input,
         uint inputLength, IntPtr output, uint outputLength, out uint needed);
  public static byte[] QueryRegistered(out uint status, out uint needed) {
    needed=0;
    status=0;
    for (int size=1024*1024; size<=8*1024*1024; size*=2) {
      IntPtr p=Marshal.AllocHGlobal(size);
      try {
        status=EnumerateTraceGuidsEx(0, IntPtr.Zero, 0, p, (uint)size, out needed);
        if(status==0 && needed<=(uint)size) {
          var bytes=new byte[needed];
          Marshal.Copy(p,bytes,0,(int)needed);
          return bytes;
        }
        if(status!=122 && status!=234) return new byte[0];
      } finally {Marshal.FreeHGlobal(p);}
    }
    return new byte[0];
  }
  public static int FindBytes(byte[] haystack, byte[] needle) {
    if(haystack==null || needle==null || needle.Length!=16) return -1;
    int from=0;
    while (from<=haystack.Length-needle.Length) {
      int i=Array.IndexOf(haystack, needle[0], from);
      if(i<0 || i>haystack.Length-needle.Length) return -1;
      bool eq=true;
      for(int j=1;j<needle.Length;j++) {
        if(haystack[i+j]!=needle[j]){eq=false;break;}
      }
      if(eq)return i;
      from=i+1;
    }
    return -1;
  }
  public static string[] Matches(byte[] traceList, byte[] pe, int align) {
    var seen=new HashSet<Guid>();
    var matched=new List<string>();
    for(int i=align;i+16<=traceList.Length;i+=16) {
      var b=new byte[16];
      Buffer.BlockCopy(traceList,i,b,0,16);
      var g=new Guid(b);
      if(g==Guid.Empty || !seen.Add(g)) continue;
      int address=FindBytes(pe,b);
      if(address>=0) matched.Add(g.ToString("D")+" | PE_FILE_OFFSET="+address);
    }
    return matched.ToArray();
  }
}
}
'@
if(-not('E004noProviderAudit.TraceApi' -as [type])){
  Add-Type -TypeDefinition $source -Language CSharp -ErrorAction Stop
}
$driver='C:\Windows\System32\DriverStore\FileRepository\qccamisp8380.inf_arm64_068a5d125dcec104\qccamisp8380.sys'
if(-not(Test-Path -LiteralPath $driver)){throw 'E004NO installed qcISP source driver path absent'}
$bytes=[IO.File]::ReadAllBytes($driver)
$sha=[BitConverter]::ToString(([Security.Cryptography.SHA256]::Create()).ComputeHash($bytes)).Replace('-','').ToLowerInvariant()
if($sha -ne '64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c'){
  throw 'E004NO installed qcISP digest changed; do not mix vendor drivers'
}
[uint32]$status=0; [uint32]$size=0
$list=[E004noProviderAudit.TraceApi]::QueryRegistered([ref]$status,[ref]$size)
$results=@()
if($status -eq 0 -and $list.Length -gt 0){
  for($align=0;$align -lt 16;$align++){
    $hits=@([E004noProviderAudit.TraceApi]::Matches($list,$bytes,$align))
    if($hits.Count -gt 0){
      $results += [pscustomobject]@{alignment=$align;embedded_and_runtime_matches=$hits}
    }
  }
}
[pscustomobject][ordered]@{
  experiment='E004no'
  evidence_scope='same_SP11_Windows_live_registered_ETW_guid_list_intersect_OEM_qcISP_PE_bytes'
  driver_sha256=$sha
  enum_trace_guids_ex_status=$status
  enum_trace_guids_ex_returned_bytes=$size
  GUID_alignment_matches=$results
  registered_GUID_identified_as_qcISP_driver_owned=$false
  active_rear_IFE_or_CSID0_resource_proven=$false
  active_rear_VFE0_output_DMA_proven=$false
  no_ETW_session_started=$true
  no_camera_opened=$true
  original_driver_binary_exported=$false
} | ConvertTo-Json -Depth 8
