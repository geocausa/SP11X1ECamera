$ErrorActionPreference='Stop'
$out='C:\Users\Geoca\Documents\E004DH-swasf-c230-random-diff'
New-Item -ItemType Directory -Force -Path $out | Out-Null
$dll=Get-ChildItem 'C:\WINDOWS\System32\DriverStore\FileRepository\qccamsecureisp8380.inf_arm64_*\QcISPTrustlet8380.dll' -ErrorAction Stop | Select-Object -First 1
$cs=@'
using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
public static class E004DHC230RandomDiff {
 [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)] static extern IntPtr LoadLibraryW(string p);
 [UnmanagedFunctionPointer(CallingConvention.Winapi)] delegate uint InitFn(uint a0,ulong a1,ulong a2,ulong a3,ulong a4,ulong a5,ulong a6,ulong a7);
 [UnmanagedFunctionPointer(CallingConvention.Winapi)] delegate void C230(IntPtr rows,ulong a2,ulong a3,IntPtr out4,IntPtr out2,ulong a6,ulong a7,IntPtr tail2);
 static readonly int[,] HP={{-7,-23,-41,-49,-41,-23,-7},{-23,-73,-74,-53,-74,-73,-23},{-41,-74,89,242,89,-74,-41},{-49,-53,242,0,242,-53,-49},{-41,-74,89,242,89,-74,-41},{-23,-73,-74,-53,-74,-73,-23},{-7,-23,-41,-49,-41,-23,-7}};
 static readonly int[,] LP={{0,0,0,0,0,0,0},{0,9,23,31,23,9,0},{0,23,60,82,60,23,0},{0,31,82,0,82,31,0},{0,23,60,82,60,23,0},{0,9,23,31,23,9,0},{0,0,0,0,0,0,0}};
 static int Sr(long v,int s){return (int)((v+(1L<<(s-1)))>>s);}
 static void Scalar(short[][] rows,short[] tail,int[] o4,byte[] o2){for(int lane=0;lane<2;lane++){long hp=508L*tail[lane],lp=112L*tail[lane];for(int r=0;r<7;r++)for(int c=0;c<7;c++){int px=rows[r][c+lane];hp+=HP[r,c]*px;lp+=LP[r,c]*px;}o4[lane]=Sr(hp,8);o2[lane]=(byte)Sr(lp,12);}}
 static uint Xs(ref uint x){x^=x<<13;x^=x>>17;x^=x<<5;return x;}
 static string Sha(byte[] b){using(var s=SHA256.Create())return BitConverter.ToString(s.ComputeHash(b)).Replace("-","").ToLowerInvariant();}
 static void Put(MemoryStream m,int[] o4,byte[] o2){foreach(int v in o4){byte[] b=BitConverter.GetBytes(v);m.Write(b,0,b.Length);}m.WriteByte(o2[0]);m.WriteByte(o2[1]);}
 public static string Run(string dll,string outDir){
   IntPtr h=LoadLibraryW(dll);if(h==IntPtr.Zero)throw new Exception("LoadLibrary "+Marshal.GetLastWin32Error());var init=(InitFn)Marshal.GetDelegateForFunctionPointer(IntPtr.Add(h,0x19440),typeof(InitFn));var f=(C230)Marshal.GetDelegateForFunctionPointer(IntPtr.Add(h,0x1c230),typeof(C230));const int W=16,H=16;ulong dims=(ulong)W|((ulong)H<<16)|((ulong)W<<32);uint ir=init(0,dims,0,0,0,0,0,0);var log=new StringBuilder();log.AppendLine("INIT=0x"+ir.ToString("x8"));if(ir!=0)return log.ToString();
   const int N=4096;uint rng=0x1e80100u;var winStream=new MemoryStream();var refStream=new MemoryStream();
   for(int it=0;it<N;it++){
     short[][] rows=new short[7][];var gr=new GCHandle[7];var rp=new IntPtr[7];for(int r=0;r<7;r++){rows[r]=new short[8];for(int c=0;c<8;c++)rows[r][c]=(short)(Xs(ref rng)&1023);gr[r]=GCHandle.Alloc(rows[r],GCHandleType.Pinned);rp[r]=gr[r].AddrOfPinnedObject();}
     short[] tail={(short)(Xs(ref rng)&1023),(short)(Xs(ref rng)&1023)};int[] wo4=new int[2],ro4=new int[2];byte[] wo2=new byte[2],ro2=new byte[2];var gp=GCHandle.Alloc(rp,GCHandleType.Pinned);var gt=GCHandle.Alloc(tail,GCHandleType.Pinned);var g4=GCHandle.Alloc(wo4,GCHandleType.Pinned);var g2=GCHandle.Alloc(wo2,GCHandleType.Pinned);
     try{f(gp.AddrOfPinnedObject(),0,0,g4.AddrOfPinnedObject(),g2.AddrOfPinnedObject(),0,0,gt.AddrOfPinnedObject());}finally{gp.Free();gt.Free();g4.Free();g2.Free();for(int r=0;r<7;r++)gr[r].Free();}
     Scalar(rows,tail,ro4,ro2);Put(winStream,wo4,wo2);Put(refStream,ro4,ro2);
     if(wo4[0]!=ro4[0]||wo4[1]!=ro4[1]||wo2[0]!=ro2[0]||wo2[1]!=ro2[1]){log.AppendLine("FAIL it="+it+" WIN="+wo4[0]+","+wo4[1]+","+wo2[0]+","+wo2[1]+" REF="+ro4[0]+","+ro4[1]+","+ro2[0]+","+ro2[1]);File.WriteAllText(Path.Combine(outDir,"RESULT.txt"),log.ToString());return log.ToString();}
   }
   string ws=Sha(winStream.ToArray()),rs=Sha(refStream.ToArray());log.AppendLine("CASES="+N);log.AppendLine("WINDOWS_SHA256="+ws);log.AppendLine("SCALAR_SHA256="+rs);log.AppendLine("BYTE_EXACT="+(ws==rs?"true":"false"));File.WriteAllText(Path.Combine(outDir,"RESULT.txt"),log.ToString());return log.ToString();
 }
}
'@
Add-Type -TypeDefinition $cs -Language CSharp
$head=@('E004dh C230 random differential',('time='+[DateTimeOffset]::Now.ToString('o')),('dll_sha256='+(Get-FileHash $dll.FullName -Algorithm SHA256).Hash.ToLower()))
$body=[E004DHC230RandomDiff]::Run($dll.FullName,$out)
(($head -join "`r`n")+"`r`n"+$body) | Tee-Object -FilePath "$out\ORACLE.log"
