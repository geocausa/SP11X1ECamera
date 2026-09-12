// Search target strings, xrefs, and decompile referencing functions.
// @category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.util.*;

public class E004StringXrefs extends GhidraScript {
    private static final String[] KEYS = {
        "Csi2PhaseNumOfLanes","Csi2DataRateKbps","xCsi2PHYIndex","Csi2PhasePhyMode",
        "settle","lane","data rate","datarate","phy","mipi","sensor","patch","revision",
        "firmware","stream","cci","i2c","strobe","illum","face","auth"
    };
    private boolean hit(String s) {
        String l=s.toLowerCase(Locale.ROOT);
        for(String k:KEYS) if(l.contains(k.toLowerCase(Locale.ROOT))) return true;
        return false;
    }
    public void run() throws Exception {
        Listing listing=currentProgram.getListing();
        ReferenceManager rm=currentProgram.getReferenceManager();
        Set<Function> funcs=new LinkedHashSet<>();
        DataIterator it=listing.getDefinedData(true);
        while(it.hasNext()) {
            Data d=it.next();
            Object v=d.getValue();
            if(!(v instanceof String)) continue;
            String s=(String)v;
            if(!hit(s)) continue;
            println(String.format("STRING %s %s",d.getAddress(),s.replace("\n","\\n")));
            ReferenceIterator ri=rm.getReferencesTo(d.getAddress());
            while(ri.hasNext()) {
                Reference ref=ri.next();
                Function f=listing.getFunctionContaining(ref.getFromAddress());
                println(String.format("  XREF %s %s",ref.getFromAddress(),f==null?"<no-func>":f.getName()+"@"+f.getEntryPoint()));
                if(f!=null) funcs.add(f);
            }
        }
        println("=== DECOMPILE ===");
        DecompInterface di=new DecompInterface();
        di.openProgram(currentProgram);
        for(Function f:funcs) {
            println("=== FUNCTION "+f.getName()+" @ "+f.getEntryPoint()+" ===");
            DecompileResults dr=di.decompileFunction(f,60,monitor);
            if(dr.decompileCompleted()) println(dr.getDecompiledFunction().getC());
            else println("DECOMP_FAIL "+dr.getErrorMessage());
        }
        di.dispose();
    }
}
