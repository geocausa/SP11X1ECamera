#!/usr/bin/env python3
import argparse, hashlib, json, struct
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN
from capstone.arm64 import ARM64_OP_REG, ARM64_OP_MEM, ARM64_OP_IMM

EXPECTED_SHA256 = "64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
IMAGE_BASE = 0x140000000
TEXT_RAW = 0x400
TEXT_RVA = 0x1000
TEXT_SIZE = 0x3d48c

# Exact RVAs from the same-machine qccamisp8380.sys.
EXPECTED = {
    "barrier_dmb": 0x9710,
    "open_irq_mask": 0x187a8,
    "open_reset": 0x187b4,
    "open_reset_wait_call": 0x187b8,
    "open_core_cfg": 0x18814,
    "start_irq_mask": 0x285d0,
    "start_core_en": 0x285e0,
    "stop_irq_mask": 0x28550,
    "flush_core_pause": 0x28608,
    "flush_reset": 0x28614,
    "fifo0_base": 0x28884,
    "fifo0_len": 0x2888c,
    "fifo0_store": 0x28894,
    "irq0_clear": 0x29228,
    "irq0_clear_cmd": 0x29248,
    "isp_cdm_start_call": 0x15f50,
    "isp_ife_start_call": 0x15fec,
    "isp_initial_ife_packet_call": 0x160a4,
    "isp_initial_csid_packet_call": 0x16138,
    "isp_csid_start_call": 0x16208,
    "isp_csid_stop_call": 0x163c8,
    "isp_ife_stop_call": 0x16434,
    "isp_cdm_stop_call": 0x164b4,
}

FAIL_STRINGS = {
    0x33fd8: "ISP HW Mgr :: CDM%d Start_cmd is failed with result 0x%x",
    0x34018: "ISP HW Mgr :: ife%d Start_cmd is failed with result 0x%x",
    0x34058: "Initial packet %d to ife%d is failed with result 0x%x ",
    0x34090: "Initial packet %d to SFE0 is failed with result 0x%x ",
    0x340c8: "Initial packet %d to csid%d is failed with result 0x%x ",
    0x34100: "ISP HW Mgr :: CSID%d Start_cmd is failed with result 0x%x",
    0x34200: "ISP HW Mgr :: CSID Core0 stop cmd is failed with result =0x%x",
    0x34240: "ISP HW Mgr :: IFE Core%x  stop cmd is failed with result =0x%x",
    0x34280: "ISP HW Mgr :: CDM Core%x  stop cmd is failed with result =0x%x",
    0x3c478: "CDM: DAL_cdm_init Failed with result 0x%x.",
    0x3c508: "CDMDrv: cdm wait on reset failed with result 0x%x !!",
    0x3c7b8: "CDMDrv: CDM core Flush is successful!!",
    0x3c7e0: "CDMDrv: cdm wait on reset during flsuh failed with result 0x%x !!",
}

def die(msg):
    raise SystemExit("FAIL: " + msg)

def insns(data):
    md=Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN)
    md.detail=True; md.skipdata=True
    return list(md.disasm(data[TEXT_RAW:TEXT_RAW+TEXT_SIZE], IMAGE_BASE+TEXT_RVA))

def by_addr(xs): return {x.address-IMAGE_BASE:x for x in xs if x.mnemonic != '.byte'}

def need_ins(m, rva, mnemonic=None, contains=None):
    x=m.get(rva)
    if not x: die(f"missing instruction at RVA 0x{rva:x}")
    if mnemonic and x.mnemonic != mnemonic: die(f"RVA 0x{rva:x}: expected {mnemonic}, got {x.mnemonic}")
    if contains and contains not in x.op_str: die(f"RVA 0x{rva:x}: expected {contains!r} in {x.op_str!r}")
    return x

def extract_ascii(data):
    # Search exact strings directly in the PE; no PE parser dependency needed.
    for rva,s in FAIL_STRINGS.items():
        if s.encode('ascii') not in data:
            die(f"missing diagnostic string RVA-labelled 0x{rva:x}: {s}")

