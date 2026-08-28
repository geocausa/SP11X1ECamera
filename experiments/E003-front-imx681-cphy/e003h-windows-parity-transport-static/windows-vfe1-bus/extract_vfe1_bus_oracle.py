#!/usr/bin/env python3
import csv, hashlib, json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROUTE_DIR = HERE.parents[1] / 'e003g-windows-csid-vfe-oracle'
RAW = ROUTE_DIR / 'raw' / 'E003G_ROUTE_ORACLE_20260828.log'
RAW_SHA = 'fd8edcee46e794dffa0e2305331f19d4e9d2cd5b9ba5197484aa1cc7fa6c6fca'
QREF = '0f16924ff6a7f9bb56a7e958016da2ed8a174f2f'
VFE1 = 0x0AC71000
SIZE = 0x4000
PHASES = ('LIVE1', 'LIVE2')
LINE = re.compile(r'^([0-9a-f]{8})`([0-9a-f]{8})\s+([0-9a-f]{8})\s+([0-9a-f]{8})\s+([0-9a-f]{8})\s+([0-9a-f]{8})\s*$', re.I|re.M)

CLIENT_NAMES = {
 0:'FULL_Y',1:'FULL_C',2:'DS4',3:'DS16',4:'DISP_Y',5:'DISP_C',6:'DISP_DS4',7:'DISP_DS16',
 8:'FD_Y',9:'FD_C',10:'PIXEL_RAW',11:'STATS_BE0',12:'STATS_BHIST0',13:'STATS_TINTLESS_BG',14:'STATS_AWB_BG',
 15:'STATS_AWB_BFW',16:'STATS_BAF',17:'STATS_BHIST',18:'STATS_RS',19:'STATS_IHIST',20:'SPARSE_PD',
 21:'PDAF_PD_DATA',22:'PDAF_SAD',23:'LCR',24:'RDI0',25:'RDI1',26:'RDI2',27:'LTM_STATS'
}
ACTIVE = [0,1,2,3,11,12,13,14,18]
FIELDS = [
 ('cfg',0x00,'writable_config'), ('image_addr',0x04,'dynamic_buffer_address'),
 ('frame_incr',0x08,'writable_config'), ('image_cfg0',0x0c,'writable_config'),
 ('image_cfg1',0x10,'writable_config'), ('image_cfg2',0x14,'writable_config'),
 ('packer_cfg',0x18,'writable_config'), ('bw_limit',0x1c,'writable_config'),
 ('frame_header_addr',0x20,'dynamic_buffer_address'), ('frame_header_incr',0x24,'writable_config'),
 ('frame_header_cfg',0x28,'writable_config'), ('irq_subsample_period',0x30,'writable_config'),
 ('irq_subsample_pattern',0x34,'writable_config'), ('framedrop_period',0x38,'writable_config'),
 ('framedrop_pattern',0x3c,'writable_config'), ('meta_addr',0x40,'dynamic_buffer_address'),
 ('meta_cfg',0x44,'writable_config'), ('mode_cfg',0x48,'writable_config'),
 ('stats_ctrl',0x4c,'writable_config'), ('ctrl_2',0x50,'writable_config'),
 ('lossy_thresh0',0x54,'writable_config'), ('lossy_thresh1',0x58,'writable_config'),
 ('lossy_var_offset',0x5c,'writable_config'), ('mmu_prefetch_cfg',0x60,'writable_config'),
 ('mmu_prefetch_max_offset',0x64,'writable_config'), ('system_cache_cfg',0x68,'writable_config'),
 ('addr_status0',0x70,'status_readback'), ('addr_status1',0x74,'status_readback'),
 ('addr_status2',0x78,'status_readback'), ('addr_status3',0x7c,'status_readback'),
 ('debug_status_cfg',0x80,'writable_debug_config'), ('debug_status0',0x84,'status_readback'),
 ('debug_status1',0x88,'status_readback'),
]

def parse_dump(text, phase):
    begin=f'===E003G3_{phase}_VFE1_BEGIN==='; end=f'===E003G3_{phase}_VFE1_END==='
    assert begin in text and end in text
    body=text.rsplit(begin,1)[1].split(end,1)[0]
    out={}
    for m in LINE.finditer(body):
        a=int(m.group(1)+m.group(2),16)
        for i in range(4): out[a+4*i]=int(m.group(3+i),16)
    assert len(out)==SIZE//4
    return out

def hx(v): return f'0x{v:08x}'

