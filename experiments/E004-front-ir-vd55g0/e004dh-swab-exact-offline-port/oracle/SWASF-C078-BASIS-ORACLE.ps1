$ErrorActionPreference='Stop'
$out='C:\Users\Geoca\Documents\E004DH-swasf-c078-basis'
New-Item -ItemType Directory -Force -Path $out | Out-Null
$dll=Get-ChildItem 'C:\WINDOWS\System32\DriverStore\FileRepository\qccamsecureisp8380.inf_arm64_*\QcISPTrustlet8380.dll' -ErrorAction Stop | Select-Object -First 1
$cs=@'
using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
public static class E004DHC078Basis {
 [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)] static extern IntPtr LoadLibraryW(string p);
 [UnmanagedFunctionPointer(CallingConvention.Winapi)] delegate void C078(IntPtr rows,IntPtr output,short center,short scale);
 static byte Eval(C078 f,int rr,int cc,short delta){
   short[][] v=new short[5][]; GCHandle[] gr=new GCHandle[5]; IntPtr[] rp=new IntPtr[5];
   byte[] o=new byte[1]; var go=GCHandle.Alloc(o,GCHandleType.Pinned); GCHandle pa=default(GCHandle);
   try{
     for(int r=0;r<5;r++){v[r]=new short[8];for(int c=0;c<8;c++)v[r][c]=100;}
     if(rr>=0)v[rr][cc]=(short)(100+delta);
     for(int r=0;r<5;r++){gr[r]=GCHandle.Alloc(v[r],GCHandleType.Pinned);rp[r]=gr[r].AddrOfPinnedObject();}
     pa=GCHandle.Alloc(rp,GCHandleType.Pinned); f(pa.AddrOfPinnedObject(),go.AddrOfPinnedObject(),100,253); return o[0];
   } finally {if(pa.IsAllocated)pa.Free();for(int r=0;r<5;r++)if(gr[r].IsAllocated)gr[r].Free();go.Free();}
 }
 public static string Run(string dll){
   IntPtr h=LoadLibraryW(dll);if(h==IntPtr.Zero)throw new Exception("LoadLibrary "+Marshal.GetLastWin32Error());
   var f=(C078)Marshal.GetDelegateForFunctionPointer(IntPtr.Add(h,0x1c078),typeof(C078));var s=new StringBuilder();
   s.AppendLine("DLL_BASE=0x"+h.ToInt64().ToString("x"));s.AppendLine("BASE="+Eval(f,-1,0,0));
   foreach(short d in new short[]{64,-64}){s.AppendLine("DELTA="+d);for(int r=0;r<5;r++){s.Append("R"+r+"=");for(int c=0;c<8;c++){if(c!=0)s.Append(',');s.Append(Eval(f,r,c,d));}s.AppendLine();}}
   return s.ToString();
 }
}
'@
Add-Type -TypeDefinition $cs -Language CSharp
$head=@('E004dh C078 basis oracle',('time='+[DateTimeOffset]::Now.ToString('o')),('dll_sha256='+(Get-FileHash $dll.FullName -Algorithm SHA256).Hash.ToLower()))
$body=[E004DHC078Basis]::Run($dll.FullName)
(($head -join "`r`n")+"`r`n"+$body) | Tee-Object -FilePath "$out\C078-BASIS.txt"
