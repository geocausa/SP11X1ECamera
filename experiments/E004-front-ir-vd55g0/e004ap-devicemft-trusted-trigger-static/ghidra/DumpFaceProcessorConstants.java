// DumpFaceProcessorConstants.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.*;
import java.io.*;
public class DumpFaceProcessorConstants extends GhidraScript {
  private Address A(long v){return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(v);}
  public void run() throws Exception{
    PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(getScriptArgs()[0]),"UTF-8"));
    Listing l=currentProgram.getListing(); Memory m=currentProgram.getMemory();
    long[] addrs={0x1800e48f0L,0x1800e4900L,0x1800e4910L,0x1800e4920L,0x1800e4928L,0x1800e4938L,0x1800e4948L};
    for(long x:addrs){
      Address a=A(x); Data d=l.getDataAt(a);
      pw.println("ADDR "+a+" data="+(d==null?"<none>":d.toString())+" value="+(d==null?"":String.valueOf(d.getValue())));
      byte[] b=new byte[64]; try{m.getBytes(a,b);}catch(Exception e){}
      StringBuilder sb=new StringBuilder(); for(byte q:b) sb.append(String.format("%02x",q&255));
      pw.println("BYTES "+sb);
      StringBuilder ws=new StringBuilder();
      for(int i=0;i+1<b.length;i+=2){int c=(b[i]&255)|((b[i+1]&255)<<8); if(c==0) {ws.append("\\0"); break;} if(c>=32&&c<127) ws.append((char)c); else ws.append(String.format("\\u%04x",c));}
      pw.println("UTF16 "+ws);
    }
    pw.close();
  }
}
