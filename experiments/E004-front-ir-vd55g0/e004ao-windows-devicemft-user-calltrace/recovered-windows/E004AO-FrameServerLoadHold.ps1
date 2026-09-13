$ErrorActionPreference='Stop'
Add-Type -TypeDefinition @'
using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text;

public static class E004AODebug {
  const uint DEBUG_PROCESS = 0x00000001;
  const uint TOKEN_ADJUST_PRIVILEGES = 0x20;
  const uint TOKEN_QUERY = 0x8;
  const uint SE_PRIVILEGE_ENABLED = 0x2;
  const uint DBG_CONTINUE = 0x00010002;
  const int LOAD_DLL_DEBUG_EVENT = 6;
  const int CREATE_PROCESS_DEBUG_EVENT = 3;
  const int EXCEPTION_DEBUG_EVENT = 1;

  [StructLayout(LayoutKind.Sequential)]
  struct LUID { public uint LowPart; public int HighPart; }
  [StructLayout(LayoutKind.Sequential)]
  struct TOKEN_PRIVILEGES {
    public uint PrivilegeCount;
    public LUID Luid;
    public uint Attributes;
  }

  [DllImport("kernel32.dll", SetLastError=true)]
  static extern bool DebugActiveProcess(uint pid);
  [DllImport("kernel32.dll", SetLastError=true)]
  static extern bool DebugActiveProcessStop(uint pid);
  [DllImport("kernel32.dll", SetLastError=true)]
  static extern bool WaitForDebugEvent(IntPtr lpDebugEvent, uint dwMilliseconds);
  [DllImport("kernel32.dll", SetLastError=true)]
  static extern bool ContinueDebugEvent(uint pid, uint tid, uint status);
  [DllImport("kernel32.dll", SetLastError=true)]
  static extern bool CloseHandle(IntPtr h);
  [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
  static extern uint GetFinalPathNameByHandleW(IntPtr h, StringBuilder s, uint n, uint flags);
  [DllImport("advapi32.dll", SetLastError=true)]
  static extern bool OpenProcessToken(IntPtr process, uint access, out IntPtr token);
  [DllImport("advapi32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
  static extern bool LookupPrivilegeValue(string system, string name, out LUID luid);
  [DllImport("advapi32.dll", SetLastError=true)]
  static extern bool AdjustTokenPrivileges(IntPtr token, bool disableAll, ref TOKEN_PRIVILEGES state, uint len, IntPtr prev, IntPtr ret);
  [DllImport("kernel32.dll")]
  static extern IntPtr GetCurrentProcess();

  static void EnableDebugPrivilege() {
    IntPtr tok;
    if(!OpenProcessToken(GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY, out tok)) return;
    try {
      LUID l;
      if(!LookupPrivilegeValue(null,"SeDebugPrivilege",out l)) return;
      TOKEN_PRIVILEGES tp=new TOKEN_PRIVILEGES { PrivilegeCount=1, Luid=l, Attributes=SE_PRIVILEGE_ENABLED };
      AdjustTokenPrivileges(tok,false,ref tp,0,IntPtr.Zero,IntPtr.Zero);
    } finally { CloseHandle(tok); }
  }

  static string PathFromHandle(IntPtr h) {
    if(h==IntPtr.Zero || h.ToInt64()==-1) return "";
    var sb=new StringBuilder(2048);
    uint n=GetFinalPathNameByHandleW(h,sb,(uint)sb.Capacity,0);
    return n>0 && n<sb.Capacity ? sb.ToString() : "";
  }

  static bool IsTargetLoaded(uint pid, out long baseAddr, out string path) {
    baseAddr=0; path="";
    try {
      using(var p=Process.GetProcessById((int)pid)) {
        foreach(ProcessModule m in p.Modules) {
          if(string.Equals(m.ModuleName,"QcDeviceMFT8380.dll",StringComparison.OrdinalIgnoreCase)) {
            baseAddr=m.BaseAddress.ToInt64(); path=m.FileName; return true;
          }
        }
      }
    } catch {}
    return false;
  }

  public static int HoldOnDeviceMFT(uint pid) {
    EnableDebugPrivilege();
    Console.WriteLine("E004AO_UMDBG_ATTACH_BEGIN pid="+pid);
    if(!DebugActiveProcess(pid)) {
      Console.WriteLine("E004AO_UMDBG_ATTACH_FAIL pid="+pid+" err="+Marshal.GetLastWin32Error());
      return 2;
    }
    Console.WriteLine("E004AO_UMDBG_ATTACH_PASS pid="+pid);
    IntPtr ev=Marshal.AllocHGlobal(256);
    try {
      for(;;) {
        for(int i=0;i<256;i++) Marshal.WriteByte(ev,i,0);
        if(!WaitForDebugEvent(ev,30000)) {
          int err=Marshal.GetLastWin32Error();
          Console.WriteLine("E004AO_UMDBG_WAIT_TIMEOUT_OR_FAIL err="+err);
          continue;
        }
        int code=Marshal.ReadInt32(ev,0);
        uint ep=(uint)Marshal.ReadInt32(ev,4);
        uint et=(uint)Marshal.ReadInt32(ev,8);
        IntPtr hFile=IntPtr.Zero;
        if(code==LOAD_DLL_DEBUG_EVENT || code==CREATE_PROCESS_DEBUG_EVENT) {
          hFile=Marshal.ReadIntPtr(ev,16);
        }
        string hp=PathFromHandle(hFile);
        if(code==LOAD_DLL_DEBUG_EVENT) {
          long b=Marshal.ReadIntPtr(ev,24).ToInt64();
          if(hp.IndexOf("QcDeviceMFT8380.dll",StringComparison.OrdinalIgnoreCase)>=0) {
            Console.WriteLine("E004AO_UMDBG_TARGET_LOAD pid="+ep+" tid="+et+" base=0x"+b.ToString("x")+" path="+hp);
            Console.WriteLine("E004AO_UMDBG_TARGET_GATE");
            string gate=Console.ReadLine();
            Console.WriteLine("E004AO_UMDBG_TARGET_RELEASE="+gate);
            ContinueDebugEvent(ep,et,DBG_CONTINUE);
            if(hFile!=IntPtr.Zero && hFile.ToInt64()!=-1) CloseHandle(hFile);
            DebugActiveProcessStop(pid);
            Console.WriteLine("E004AO_UMDBG_DETACHED");
            return 0;
          }
        }
        if(code==LOAD_DLL_DEBUG_EVENT && string.IsNullOrEmpty(hp)) {
          long b2; string p2;
          if(IsTargetLoaded(ep,out b2,out p2)) {
            Console.WriteLine("E004AO_UMDBG_TARGET_LOAD_FALLBACK pid="+ep+" tid="+et+" base=0x"+b2.ToString("x")+" path="+p2);
            Console.WriteLine("E004AO_UMDBG_TARGET_GATE");
            string gate=Console.ReadLine();
            Console.WriteLine("E004AO_UMDBG_TARGET_RELEASE="+gate);
            ContinueDebugEvent(ep,et,DBG_CONTINUE);
            if(hFile!=IntPtr.Zero && hFile.ToInt64()!=-1) CloseHandle(hFile);
            DebugActiveProcessStop(pid);
            Console.WriteLine("E004AO_UMDBG_DETACHED");
            return 0;
          }
        }
        ContinueDebugEvent(ep,et,DBG_CONTINUE);
        if(hFile!=IntPtr.Zero && hFile.ToInt64()!=-1) CloseHandle(hFile);
      }
    } finally {
      Marshal.FreeHGlobal(ev);
    }
  }
}
'@
$s=Get-CimInstance Win32_Service -Filter "Name='FrameServer'"
Write-Output ("E004AO_UMDBG_SERVICE state={0} pid={1}" -f $s.State,$s.ProcessId)
if($s.State -ne 'Running' -or $s.ProcessId -eq 0){ throw 'FrameServer not running' }
exit [E004AODebug]::HoldOnDeviceMFT([uint32]$s.ProcessId)
