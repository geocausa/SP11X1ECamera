$ErrorActionPreference='Stop'
$out='C:\Users\Geoca\Documents\E004DH-swasf-c3e8-tile-oracle'
New-Item -ItemType Directory -Force -Path $out | Out-Null
$dll=Get-ChildItem 'C:\WINDOWS\System32\DriverStore\FileRepository\qccamsecureisp8380.inf_arm64_*\QcISPTrustlet8380.dll' -ErrorAction Stop | Select-Object -First 1
$cs=@'
using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
public static class E004DHC3E8TileOracle {
 [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)] static extern IntPtr LoadLibraryW(string p);
 [UnmanagedFunctionPointer(CallingConvention.Winapi)] delegate uint InitFn(uint a0,ulong a1,ulong a2,ulong a3,ulong a4,ulong a5,ulong a6,ulong a7);
 [UnmanagedFunctionPointer(CallingConvention.Winapi)] delegate void C3E8(IntPtr src,ushort stride,ushort x0,ushort x1,ushort y0,ushort y1,ushort width,ushort height,IntPtr p9,IntPtr p10,IntPtr o11,IntPtr o12,IntPtr o13);
 static string Sha(byte[] b){using(var s=SHA256.Create())return BitConverter.ToString(s.ComputeHash(b)).Replace("-","").ToLowerInvariant();}
 static uint Xs(ref uint x){x^=x<<13;x^=x>>17;x^=x<<5;return x;}
 static short[] Pattern(string n,int w,int h){var a=new short[w*h];for(int i=0;i<a.Length;i++)a[i]=512;if(n=="const")return a;if(n=="impulsep"){a[(h/2)*w+w/2]=768;return a;}if(n=="impulsem"){a[(h/2)*w+w/2]=256;return a;}if(n=="hstep"){for(int y=0;y<h;y++)for(int x=0;x<w;x++)a[y*w+x]=(short)(x<w/2?256:768);return a;}if(n=="vstep"){for(int y=0;y<h;y++)for(int x=0;x<w;x++)a[y*w+x]=(short)(y<h/2?256:768);return a;}if(n=="checker"){for(int y=0;y<h;y++)for(int x=0;x<w;x++)a[y*w+x]=(short)(((x^y)&1)!=0?768:256);return a;}if(n=="random"){uint q=0x80100u;for(int i=0;i<a.Length;i++)a[i]=(short)(Xs(ref q)&1023);return a;}throw new Exception(n);}
 static byte[] Bytes(short[] a){byte[] b=new byte[a.Length*2];Buffer.BlockCopy(a,0,b,0,b.Length);return b;}
 public static string Run(string dll,string outDir){
  IntPtr hm=LoadLibraryW(dll);if(hm==IntPtr.Zero)throw new Exception("LoadLibrary "+Marshal.GetLastWin32Error());var init=(InitFn)Marshal.GetDelegateForFunctionPointer(IntPtr.Add(hm,0x19440),typeof(InitFn));var f=(C3E8)Marshal.GetDelegateForFunctionPointer(IntPtr.Add(hm,0x1c3e8),typeof(C3E8));const int W=16,H=16,N=W*H;ulong dims=(ulong)W|((ulong)H<<16)|((ulong)W<<32);uint ir=init(0,dims,0,0,0,0,0,0);var log=new StringBuilder();log.AppendLine("INIT=0x"+ir.ToString("x8"));if(ir!=0)return log.ToString();
  foreach(string n in new[]{"const","impulsep","impulsem","hstep","vstep","checker","random"}){
   short[] src=Pattern(n,W,H),flt=new short[N];for(int i=0;i<N;i++)flt[i]=unchecked((short)0xcafe);int[] o11=new int[H*8+32];byte[] o12=new byte[H*8+32];
   var gs=GCHandle.Alloc(src,GCHandleType.Pinned);var gf=GCHandle.Alloc(flt,GCHandleType.Pinned);var g11=GCHandle.Alloc(o11,GCHandleType.Pinned);var g12=GCHandle.Alloc(o12,GCHandleType.Pinned);
   try{for(int x0=0;x0<W;x0+=8){int x1=Math.Min(W,x0+8);f(gs.AddrOfPinnedObject(),W,(ushort)x0,(ushort)x1,0,H,W,H,IntPtr.Add(hm,0x3c138),IntPtr.Add(hm,0x3c120),g11.AddrOfPinnedObject(),g12.AddrOfPinnedObject(),gf.AddrOfPinnedObject());}}
   finally{gs.Free();gf.Free();g11.Free();g12.Free();}
   byte[] sb=Bytes(src),fb=Bytes(flt);int sent=0;short mn=short.MaxValue,mx=short.MinValue;for(int i=0;i<N;i++){if(flt[i]==unchecked((short)0xcafe))sent++;if(flt[i]<mn)mn=flt[i];if(flt[i]>mx)mx=flt[i];}
   File.WriteAllBytes(Path.Combine(outDir,n+"-src16.bin"),sb);File.WriteAllBytes(Path.Combine(outDir,n+"-filter16.bin"),fb);log.AppendLine(n+" SRC="+Sha(sb)+" FILTER="+Sha(fb)+" SENTINEL="+sent+" MIN="+mn+" MAX="+mx);
  }
  File.WriteAllText(Path.Combine(outDir,"RESULT.txt"),log.ToString());return log.ToString();
 }
}
'@
Add-Type -TypeDefinition $cs -Language CSharp
$head=@('E004dh C3E8 8-pixel tile oracle',('time='+[DateTimeOffset]::Now.ToString('o')),('dll_sha256='+(Get-FileHash $dll.FullName -Algorithm SHA256).Hash.ToLower()))
$body=[E004DHC3E8TileOracle]::Run($dll.FullName,$out)
(($head -join "`r`n")+"`r`n"+$body) | Tee-Object -FilePath "$out\ORACLE.log"
