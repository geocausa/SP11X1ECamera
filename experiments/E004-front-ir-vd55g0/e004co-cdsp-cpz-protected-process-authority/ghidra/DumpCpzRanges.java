//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import java.io.*;
public class DumpCpzRanges extends GhidraScript {
 public void run() throws Exception {
  String[] a=getScriptArgs(); PrintWriter pw=new PrintWriter(new FileOutputStream(a[0]));
  String[][] rs={{"f000f780","f000f920"},{"f000fb80","f000ff80"},{"f0114300","f0114780"},{"f011b800","f011bd60"},{"f0122c80","f0123420"}};
  Listing l=currentProgram.getListing();
  for(String[] r:rs){ Address s=toAddr(r[0]),e=toAddr(r[1]); pw.println("===== "+s+".."+e+" ====="); InstructionIterator it=l.getInstructions(new AddressSet(s,e),true); while(it.hasNext()){ Instruction i=it.next(); pw.println(i.getAddress()+"  "+i.toString()); } }
  pw.close();
 }
}
