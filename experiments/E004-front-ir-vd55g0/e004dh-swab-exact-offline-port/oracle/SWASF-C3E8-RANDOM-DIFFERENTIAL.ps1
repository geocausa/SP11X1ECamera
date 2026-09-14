$ErrorActionPreference='Stop'
$out='C:\Users\Geoca\Documents\E004DH-swasf-c3e8-random-diff'
New-Item -ItemType Directory -Force -Path $out | Out-Null
$dll=Get-ChildItem 'C:\WINDOWS\System32\DriverStore\FileRepository\qccamsecureisp8380.inf_arm64_*\QcISPTrustlet8380.dll' -ErrorAction Stop | Select-Object -First 1
$cs=@'
using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
public static class E004DHC3E8RandomDiff {
 [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)] static extern IntPtr LoadLibraryW(string p);
 [UnmanagedFunctionPointer(CallingConvention.Winapi)] delegate uint InitFn(uint a0,ulong a1,ulong a2,ulong a3,ulong a4,ulong a5,ulong a6,ulong a7);
 [UnmanagedFunctionPointer(CallingConvention.Winapi)] delegate void C3E8(IntPtr src,ushort stride,ushort x0,ushort x1,ushort y0,ushort y1,ushort width,ushort height,IntPtr p9,IntPtr p10,IntPtr o11,IntPtr o12,IntPtr o13);
 static readonly int[,] HP={{-7,-23,-41,-49,-41,-23,-7},{-23,-73,-74,-53,-74,-73,-23},{-41,-74,89,242,89,-74,-41},{-49,-53,242,0,242,-53,-49},{-41,-74,89,242,89,-74,-41},{-23,-73,-74,-53,-74,-73,-23},{-7,-23,-41,-49,-41,-23,-7}};
 static readonly int[,] LP={{0,0,0,0,0,0,0},{0,9,23,31,23,9,0},{0,23,60,82,60,23,0},{0,31,82,0,82,31,0},{0,23,60,82,60,23,0},{0,9,23,31,23,9,0},{0,0,0,0,0,0,0}};
 static int Sr(long v,int s){return (int)((v+(1L<<(s-1)))>>s);} static int Clamp(int v,int lo,int hi){return v<lo?lo:(v>hi?hi:v);}
 static short Px(short[] a,int stride,int w,int h,int y,int x){y=Clamp(y,0,h-1);x=Clamp(x,0,w-1);return a[y*stride+x];}
 static short Med5(short a,short b,short c,short d,short e){short[] q={a,b,c,d,e};Array.Sort(q);return q[2];}
 static void C230(short[,] rows,short[] tail,int[] o4,byte[] o2){for(int lane=0;lane<2;lane++){long hp=508L*tail[lane],lp=112L*tail[lane];for(int r=0;r<7;r++)for(int c=0;c<7;c++){int px=rows[r,c+lane];hp+=HP[r,c]*px;lp+=LP[r,c]*px;}o4[lane]=Sr(hp,8);o2[lane]=(byte)Sr(lp,12);}}
 static void Scalar(short[] src,int stride,int x0,int x1,int y0,int y1,int w,int h,int[] hp,byte[] lp,short[] med){int tile=x1-x0;for(int y=y0;y<y1;y++){int row=(y-y0)*tile;for(int lx=0;lx<tile;lx++){int x=x0+lx;med[row+lx]=Med5(Px(src,stride,w,h,y,x),Px(src,stride,w,h,y,x-1),Px(src,stride,w,h,y,x+1),Px(src,stride,w,h,y-1,x),Px(src,stride,w,h,y+1,x));}for(int lx=0;lx<tile;lx+=2){int x=x0+lx;short[,] rows=new short[7,8];for(int r=0;r<7;r++)for(int c=0;c<8;c++)rows[r,c]=Px(src,stride,w,h,y+r-3,x+c-3);short[] t={med[row+lx],med[row+lx+1]};int[] o4=new int[2];byte[] o2=new byte[2];C230(rows,t,o4,o2);hp[row+lx]=o4[0];hp[row+lx+1]=o4[1];lp[row+lx]=o2[0];lp[row+lx+1]=o2[1];}}}
 static uint Xs(ref uint x){x^=x<<13;x^=x>>17;x^=x<<5;return x;} static string Sha(byte[] b){using(var s=SHA256.Create())return BitConverter.ToString(s.ComputeHash(b)).Replace("-","").ToLowerInvariant();}
 static void Put(MemoryStream m,int[] hp,byte[] lp,short[] med,int n){for(int i=0;i<n;i++){byte[] b=BitConverter.GetBytes(hp[i]);m.Write(b,0,4);}m.Write(lp,0,n);for(int i=0;i<n;i++){byte[] b=BitConverter.GetBytes(med[i]);m.Write(b,0,2);}}
 public static string Run(string dll,string outDir){IntPtr hm=LoadLibraryW(dll);if(hm==IntPtr.Zero)throw new Exception("LoadLibrary "+Marshal.GetLastWin32Error());var init=(InitFn)Marshal.GetDelegateForFunctionPointer(IntPtr.Add(hm,0x19440),typeof(InitFn));var f=(C3E8)Marshal.GetDelegateForFunctionPointer(IntPtr.Add(hm,0x1c3e8),typeof(C3E8));const int W=16,H=16,T=8,N=512,USED=H*T,EX=32;ulong dims=(ulong)W|((ulong)H<<16)|((ulong)W<<32);uint ir=init(0,dims,0,0,0,0,0,0);var log=new StringBuilder();log.AppendLine("INIT=0x"+ir.ToString("x8"));if(ir!=0)return log.ToString();uint rng=0x8380c3e8u;var ws=new MemoryStream();var rs=new MemoryStream();int extraHp=0,extraLp=0,extraMed=0;
 for(int it=0;it<N;it++){short[] src=new short[W*H];for(int i=0;i<src.Length;i++)src[i]=(short)(Xs(ref rng)&1023);var gs=GCHandle.Alloc(src,GCHandleType.Pinned);try{for(int x0=0;x0<W;x0+=T){int[] whp=new int[USED+EX],rhp=new int[USED+EX];byte[] wlp=new byte[USED+EX],rlp=new byte[USED+EX];short[] wmed=new short[USED+EX],rmed=new short[USED+EX];for(int i=0;i<USED+EX;i++){whp[i]=unchecked((int)0x5a5a5a5a);wlp[i]=0x5a;wmed[i]=0x5a5a;}var gh=GCHandle.Alloc(whp,GCHandleType.Pinned);var gl=GCHandle.Alloc(wlp,GCHandleType.Pinned);var gm=GCHandle.Alloc(wmed,GCHandleType.Pinned);try{f(gs.AddrOfPinnedObject(),W,(ushort)x0,(ushort)(x0+T),0,H,W,H,IntPtr.Add(hm,0x3c138),IntPtr.Add(hm,0x3c120),gh.AddrOfPinnedObject(),gl.AddrOfPinnedObject(),gm.AddrOfPinnedObject());}finally{gh.Free();gl.Free();gm.Free();}Scalar(src,W,x0,x0+T,0,H,W,H,rhp,rlp,rmed);for(int i=0;i<USED;i++)if(whp[i]!=rhp[i]||wlp[i]!=rlp[i]||wmed[i]!=rmed[i]){log.AppendLine("FAIL it="+it+" x0="+x0+" i="+i+" WHP="+whp[i]+" RHP="+rhp[i]+" WLP="+wlp[i]+" RLP="+rlp[i]+" WM="+wmed[i]+" RM="+rmed[i]);File.WriteAllText(Path.Combine(outDir,"RESULT.txt"),log.ToString());return log.ToString();}for(int i=USED;i<USED+EX;i++){if(whp[i]!=unchecked((int)0x5a5a5a5a))extraHp++;if(wlp[i]!=0x5a)extraLp++;if(wmed[i]!=0x5a5a)extraMed++;}Put(ws,whp,wlp,wmed,USED);Put(rs,rhp,rlp,rmed,USED);}}finally{gs.Free();}}
 string a=Sha(ws.ToArray()),b=Sha(rs.ToArray());log.AppendLine("IMAGES="+N);log.AppendLine("TILES="+(N*2));log.AppendLine("WINDOWS_SHA256="+a);log.AppendLine("SCALAR_SHA256="+b);log.AppendLine("BYTE_EXACT="+(a==b?"true":"false"));log.AppendLine("EXTRA_WRITES_HP="+extraHp+" LP="+extraLp+" MED="+extraMed);File.WriteAllText(Path.Combine(outDir,"RESULT.txt"),log.ToString());return log.ToString();}
}
'@
Add-Type -TypeDefinition $cs -Language CSharp
$head=@('E004dh C3E8 random differential',('time='+[DateTimeOffset]::Now.ToString('o')),('dll_sha256='+(Get-FileHash $dll.FullName -Algorithm SHA256).Hash.ToLower()))
$body=[E004DHC3E8RandomDiff]::Run($dll.FullName,$out)
(($head -join "`r`n")+"`r`n"+$body) | Tee-Object -FilePath "$out\ORACLE.log"