def main():
    raw=RAW.read_bytes(); assert hashlib.sha256(raw).hexdigest()==RAW_SHA
    text=raw.decode('utf-16',errors='replace')
    d={p:parse_dump(text,p) for p in PHASES}
    rows=[]; clients=[]
    for c in range(28):
        base=0xe00+c*0x100
        cfg1=d['LIVE1'][VFE1+base]; cfg2=d['LIVE2'][VFE1+base]
        client={'client':c,'name':CLIENT_NAMES[c],'enabled_live1':bool(cfg1&1),'enabled_live2':bool(cfg2&1),'cfg_live1':hx(cfg1),'cfg_live2':hx(cfg2)}
        clients.append(client)
        for name,delta,role in FIELDS:
            v1=d['LIVE1'][VFE1+base+delta]; v2=d['LIVE2'][VFE1+base+delta]
            rows.append({'client':c,'name':CLIENT_NAMES[c],'register':name,'offset':f'0x{base+delta:04x}',
                         'role':role,'live1':hx(v1),'live2':hx(v2),'stable':int(v1==v2)})
    enabled1=[c['client'] for c in clients if c['enabled_live1']]
    enabled2=[c['client'] for c in clients if c['enabled_live2']]
    assert enabled1==ACTIVE and enabled2==ACTIVE, (enabled1,enabled2)

    # All writable non-address configuration of active clients is stable across the two Windows starts.
    active_cfg=[r for r in rows if r['client'] in ACTIVE and r['role'] in ('writable_config','writable_debug_config')]
    unstable_cfg=[r for r in active_cfg if not r['stable']]
    assert not unstable_cfg, unstable_cfg

    def val(passname,c,delta): return d[passname][VFE1+0xe00+c*0x100+delta]
    layout=[]
    for p in PHASES:
        y_meta=val(p,0,0x40); y_data=val(p,0,0x04); c_meta=val(p,1,0x40); c_data=val(p,1,0x04)
        assert y_data-y_meta==0x6000
        assert c_meta-y_meta==0x4f2000
        assert c_data-y_meta==0x4f5000
        assert c_data-c_meta==0x3000
        assert val(p,0,0x08)==0x4f2000
        assert val(p,1,0x08)==0x279000
        assert (c_meta-y_meta)+val(p,1,0x08)==0x76b000
        layout.append({'pass':p,'surface_base':hx(y_meta),'y_meta':hx(y_meta),'y_data':hx(y_data),'c_meta':hx(c_meta),'c_data':hx(c_data)})

    def client_static(c):
        base=0xe00+c*0x100
        return {name:hx(d['LIVE1'][VFE1+base+delta]) for name,delta,role in FIELDS if role in ('writable_config','writable_debug_config')}

    summary={
      'status':'PASS',
      'policy':'Same-machine Windows is behavioral oracle; Qualcomm commit is used only for VFE680 bus register names/layout and programming mechanics.',
      'raw':{'file':RAW.name,'bytes':len(raw),'sha256':RAW_SHA,'windows_live_passes':2},
      'qualcomm_vfe680_reference_commit':QREF,
      'enabled_clients':[{k:c[k] for k in ('client','name','cfg_live1')} for c in clients if c['client'] in ACTIVE],
      'inactive_parity_relevant_clients':{'PIXEL_RAW':10,'RDI0':24,'RDI1':25,'RDI2':26},
      'active_writable_configuration_stable_across_two_passes':True,
      'full_qc10c':{
        'width':2560,'height':1440,'stride_bytes':3584,'surface_bytes':0x76b000,
        'layout':'Y_META -> Y_TP10 -> C_META -> C_TP10',
        'offsets':{'y_meta':0,'y_data':0x6000,'c_meta':0x4f2000,'c_data':0x4f5000},
        'y_meta_bytes':0x6000,'c_meta_bytes':0x3000,'y_frame_increment':0x4f2000,'c_frame_increment':0x279000,
        'packer_cfg':'0x0000000b','windows_format_family':'TP10 UBWC / QC10C','two_pass_address_proof':layout,
        'client0_full_y_static':client_static(0),'client1_full_c_static':client_static(1),
      },
      'ds':{'client2_ds4_static':client_static(2),'client3_ds16_static':client_static(3)},
      'stats':{str(c):client_static(c) for c in (11,12,13,14,18)},
      'ownership':{
        'dynamic_buffer_address_fields':['image_addr','frame_header_addr','meta_addr'],
        'status_readback_fields':['addr_status0','addr_status1','addr_status2','addr_status3','debug_status0','debug_status1'],
        'rule':'Never copy Windows live addresses/status into Linux. Derive per-buffer addresses; program only stable configuration values whose register semantics are writable/configuration.',
      },
      'linux_architecture_consequence':'Windows FULL requires two write clients (0 FULL_Y + 1 FULL_C) pointing into one contiguous QC10C allocation. Current VFE680 RDI-only single-WM plumbing cannot represent this path.',
    }
    with open(HERE/'vfe1-bus-registers.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys(), lineterminator='\n'); w.writeheader(); w.writerows(rows)
    (HERE/'vfe1-bus-oracle.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
