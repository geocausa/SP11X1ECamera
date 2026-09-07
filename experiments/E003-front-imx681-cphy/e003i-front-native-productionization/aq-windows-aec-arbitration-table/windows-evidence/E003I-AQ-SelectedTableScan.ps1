$ErrorActionPreference='Stop'
Add-Type -TypeDefinition @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;
public static class AQScan {
 [StructLayout(LayoutKind.Sequential)] public struct MBI { public IntPtr BaseAddress; public IntPtr AllocationBase; public uint AllocationProtect; public UIntPtr RegionSize; public uint State; public uint Protect; public uint Type; }
 [DllImport("kernel32.dll", SetLastError=true)] public static extern IntPtr OpenProcess(uint access, bool inherit, int pid);
 [DllImport("kernel32.dll", SetLastError=true)] public static extern bool ReadProcessMemory(IntPtr h, IntPtr a, byte[] b, UIntPtr n, out UIntPtr r);
 [DllImport("kernel32.dll", SetLastError=true)] public static extern UIntPtr VirtualQueryEx(IntPtr h, IntPtr a, out MBI mbi, UIntPtr n);
 [DllImport("kernel32.dll")] public static extern bool CloseHandle(IntPtr h);
 static bool Read(IntPtr h, ulong a, byte[] b) { UIntPtr r; return ReadProcessMemory(h,(IntPtr)(long)a,b,(UIntPtr)b.Length,out r) && r.ToUInt64()==(ulong)b.Length; }
 static uint U32(byte[] b,int o){ return BitConverter.ToUInt32(b,o); } static ulong U64(byte[] b,int o){ return BitConverter.ToUInt64(b,o); } static float F32(byte[] b,int o){ return BitConverter.ToSingle(b,o); }
 static bool Readable(uint p){ p &= 0xff; return p==0x02||p==0x04||p==0x08||p==0x20||p==0x40||p==0x80; }
 public sealed class T { public ulong H,D,K; public int N; public string S=""; public List<ulong> Refs=new List<ulong>(); public List<ulong> HRefs=new List<ulong>(); }
 public static List<T> Run(int pid){
  var outv=new List<T>(); IntPtr h=OpenProcess(0x0410,false,pid); if(h==IntPtr.Zero) throw new Exception("OpenProcess "+Marshal.GetLastWin32Error());
  try {
   var regs=new List<Tuple<ulong,ulong>>(); ulong a=0; int msz=Marshal.SizeOf(typeof(MBI));
   while(a<0x0000800000000000UL){ MBI m; var q=VirtualQueryEx(h,(IntPtr)(long)a,out m,(UIntPtr)msz); if(q.ToUInt64()==0) break; ulong bs=(ulong)m.BaseAddress.ToInt64(), sz=m.RegionSize.ToUInt64(); if(m.State==0x1000 && Readable(m.Protect) && sz>0 && sz<=0x20000000UL) regs.Add(Tuple.Create(bs,sz)); ulong na=bs+sz; if(na<=a) break; a=na; }
   // structural table scan
   foreach(var rg in regs){ ulong pos=0; const int CH=1<<20; byte[] buf=new byte[CH+64]; while(pos<rg.Item2){ int want=(int)Math.Min((ulong)CH,rg.Item2-pos); byte[] bb= want+64==buf.Length?buf:new byte[want+64]; int read=want; UIntPtr got; if(!ReadProcessMemory(h,(IntPtr)(long)(rg.Item1+pos),bb,(UIntPtr)read,out got)||got.ToUInt64()<40){pos+=(ulong)want;continue;} int n=(int)got.ToUInt64(); for(int o=0;o+40<=n;o+=4){ if(U32(bb,o)!=0x3f800000) continue; int cnt=(int)U32(bb,o+0x14); if(cnt<2||cnt>8) continue; ulong kp=U64(bb,o+0x20); if(kp<0x10000||kp>=0x0000800000000000UL) continue; byte[] kb=new byte[cnt*16]; if(!Read(h,kp,kb)) continue; bool ok=true; ulong prev=0; for(int i=0;i<cnt;i++){ float g=F32(kb,i*16+4); ulong t=U64(kb,i*16+8); if(!(g>=0.5f&&g<=256f) || t<1000 || t>500000000UL || (i>0&&t<prev)){ok=false;break;} prev=t; } if(!ok) continue; ulong hdr=rg.Item1+pos+(ulong)o; bool dup=false; foreach(var x in outv) if(x.H==hdr){dup=true;break;} if(dup) continue; var Tt=new T(); Tt.H=hdr;Tt.D=hdr-0x10;Tt.K=kp;Tt.N=cnt; // name pointer at hdr-8
     byte[] npb=new byte[8]; if(Read(h,hdr-8,npb)){ ulong np=U64(npb,0); if(np>0x10000&&np<0x0000800000000000UL){ byte[] sb=new byte[64]; if(Read(h,np,sb)){ int z=Array.IndexOf(sb,(byte)0); if(z<0)z=sb.Length; Tt.S=Encoding.ASCII.GetString(sb,0,z); } } }
     outv.Add(Tt);
   } pos+=(ulong)want; } }
   // pointer references to DB and header
   foreach(var rg in regs){ ulong pos=0; const int CH=1<<20; while(pos<rg.Item2){ int want=(int)Math.Min((ulong)CH,rg.Item2-pos); byte[] bb=new byte[want]; UIntPtr got; if(!ReadProcessMemory(h,(IntPtr)(long)(rg.Item1+pos),bb,(UIntPtr)want,out got)){pos+=(ulong)want;continue;} int n=(int)got.ToUInt64(); for(int o=0;o+8<=n;o+=8){ ulong v=U64(bb,o); foreach(var t in outv){ if(v==t.D)t.Refs.Add(rg.Item1+pos+(ulong)o); if(v==t.H)t.HRefs.Add(rg.Item1+pos+(ulong)o); } } pos+=(ulong)want; } }
   return outv;
  } finally { CloseHandle(h); }
 }
}
'@
$p = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'svchost.exe -k Camera -s FrameServer' } | Select-Object -First 1
if(-not $p){ throw 'FrameServer not found' }
$r=[AQScan]::Run([int]$p.ProcessId)
"PID=$($p.ProcessId) TABLES=$($r.Count)"
$i=0
foreach($t in $r){ $i++; "T$i hdr=0x{0:X} db=0x{1:X} name={2} knees={3} dbrefs={4} hrefs={5}" -f $t.H,$t.D,$t.S,$t.N,$t.Refs.Count,$t.HRefs.Count; if($t.Refs.Count){ ' DBREFS '+(($t.Refs|ForEach-Object{'0x{0:X}' -f $_}) -join ',') }; if($t.HRefs.Count){ ' HREFS '+(($t.HRefs|ForEach-Object{'0x{0:X}' -f $_}) -join ',') } }
