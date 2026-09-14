$ErrorActionPreference='Stop'
$out='C:\Users\Geoca\Documents\E004DH-trustlet-oracle'
New-Item -ItemType Directory -Force -Path $out | Out-Null
$dll=Get-ChildItem 'C:\WINDOWS\System32\DriverStore\FileRepository\qccamsecureisp8380.inf_arm64_*\QcISPTrustlet8380.dll' -ErrorAction Stop | Select-Object -First 1
if(-not $dll){ throw 'QcISPTrustlet8380.dll not found' }
$swabPath='C:\Users\Geoca\Documents\E004DH-oracle\SWABF-derived-from-live-cache.bin'
$swasfPath='C:\Users\Geoca\Documents\E004DH-oracle\SWASF-derived-from-live-cache.bin'
if(-not (Test-Path $swabPath)){throw 'SWABF live-oracle payload missing'}
if(-not (Test-Path $swasfPath)){throw 'SWASF live-oracle payload missing'}
$swab=[IO.File]::ReadAllBytes($swabPath); $swasf=[IO.File]::ReadAllBytes($swasfPath)
if($swab.Length -ne 0x22){throw 'bad SWABF payload length'}
if($swasf.Length -ne 0x804){throw 'bad SWASF payload length'}

$cs=@'
using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
public static class E004DHTrustletOracle {
  [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
  static extern IntPtr LoadLibraryW(string path);
  [DllImport("kernel32.dll", SetLastError=true)]
  static extern bool FreeLibrary(IntPtr h);
  [UnmanagedFunctionPointer(CallingConvention.Winapi)]
  delegate uint Fn8(uint a0, ulong a1, ulong a2, ulong a3, ulong a4, ulong a5, ulong a6, ulong a7);
  [UnmanagedFunctionPointer(CallingConvention.Winapi)]
  delegate void FnDeinit(int module);
  static string Sha(byte[] b){ using(var s=SHA256.Create()) return BitConverter.ToString(s.ComputeHash(b)).Replace("-","").ToLowerInvariant(); }
  static string Hex(byte[] b,int n){ n=Math.Min(n,b.Length); var c=new char[n*2]; const string h="0123456789abcdef"; for(int i=0;i<n;i++){c[i*2]=h[b[i]>>4];c[i*2+1]=h[b[i]&15];} return new string(c); }
  public static string Run(string dll, byte[] swab, byte[] swasf, string outDir){
    Directory.CreateDirectory(outDir);
    IntPtr h=LoadLibraryW(dll);
    if(h==IntPtr.Zero) return "LOAD_FAIL win32="+Marshal.GetLastWin32Error();
    var log=new System.Text.StringBuilder();
    log.AppendLine("LOAD_OK base=0x"+h.ToInt64().ToString("x"));
    log.AppendLine("dll="+dll);
    try {
      var init=(Fn8)Marshal.GetDelegateForFunctionPointer(IntPtr.Add(h,0x19440),typeof(Fn8));
      var proc=(Fn8)Marshal.GetDelegateForFunctionPointer(IntPtr.Add(h,0x19828),typeof(Fn8));
      var deinit=(FnDeinit)Marshal.GetDelegateForFunctionPointer(IntPtr.Add(h,0x19ae0),typeof(FnDeinit));
      const int W=16,H=16,N=W*H*3/2;
      ulong dims=(ulong)W | ((ulong)H<<16) | ((ulong)W<<32);
      byte[] src=new byte[N], scratch=new byte[N], dst=new byte[N];
      for(int y=0;y<H;y++) for(int x=0;x<W;x++) src[y*W+x]=(byte)((x*17+y*29+((x*y)%31))&255);
      for(int i=W*H;i<N;i++) src[i]=(byte)(0x80+((i-W*H)&0x1f));
      Buffer.BlockCopy(src,0,scratch,0,N);
      for(int i=0;i<N;i++) dst[i]=0x5a;
      File.WriteAllBytes(Path.Combine(outDir,"input-16x16-nv12.bin"),src);
      uint i1=0xffffffff,i0=0xffffffff,p1=0xffffffff,p0=0xffffffff;
      bool did1=false,did0=false;
      GCHandle gs=default(GCHandle),gx=default(GCHandle),gd=default(GCHandle);
      try {
        i1=init(1,dims,0,0,0,0,0,0); did1=(i1==0);
        log.AppendLine("SWABF_INIT=0x"+i1.ToString("x8"));
        i0=init(0,dims,0,0,0,0,0,0); did0=(i0==0);
        log.AppendLine("SWASF_INIT=0x"+i0.ToString("x8"));
        if(did1 && did0){
          Marshal.Copy(swab,0,IntPtr.Add(h,0x3da50),swab.Length);
          Marshal.Copy(swasf,0,IntPtr.Add(h,0x3d240),swasf.Length);
          gs=GCHandle.Alloc(src,GCHandleType.Pinned); gx=GCHandle.Alloc(scratch,GCHandleType.Pinned); gd=GCHandle.Alloc(dst,GCHandleType.Pinned);
          ulong ps=(ulong)gs.AddrOfPinnedObject().ToInt64(), px=(ulong)gx.AddrOfPinnedObject().ToInt64(), pd=(ulong)gd.AddrOfPinnedObject().ToInt64();
          p1=proc(1,ps,px,dims,0,0,0,0);
          log.AppendLine("SWABF_PROCESS=0x"+p1.ToString("x8"));
          File.WriteAllBytes(Path.Combine(outDir,"windows-trustlet-swabf-16x16.bin"),scratch);
          log.AppendLine("SWABF_SHA256="+Sha(scratch)); log.AppendLine("SWABF_Y="+Hex(scratch,W*H));
          p0=proc(0,px,pd,dims,0,0,0,0);
          log.AppendLine("SWASF_PROCESS=0x"+p0.ToString("x8"));
          File.WriteAllBytes(Path.Combine(outDir,"windows-trustlet-swasf-16x16.bin"),dst);
          log.AppendLine("SWASF_SHA256="+Sha(dst)); log.AppendLine("SWASF_Y="+Hex(dst,W*H));
        }
      } finally {
        if(gs.IsAllocated)gs.Free(); if(gx.IsAllocated)gx.Free(); if(gd.IsAllocated)gd.Free();
        try { if(did0) deinit(0); } catch(Exception e){log.AppendLine("SWASF_DEINIT_EXCEPTION="+e.GetType().Name+":"+e.Message);}
        try { if(did1) deinit(1); } catch(Exception e){log.AppendLine("SWABF_DEINIT_EXCEPTION="+e.GetType().Name+":"+e.Message);}
      }
      File.WriteAllText(Path.Combine(outDir,"RESULT.txt"),log.ToString());
      return log.ToString();
    } catch(Exception e){
      log.AppendLine("HARNESS_EXCEPTION="+e.GetType().FullName+":"+e.Message);
      log.AppendLine(e.StackTrace??""); File.WriteAllText(Path.Combine(outDir,"RESULT.txt"),log.ToString()); return log.ToString();
    } finally { FreeLibrary(h); }
  }
}
'@
Add-Type -TypeDefinition $cs -Language CSharp
$header=@()
$header += 'E004DH Windows trustlet differential oracle'
$header += ('time='+[DateTimeOffset]::Now.ToString('o'))
$header += ('os='+(Get-CimInstance Win32_OperatingSystem).Caption+' build '+(Get-CimInstance Win32_OperatingSystem).BuildNumber)
$header += ('dll_sha256='+(Get-FileHash $dll.FullName -Algorithm SHA256).Hash.ToLower())
$header += ('swab_sha256='+(Get-FileHash $swabPath -Algorithm SHA256).Hash.ToLower())
$header += ('swasf_sha256='+(Get-FileHash $swasfPath -Algorithm SHA256).Hash.ToLower())
$body=[E004DHTrustletOracle]::Run($dll.FullName,$swab,$swasf,$out)
($header -join "`r`n")+"`r`n"+$body | Tee-Object -FilePath "$out\ORACLE.log"
