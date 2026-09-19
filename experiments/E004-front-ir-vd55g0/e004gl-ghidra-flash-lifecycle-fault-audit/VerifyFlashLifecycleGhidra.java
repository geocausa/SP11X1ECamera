// Targeted offline Ghidra checks of original Windows ARM64 flash/PMIC PEs.
// @category SP11
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import java.util.*;

public class VerifyFlashLifecycleGhidra extends GhidraScript {
    private void need(boolean ok, String why) {
        if (!ok) throw new IllegalStateException("E004GL_GHIDRA_FAIL_CLOSED " + why);
    }
    private Address at(long rva) { return currentProgram.getImageBase().add(rva); }
    private String decomp(DecompInterface d, long rva) {
        Function f=currentProgram.getFunctionManager().getFunctionContaining(at(rva));
        need(f != null && f.getEntryPoint().equals(at(rva)), "target function RVA " + Long.toHexString(rva));
        DecompileResults result=d.decompileFunction(f,40,monitor);
        need(result.decompileCompleted(), "decompile RVA " + Long.toHexString(rva));
        return result.getDecompiledFunction().getC();
    }
    private boolean hasDirectCall(long target, long from) {
        ReferenceIterator refs=currentProgram.getReferenceManager().getReferencesTo(at(target));
        while(refs.hasNext()) {
            Reference r=refs.next();
            if(r.getFromAddress().equals(at(from)) && r.getReferenceType().isCall()) return true;
        }
        return false;
    }
    private boolean hasDataReference(long target, long from) {
        ReferenceIterator refs=currentProgram.getReferenceManager().getReferencesTo(at(target));
        while(refs.hasNext()) {
            Reference r=refs.next();
            if(r.getFromAddress().equals(at(from)) && r.getReferenceType().isData()) return true;
        }
        return false;
    }
    private void contains(String src, String needle, String why) {
        need(src.contains(needle),why);
    }
    public void run() throws Exception {
        DecompInterface d=new DecompInterface(); need(d.openProgram(currentProgram),"decompiler init");
        String name=currentProgram.getName().toLowerCase();
        need(currentProgram.getImageBase().toString().equals("140000000"),"unexpected original Windows PE base");
        need(currentProgram.getLanguageID().toString().startsWith("AARCH64:LE:64"),"wrong CPU architecture");
        if(name.equals("qccamflash8380.sys")) {
            String init=decomp(d,0x48c8), stop=decomp(d,0x4828), timer=decomp(d,0x4dd0);
            contains(init,"FUN_140004ce0","current helper in start routine");
            contains(init,"FUN_140004dd0","timer helper in start routine");
            contains(init,"FUN_140004d58","strobe helper in start routine");
            contains(init,"DAT_14000e4b5","active state in start routine");
            need(init.indexOf("FUN_140004ce0") < init.indexOf("FUN_140004dd0") &&
                 init.indexOf("FUN_140004dd0") < init.lastIndexOf("FUN_140004d58"),
                 "current->timer->strobe request order");
            contains(stop,"FUN_140004d58(0,0,0","stop requests flash off");
            contains(stop,"DAT_14000e4b5 = 0","stop clears active flag after helper");
            contains(timer,"CameraWhiteLEDFlashPMIC_SetSafetyTimer","nominal timer helper");
            need(hasDirectCall(0x4dd0,0x4938) && hasDirectCall(0x4dd0,0x5b2c),
                 "expected two timer direct-call sites");
            need(hasDirectCall(0x4d58,0x4918) && hasDirectCall(0x4d58,0x4954),
                 "start routine off/on strobe request sites");
            println("E004GL_GHIDRA_FLASH_DECOMP=PASS current_then_timer_then_strobe prior_off_and_stop_state=VERIFIED");
            println("E004GL_GHIDRA_TIMER_CALLERS=0x4938,0x5b2c");
        } else if(name.equals("qcpmic8380.sys")) {
            String timer=decomp(d,0x26d50), module=decomp(d,0x285c0);
            contains(timer,"FUN_140023968","PMIC timer uses masked-write helper");
            contains(timer,"DAT_140036d48","PMIC timer register table");
            contains(module,"0xee46","PMIC flash module enable register");
            contains(module,"0xee4e","PMIC channel enable register");
            need(module.indexOf("0xee46")<module.indexOf("0xee4e"),"module before channel masked writes");
            need(hasDataReference(0x26d50,0x39498),"timer function address in PMIC dispatch table");
            println("E004GL_GHIDRA_PMIC_DECOMP=PASS module_before_channel timer_callback_indirect_table=VERIFIED");
        } else need(false,"unexpected PE identity "+name);
        d.dispose();
        println("E004GL_GHIDRA_DONE="+name);
    }
}
