// ExtractSecureModeBrokerFocused.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;

public class ExtractSecureModeBrokerFocused extends GhidraScript {
    private Address A(long v) {
        return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(v);
    }
    private String fn(Function f) {
        return f == null ? "<none>" : f.getName() + "@" + f.getEntryPoint();
    }
    public void run() throws Exception {
        String out = getScriptArgs()[0];
        PrintWriter pw = new PrintWriter(new OutputStreamWriter(new FileOutputStream(out), "UTF-8"));
        Listing listing = currentProgram.getListing();
        ReferenceManager rm = currentProgram.getReferenceManager();
        LinkedHashSet<Function> funcs = new LinkedHashSet<>();

        long[] targets = {
            0x1802f7458L, 0x1802f9540L,
            0x180309620L, 0x180309760L, 0x180309880L,
            0x180302d20L, 0x180302f40L,
            0x180043ce0L, 0x180043f60L,
            0x180291c00L, 0x180293ad8L
        };

        pw.println("program=" + currentProgram.getName());
        pw.println("image_base=" + currentProgram.getImageBase());
        pw.println("=== REFERENCES ===");
        for (long t : targets) {
            Address a=A(t);
            Function f=listing.getFunctionAt(a);
            pw.println("TARGET " + a + " " + fn(f));
            if (f != null) funcs.add(f);
            ReferenceIterator ri=rm.getReferencesTo(a);
            int n=0;
            while(ri.hasNext()) {
                Reference r=ri.next();
                Function caller=listing.getFunctionContaining(r.getFromAddress());
                pw.println("  REF " + r.getFromAddress() + " type=" + r.getReferenceType() +
                           " caller=" + fn(caller));
                if (caller != null) funcs.add(caller);
                n++;
            }
            pw.println("  REFCOUNT " + n);
        }

        pw.println();
        pw.println("=== SECURE PROPERTY VTABLE WINDOW ===");
        Memory mem=currentProgram.getMemory();
        for (long a=0x181333680L; a<=0x1813337d0L; a+=8) {
            try {
                long v=mem.getLong(A(a));
                Function f=listing.getFunctionAt(A(v));
                pw.printf("%s -> %016x %s%n", A(a), v, fn(f));
            } catch(Exception e) {
                pw.println(A(a) + " -> [unreadable]");
            }
        }

        pw.println();
        pw.println("=== DECOMPILATIONS ===");
        DecompInterface di=new DecompInterface();
        di.openProgram(currentProgram);
        for(Function f: funcs) {
            pw.println();
            pw.println("//// " + f.getName() + " @" + f.getEntryPoint() + " ////");
            DecompileResults dr=di.decompileFunction(f,90,monitor);
            if(dr!=null && dr.decompileCompleted() && dr.getDecompiledFunction()!=null)
                pw.println(dr.getDecompiledFunction().getC());
            else
                pw.println("[decompile failed] " + (dr==null?"null":dr.getErrorMessage()));
        }
        di.dispose();
        pw.close();
        println("wrote " + out + " funcs=" + funcs.size());
    }
}
