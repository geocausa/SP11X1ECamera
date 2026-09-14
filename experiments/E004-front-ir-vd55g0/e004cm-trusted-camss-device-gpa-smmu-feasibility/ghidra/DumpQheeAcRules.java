//@category SP11.Camera
import ghidra.app.script.GhidraScript; import ghidra.program.model.mem.Memory; import ghidra.program.model.address.Address; import java.io.*;
public class DumpQheeAcRules extends GhidraScript {
 public void run() throws Exception { String[] a=getScriptArgs(); PrintWriter p=new PrintWriter(new FileOutputStream(a[0])); Memory m=currentProgram.getMemory(); long buckets=0x00309da8L; long targetSrc=1L<<3; long targetDst=(1L<<13)|(1L<<63); boolean found=false; int total=0;
  for(int i=0;i<0x51;i++){ Address b=toAddr(Long.toHexString(buckets+i*0x10L)); long ptr=m.getLong(b); int count=m.getInt(b.add(8)); if(ptr==0||count<=0) continue; p.printf("BUCKET %d ptr=0x%x count=%d%n",i,ptr,count); for(int j=0;j<count;j++){ Address r=toAddr(Long.toHexString(ptr+j*0x30L)); long src=m.getLong(r.add(8)); int active=m.getInt(r.add(0x14)); long dp=m.getLong(r.add(0x20)); int dc=m.getInt(r.add(0x28)); long dm=0; StringBuilder ds=new StringBuilder(); for(int k=0;k<dc;k++){Address e=toAddr(Long.toHexString(dp+k*8L)); int vm=m.getInt(e); int fl=m.getInt(e.add(4)); if(vm>=0&&vm<64)dm|=1L<<vm; ds.append(String.format(" vmid=0x%x flags=0x%x",vm,fl));} p.printf(" RULE %d.%d addr=%s src=0x%016x dst=0x%016x active=%d dcount=%d%s%n",i,j,r,src,dm,active,dc,ds); total++; if(src==targetSrc&&dm==targetDst){found=true;p.println(" *** TARGET_HLOS_TO_CP_CAMERA_PLUS_TRUSTED_VM_CLASS ***");}}
  }
  p.printf("TOTAL_RULES=%d%nTARGET_SRC=0x%016x%nTARGET_DST=0x%016x%nTARGET_FOUND=%s%n",total,targetSrc,targetDst,found); p.close(); }
}
