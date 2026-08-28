#!/usr/bin/env python3
import argparse, hashlib, json, re
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN

EXPECTED_BIN_SHA256='64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c'
EXPECTED_BIN_BYTES=376560
EXPECTED_LOG_SHA256='4d54bca3a1c8d2c542b6b09361e9cdee50a4e85175cb0667f0b8dd10c92076bb'
EXPECTED_LOG_BYTES=18444
IMAGE_BASE=0x140000000
TEXT_RAW=0x400
TEXT_RVA=0x1000
TEXT_SIZE=0x3D48C
FE_CFG=0x20
FIFO0_CFG=0x5c
EXPECTED_FE=0x07ff000f
EXPECTED_FIFO=0x01000000
EXPECTED_HW=0x20010000


def die(msg): raise SystemExit('FAIL: '+msg)

def disassemble(data):
    md=Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN); md.detail=True; md.skipdata=True
    return {i.address-IMAGE_BASE:i for i in md.disasm(data[TEXT_RAW:TEXT_RAW+TEXT_SIZE], IMAGE_BASE+TEXT_RVA) if i.mnemonic!='.byte'}

def need(m,rva,mn,sub):
    i=m.get(rva)
    if i is None or i.mnemonic!=mn or sub not in i.op_str:
        got='<missing>' if i is None else f'{i.mnemonic} {i.op_str}'
        die(f'RVA 0x{rva:x}: expected {mn} containing {sub!r}, got {got}')

def lines_after(lines, marker, occurrence, n):
    hits=[i for i,x in enumerate(lines) if x.strip()==marker]
    if len(hits)<=occurrence: die(f'{marker}: missing occurrence {occurrence}, hits={len(hits)}')
    i=hits[occurrence]+1
    return lines[i:i+n]

def parse_dump(lines, marker, occurrence, has_meta=True):
    chunk=lines_after(lines,marker,occurrence,10 if has_meta else 9)
    meta=None
    if has_meta:
        meta=chunk[0].strip(); dump_lines=chunk[1:9]
        mm=re.fullmatch(r'CDMID=([0-9a-fA-F]+) OBJ=([0-9a-fA-F]+) BASE=([0-9a-fA-F]+)',meta)
        if not mm: die(f'{marker}[{occurrence}] bad metadata: {meta!r}')
        cdm_id=int(mm.group(1),16); obj=int(mm.group(2),16); base=int(mm.group(3),16)
    else:
        dump_lines=chunk[:8]; cdm_id=obj=base=None
    vals=[]; addrs=[]
    for ln in dump_lines:
        mm=re.match(r'^([0-9a-fA-F]+)`([0-9a-fA-F]+)\s+(.+)$',ln.strip())
        if not mm: die(f'{marker}[{occurrence}] bad dump line: {ln!r}')
        addr=int(mm.group(1)+mm.group(2),16); words=re.findall(r'\b[0-9a-fA-F]{8}\b',mm.group(3))
        if len(words)!=4: die(f'{marker}[{occurrence}] expected 4 dwords, got {len(words)}: {ln!r}')
        addrs.append(addr); vals.extend(int(w,16) for w in words)
    if len(vals)!=32: die(f'{marker}[{occurrence}] expected 32 dwords')
    if base is None: base=addrs[0]
    for j,a in enumerate(addrs):
        if a!=base+j*0x10: die(f'{marker}[{occurrence}] address discontinuity')
    return {'cdm_id':cdm_id,'object':obj,'base':base,'values':vals}

