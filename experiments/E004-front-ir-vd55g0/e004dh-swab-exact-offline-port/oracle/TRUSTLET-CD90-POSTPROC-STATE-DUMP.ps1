$ErrorActionPreference='Stop'
$out='C:\Users\Geoca\Documents\E004DH-cd90-postproc-state'
New-Item -ItemType Directory -Force -Path $out | Out-Null
$dll=Get-ChildItem 'C:\WINDOWS\System32\DriverStore\FileRepository\qccamsecureisp8380.inf_arm64_*\QcISPTrustlet8380.dll' -ErrorAction Stop | Select-Object -First 1
$tune=[IO.File]::ReadAllBytes('C:\Users\Geoca\Documents\E004DH-oracle\SWASF-derived-from-live-cache.bin')
$cs=@'
using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
public static class E004DHPostProcState {
 [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)] static extern IntPtr LoadLibraryW(string p);
 [UnmanagedFunctionPointer(CallingConvention.Winapi)] delegate uint Fn8(uint a0,ulong a1,ulong a2,ulong a3,ulong a4,ulong a5,ulong a6,ulong a7);
 static string Sha(byte[] b){using(var s=SHA256.Create())return BitConverter.ToString(s.ComputeHash(b)).Replace("-","").ToLowerInvariant();}
 static byte[] Dump(IntPtr m,int off,int n){var b=new byte[n];Marshal.Copy(IntPtr.Add(m,off),b,0,n);return b;}
 static void Save(StringBuilder s,string outDir,IntPtr m,string name,int off,int n){var b=Dump(m,off,n);File.WriteAllBytes(Path.Combine(outDir,name+".bin"),b);s.AppendLine(name+" off=0x"+off.ToString("x")+" len="+n+" sha256="+Sha(b));}
 public static string Run(string dll,byte[] tune,string outDir){
  IntPtr m=LoadLibraryW(dll);if(m==IntPtr.Zero)throw new Exception("LoadLibrary "+Marshal.GetLastWin32Error());
  var init=(Fn8)Marshal.GetDelegateForFunctionPointer(IntPtr.Add(m,0x19440),typeof(Fn8));
  var proc=(Fn8)Marshal.GetDelegateForFunctionPointer(IntPtr.Add(m,0x19828),typeof(Fn8));
  const int W=64,H=64,N=W*H*3/2;ulong dims=(ulong)W|((ulong)H<<16)|((ulong)W<<32);
  byte[] src=new byte[N],dst=new byte[N];for(int y=0;y<H;y++)for(int x=0;x<W;x++)src[y*W+x]=(byte)((x*17+y*29+((x*y)%31))&255);for(int i=W*H;i<N;i++)src[i]=(byte)(0x80+((i-W*H)&31));
  uint ir=init(0,dims,0,0,0,0,0,0);if(ir!=0)throw new Exception("init 0x"+ir.ToString("x8"));Marshal.Copy(tune,0,IntPtr.Add(m,0x3d240),tune.Length);
  var gs=GCHandle.Alloc(src,GCHandleType.Pinned);var gd=GCHandle.Alloc(dst,GCHandleType.Pinned);uint pr;
  try{pr=proc(0,(ulong)gs.AddrOfPinnedObject().ToInt64(),(ulong)gd.AddrOfPinnedObject().ToInt64(),dims,0,0,0,0);}finally{gs.Free();gd.Free();}
  var s=new StringBuilder();s.AppendLine("DLL_BASE=0x"+m.ToInt64().ToString("x"));s.AppendLine("INIT=0x"+ir.ToString("x8"));s.AppendLine("PROC=0x"+pr.ToString("x8"));s.AppendLine("OUTPUT_SHA256="+Sha(dst));
  Save(s,outDir,m,"globals-3d230",0x3d230,0x20);
  Save(s,outDir,m,"tune-global-3d240",0x3d240,0x804);
  Save(s,outDir,m,"tab-3dea0",0x3dea0,0x200);
  Save(s,outDir,m,"tab-3dfe0",0x3dfe0,0x200);
  Save(s,outDir,m,"tab-3e100",0x3e100,0x200);
  Save(s,outDir,m,"tab-2f620",0x2f620,0x100);
  Save(s,outDir,m,"tab-2f720",0x2f720,0x400);
  Save(s,outDir,m,"tab-2fb20",0x2fb20,0x100);
  Save(s,outDir,m,"tab-2fc20",0x2fc20,0x400);
  File.WriteAllBytes(Path.Combine(outDir,"output-64x64-nv12.bin"),dst);
  File.WriteAllText(Path.Combine(outDir,"RESULT.txt"),s.ToString());return s.ToString();
 }
}
'@
Add-Type -TypeDefinition $cs -Language CSharp
$head=@('E004dh CD90 post-proc state dump',('time='+[DateTimeOffset]::Now.ToString('o')),('dll_sha256='+(Get-FileHash $dll.FullName -Algorithm SHA256).Hash.ToLower()),('tune_sha256='+(Get-FileHash 'C:\Users\Geoca\Documents\E004DH-oracle\SWASF-derived-from-live-cache.bin' -Algorithm SHA256).Hash.ToLower()))
$body=[E004DHPostProcState]::Run($dll.FullName,$tune,$out)
(($head -join "`r`n")+"`r`n"+$body) | Tee-Object -FilePath "$out\ORACLE.log"
