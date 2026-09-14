$ErrorActionPreference='Stop'
$out='C:\Users\Geoca\Documents\E004DH-swasf-runtime-dump'
New-Item -ItemType Directory -Force -Path $out | Out-Null
$dll=Get-ChildItem 'C:\WINDOWS\System32\DriverStore\FileRepository\qccamsecureisp8380.inf_arm64_*\QcISPTrustlet8380.dll' -ErrorAction Stop | Select-Object -First 1
$tune=[IO.File]::ReadAllBytes('C:\Users\Geoca\Documents\E004DH-oracle\SWASF-derived-from-live-cache.bin')
$cs=@'
using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
public static class E004DHSwasfRuntimeDump {
 [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)] static extern IntPtr LoadLibraryW(string path);
 [DllImport("kernel32.dll")] static extern bool FreeLibrary(IntPtr h);
 [UnmanagedFunctionPointer(CallingConvention.Winapi)] delegate uint Fn8(uint a0, ulong a1, ulong a2, ulong a3, ulong a4, ulong a5, ulong a6, ulong a7);
 [UnmanagedFunctionPointer(CallingConvention.Winapi)] delegate void FnDeinit(int module);
 static string Sha(byte[] b){using(var s=SHA256.Create())return BitConverter.ToString(s.ComputeHash(b)).Replace("-","").ToLowerInvariant();}
 static byte[] Read(IntPtr h,int rva,int n){var b=new byte[n];Marshal.Copy(IntPtr.Add(h,rva),b,0,n);return b;}
 static string U32(byte[] b,int off){return BitConverter.ToUInt32(b,off).ToString("x8");}
 public static string Run(string dll,byte[] tune,string outDir){
   Directory.CreateDirectory(outDir); IntPtr h=LoadLibraryW(dll); if(h==IntPtr.Zero)throw new Exception("LoadLibrary "+Marshal.GetLastWin32Error());
   var init=(Fn8)Marshal.GetDelegateForFunctionPointer(IntPtr.Add(h,0x19440),typeof(Fn8)); var deinit=(FnDeinit)Marshal.GetDelegateForFunctionPointer(IntPtr.Add(h,0x19ae0),typeof(FnDeinit));
   var log=new System.Text.StringBuilder(); log.AppendLine("base=0x"+h.ToInt64().ToString("x"));
   byte[] pre=Read(h,0x3c000,0x2200); File.WriteAllBytes(Path.Combine(outDir,"data-pre-init.bin"),pre); log.AppendLine("pre="+Sha(pre));
   const int W=64,H=64; ulong dims=(ulong)W|((ulong)H<<16)|((ulong)W<<32); uint ir=init(0,dims,0,0,0,0,0,0); log.AppendLine("init=0x"+ir.ToString("x8"));
   if(ir==0){
     Marshal.Copy(tune,0,IntPtr.Add(h,0x3d240),tune.Length);
     byte[] post=Read(h,0x3c000,0x2200); File.WriteAllBytes(Path.Combine(outDir,"data-post-init-tuned.bin"),post); log.AppendLine("post="+Sha(post));
     byte[] focus=Read(h,0x3d200,0x1000); File.WriteAllBytes(Path.Combine(outDir,"focus-3d200-3e200.bin"),focus); log.AppendLine("focus="+Sha(focus));
     log.AppendLine("3d238="+U32(post,0x1238)); log.AppendLine("3d23c="+U32(post,0x123c));
     log.AppendLine("3daa0="+U32(post,0x1aa0)+" 3daa4="+U32(post,0x1aa4)+" 3daa8="+U32(post,0x1aa8)+" 3daac="+U32(post,0x1aac));
     log.AppendLine("3dab0="+U32(post,0x1ab0)+" 3dab4="+U32(post,0x1ab4)+" 3dab8="+U32(post,0x1ab8)+" 3dabc="+U32(post,0x1abc));
     log.AppendLine("3dac0="+U32(post,0x1ac0));
     ulong handle=(ulong)Marshal.ReadInt64(IntPtr.Add(h,0x3da78)); log.AppendLine("handle=0x"+handle.ToString("x"));
     if(handle!=0){try{var hb=new byte[0x200];Marshal.Copy(new IntPtr((long)handle),hb,0,hb.Length);File.WriteAllBytes(Path.Combine(outDir,"swasf-handle-head.bin"),hb);log.AppendLine("handle_head="+Sha(hb));}catch(Exception e){log.AppendLine("handle_dump="+e.GetType().Name+":"+e.Message);}}
     deinit(0);
   }
   File.WriteAllText(Path.Combine(outDir,"DUMP.txt"),log.ToString()); FreeLibrary(h); return log.ToString();
 }
}
'@
Add-Type -TypeDefinition $cs -Language CSharp
$hdr='dll_sha256='+(Get-FileHash $dll.FullName -Algorithm SHA256).Hash.ToLower()+"`r`ntune_sha256="+(Get-FileHash 'C:\Users\Geoca\Documents\E004DH-oracle\SWASF-derived-from-live-cache.bin' -Algorithm SHA256).Hash.ToLower()+"`r`n"
$body=[E004DHSwasfRuntimeDump]::Run($dll.FullName,$tune,$out)
$hdr+$body | Tee-Object -FilePath "$out\ORACLE.log"
