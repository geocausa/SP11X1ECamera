$ErrorActionPreference='Stop'
$out='C:\Users\Geoca\Documents\E004DH-swasf-cd90-basis'
New-Item -ItemType Directory -Force -Path $out | Out-Null
$dll=Get-ChildItem 'C:\WINDOWS\System32\DriverStore\FileRepository\qccamsecureisp8380.inf_arm64_*\QcISPTrustlet8380.dll' -ErrorAction Stop | Select-Object -First 1
$tune=[IO.File]::ReadAllBytes('C:\Users\Geoca\Documents\E004DH-oracle\SWASF-derived-from-live-cache.bin')
$cs=@'
using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
public static class E004DHCD90Basis {
 [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)] static extern IntPtr LoadLibraryW(string p);
 [UnmanagedFunctionPointer(CallingConvention.Winapi)] delegate uint InitFn(uint a0,ulong a1,ulong a2,ulong a3,ulong a4,ulong a5,ulong a6,ulong a7);
 [UnmanagedFunctionPointer(CallingConvention.Winapi)] delegate void CD90(IntPtr p1,IntPtr p2,IntPtr p3,IntPtr p4,IntPtr p5,IntPtr p6,IntPtr p7,IntPtr p8,IntPtr p9,IntPtr p10,IntPtr p11,IntPtr p12,IntPtr p13);
 static string B(byte[] a){return BitConverter.ToString(a).Replace("-","").ToLowerInvariant();}
 static void Fill(short[] a,short v){for(int i=0;i<a.Length;i++)a[i]=v;} static void Fill(int[] a,int v){for(int i=0;i<a.Length;i++)a[i]=v;} static void Fill(byte[] a,byte v){for(int i=0;i<a.Length;i++)a[i]=v;}
 sealed class V:IDisposable {
  public short[] p1=new short[8],p4=new short[8],p5=new short[8],p6=new short[8],p7=new short[8],p10=new short[8],p11=new short[8],p12=new short[8];
  public byte[] p2=new byte[8],p3=new byte[8],p9=new byte[8]; public int[] p8=new int[8]; public byte[] tune;
  GCHandle[] h;
  public V(byte[] t){tune=(byte[])t.Clone(); Neutral(); Pin();}
  public void Neutral(){Fill(p1,512);Fill(p2,0x5a);Fill(p3,0);Fill(p4,0);Fill(p5,0);Fill(p6,0);Fill(p7,0);Fill(p8,0);Fill(p9,128);Fill(p10,512);Fill(p11,512);Fill(p12,512);}
  void Pin(){object[] a={p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,tune};h=new GCHandle[a.Length];for(int i=0;i<a.Length;i++)h[i]=GCHandle.Alloc(a[i],GCHandleType.Pinned);}
  public IntPtr P(int i){return h[i].AddrOfPinnedObject();}
  public void Dispose(){foreach(var x in h)if(x.IsAllocated)x.Free();}
 }
 static string Eval(CD90 f,byte[] tune,Action<V> edit){using(var v=new V(tune)){edit(v);f(v.P(0),v.P(1),v.P(2),v.P(3),v.P(4),v.P(5),v.P(6),v.P(7),v.P(8),v.P(9),v.P(10),v.P(11),v.P(12));return B(v.p2);}}
 public static string Run(string dll,byte[] tune,string outDir){
  IntPtr hm=LoadLibraryW(dll);if(hm==IntPtr.Zero)throw new Exception("LoadLibrary "+Marshal.GetLastWin32Error());var init=(InitFn)Marshal.GetDelegateForFunctionPointer(IntPtr.Add(hm,0x19440),typeof(InitFn));var f=(CD90)Marshal.GetDelegateForFunctionPointer(IntPtr.Add(hm,0x1cd90),typeof(CD90));const int W=16,H=16;ulong dims=(ulong)W|((ulong)H<<16)|((ulong)W<<32);uint ir=init(0,dims,0,0,0,0,0,0);var s=new StringBuilder();s.AppendLine("INIT=0x"+ir.ToString("x8"));if(ir!=0)return s.ToString();
  foreach(var z in new[]{new[]{"tab-2f620","2f620","1024"},new[]{"tab-2fb20","2fb20","1024"},new[]{"tab-3dea0","3dea0","512"},new[]{"tab-3dfe0","3dfe0","512"},new[]{"tab-3e100","3e100","512"},new[]{"globals-3d230","3d230","32"}}){int off=Convert.ToInt32(z[1],16),n=int.Parse(z[2]);byte[] b=new byte[n];Marshal.Copy(IntPtr.Add(hm,off),b,0,n);File.WriteAllBytes(Path.Combine(outDir,z[0]+".bin"),b);s.AppendLine(z[0].ToUpper()+"="+B(b));}
  s.AppendLine("BASE="+Eval(f,tune,v=>{}));
  string[] names={"p1","p3","p4","p5","p6","p7","p8","p9","p10","p11","p12"};
  foreach(string n in names){foreach(int d in new[]{-256,-64,-1,1,64,256}){string o=Eval(f,tune,v=>{switch(n){case "p1":v.p1[0]=(short)(512+d);break;case "p3":v.p3[0]=(byte)Math.Max(0,Math.Min(255,d+128));break;case "p4":v.p4[0]=(short)d;break;case "p5":v.p5[0]=(short)d;break;case "p6":v.p6[0]=(short)d;break;case "p7":v.p7[0]=(short)d;break;case "p8":v.p8[0]=d;break;case "p9":v.p9[0]=(byte)Math.Max(0,Math.Min(255,128+d));break;case "p10":v.p10[0]=(short)(512+d);break;case "p11":v.p11[0]=(short)(512+d);break;case "p12":v.p12[0]=(short)(512+d);break;}});s.AppendLine(n+" D="+d+" OUT="+o);}}
  // Cross-lane probe: perturb lane 3 of every input independently.
  foreach(string n in names){string o=Eval(f,tune,v=>{switch(n){case "p1":v.p1[3]=768;break;case "p3":v.p3[3]=192;break;case "p4":v.p4[3]=256;break;case "p5":v.p5[3]=256;break;case "p6":v.p6[3]=256;break;case "p7":v.p7[3]=256;break;case "p8":v.p8[3]=256;break;case "p9":v.p9[3]=192;break;case "p10":v.p10[3]=768;break;case "p11":v.p11[3]=768;break;case "p12":v.p12[3]=768;break;}});s.AppendLine(n+" L3 OUT="+o);}
  File.WriteAllText(Path.Combine(outDir,"RESULT.txt"),s.ToString());return s.ToString();
 }
}
'@
Add-Type -TypeDefinition $cs -Language CSharp
$head=@('E004dh CD90 basis oracle',('time='+[DateTimeOffset]::Now.ToString('o')),('dll_sha256='+(Get-FileHash $dll.FullName -Algorithm SHA256).Hash.ToLower()))
$body=[E004DHCD90Basis]::Run($dll.FullName,$tune,$out)
(($head -join "`r`n")+"`r`n"+$body) | Tee-Object -FilePath "$out\ORACLE.log"
