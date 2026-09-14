$ErrorActionPreference='Stop'
$out='C:\Users\Geoca\Documents\E004DH-swasf-c230-basis'
New-Item -ItemType Directory -Force -Path $out | Out-Null
$dll=Get-ChildItem 'C:\WINDOWS\System32\DriverStore\FileRepository\qccamsecureisp8380.inf_arm64_*\QcISPTrustlet8380.dll' -ErrorAction Stop | Select-Object -First 1
$cs=@'
using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
public static class E004DHC230Basis {
 [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)] static extern IntPtr LoadLibraryW(string p);
 [UnmanagedFunctionPointer(CallingConvention.Winapi)] delegate uint InitFn(uint a0,ulong a1,ulong a2,ulong a3,ulong a4,ulong a5,ulong a6,ulong a7);
 [UnmanagedFunctionPointer(CallingConvention.Winapi)] delegate void C230(IntPtr rows,ulong a2,ulong a3,IntPtr out4,IntPtr out2,ulong a6,ulong a7,IntPtr tail2);
 static string Hex(byte[] b){return BitConverter.ToString(b).Replace("-","").ToLowerInvariant();}
 static string S4(short[] v){return v[0]+","+v[1]+","+v[2]+","+v[3];}
 static string B2(byte[] v){return v[0]+","+v[1];}
 static void Eval(C230 f,short[][] rows,short t0,short t1,out short[] o4,out byte[] o2){
   var gr=new GCHandle[7];var rp=new IntPtr[7];o4=new short[4];o2=new byte[2];short[] tail={t0,t1};
   GCHandle gp=default(GCHandle),g4=default(GCHandle),g2=default(GCHandle),gt=default(GCHandle);
   try{for(int r=0;r<7;r++){gr[r]=GCHandle.Alloc(rows[r],GCHandleType.Pinned);rp[r]=gr[r].AddrOfPinnedObject();}gp=GCHandle.Alloc(rp,GCHandleType.Pinned);g4=GCHandle.Alloc(o4,GCHandleType.Pinned);g2=GCHandle.Alloc(o2,GCHandleType.Pinned);gt=GCHandle.Alloc(tail,GCHandleType.Pinned);f(gp.AddrOfPinnedObject(),0,0,g4.AddrOfPinnedObject(),g2.AddrOfPinnedObject(),0,0,gt.AddrOfPinnedObject());}
   finally{if(gp.IsAllocated)gp.Free();if(g4.IsAllocated)g4.Free();if(g2.IsAllocated)g2.Free();if(gt.IsAllocated)gt.Free();for(int r=0;r<7;r++)if(gr[r].IsAllocated)gr[r].Free();}
 }
 static short[][] Flat(short v){var a=new short[7][];for(int r=0;r<7;r++){a[r]=new short[8];for(int c=0;c<8;c++)a[r][c]=v;}return a;}
 public static string Run(string dll,string outDir){
   IntPtr h=LoadLibraryW(dll);if(h==IntPtr.Zero)throw new Exception("LoadLibrary "+Marshal.GetLastWin32Error());
   var init=(InitFn)Marshal.GetDelegateForFunctionPointer(IntPtr.Add(h,0x19440),typeof(InitFn));var f=(C230)Marshal.GetDelegateForFunctionPointer(IntPtr.Add(h,0x1c230),typeof(C230));
   const int W=16,H=16;ulong dims=(ulong)W|((ulong)H<<16)|((ulong)W<<32);uint ir=init(0,dims,0,0,0,0,0,0);var s=new StringBuilder();s.AppendLine("DLL_BASE=0x"+h.ToInt64().ToString("x"));s.AppendLine("INIT=0x"+ir.ToString("x8"));if(ir!=0)return s.ToString();
   byte[] k=new byte[0x30];Marshal.Copy(IntPtr.Add(h,0x3c120),k,0,k.Length);File.WriteAllBytes(Path.Combine(outDir,"constants-3c120.bin"),k);s.AppendLine("CONSTANTS="+Hex(k));
   short[] b4;byte[] b2;Eval(f,Flat(512),512,512,out b4,out b2);s.AppendLine("BASE O4="+S4(b4)+" O2="+B2(b2));
   foreach(short delta in new short[]{256,-256}){
     s.AppendLine("DELTA="+delta);
     for(int r=0;r<7;r++)for(int c=0;c<8;c++){var a=Flat(512);a[r][c]=(short)(512+delta);short[] o4;byte[] o2;Eval(f,a,512,512,out o4,out o2);s.AppendLine("R="+r+" C="+c+" O4="+S4(o4)+" O2="+B2(o2));}
     for(int t=0;t<2;t++){short[] o4;byte[] o2;Eval(f,Flat(512),(short)(512+(t==0?delta:0)),(short)(512+(t==1?delta:0)),out o4,out o2);s.AppendLine("T="+t+" O4="+S4(o4)+" O2="+B2(o2));}
   }
   File.WriteAllText(Path.Combine(outDir,"RESULT.txt"),s.ToString());return s.ToString();
 }
}
'@
Add-Type -TypeDefinition $cs -Language CSharp
$head=@('E004dh C230 linear basis oracle',('time='+[DateTimeOffset]::Now.ToString('o')),('dll_sha256='+(Get-FileHash $dll.FullName -Algorithm SHA256).Hash.ToLower()))
$body=[E004DHC230Basis]::Run($dll.FullName,$out)
(($head -join "`r`n")+"`r`n"+$body) | Tee-Object -FilePath "$out\ORACLE.log"