def v(d,off): return d['values'][off//4]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('binary',type=Path); ap.add_argument('log',type=Path); ap.add_argument('-o','--output',type=Path); a=ap.parse_args()
    b=a.binary.read_bytes(); raw=a.log.read_bytes()
    if len(b)!=EXPECTED_BIN_BYTES or hashlib.sha256(b).hexdigest()!=EXPECTED_BIN_SHA256: die('binary identity mismatch')
    if len(raw)!=EXPECTED_LOG_BYTES or hashlib.sha256(raw).hexdigest()!=EXPECTED_LOG_SHA256: die('log identity mismatch')
    text=raw.decode('utf-16le'); lines=text.replace('\r\n','\n').split('\n')
    m=disassemble(b)
    for rva,mn,sub in [
        (0x18494,'bl','#0x14002b568'),
        (0x1849c,'str','x0, [x19, #0x48]'),
        (0x187a0,'ldr','x9, [x26, #0x48]'),
        (0x187a8,'str','w8, [x9, #0x30]'),
        (0x187b4,'str','w8, [x9, #0x10]'),
        (0x18814,'str','w8, [x9, #0x18]'),
    ]: need(m,rva,mn,sub)
    counts={x:sum(1 for l in lines if l.strip()==x) for x in [
        '===E003H_FEFIFO_MAP_RETURN===','===E003H_FEFIFO_PRE_FIRST_MMIO===',
        '===E003H_FEFIFO_POST_RESET_WAIT===','===E003H_FEFIFO_POST_CORE_CFG===',
        '===E003H_FEFIFO_BETWEEN_CYCLES_IDLE===','===E003H_FEFIFO_FINAL_IDLE===',
        '===E003H_FEFIFO_ORIGIN_ORACLE_END===']}
    expected_counts={
        '===E003H_FEFIFO_MAP_RETURN===':2,'===E003H_FEFIFO_PRE_FIRST_MMIO===':2,
        '===E003H_FEFIFO_POST_RESET_WAIT===':2,'===E003H_FEFIFO_POST_CORE_CFG===':2,
        '===E003H_FEFIFO_BETWEEN_CYCLES_IDLE===':1,'===E003H_FEFIFO_FINAL_IDLE===':1,
        '===E003H_FEFIFO_ORIGIN_ORACLE_END===':1}
    if counts!=expected_counts: die('marker count mismatch: '+repr(counts))
    maps=[parse_dump(lines,'===E003H_FEFIFO_MAP_RETURN===',i) for i in range(2)]
    pres=[parse_dump(lines,'===E003H_FEFIFO_PRE_FIRST_MMIO===',i) for i in range(2)]
    posts=[parse_dump(lines,'===E003H_FEFIFO_POST_RESET_WAIT===',i) for i in range(2)]
    cores=[parse_dump(lines,'===E003H_FEFIFO_POST_CORE_CFG===',i) for i in range(2)]
    between=parse_dump(lines,'===E003H_FEFIFO_BETWEEN_CYCLES_IDLE===',0,False)
    final=parse_dump(lines,'===E003H_FEFIFO_FINAL_IDLE===',0,False)
    if any(x!=0x80000000 for x in between['values']) or any(x!=0x80000000 for x in final['values']): die('idle sentinel mismatch')
    bases={d['base'] for d in maps+pres+posts+cores}
    if len(bases)!=1 or between['base'] not in bases or final['base'] not in bases: die('RT_CDM1 base changed')
    for name,group in [('map',maps),('pre',pres),('post_reset',posts),('post_core',cores)]:
        for i,d in enumerate(group):
            if d['cdm_id']!=1: die(f'{name}[{i}] CDMID != 1')
            if v(d,0)!=EXPECTED_HW: die(f'{name}[{i}] HW_VERSION mismatch')
            if v(d,FE_CFG)!=EXPECTED_FE: die(f'{name}[{i}] FE_CFG mismatch')
            if v(d,FIFO0_CFG)!=EXPECTED_FIFO: die(f'{name}[{i}] FIFO0_CFG mismatch')
    for i in range(2):
        if maps[i]['values']!=pres[i]['values']: die(f'cycle {i+1}: map-return differs before first MMIO')
    # The second cycle is decisive: it starts from a proven powered-off sentinel,
    # then the exact literals are already present at map-return before the first
    # CDM-object MMIO write. Reset and CORE_CFG do not change them.
    result={
      'schema':'sp11-e003h-windows-rtcdm1-fe-fifo-origin-v1','accepted':True,
      'source':{'binary':'qccamisp8380.sys','binary_bytes':len(b),'binary_sha256':EXPECTED_BIN_SHA256,'raw_log':a.log.name,'raw_log_bytes':len(raw),'raw_log_sha256':EXPECTED_LOG_SHA256},
      'instruction_boundaries':{
        'resource_getter_call_rva':'0x18494','map_return_store_rva':'0x1849c',
        'pre_first_mmio_boundary_rva':'0x187a0','first_cdm_object_mmio_write_rva':'0x187a8',
        'first_cdm_object_mmio_write':'IRQ0_MASK +0x30 = 1','reset_cmd_write_rva':'0x187b4','core_cfg_write_rva':'0x18814'},
      'two_cycle_oracle':{
        'between_cycles_first_0x80_bytes':'all 0x80000000 powered-off sentinel',
        'cycle1_object':f"0x{maps[0]['object']:x}",'cycle2_object':f"0x{maps[1]['object']:x}",
        'rtcdm1_mapped_va':f"0x{maps[0]['base']:x}",
        'map_return_fe_cfg':'0x07ff000f','map_return_fifo0_cfg':'0x01000000',
        'map_return_before_first_cdm_object_mmio':True,
        'map_return_equals_pre_first_mmio':True,
        'fe_fifo_unchanged_after_reset_wait':True,'fe_fifo_unchanged_after_core_cfg':True,
        'final_first_0x80_bytes':'all 0x80000000 powered-off sentinel'},
      'ownership_classification':'positive same-machine timing: FE_CFG/FIFO0_CFG are restored by pre-CDM-object platform/power-up/hardware state; they are not programmed by the front CDM-object MMIO path. This does not distinguish firmware from hardware reset/default ownership.',
      'linux_consequence':'Do not write FE_CFG or FIFO0_CFG. After the proven-equivalent platform/power domain is active and before the first RT-CDM MMIO write, read-only validate HW_VERSION=0x20010000, FE_CFG=0x07ff000f and FIFO0_CFG=0x01000000; fail closed without MMIO writes if any mismatch. Then follow the Windows init sequence.',
      'remaining_before_static_linux_rtcdm_init':'derive the Linux read-only validation/power-ownership placement and implement the exact init/reset/IRQ/FIFO state machine without enabling runtime',
    }
    out=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if a.output: a.output.write_text(out)
    else: print(out,end='')
    print('PASS: FE_CFG/FIFO0_CFG positive origin timing closed; values reappear before first CDM-object MMIO after a proven powered-off interval',file=__import__('sys').stderr)
if __name__=='__main__': main()
