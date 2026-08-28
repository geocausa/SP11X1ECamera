#!/usr/bin/env python3
from pathlib import Path
from collections import Counter
import argparse,csv,hashlib,json,re,struct

RAW_SHA='a22f94b6a024226791c139336b17777f1359f1847146bafa6e092215e86e762a'
QREF='0f16924ff6a7f9bb56a7e958016da2ed8a174f2f'
MARK='===E003H_INIT_803_BREAK==='
VFE1=0x0ac71000
MAPLEN=0x4000
EXP_USED=[0xe94,0xe34,0x904,0x4e8]
EXP_CMDS=[110,103,52,13]
EXP_WRITES=[695,687,462,287]
DD=re.compile(r'^([0-9a-f]{8})`([0-9a-f]{8})\s+((?:[0-9a-f]{8}\s+){3}[0-9a-f]{8})$',re.I)
DB=re.compile(r'^([0-9a-f]{8})`([0-9a-f]{8})\s+((?:[0-9a-f]{2}\s+){7}[0-9a-f]{2})-((?:[0-9a-f]{2}\s+){7}[0-9a-f]{2})',re.I)
NAMES={1:'DMI',3:'REG_CONT',4:'REG_RANDOM',5:'BUFF_INDIRECT',6:'GEN_IRQ',7:'WAIT_EVENT',8:'CHANGE_BASE',9:'PERF_CTRL',10:'DMI_32',11:'DMI_64',12:'COMP_WAIT',13:'CLEAR_COMP_WAIT',14:'WAIT_PREFETCH_DISABLE'}

def sha(b): return hashlib.sha256(b).hexdigest()

def dwords(block):
    out={}
    for line in block:
        m=DD.match(line)
        if not m: continue
        a=int(m.group(1)+m.group(2),16)
        for i,v in enumerate(m.group(3).split()): out[a+4*i]=int(v,16)
    return out

def dump(block,cpu):
    data=bytearray(0xf00); seen=bytearray(0xf00)
    for line in block:
        m=DB.match(line)
        if not m: continue
        a=int(m.group(1)+m.group(2),16)
        if not cpu<=a<cpu+0xf00: continue
        chunk=bytes(int(x,16) for x in (m.group(3)+' '+m.group(4)).split())
        o=a-cpu; data[o:o+16]=chunk; seen[o:o+16]=b'\1'*16
    if not all(seen): raise ValueError('incomplete 0xf00-byte KD db window')
    return bytes(data)

