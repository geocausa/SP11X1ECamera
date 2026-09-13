// ExtractSecureModeXrefs.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.data.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;

public class ExtractSecureModeXrefs extends GhidraScript {
    private boolean match(String s) {
        String x = s.toLowerCase(Locale.ROOT);
        String[] needles = {
            "securemode", "secure mode", "securecamera", "secure camera",
            "secureisp", "camera secureisp", "camerasecureisp",
            "secure kmdisp", "securecamsupported", "m_issecurecamerasupported",
            "filepath for secureisp", "secure_image", "secure image",
            "secure_buffer", "protected"
        };
        for (String n: needles) if (x.contains(n)) return true;
        return false;
    }

    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 1) throw new IllegalArgumentException("output path required");
        File out = new File(args[0]);
        PrintWriter pw = new PrintWriter(new OutputStreamWriter(new FileOutputStream(out), "UTF-8"));
        pw.println("program=" + currentProgram.getName());
        pw.println("image_base=" + currentProgram.getImageBase());
        pw.println();

        Listing listing = currentProgram.getListing();
        ReferenceManager rm = currentProgram.getReferenceManager();
        FunctionManager fm = currentProgram.getFunctionManager();
        LinkedHashSet<Function> funcs = new LinkedHashSet<>();

        DataIterator it = listing.getDefinedData(true);
        while (it.hasNext() && !monitor.isCancelled()) {
            Data d = it.next();
            Object v = d.getValue();
            if (!(v instanceof String)) continue;
            String s = (String)v;
            if (!match(s)) continue;
            pw.println("STRING @" + d.getAddress() + " = " + s.replace("\r","\\r").replace("\n","\\n"));
            ReferenceIterator refs = rm.getReferencesTo(d.getAddress());
            while (refs.hasNext()) {
                Reference ref = refs.next();
                Address from = ref.getFromAddress();
                Function f = fm.getFunctionContaining(from);
                pw.println("  XREF " + from + (f == null ? "" : " function=" + f.getName() + " entry=" + f.getEntryPoint()));
                if (f != null) funcs.add(f);
            }
        }

        pw.println();
        pw.println("=== DECOMPILATIONS ===");
        DecompInterface decomp = new DecompInterface();
        decomp.openProgram(currentProgram);
        for (Function f: funcs) {
            if (monitor.isCancelled()) break;
            pw.println();
            pw.println("//// " + f.getName() + " @" + f.getEntryPoint() + " ////");
            DecompileResults res = decomp.decompileFunction(f, 60, monitor);
            if (res != null && res.decompileCompleted() && res.getDecompiledFunction() != null) {
                pw.println(res.getDecompiledFunction().getC());
            } else {
                pw.println("[decompile failed] " + (res == null ? "null" : res.getErrorMessage()));
            }
        }
        decomp.dispose();
        pw.close();
        println("wrote " + out.getAbsolutePath() + " functions=" + funcs.size());
    }
}
