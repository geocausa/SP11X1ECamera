$ErrorActionPreference='Stop'
$out='C:\Users\Geoca\Documents\E004DH-cd90-capture'
New-Item -ItemType Directory -Force -Path $out | Out-Null
$dll=Get-ChildItem 'C:\WINDOWS\System32\DriverStore\FileRepository\qccamsecureisp8380.inf_arm64_*\QcISPTrustlet8380.dll' -ErrorAction Stop | Select-Object -First 1
$swasf=[IO.File]::ReadAllBytes('C:\Users\Geoca\Documents\E004DH-oracle\SWASF-derived-from-live-cache.bin')
$cs=@'
using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
public static class E004DHCD90Pause {
 [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)] static extern IntPtr LoadLibraryW(string p);
 [UnmanagedFunctionPointer(CallingConvention.Winapi)] delegate uint Fn8(uint a0,ulong a1,ulong a2,ulong a3,ulong a4,ulong a5,ulong a6,ulong a7);
 static IntPtr H(IntPtr m){return Marshal.ReadIntPtr(IntPtr.Add(m,0x3da78));}
 public static string Run(string dll,byte[] tune,string outDir){
  IntPtr m=LoadLibraryW(dll);if(m==IntPtr.Zero)throw new Exception("LoadLibrary "+Marshal.GetLastWin32Error());var init=(Fn8)Marshal.GetDelegateForFunctionPointer(IntPtr.Add(m,0x19440),typeof(Fn8));var proc=(Fn8)Marshal.GetDelegateForFunctionPointer(IntPtr.Add(m,0x19828),typeof(Fn8));
  const int W=64,Ht=64,N=W*Ht*3/2;ulong dims=(ulong)W|((ulong)Ht<<16)|((ulong)W<<32);byte[] src=new byte[N],dst=new byte[N];for(int y=0;y<Ht;y++)for(int x=0;x<W;x++)src[y*W+x]=(byte)((x*17+y*29+((x*y)%31))&255);for(int i=W*Ht;i<N;i++)src[i]=(byte)(0x80+((i-W*Ht)&31));for(int i=0;i<N;i++)dst[i]=0x5a;
  uint ir=init(0,dims,0,0,0,0,0,0);if(ir!=0)throw new Exception("init 0x"+ir.ToString("x8"));Marshal.Copy(tune,0,IntPtr.Add(m,0x3d240),tune.Length);IntPtr h=H(m);var gs=GCHandle.Alloc(src,GCHandleType.Pinned);var gd=GCHandle.Alloc(dst,GCHandleType.Pinned);
  try{ulong ps=(ulong)gs.AddrOfPinnedObject().ToInt64(),pd=(ulong)gd.AddrOfPinnedObject().ToInt64();var s=new StringBuilder();s.AppendLine("PID="+System.Diagnostics.Process.GetCurrentProcess().Id);s.AppendLine("DLL_BASE=0x"+m.ToInt64().ToString("x"));s.AppendLine("CD90=0x"+(m.ToInt64()+0x1cd90).ToString("x"));s.AppendLine("HANDLE=0x"+h.ToInt64().ToString("x"));s.AppendLine("SRC=0x"+ps.ToString("x"));s.AppendLine("DST=0x"+pd.ToString("x"));File.WriteAllText(Path.Combine(outDir,"READY.txt"),s.ToString());File.WriteAllBytes(Path.Combine(outDir,"input-64x64-nv12.bin"),src);System.Threading.Thread.Sleep(120000);uint pr=proc(0,ps,pd,dims,0,0,0,0);s.AppendLine("PROCESS=0x"+pr.ToString("x8"));File.WriteAllBytes(Path.Combine(outDir,"output-64x64-nv12.bin"),dst);File.WriteAllText(Path.Combine(outDir,"DONE.txt"),s.ToString());return s.ToString();}
  finally{gs.Free();gd.Free();}
 }
}
'@
Add-Type -TypeDefinition $cs -Language CSharp
[E004DHCD90Pause]::Run($dll.FullName,$swasf,$out) | Tee-Object -FilePath "$out\ORACLE.log"
