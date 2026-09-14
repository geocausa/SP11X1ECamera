$ErrorActionPreference='Stop'
$out='C:\Users\Geoca\Documents\E004DH-cd90-random-vectors'
New-Item -ItemType Directory -Force -Path $out | Out-Null
$dll=Get-ChildItem 'C:\WINDOWS\System32\DriverStore\FileRepository\qccamsecureisp8380.inf_arm64_*\QcISPTrustlet8380.dll' -ErrorAction Stop | Select-Object -First 1
$tune=[IO.File]::ReadAllBytes('C:\Users\Geoca\Documents\E004DH-oracle\SWASF-derived-from-live-cache.bin')
$cs=@'
using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
public static class E004DHCD90RandomVectors {
 [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)] static extern IntPtr LoadLibraryW(string p);
 [UnmanagedFunctionPointer(CallingConvention.Winapi)] delegate uint Fn8(uint a0,ulong a1,ulong a2,ulong a3,ulong a4,ulong a5,ulong a6,ulong a7);
 [UnmanagedFunctionPointer(CallingConvention.Winapi)] delegate void CD(IntPtr a,IntPtr b,IntPtr c,IntPtr d,IntPtr e,IntPtr f,IntPtr g,IntPtr h,IntPtr i,IntPtr j,IntPtr k,IntPtr l,IntPtr m);
 static uint Xs(ref uint x){x^=x<<13;x^=x>>17;x^=x<<5;return x;}
 static string Sha(byte[] b){using(var s=SHA256.Create())return BitConverter.ToString(s.ComputeHash(b)).Replace("-","").ToLowerInvariant();}
 sealed class V:IDisposable {
  public short[] p1=new short[64],p4=new short[64],p5=new short[64],p6=new short[64],p7=new short[64],p10=new short[64],p11=new short[64],p12=new short[64];
  public byte[] p2=new byte[64],p3=new byte[64],p9=new byte[64],p13; public int[] p8=new int[64]; GCHandle[] g;
  public V(byte[] tune){p13=(byte[])tune.Clone();object[] x={p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13};g=new GCHandle[x.Length];for(int n=0;n<x.Length;n++)g[n]=GCHandle.Alloc(x[n],GCHandleType.Pinned);}
  public IntPtr P(int n){return g[n].AddrOfPinnedObject();} public void Dispose(){foreach(var x in g)if(x.IsAllocated)x.Free();}
 }
 static void FillCase(V v,ref uint rng){
  Array.Clear(v.p2,0,v.p2.Length);
  for(int i=0;i<8;i++){
   v.p1[i]=(short)(Xs(ref rng)&1023); v.p3[i]=(byte)(Xs(ref rng)&255);
   v.p4[i]=(short)(Xs(ref rng)&511); v.p5[i]=(short)(Xs(ref rng)&511); v.p6[i]=(short)(Xs(ref rng)&511); v.p7[i]=(short)(Xs(ref rng)&511);
   int m=(int)(Xs(ref rng)&2047)+1; v.p8[i]=((Xs(ref rng)&1)!=0)?m:-m; v.p9[i]=(byte)(Xs(ref rng)&255);
   v.p10[i]=(short)(Xs(ref rng)&1023); v.p11[i]=(short)(Xs(ref rng)%257); v.p12[i]=(short)(Xs(ref rng)%257);
  }
 }
 static void Write8(BinaryWriter w,short[] a){for(int i=0;i<8;i++)w.Write(a[i]);} static void Write8(BinaryWriter w,int[] a){for(int i=0;i<8;i++)w.Write(a[i]);} static void Write8(BinaryWriter w,byte[] a){w.Write(a,0,8);}
 public static string Run(string dll,byte[] tune,string outDir){
  IntPtr m=LoadLibraryW(dll);if(m==IntPtr.Zero)throw new Exception("LoadLibrary "+Marshal.GetLastWin32Error());
  var init=(Fn8)Marshal.GetDelegateForFunctionPointer(IntPtr.Add(m,0x19440),typeof(Fn8));var proc=(Fn8)Marshal.GetDelegateForFunctionPointer(IntPtr.Add(m,0x19828),typeof(Fn8));var cd=(CD)Marshal.GetDelegateForFunctionPointer(IntPtr.Add(m,0x1cd90),typeof(CD));
  const int W=64,H=64,FN=W*H*3/2;ulong dims=64UL|(64UL<<16)|(64UL<<32);uint ir=init(0,dims,0,0,0,0,0,0);if(ir!=0)throw new Exception("init "+ir);
  Marshal.Copy(tune,0,IntPtr.Add(m,0x3d240),tune.Length);
  byte[] src=new byte[FN],dst=new byte[FN];for(int y=0;y<H;y++)for(int x=0;x<W;x++)src[y*W+x]=(byte)((x*17+y*29+x*y%31)&255);for(int i=W*H;i<FN;i++)src[i]=0x80;
  var gs=GCHandle.Alloc(src,GCHandleType.Pinned);var gd=GCHandle.Alloc(dst,GCHandleType.Pinned);uint pr;try{pr=proc(0,(ulong)gs.AddrOfPinnedObject().ToInt64(),(ulong)gd.AddrOfPinnedObject().ToInt64(),dims,0,0,0,0);}finally{gs.Free();gd.Free();} if(pr!=0)throw new Exception("proc "+pr);
  const int N=4096;uint rng=0xcd908380u;string vp=Path.Combine(outDir,"vectors.bin");
  using(var fs=new FileStream(vp,FileMode.Create,FileAccess.Write))using(var bw=new BinaryWriter(fs)){
   bw.Write(0x30394443u); bw.Write(N); bw.Write(184); bw.Write(0x8380cd90u);
   for(int it=0;it<N;it++)using(var v=new V(tune)){
    FillCase(v,ref rng); cd(v.P(0),v.P(1),v.P(2),v.P(3),v.P(4),v.P(5),v.P(6),v.P(7),v.P(8),v.P(9),v.P(10),v.P(11),v.P(12));
    Write8(bw,v.p1);Write8(bw,v.p3);Write8(bw,v.p4);Write8(bw,v.p5);Write8(bw,v.p6);Write8(bw,v.p7);Write8(bw,v.p8);Write8(bw,v.p9);Write8(bw,v.p10);Write8(bw,v.p11);Write8(bw,v.p12);Write8(bw,v.p2);
   }
  }
  byte[] vb=File.ReadAllBytes(vp);File.WriteAllBytes(Path.Combine(outDir,"tune.bin"),tune);
  var s=new StringBuilder();s.AppendLine("INIT=0x"+ir.ToString("x8"));s.AppendLine("PROC=0x"+pr.ToString("x8"));s.AppendLine("CASES="+N);s.AppendLine("RECORD_BYTES=184");s.AppendLine("VECTORS_SHA256="+Sha(vb));s.AppendLine("TUNE_SHA256="+Sha(tune));File.WriteAllText(Path.Combine(outDir,"RESULT.txt"),s.ToString());return s.ToString();
 }
}
'@
Add-Type -TypeDefinition $cs -Language CSharp
$head=@('E004dh CD90 random-vector Windows oracle',('time='+[DateTimeOffset]::Now.ToString('o')),('dll_sha256='+(Get-FileHash $dll.FullName -Algorithm SHA256).Hash.ToLower()))
$body=[E004DHCD90RandomVectors]::Run($dll.FullName,$tune,$out)
(($head -join "`r`n")+"`r`n"+$body)|Tee-Object -FilePath "$out\ORACLE.log"
