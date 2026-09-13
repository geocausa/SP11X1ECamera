// ExtractPropertyBrokerStrings.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;

public class ExtractPropertyBrokerStrings extends GhidraScript {
    public void run() throws Exception {
        String out=getScriptArgs()[0];
        PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(out),"UTF-8"));
        Listing listing=currentProgram.getListing();
        ReferenceManager rm=currentProgram.getReferenceManager();
        String[] needles={
            "CCameraControls::KsProperty",
            "CCameraControls::NotifyAllObservers",
            "CProperty::RegisterPropertyObserver",
            "CaptureProperties::RegisterPropertyObservers",
            "CaptureProperties::Initialize"
        };
        LinkedHashSet<Function> funcs=new LinkedHashSet<>();
        pw.println("program="+currentProgram.getName());
        for(Data d: iterable(listing.getDefinedData(true))) {
            if(!d.hasStringValue()) continue;
            Object v=d.getValue();
            if(v==null) continue;
            String s=v.toString();
            boolean hit=false;
            for(String n:needles) if(s.contains(n)){hit=true;break;}
            if(!hit) continue;
            pw.println("STRING "+d.getAddress()+" = "+s.replace("\n","\\n"));
            ReferenceIterator ri=rm.getReferencesTo(d.getAddress());
            while(ri.hasNext()){
                Reference r=ri.next();
                Function f=listing.getFunctionContaining(r.getFromAddress());
                pw.println("  XREF "+r.getFromAddress()+" type="+r.getReferenceType()+" function="+
                           (f==null?"<none>":f.getName()+"@"+f.getEntryPoint()));
                if(f!=null) funcs.add(f);
            }
        }
        pw.println("\n=== DECOMPILATIONS ===");
        DecompInterface dec=new DecompInterface(); dec.openProgram(currentProgram);
        for(Function f:funcs){
            pw.println("\n//// "+f.getName()+" @"+f.getEntryPoint()+" ////");
            DecompileResults dr=dec.decompileFunction(f,90,monitor);
            if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null) pw.println(dr.getDecompiledFunction().getC());
            else pw.println("[decompile failed] "+(dr==null?"null":dr.getErrorMessage()));
        }
        dec.dispose(); pw.close();
        println("wrote "+out+" funcs="+funcs.size());
    }
    private static <T> Iterable<T> iterable(final Iterator<T> it) {
        return new Iterable<T>() { public Iterator<T> iterator(){return it;} };
    }
}