def decode(data):
    pos=0; base=VFE1; cmds=[]; writes=[]; dmis=[]
    while pos<len(data):
        w0=struct.unpack_from('<I',data,pos)[0]; op=w0>>24; name=NAMES.get(op)
        if not name: raise ValueError(f'unknown opcode 0x{op:02x} at 0x{pos:x}')
        rec={'stream_offset':pos,'opcode':op,'command':name}
        if op==3:
            n=w0&0xffff; need=8+4*n; off=struct.unpack_from('<I',data,pos+4)[0]&0xffffff
            if pos+need>len(data): raise ValueError('truncated REG_CONT')
            rec.update(count=n,register_offset=off,bytes=need)
            for i in range(n):
                val=struct.unpack_from('<I',data,pos+8+4*i)[0]; ro=off+4*i
                writes.append({'stream_offset':pos,'command':name,'register_offset':ro,'absolute_address':base+ro,'value':val,'outside_linux_0x4000_mapping':ro>=MAPLEN})
            pos+=need
        elif op==4:
            n=w0&0xffff; need=4+8*n
            if pos+need>len(data): raise ValueError('truncated REG_RANDOM')
            rec.update(count=n,bytes=need)
            for i in range(n):
                ro,val=struct.unpack_from('<II',data,pos+4+8*i); ro &= 0xffffff
                writes.append({'stream_offset':pos,'command':name,'register_offset':ro,'absolute_address':base+ro,'value':val,'outside_linux_0x4000_mapping':ro>=MAPLEN})
            pos+=need
        elif op in (1,10,11):
            if pos+12>len(data): raise ValueError('truncated DMI')
            addr=struct.unpack_from('<I',data,pos+4)[0]; w2=struct.unpack_from('<I',data,pos+8)[0]
            rec.update(length=w0&0xffff,data_iova=addr,dmi_register_offset=w2&0xffffff,dmi_sel=w2>>24,bytes=12)
            dmis.append(dict(rec)); pos+=12
        elif op==5:
            rec.update(length_minus_one=w0&0xffff,data_iova=struct.unpack_from('<I',data,pos+4)[0],bytes=8); pos+=8
        elif op==6:
            rec.update(userdata=struct.unpack_from('<I',data,pos+4)[0],bytes=8); pos+=8
        elif op in (7,12,13,14): rec.update(bytes=12); pos+=12
        elif op==8: base=w0&0xffffff; rec.update(new_base=base,bytes=4); pos+=4
        elif op==9: rec.update(bytes=4); pos+=4
        cmds.append(rec)
    if pos!=len(data): raise ValueError('decode length mismatch')
    return cmds,writes,dmis

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('raw',type=Path); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
    raw=a.raw.read_bytes()
    if sha(raw)!=RAW_SHA: raise SystemExit('raw SHA mismatch')
    lines=raw.decode('utf-16').splitlines(); marks=[i for i,l in enumerate(lines) if l==MARK]
    if len(marks)!=4: raise SystemExit(f'expected 4 runtime markers, got {len(marks)}')
    a.out.mkdir(parents=True,exist_ok=True); packets=[]; allwrites=[]
    for pi,mi in enumerate(marks):
        block=lines[mi:marks[pi+1] if pi+1<len(marks) else len(lines)]
        xm=re.search(r'x2=([0-9a-f]+) x8=([0-9a-f]+)',next(l for l in block if l.startswith('x2=')),re.I)
        x2=int(xm.group(1),16); handler=int(xm.group(2),16); dw=dwords(block)
        if dw[x2+8]!=pi or dw[x2+0x1c]!=3: raise SystemExit(f'packet {pi} outer descriptor mismatch')
        desc=[]
        for di in range(3):
            b=x2+0x74+di*0x20; h=dw[b]|(dw[b+4]<<32)
            desc.append({'index':di,'handle':f'0x{h:016x}','offset':dw[b+8],'capacity':dw[b+0xc],'used_length':dw[b+0x10],'flags':dw[b+0x14],'type':dw[b+0x18]})
        used=desc[0]['used_length']
        if used!=EXP_USED[pi]: raise SystemExit(f'packet {pi} used length mismatch')
        ev=next(l for l in block if l.startswith('Evaluate expression:')); em=re.search(r'= ([0-9a-f]{8})`([0-9a-f]{8})',ev,re.I); cpu=int(em.group(1)+em.group(2),16)
        stream=dump(block,cpu)[:used]; cmds,writes,dmis=decode(stream)
        if [len(cmds),len(writes)] != [EXP_CMDS[pi],EXP_WRITES[pi]]: raise SystemExit(f'packet {pi} decode-count mismatch')
        (a.out/f'packet{pi}-main-cdm.bin').write_bytes(stream)
        with (a.out/f'packet{pi}-register-writes.csv').open('w',newline='') as f:
            fields=['stream_offset','command','register_offset','absolute_address','value','outside_linux_0x4000_mapping']; w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n'); w.writeheader()
            for r in writes: w.writerow({'stream_offset':f"0x{r['stream_offset']:04x}",'command':r['command'],'register_offset':f"0x{r['register_offset']:06x}",'absolute_address':f"0x{r['absolute_address']:08x}",'value':f"0x{r['value']:08x}",'outside_linux_0x4000_mapping':int(r['outside_linux_0x4000_mapping'])})
        allwrites += [(pi,r) for r in writes]
        packets.append({'packet':pi,'outer_packet_word':f'0x{dw[x2]:08x}','packet_index':dw[x2+8],'descriptor_count':3,'descriptors':desc,'ife_handler':f'0x{handler:016x}','mapped_main_cpu_va':f'0x{cpu:016x}','main_used_length':used,'main_sha256':sha(stream),'command_count':len(cmds),'register_write_count':len(writes),'dmi_count':len(dmis),'dmi_commands':dmis,'opcode_counts':dict(sorted(Counter(c['command'] for c in cmds).items())),'max_register_offset':max(r['register_offset'] for r in writes),'writes_outside_linux_0x4000_mapping':sum(r['outside_linux_0x4000_mapping'] for r in writes)})
    p3={r['register_offset']:r['value'] for pi,r in allwrites if pi==3}
    for off,val in {0x24:0x6000,0x90:1}.items():
        if p3.get(off)!=val: raise SystemExit(f'VFE1 MMIO cross-check failed at +0x{off:x}')
    maxoff=max(r['register_offset'] for _,r in allwrites); outside=sum(r['outside_linux_0x4000_mapping'] for _,r in allwrites)
    summary={'status':'PASS','policy':'Same-machine Windows is behavioral oracle; Qualcomm source is used only for CDM command encoding/names.','raw':{'bytes':len(raw),'sha256':RAW_SHA,'encoding':'UTF-16LE KD text log','standalone_runtime_breaks':4},'windows_isp':{'binary_sha256':'64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c','live_base_for_capture':'0xfffff80298890000','device_start_ife_0x803_callsite_rva':'0x16094','ife_handler_rva':'0x22cd0'},'qualcomm_cdm_reference_commit':QREF,'cdm_decode':{'all_streams_decode_exactly_to_declared_length':True,'unknown_opcodes':0,'change_base_commands':0,'current_base_proven_by_windows_mmio_crosscheck':'0x0ac71000 (VFE1)','base_crosscheck':{'packet3_plus_0x24':'0x00006000','route_oracle_live_plus_0x24':'0x00006000','packet3_plus_0x90':'0x00000001','route_oracle_live_plus_0x90':'0x00000001'},'max_register_offset':f'0x{maxoff:x}','linux_current_vfe1_mapping_bytes':MAPLEN,'total_register_writes_outside_linux_0x4000_mapping':outside},'packets':packets,'next_required_oracle':'Capture descriptor 1/2 mapped bytes for the same four DEVICE_START packets so DMI/LUT and companion data are preserved; main CDM alone is not sufficient for full ISP parity.'}
    (a.out/'initial-ife-cdm-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
