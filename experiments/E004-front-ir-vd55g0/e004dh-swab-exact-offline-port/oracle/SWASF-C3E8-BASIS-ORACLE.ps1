$ErrorActionPreference='Stop'
$out='C:\Users\Geoca\Documents\E004DH-swasf-c3e8-basis'
New-Item -ItemType Directory -Force -Path $out | Out-Null
$dll=Get-ChildItem 'C:\WINDOWS\System32\DriverStore\FileRepository\qccamsecureisp8380.inf_arm64_*\QcISPTrustlet8380.dll' -ErrorAction Stop | Select-Object -First 1
$cs=@'
using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
public static class E004DHC3E8Basis {
 [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)] static extern IntPtr LoadLibraryW(string p);
 [UnmanagedFunctionPointer(CallingConvention.Winapi)] delegate uint InitFn(uint a0,ulong a1,ulong a2,ulong a3,ulong a4,ulong a5,ulong a6,ulong a7);
 [UnmanagedFunctionPointer(CallingConvention.Winapi)] delegate void C3E8(IntPtr src,ushort stride,ushort x0,ushort x1,ushort y0,ushort y1,ushort width,ushort height,IntPtr p9,IntPtr p10,IntPtr o11,IntPtr o12,IntPtr o13);
 static string Sha(byte[] b){using(var s=SHA256.Create())return BitConverter.ToString(s.ComputeHash(b)).Replace("-","").ToLowerInvariant();}
 static string Span(byte[] b,byte fill){int a=-1,z=-1,n=0;for(int i=0;i<b.Length;i++)if(b[i]!=fill){if(a<0)a=i;z=i;n++;}return "first="+a+" last="+z+" changed="+n;}
 static short[] Pattern(string name,int w,int h){var a=new short[w*h];for(int i=0;i<a.Length;i++)a[i]=512;if(name=="const")return a;if(name=="impulsep"){a[(h/2)*w+w/2]=768;return a;}if(name=="impulsem"){a[(h/2)*w+w/2]=256;return a;}if(name=="hstep"){for(int y=0;y<h;y++)for(int x=0;x<w;x++)a[y*w+x]=(short)(x<w/2?256:768);return a;}throw new Exception(name);}
 public static string Run(string dll,string outDir){
   IntPtr hmod=LoadLibraryW(dll);if(hmod==IntPtr.Zero)throw new Exception("LoadLibrary "+Marshal.GetLastWin32Error());
   var init=(InitFn)Marshal.GetDelegateForFunctionPointer(IntPtr.Add(hmod,0x19440),typeof(InitFn));
   var f=(C3E8)Marshal.GetDelegateForFunctionPointer(IntPtr.Add(hmod,0x1c3e8),typeof(C3E8));
   const int W=16,H=16,N=W*H,OUT=65536;ulong dims=(ulong)W|((ulong)H<<16)|((ulong)W<<32);
   uint ir=init(0,dims,0,0,0,0,0,0);var log=new StringBuilder();log.AppendLine("DLL_BASE=0x"+hmod.ToInt64().ToString("x"));log.AppendLine("INIT=0x"+ir.ToString("x8"));if(ir!=0)return log.ToString();
   foreach(string name in new[]{"const","impulsep","impulsem","hstep"}){
     short[] src=Pattern(name,W,H);byte[] o11=new byte[OUT],o12=new byte[OUT],o13=new byte[OUT];for(int i=0;i<OUT;i++){o11[i]=0xcc;o12[i]=0xcc;o13[i]=0xcc;}
     var gs=GCHandle.Alloc(src,GCHandleType.Pinned);var g11=GCHandle.Alloc(o11,GCHandleType.Pinned);var g12=GCHandle.Alloc(o12,GCHandleType.Pinned);var g13=GCHandle.Alloc(o13,GCHandleType.Pinned);
     try{f(gs.AddrOfPinnedObject(),W,0,W,0,H,W,H,IntPtr.Add(hmod,0x3c138),IntPtr.Add(hmod,0x3c120),g11.AddrOfPinnedObject(),g12.AddrOfPinnedObject(),g13.AddrOfPinnedObject());}
     finally{gs.Free();g11.Free();g12.Free();g13.Free();}
     byte[] sb=new byte[N*2];Buffer.BlockCopy(src,0,sb,0,sb.Length);File.WriteAllBytes(Path.Combine(outDir,name+"-src16.bin"),sb);File.WriteAllBytes(Path.Combine(outDir,name+"-o11.bin"),o11);File.WriteAllBytes(Path.Combine(outDir,name+"-o12.bin"),o12);File.WriteAllBytes(Path.Combine(outDir,name+"-o13.bin"),o13);
     log.AppendLine(name+" O11 "+Span(o11,0xcc)+" sha="+Sha(o11));log.AppendLine(name+" O12 "+Span(o12,0xcc)+" sha="+Sha(o12));log.AppendLine(name+" O13 "+Span(o13,0xcc)+" sha="+Sha(o13));
   }
   File.WriteAllText(Path.Combine(outDir,"RESULT.txt"),log.ToString());return log.ToString();
 }
}
'@
Add-Type -TypeDefinition $cs -Language CSharp
$head=@('E004dh C3E8 basis oracle',('time='+[DateTimeOffset]::Now.ToString('o')),('dll_sha256='+(Get-FileHash $dll.FullName -Algorithm SHA256).Hash.ToLower()))
$body=[E004DHC3E8Basis]::Run($dll.FullName,$out)
(($head -join "`r`n")+"`r`n"+$body) | Tee-Object -FilePath "$out\ORACLE.log"