def mapped_base_direct_stores(xs):
    # Mechanical, deliberately bounded negative proof. In the CDM driver region,
    # follow a mapped RT-CDM base loaded as ldr Xb,[Xctx,#0x48] until Xb is
    # clobbered, and record direct STR/STUR writes using that exact base register.
    out=[]
    lo=IMAGE_BASE+0x18000; hi=IMAGE_BASE+0x2a000
    for i,x in enumerate(xs):
        if not (lo <= x.address < hi) or x.mnemonic != 'ldr' or len(x.operands)!=2: continue
        d,mem=x.operands
        if d.type!=ARM64_OP_REG or mem.type!=ARM64_OP_MEM or mem.mem.disp!=0x48: continue
        if not x.reg_name(d.reg).startswith('x'): continue
        br=d.reg
        for y in xs[i+1:min(i+100,len(xs))]:
            if y.mnemonic=='.byte': break
            if y.mnemonic in ('str','stur') and len(y.operands)==2 and y.operands[1].type==ARM64_OP_MEM:
                mm=y.operands[1].mem
                if mm.base==br and mm.index==0 and 0 <= mm.disp <= 0x400:
                    out.append({"load_rva":x.address-IMAGE_BASE,"store_rva":y.address-IMAGE_BASE,"offset":mm.disp,"instruction":f"{y.mnemonic} {y.op_str}"})
            # stop if the exact base register is overwritten
            if y.operands and y.operands[0].type==ARM64_OP_REG and y.operands[0].reg==br and y.mnemonic not in ('str','stur','cmp','tst','cbz','cbnz','tbz','tbnz','bl','blr','b'):
                break
    uniq=[]; seen=set()
    for r in out:
        k=(r['store_rva'],r['offset'],r['instruction'])
        if k not in seen: seen.add(k); uniq.append(r)
    return sorted(uniq,key=lambda r:r['store_rva'])

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('binary', type=Path)
    ap.add_argument('-o','--output', type=Path)
    a=ap.parse_args()
    data=a.binary.read_bytes()
    sha=hashlib.sha256(data).hexdigest()
    if sha != EXPECTED_SHA256: die(f"SHA256 {sha} != {EXPECTED_SHA256}")
    if len(data)!=376560: die(f"unexpected byte count {len(data)}")
    extract_ascii(data)
    xs=insns(data); m=by_addr(xs)

    # Exact direct-write sequences.
    checks=[
      (0x187a0,'ldr','[x26, #0x48]'),(0x187a8,'str','[x9, #0x30]'),
      (0x187ac,'ldr','[x26, #0x48]'),(0x187b0,'mov','#9'),(0x187b4,'str','[x9, #0x10]'),(0x187b8,'bl','#0x140028d60'),
      (0x18808,'bl','#0x140009718'),(0x1880c,'ldr','[x26, #0x48]'),(0x18810,'mov','#0x11f'),(0x18814,'str','[x9, #0x18]'),
      (0x285c8,'ldr','[x19, #0x48]'),(0x285cc,'mov','#0x70007'),(0x285d0,'str','[x9, #0x30]'),(0x285d4,'bl','#0x140009718'),(0x285d8,'ldr','[x19, #0x48]'),(0x285dc,'mov','#1'),(0x285e0,'str','[x9, #0x1c]'),
      (0x2854c,'ldr','[x19, #0x48]'),(0x28550,'str','[x8, #0x30]'),
      (0x2860c,'ldr','[x19, #0x48]'),(0x28610,'mov','#9'),(0x28614,'str','[x9, #0x10]'),
      (0x28874,'ldr','[x19, #0x48]'),(0x28884,'str','[x8, #0x50]'),(0x28888,'ldr','[x19, #0x48]'),(0x2888c,'str','[x8, #0x54]'),(0x28890,'ldr','[x19, #0x48]'),(0x28894,'str','[x8, #0x58]'),
      (0x29220,'ldr','[x19, #0x48]'),(0x29228,'str','[x8, #0x34]'),(0x29248,'str','[x8, #0x38]'),
      (0x9710,'dmb','sy'),(0x9714,'ret',None),
    ]
    for r,mn,sub in checks: need_ins(m,r,mn,sub)

    # Manager ordering anchors and exact command opcodes at call sites.
    mgr=[
      (0x15f3c,'mov','#0x804'),(0x15f50,'blr','x15'),
      (0x15fd8,'mov','#0x804'),(0x15fec,'blr','x15'),
      (0x1608c,'mov','#0x803'),(0x160a4,'blr','x15'),
      (0x160d4,'mov','#0x803'),(0x160f4,'blr','x15'),
      (0x16118,'mov','#0x803'),(0x16138,'blr','x15'),
      (0x161ec,'mov','#0x804'),(0x16208,'blr','x15'),
      (0x163ac,'mov','#0x805'),(0x163c8,'blr','x15'),
      (0x16414,'mov','#0x805'),(0x16434,'blr','x15'),
      (0x164a0,'mov','#0x805'),(0x164b4,'blr','x15'),
    ]
    for r,mn,sub in mgr: need_ins(m,r,mn,sub)

    stores=mapped_base_direct_stores(xs)
    offsets=sorted(set(r['offset'] for r in stores))
    if 0x20 in offsets: die('direct mapped-base FE_CFG +0x20 store unexpectedly present')
    if 0x5c in offsets: die('direct mapped-base FIFO0_CFG +0x5c store unexpectedly present')

    # Ensure all expected write classes are present in bounded direct-store sweep.
    required={0x10,0x14,0x18,0x1c,0x30,0x34,0x38,0x50,0x54,0x58,0x134,0x138,0x234,0x238,0x334,0x338}
    missing=sorted(required-set(offsets))
    if missing: die('mapped-base store sweep missing expected offsets: '+','.join(hex(x) for x in missing))

    out={
      'schema':'sp11-e003h-windows-rtcdm1-init-order-v1',
      'accepted':True,
      'source':{'binary':'qccamisp8380.sys','bytes':len(data),'sha256':sha,'image_base':'0x140000000'},
      'open_init':{
        'order':['IRQ0_MASK=0x00000001','RST_CMD=0x00000009','wait reset completion up to 500 ms','DMB SY','CORE_CFG=0x0000011f'],
        'evidence_rvas':['0x187a8','0x187b4','0x187b8','0x18808','0x18814'],
      },
      'device_start':{
        'manager_order':['CDM start command 0x804','IFE start command 0x804','initial packet command 0x803 to IFE/SFE/CSID resources','CSID start command 0x804'],
        'rtcdm_start_order':['IRQ0_MASK=0x00070007','DMB SY','CORE_EN=0x00000001'],
        'manager_evidence_rvas':['0x15f50','0x15fec','0x160a4','0x160f4','0x16138','0x16208'],
        'rtcdm_evidence_rvas':['0x285d0','0x285d4','0x285e0'],
      },
      'dynamic_fifo0_commit':{
        'order':['FIFO0_BASE=dynamic request base','FIFO0_LEN=dynamic encoded len/tag/arb','FIFO0_STORE=1'],
        'evidence_rvas':['0x28884','0x2888c','0x28894'],
        'dynamic_addresses_must_not_be_hard_coded':True,
      },
      'irq_clear':{
        'mechanism':'read per-FIFO status; mask with 0x00070007; write status to CLEAR; write 1 to CLEAR_CMD',
        'fifo0_evidence_rvas':['0x29228','0x29248'],
      },
      'device_stop':{
        'manager_order':['CSID stop command 0x805','IFE stop command 0x805','CDM stop command 0x805'],
        'rtcdm_stop_direct_write':['IRQ0_MASK=0x00000000'],
        'manager_evidence_rvas':['0x163c8','0x16434','0x164b4'],
        'rtcdm_evidence_rvas':['0x28550'],
        'core_enable_disable_direct_write_observed':False,
        'teardown_after_mask_zero_status':'unresolved; do not invent CORE_EN=0',
      },
      'flush_reset_path':{
        'association':'diagnostic strings mechanically associate command path with CDM core Flush / reset wait',
        'observed_writes':['CORE_EN read-modify-write sets pause bit while preserving enable','RST_CMD=0x00000009'],
        'front_runtime_use':'not established by this static oracle',
      },
      'direct_mapped_base_store_sweep':{
        'region_rva':'0x18000..0x2a000','offsets':[f'0x{x:x}' for x in offsets], 'count':len(stores),
        'fe_cfg_0x20_store_present':False,'fifo0_cfg_0x5c_store_present':False,
        'interpretation':'bounded static negative only; does not prove reset/default ownership',
      },
      'unresolved':[
        'origin/ownership of live FE_CFG +0x20 = 0x07ff000f',
        'origin/ownership of live FIFO0_CFG +0x5c = 0x01000000',
        'whether conditional CGC_CFG +0x14 = 7 path applies to the accepted front RT_CDM1 instance',
        'exact hardware/power semantics after CDM stop masks IRQ0 to zero',
      ],
      'linux_consequence':'Do not add RT-CDM MMIO init/arm/submit from generic Qualcomm defaults. Open/init, start, dynamic commit and manager ordering are now statically pinned; FE_CFG/FIFO0_CFG ownership and final stop semantics remain blocked pending same-machine evidence.'
    }
    if a.output:
        a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else: print(json.dumps(out,indent=2,sort_keys=True))
    print('PASS: exact Windows RT-CDM init/start/commit/stop ordering pinned; FE_CFG/FIFO0_CFG remain unresolved')

if __name__=='__main__': main()
