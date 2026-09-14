$ErrorActionPreference='Stop'
$out='C:\Users\Geoca\Documents\E004DH-trustlet-sync-oracle'
New-Item -ItemType Directory -Force -Path $out | Out-Null
$dll=Get-ChildItem 'C:\WINDOWS\System32\DriverStore\FileRepository\qccamsecureisp8380.inf_arm64_*\QcISPTrustlet8380.dll' -ErrorAction Stop | Select-Object -First 1
$swabPath='C:\Users\Geoca\Documents\E004DH-oracle\SWABF-derived-from-live-cache.bin'
$swasfPath='C:\Users\Geoca\Documents\E004DH-oracle\SWASF-derived-from-live-cache.bin'
$swab=[IO.File]::ReadAllBytes($swabPath); $swasf=[IO.File]::ReadAllBytes($swasfPath)
if($swab.Length -ne 0x22){throw 'bad SWABF payload length'}
if($swasf.Length -ne 0x804){throw 'bad SWASF payload length'}
$cs=@'
using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
public static class E004DHSyncOracle {
  [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)] static extern IntPtr LoadLibraryW(string p);
  [UnmanagedFunctionPointer(CallingConvention.Winapi)] delegate uint Fn8(uint a0,ulong a1,ulong a2,ulong a3,ulong a4,ulong a5,ulong a6,ulong a7);
  static string Sha(byte[] b){using(var s=SHA256.Create())return BitConverter.ToString(s.ComputeHash(b)).Replace("-","").ToLowerInvariant();}
  static void WB(IntPtr p,int off,byte v){Marshal.WriteByte(IntPtr.Add(p,off),v);}
  static byte RB(IntPtr p,int off){return Marshal.ReadByte(IntPtr.Add(p,off));}
  static void ClearSwabReady(IntPtr h){int[] a={0x3db91,0x3dc49,0x3dd01,0x3ddb9};foreach(int x in a)WB(h,x,0);}
  static IntPtr SwasfHandle(IntPtr h){return Marshal.ReadIntPtr(IntPtr.Add(h,0x3da78));}
  static void ClearSwasfReady(IntPtr q){int[] a={0x2e1,0x3a1,0x461,0x521,0x5e1,0x6a1,0x761,0x821};foreach(int x in a)WB(q,x,0);}
  static string Ready4(IntPtr h){int[] a={0x3db91,0x3dc49,0x3dd01,0x3ddb9};var s=new StringBuilder();foreach(int x in a)s.Append(RB(h,x));return s.ToString();}
  static string Ready8(IntPtr q){int[] a={0x2e1,0x3a1,0x461,0x521,0x5e1,0x6a1,0x761,0x821};var s=new StringBuilder();foreach(int x in a)s.Append(RB(q,x));return s.ToString();}
  public static string Run(string dll,byte[] swab,byte[] swasf,string outDir){
    Directory.CreateDirectory(outDir); var log=new StringBuilder();
    IntPtr h=LoadLibraryW(dll); if(h==IntPtr.Zero)return "LOAD_FAIL win32="+Marshal.GetLastWin32Error();
    log.AppendLine("LOAD_OK base=0x"+h.ToInt64().ToString("x"));
    var init=(Fn8)Marshal.GetDelegateForFunctionPointer(IntPtr.Add(h,0x19440),typeof(Fn8));
    var proc=(Fn8)Marshal.GetDelegateForFunctionPointer(IntPtr.Add(h,0x19828),typeof(Fn8));
    const int W=644,H=604,N=W*H*3/2; ulong dims=(ulong)W|((ulong)H<<16)|((ulong)W<<32);
    byte[] src=new byte[N],scratch=new byte[N],dst=new byte[N];
    for(int y=0;y<H;y++)for(int x=0;x<W;x++)src[y*W+x]=(byte)((x*17+y*29+((x*y)%31))&255);
    for(int i=W*H;i<N;i++)src[i]=(byte)(0x80+((i-W*H)&0x1f));
    Buffer.BlockCopy(src,0,scratch,0,N); for(int i=0;i<N;i++)dst[i]=0x5a;
    File.WriteAllBytes(Path.Combine(outDir,"input-644x604-nv12.bin"),src);
    uint i1=init(1,dims,0,0,0,0,0,0); uint i0=init(0,dims,0,0,0,0,0,0);
    log.AppendLine("SWABF_INIT=0x"+i1.ToString("x8")); log.AppendLine("SWASF_INIT=0x"+i0.ToString("x8"));
    if(i1!=0||i0!=0){File.WriteAllText(Path.Combine(outDir,"RESULT.txt"),log.ToString());return log.ToString();}
    Marshal.Copy(swab,0,IntPtr.Add(h,0x3da50),swab.Length); Marshal.Copy(swasf,0,IntPtr.Add(h,0x3d240),swasf.Length);
    IntPtr q=SwasfHandle(h); log.AppendLine("SWASF_HANDLE=0x"+q.ToInt64().ToString("x")); if(q==IntPtr.Zero)throw new Exception("null SWASF handle");
    var gs=GCHandle.Alloc(src,GCHandleType.Pinned); var gx=GCHandle.Alloc(scratch,GCHandleType.Pinned); var gd=GCHandle.Alloc(dst,GCHandleType.Pinned);
    try{
      ulong ps=(ulong)gs.AddrOfPinnedObject().ToInt64(),px=(ulong)gx.AddrOfPinnedObject().ToInt64(),pd=(ulong)gd.AddrOfPinnedObject().ToInt64();
      log.AppendLine("SWABF_READY_PRE="+Ready4(h)); ClearSwabReady(h); log.AppendLine("SWABF_READY_CLEARED="+Ready4(h));
      uint p1=proc(1,ps,px,dims,0,0,0,0); log.AppendLine("SWABF_PROCESS=0x"+p1.ToString("x8")+" READY_POST="+Ready4(h));
      File.WriteAllBytes(Path.Combine(outDir,"windows-trustlet-sync-swabf-644x604.bin"),scratch); log.AppendLine("SWABF_SHA256="+Sha(scratch));
      log.AppendLine("SWASF_READY_PRE="+Ready8(q)); ClearSwasfReady(q); log.AppendLine("SWASF_READY_CLEARED="+Ready8(q));
      uint p0=proc(0,px,pd,dims,0,0,0,0); log.AppendLine("SWASF_PROCESS=0x"+p0.ToString("x8")+" READY_POST="+Ready8(q));
      File.WriteAllBytes(Path.Combine(outDir,"windows-trustlet-sync-swasf-644x604.bin"),dst); log.AppendLine("SWASF_SHA256="+Sha(dst));
    } finally {gs.Free();gx.Free();gd.Free();}
    File.WriteAllText(Path.Combine(outDir,"RESULT.txt"),log.ToString()); return log.ToString();
    // Deliberately do not deinitialize/unload the IUM trustlet in a normal VTL0 process.
    // Process teardown owns cleanup for this bounded differential probe.
  }
}
'@
Add-Type -TypeDefinition $cs -Language CSharp
$header=@('E004DH synchronized Windows trustlet differential oracle',('time='+[DateTimeOffset]::Now.ToString('o')),('os='+(Get-CimInstance Win32_OperatingSystem).Caption+' build '+(Get-CimInstance Win32_OperatingSystem).BuildNumber),('dll_sha256='+(Get-FileHash $dll.FullName -Algorithm SHA256).Hash.ToLower()),('swab_sha256='+(Get-FileHash $swabPath -Algorithm SHA256).Hash.ToLower()),('swasf_sha256='+(Get-FileHash $swasfPath -Algorithm SHA256).Hash.ToLower()))
$body=[E004DHSyncOracle]::Run($dll.FullName,$swab,$swasf,$out)
(($header -join "`r`n")+"`r`n"+$body) | Tee-Object -FilePath "$out\ORACLE.log"
