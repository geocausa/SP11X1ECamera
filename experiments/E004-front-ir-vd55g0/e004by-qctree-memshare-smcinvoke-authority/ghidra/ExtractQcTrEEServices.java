// ExtractQcTrEEServices.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.address.*;
import ghidra.program.model.data.*;
import java.io.*;
import java.util.*;

public class ExtractQcTrEEServices extends GhidraScript {
    private boolean match(String s) {
        String x=s.toLowerCase(Locale.ROOT);
        String[] n={"memshareservice","memsharingservice","smcinvokeservice","invokeservice",
                    "shmbridge","mem share","memshare","smc invoke","smcinvoke"};
        for(String q:n) if(x.contains(q)) return true;
        return false;
    }
    public void run() throws Exception {
        String[] args=getScriptArgs();
        if(args.length<1) throw new IllegalArgumentException("output path required");
        PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(args[0]),"UTF-8"));
        Listing listing=currentProgram.getListing();
        ReferenceManager rm=currentProgram.getReferenceManager();
        FunctionManager fm=currentProgram.getFunctionManager();
        LinkedHashSet<Function> roots=new LinkedHashSet<>();
        pw.println("program="+currentProgram.getName());
        pw.println("image_base="+currentProgram.getImageBase());
        pw.println("=== MATCHED STRINGS / XREFS ===");
        DataIterator it=listing.getDefinedData(true);
        while(it.hasNext()&&!monitor.isCancelled()) {
            Data d=it.next(); Object v=d.getValue();
            if(!(v instanceof String)) continue;
            String s=(String)v; if(!match(s)) continue;
            pw.println("STRING @"+d.getAddress()+" = "+s.replace("\r","\\r").replace("\n","\\n"));
            ReferenceIterator refs=rm.getReferencesTo(d.getAddress());
            while(refs.hasNext()) {
                Reference ref=refs.next(); Address from=ref.getFromAddress();
                Function f=fm.getFunctionContaining(from);
                pw.println("  XREF "+from+(f==null?"":" function="+f.getName()+" entry="+f.getEntryPoint()));
                if(f!=null) roots.add(f);
            }
        }
        LinkedHashSet<Function> funcs=new LinkedHashSet<>(roots);
        for(Function f: roots) {
            funcs.addAll(f.getCalledFunctions(monitor));
            funcs.addAll(f.getCallingFunctions(monitor));
        }
        pw.println(); pw.println("=== ROOT FUNCTIONS ===");
        for(Function f:roots) pw.println(f.getName()+" @"+f.getEntryPoint());
        pw.println(); pw.println("=== ROOT + 1-HOP CALLGRAPH DECOMPILATIONS ===");
        DecompInterface di=new DecompInterface(); di.openProgram(currentProgram);
        for(Function f:funcs) {
            pw.println(); pw.println("//// "+f.getName()+" @"+f.getEntryPoint()+" root="+roots.contains(f)+" ////");
            DecompileResults dr=di.decompileFunction(f,90,monitor);
            if(dr!=null && dr.decompileCompleted() && dr.getDecompiledFunction()!=null)
                pw.println(dr.getDecompiledFunction().getC());
            else pw.println("[decompile failed] "+(dr==null?"null":dr.getErrorMessage()));
        }
        di.dispose(); pw.close();
        println("wrote "+args[0]+" roots="+roots.size()+" total="+funcs.size());
    }
}
