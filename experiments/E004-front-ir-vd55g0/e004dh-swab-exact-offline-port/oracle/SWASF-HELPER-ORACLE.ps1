$ErrorActionPreference='Stop'
$out='C:\Users\Geoca\Documents\E004DH-swasf-helper-oracle'
New-Item -ItemType Directory -Force -Path $out | Out-Null
$dll=Get-ChildItem 'C:\WINDOWS\System32\DriverStore\FileRepository\qccamsecureisp8380.inf_arm64_*\QcISPTrustlet8380.dll' -ErrorAction Stop | Select-Object -First 1
$cs=@'
using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
public static class E004DHSwasfHelpers {
 [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)] static extern IntPtr LoadLibraryW(string p);
 [UnmanagedFunctionPointer(CallingConvention.Winapi)] delegate void B848(IntPtr rows,IntPtr pos,IntPtr neg);
 [UnmanagedFunctionPointer(CallingConvention.Winapi)] delegate void C078(IntPtr rows,IntPtr output,short center,short scale);
 static string Hex(byte[] b){return BitConverter.ToString(b).Replace("-","").ToLowerInvariant();}
 static byte[] Shorts(params short[] v){byte[] b=new byte[v.Length*2];Buffer.BlockCopy(v,0,b,0,b.Length);return b;}
 static void One(StringBuilder log,B848 b848,C078 c078,int id,short[][] rv,short center,short scale){
   GCHandle[] gr=new GCHandle[5]; IntPtr[] rp=new IntPtr[5];
   byte[] op=new byte[8], on=new byte[8], oc=new byte[1];
   var gp=GCHandle.Alloc(op,GCHandleType.Pinned); var gn=GCHandle.Alloc(on,GCHandleType.Pinned); var gc=GCHandle.Alloc(oc,GCHandleType.Pinned);
   var pa=GCHandle.Alloc(rp,GCHandleType.Pinned);
   try{
     for(int i=0;i<5;i++){gr[i]=GCHandle.Alloc(rv[i],GCHandleType.Pinned);rp[i]=gr[i].AddrOfPinnedObject();}
     // Re-pin pointer array after values have been populated.
     pa.Free(); pa=GCHandle.Alloc(rp,GCHandleType.Pinned);
     b848(pa.AddrOfPinnedObject(),gp.AddrOfPinnedObject(),gn.AddrOfPinnedObject());
     c078(pa.AddrOfPinnedObject(),gc.AddrOfPinnedObject(),center,scale);
     log.AppendLine("CASE="+id+" CENTER="+center+" SCALE="+scale);
     for(int i=0;i<5;i++){byte[] bb=Shorts(rv[i]);log.AppendLine("ROW"+i+"="+Hex(bb));}
     log.AppendLine("B848_POS="+Hex(op)); log.AppendLine("B848_NEG="+Hex(on)); log.AppendLine("C078="+oc[0].ToString("x2"));
   } finally {if(pa.IsAllocated)pa.Free();for(int i=0;i<5;i++)if(gr[i].IsAllocated)gr[i].Free();gp.Free();gn.Free();gc.Free();}
 }
 public static string Run(string dll){
   IntPtr h=LoadLibraryW(dll); if(h==IntPtr.Zero)return "LOAD_FAIL="+Marshal.GetLastWin32Error();
   var b=(B848)Marshal.GetDelegateForFunctionPointer(IntPtr.Add(h,0x1b848),typeof(B848));
   var c=(C078)Marshal.GetDelegateForFunctionPointer(IntPtr.Add(h,0x1c078),typeof(C078));
   var log=new StringBuilder(); log.AppendLine("DLL_BASE=0x"+h.ToInt64().ToString("x"));
   One(log,b,c,0,new[]{new short[]{0,4,8,12,16,20,24,28},new short[]{2,6,10,14,18,22,26,30},new short[]{1,5,9,13,17,21,25,29},new short[]{3,7,11,15,19,23,27,31},new short[]{4,8,12,16,20,24,28,32}},13,24);
   One(log,b,c,1,new[]{new short[]{400,300,200,100,0,100,200,300},new short[]{350,280,210,140,70,0,70,140},new short[]{320,240,160,80,0,80,160,240},new short[]{300,230,160,90,20,90,160,230},new short[]{280,220,160,100,40,100,160,220}},160,17);
   One(log,b,c,2,new[]{new short[]{1020,900,700,500,300,100,0,50},new short[]{900,800,650,500,350,200,100,0},new short[]{800,700,600,500,400,300,200,100},new short[]{700,650,600,550,500,450,400,350},new short[]{600,590,580,570,560,550,540,530}},500,31);
   One(log,b,c,3,new[]{new short[]{0,1023,0,1023,0,1023,0,1023},new short[]{1023,0,1023,0,1023,0,1023,0},new short[]{0,0,1023,1023,0,0,1023,1023},new short[]{1023,1023,0,0,1023,1023,0,0},new short[]{100,200,300,400,500,600,700,800}},512,8);
   return log.ToString();
 }
}
'@
Add-Type -TypeDefinition $cs -Language CSharp
$head=@('E004dh SWASF helper oracle',('time='+[DateTimeOffset]::Now.ToString('o')),('dll_sha256='+(Get-FileHash $dll.FullName -Algorithm SHA256).Hash.ToLower()))
$body=[E004DHSwasfHelpers]::Run($dll.FullName)
(($head -join "`r`n")+"`r`n"+$body) | Tee-Object -FilePath "$out\HELPERS.txt"
