#!/usr/bin/env python3
from pathlib import Path
import hashlib, json
import pefile
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN, CS_OP_REG, CS_OP_MEM

BIN=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys')
EXPECTED_SHA='64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c'
IMAGE=0x140000000
READER=(0x1b5f0,0x1b7cc)
HANDLER=(0x1b840,0x1bdcc)
EXPECTED_READER_STORES=[0x84,0xa4,0x94,0xb4,0xd4,0x14]
EXPECTED_W24_TESTS=[('tbz',12),('tst_mask',0x3c1c6004),('tbz',1),('tbz',4),('tbz',3)]
RUP_DONE_BIT=23

def die(s): raise SystemExit('FAIL: '+s)
def main():
    raw=BIN.read_bytes(); got=hashlib.sha256(raw).hexdigest()
    if got!=EXPECTED_SHA: die('qccamisp hash drift '+got)
    pe=pefile.PE(str(BIN),fast_load=True)
    if pe.OPTIONAL_HEADER.ImageBase!=IMAGE: die('image base drift')
    md=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN); md.detail=True
    def dis(s,e): return list(md.disasm(pe.get_data(s,e-s),IMAGE+s))
    def direct_mmio_stores(insns):
        mmio=set(); out=[]
        for ins in insns:
            dest=None
            if ins.operands and ins.operands[0].type==CS_OP_REG:
                dest=ins.reg_name(ins.operands[0].reg)
            establish=None
            if ins.mnemonic=='ldr' and len(ins.operands)>=2 and ins.operands[0].type==CS_OP_REG and ins.operands[1].type==CS_OP_MEM:
                if ins.reg_name(ins.operands[1].mem.base)=='x19' and ins.operands[1].mem.disp==8:
                    establish=ins.reg_name(ins.operands[0].reg)
            if ins.mnemonic.startswith(('str','stp','stur')):
                for o in ins.operands:
                    if o.type==CS_OP_MEM and ins.reg_name(o.mem.base) in mmio:
                        out.append({'rva':ins.address-IMAGE,'mnemonic':ins.mnemonic,'op_str':ins.op_str,'offset':o.mem.disp})
            if dest in mmio and ins.mnemonic not in ('str','stp','stur'):
                mmio.discard(dest)
            if establish: mmio.add(establish)
        return out
    reader=dis(*READER); handler=dis(*HANDLER)
    rs=direct_mmio_stores(reader); hs=direct_mmio_stores(handler)
    if [x['offset'] for x in rs]!=EXPECTED_READER_STORES: die('reader direct MMIO store set/order drift '+repr(rs))
    if hs: die('handler gained direct MMIO stores '+repr(hs))
    if any(x['offset']==0x18 for x in rs+hs): die('direct REG_UPDATE_CMD +0x18 write found in IRQ reader/handler')
    # Recover all actual condition tests of w24, the IPP payload loaded at RVA 0x1b8b0.
    tests=[]
    w27_mask=None
    for ins in handler:
        rva=ins.address-IMAGE
        if rva==0x1b8b0 and not (ins.mnemonic=='ldp' and ins.op_str.startswith('w25, w24, [x1, #0xc]')):
            die('IPP payload load anchor drift')
        if ins.mnemonic in ('tbz','tbnz') and len(ins.operands)>=2 and ins.operands[0].type==CS_OP_REG and ins.reg_name(ins.operands[0].reg)=='w24':
            tests.append((ins.mnemonic,ins.operands[1].imm,rva))
        if rva==0x1b9f8:
            # ldr w27, literal 0x14001bdd8; exact literal already disassembled from the pinned image.
            if not (ins.mnemonic=='ldr' and ins.op_str.startswith('w27, ')): die('w27 error-mask load anchor drift')
            w27_mask=int.from_bytes(pe.get_data(0x1bdd8,4),'little')
        if ins.mnemonic=='tst' and ins.op_str=='w24, w27':
            if w27_mask is None: die('error mask unavailable before tst')
            tests.append(('tst_mask',w27_mask,rva))
    normalized=[(a,b) for a,b,_ in tests]
    if normalized!=EXPECTED_W24_TESTS: die('IPP handler condition set drift '+repr(tests))
    if any(a in ('tbz','tbnz') and b==RUP_DONE_BIT for a,b,_ in tests): die('RUP_DONE bit23 conditional handling found')
    if any(a=='tst_mask' and (b & (1<<RUP_DONE_BIT)) for a,b,_ in tests): die('RUP_DONE included in handler mask')
    out={
      'schema':'sp11-e003h-windows-csid1-rupdone-irq-ownership-v1','accepted':True,
      'driver':{'path':str(BIN),'sha256':got,'image_base':'0x140000000'},
      'reader':{'rva':'0x1b5f0..0x1b7c8','direct_mmio_stores':[{'rva':f"0x{x['rva']:x}",'offset':f"0x{x['offset']:x}",'instruction':x['mnemonic']+' '+x['op_str']} for x in rs],
                'direct_mmio_store_offsets':[f'0x{x:x}' for x in EXPECTED_READER_STORES],
                'reg_update_cmd_0x18_written':False,
                'ipp_irq_status_read_rva':'0x1b65c','ipp_irq_clear_write_rva':'0x1b750'},
      'handler':{'rva':'0x1b840..0x1bdc8','ipp_payload_load_rva':'0x1b8b0','direct_mmio_stores':[],
                 'ipp_condition_tests':[{'kind':a,'value':(hex(b) if a=='tst_mask' else b),'rva':f'0x{r:x}'} for a,b,r in tests],
                 'rup_done_bit':23,'rup_done_conditionally_handled':False,'reg_update_cmd_0x18_written':False},
      'classification':{
        'windows_irq_acknowledges_full_ipp_status':True,
        'windows_rup_done_causes_reg_update_cmd_write':False,
        'windows_rup_done_causes_zero_write_to_reg_update_cmd':False,
        'linux_generic_post_rup_zero_write_is_windows_parity':False,
        'linux_consequence':'For the X1E80100 front IPP path whose RUP/AUP command is RT-CDM-owned, software may clear its bookkeeping shadow after RUP_DONE but must not emit a second MMIO write to CSID +0x18. Preserve existing legacy RDI/non-front behavior.'
      },
      'next_gate':'Represent the smallest X1E front-IPP-only Linux delta that suppresses the post-RUP_DONE +0x18 MMIO write while retaining software-shadow clear and all non-front/RDI behavior. Inspect/build before runtime.'
    }
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()
