// SPDX-License-Identifier: MIT
using System;
using System.IO;
public static class SP11WindowsFrontQualityStats02 {
 const int Width=2560,Height=1440,ImageBytes=5529600;
 static double[] Plane(byte[] d,int start,int count,int step) {
  long[] hist=new long[256];double sum=0,sq=0;int lo=255,hi=0;
  for(int j=0;j<count;j++) {int v=d[start+j*step];hist[v]++;sum+=v;sq+=(double)v*v;lo=Math.Min(lo,v);hi=Math.Max(hi,v);}
  double mean=sum/count;double[] r={lo,hi,mean,Math.Sqrt(Math.Max(0,sq/count-mean*mean)),0,0,0};
  int[] percent={1,50,99};
  for(int i=0;i<3;i++){long rank=(long)Math.Floor((count-1)*percent[i]/100.0),total=0;for(int v=0;v<256;v++){total+=hist[v];if(total>rank){r[4+i]=v;break;}}}
  return r;
 }
 public static double[] Summarize(byte[] d,int w,int h) {
  if(w!=Width||h!=Height||d==null||d.Length!=ImageBytes)throw new ArgumentException("exact native 2560x1440 NV12 required");
  int n=w*h;double[] result=new double[25];
  Array.Copy(Plane(d,0,n,1),0,result,0,7);
  Array.Copy(Plane(d,n,n/4,2),0,result,7,7);
  Array.Copy(Plane(d,n+1,n/4,2),0,result,14,7);
  long black=0,white=0,hd=0,vd=0;
  for(int y=0;y<h;y++)for(int x=0;x<w;x++){int i=y*w+x,v=d[i];if(v<=16)black++;if(v>=235)white++;if(x>0)hd+=Math.Abs(v-d[i-1]);if(y>0)vd+=Math.Abs(v-d[i-w]);}
  result[21]=(double)black/n;result[22]=(double)white/n;result[23]=(double)hd/(h*(w-1));result[24]=(double)vd/(w*(h-1));return result;
 }
 public static void SaveNew(byte[] d,string path) {
  if(d==null||d.Length!=ImageBytes)throw new ArgumentException("exact native bytes required");
  using(var f=new FileStream(path,FileMode.CreateNew,FileAccess.Write,FileShare.None)){f.Write(d,0,d.Length);f.Flush(true);}
 }
 public static string SelfTest() {
  int a=0,neg=0;byte[] d=new byte[ImageBytes];
  for(int i=0;i<d.Length;i++)d[i]=37;
  double[] s=Summarize(d,Width,Height);
  for(int k=0;k<3;k++){int off=k*7;if(s[off]!=37||s[off+1]!=37||s[off+2]!=37||s[off+3]!=0||s[off+4]!=37||s[off+5]!=37||s[off+6]!=37)throw new Exception("constant metrics");a+=7;}
  if(s[21]!=0||s[22]!=0||s[23]!=0||s[24]!=0)throw new Exception("constant fractions/gradient");a+=4;
  for(int i=0;i<Width*Height;i++)d[i]=(byte)(i%Width%256);
  for(int i=Width*Height;i<d.Length;i+=2){d[i]=128;d[i+1]=129;}
  s=Summarize(d,Width,Height);
  if(s[0]!=0||s[1]!=255||s[2]!=127.5||s[4]!=2||s[5]!=127||s[6]!=253||s[9]!=128||s[16]!=129||s[24]!=0)throw new Exception("gradient metrics");a+=9;
  foreach(int n in new int[]{0,ImageBytes-1,ImageBytes+1}){try{Summarize(new byte[n],Width,Height);throw new Exception("bad extent admitted");}catch(ArgumentException){neg++;}}
  foreach(int w in new int[]{0,1280,2559,2561}){try{Summarize(d,w,Height);throw new Exception("bad width admitted");}catch(ArgumentException){neg++;}}
  foreach(int h in new int[]{0,720,1439,1441}){try{Summarize(d,Width,h);throw new Exception("bad height admitted");}catch(ArgumentException){neg++;}}
  try{Summarize(null,Width,Height);throw new Exception("null admitted");}catch(ArgumentException){neg++;}
  string path=Path.Combine(Path.GetTempPath(),"SP11-QUALITY-SYNTHETIC-"+Guid.NewGuid().ToString("N")+".nv12");
  try{SaveNew(d,path);if(new FileInfo(path).Length!=ImageBytes)throw new Exception("save extent");a++;try{SaveNew(d,path);throw new Exception("duplicate overwrite");}catch(IOException){neg++;}}
  finally{if(File.Exists(path))File.Delete(path);Array.Clear(d,0,d.Length);}
  return "PASS_WINDOWS_NATIVE_METRICS_MODEL assertions="+a+" negatives="+neg+" hardware_access=False";
 }
}
