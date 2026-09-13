#!/usr/bin/env python3
from pathlib import Path
import csv, hashlib, json, re, struct

D=Path(__file__).resolve().parent
P=D.parent
RAW=D/'raw/E004_IR_CSID_ROUTE_ORACLE_20260913.log'
HOLDER=D/'E004-IR-RouteHolder.ps1'
TRANSCRIPT=D/'E004_IR_ROUTE_HOLDER_20260913.txt'
RESOURCES=D/'WINDOWS-SECUREISP-RESOURCE-PROOF.txt'
E003G=P.parent/'E003-front-imx681-cphy/e003g-windows-csid-vfe-oracle/csid0-route-live-nonzero.csv'
OUT=D/'WINDOWS-IR-SECURE-ROUTE-SUMMARY.json'

EXPECTED={
 'raw':'d63a755a97acfbb0b4a5f51cdcd557df0da482332fbd556a742d1a8c06101787',
 'holder':'d2a987cfb441f12d775cf711ff9585290ce04f81842b6dedeb0fc7230a124652',
 'transcript':'b7854a0bdfb56c229d2e0ef5a3e6fc507cfe03ecaf07e9d264d72e9c57d8128c',
 'resources':'3934dea5013db9ecfe1c855dd6c52507a68f4c961be7b4afa3bcc71a667ea89b',
}
REGIONS={
 'WRAPPER':(0x0acb6000,0x400),
 'CSID0':(0x0acb7000,0x800),
 'CSID1':(0x0acb9000,0x800),
 'CSID2':(0x0acbb000,0x800),
 'VFE0':(0x0ac62000,0x1000),
 'VFE1':(0x0ac71000,0x1000),
}

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v: raise AssertionError(m)
for k,p in [('raw',RAW),('holder',HOLDER),('transcript',TRANSCRIPT),('resources',RESOURCES)]:
    need(sha(p)==EXPECTED[k],f'{k} hash drift')

s=RAW.read_bytes().decode('utf-16le',errors='strict')

def region_block(phase,reg):
    a=f'===E004IR_{phase}_{reg}_BEGIN==='
    b=f'===E004IR_{phase}_{reg}_END==='
    m=re.search(r'(?:^|\r?\n)'+re.escape(a)+r'\r?\n(.*?)\r?\n'+re.escape(b)+r'(?:\r?\n|$)',s,re.S)
    need(m is not None,f'missing block {phase}/{reg}')
    return m.group(1)

def region_values(phase,reg):
    base,count=REGIONS[reg]
    vals={}
    for ln in region_block(phase,reg).splitlines():
        q=re.match(r'#\s*([0-9a-fA-F]+)\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})',ln)
        if not q: continue
        addr=int(q.group(1),16)
        for k in range(4):
            vals[addr+4*k]=int(q.group(2+k),16)
    need(len(vals)==count,f'{phase}/{reg} dword count {len(vals)} != {count}')
    return [vals[base+4*i] for i in range(count)]

def image_hash(arr):
    return hashlib.sha256(b''.join(struct.pack('<I',x) for x in arr)).hexdigest()

summary={
 'schema':'sp11-camera-e004y-windows-ir-secure-route-oracle-v1',
 'status':'PASS_WINDOWS_IR_STANDARD_CAMSS_BYPASSED_SECUREISP_PRESENT_PROTECTED',
 'raw':{'bytes':RAW.stat().st_size,'sha256':EXPECTED['raw']},
 'winrt':{},
 'regions':{},
 'comparisons':{},
 'secureisp':{},
}
t=TRANSCRIPT.read_text()
need('E004_IR_ROUTE_SELECTED kind=Infrared stream=VideoPreview subtype=NV12 dims=644x604 fps=60/1' in t,'IR format')
need('E004_IR_ROUTE_START_STATUS=Success' in t,'StartAsync')
need('E004_IR_ROUTE_ACQUIRED=12' in t,'frame acquisition')
need('E004_IR_ROUTE_STOP_PASS' in t,'StopAsync')
frames=re.findall(r'^E004_IR_ROUTE_FRAME n=(\d+) system_relative_time=(.+)$',t,re.M)
need(len(frames)==12 and [int(x[0]) for x in frames]==list(range(1,13)),'frame transcript')
summary['winrt']={
 'device':'Surface IR Camera Front',
 'source_kind':'Infrared',
 'stream':'VideoPreview',
 'subtype':'NV12',
 'width':644,'height':604,'fps_num':60,'fps_den':1,
 'start_async':'Success','acquired_frames':12,'stop_async':'Success',
 'holder_sha256':EXPECTED['holder'],'transcript_sha256':EXPECTED['transcript'],
}

for phase in ('LIVE1','POST1','LIVE2','POST2'):
    summary['regions'][phase]={}
    for reg in REGIONS:
        a=region_values(phase,reg)
        summary['regions'][phase][reg]={
            'dwords':len(a),
            'nonzero_dwords':sum(x!=0 for x in a),
            'sentinel_0x80000000_dwords':sum(x==0x80000000 for x in a),
            'image_sha256_le32':image_hash(a),
            'first_four':[f'0x{x:08x}' for x in a[:4]],
        }

# Live reader-only and live real-frame acquisitions are exactly identical.
live_diffs={}
for reg in REGIONS:
    a=region_values('LIVE1',reg); b=region_values('LIVE2',reg)
    live_diffs[reg]=sum(x!=y for x,y in zip(a,b))
    need(live_diffs[reg]==0,f'{reg} changed after actual frame acquisition')
summary['comparisons']['live1_vs_live2_mismatches']=live_diffs

# All post blocks must be completely powered off/inaccessible sentinels.
for phase in ('POST1','POST2'):
    for reg,(base,count) in REGIONS.items():
        a=region_values(phase,reg)
        need(all(x==0x80000000 for x in a),f'{phase}/{reg} not fully sentinel')

# Wrapper: each CSID IO_PATH_CFG0 remains 1, so no OUTPUT_IFE_EN bit8 is set.
wrap=region_values('LIVE2','WRAPPER')
need(wrap[0]==1 and wrap[1]==1 and wrap[2]==1,'wrapper CSID IO path state')
need(all((x & 0x100)==0 for x in wrap[:3]),'unexpected OUTPUT_IFE_EN')
summary['comparisons']['live_wrapper_io_path_cfg0']={
 'csid0':'0x00000001','csid1':'0x00000001','csid2':'0x00000001',
 'output_ife_en_any':False,
}

# VFE0/VFE1 are completely zero while real frames are delivered.
for reg in ('VFE0','VFE1'):
    a=region_values('LIVE2',reg)
    need(all(x==0 for x in a),f'{reg} active during IR')
summary['comparisons']['vfe_live_all_zero']=True

# Reconstruct the prior Windows RGB inactive/default CSID0 image from its 79 nonzero rows.
rows=list(csv.DictReader(open(E003G,newline='')))
ref=[0]*0x800
for rr in rows:
    ref[int(rr['offset'],16)//4]=int(rr['live1'],16)
need(sum(x!=0 for x in ref)==79,'E003g inactive CSID nonzero count')
ref_hash=image_hash(ref)
need(ref_hash=='f4cdd9594c9e63600c087a6bc653ebce05468e1d6ce0f9a20b7d10cd81afc60a','E003g inactive CSID hash')
summary['comparisons']['e003g_windows_inactive_csid0_sha256_le32']=ref_hash
summary['comparisons']['ir_csid_equal_to_e003g_inactive_default']={}
for reg in ('CSID0','CSID1','CSID2'):
    a=region_values('LIVE2',reg)
    need(a==ref,f'{reg} differs from Windows inactive/default CSID image')
    summary['comparisons']['ir_csid_equal_to_e003g_inactive_default'][reg]=True

res=RESOURCES.read_text()
for tok in ('ACPI\\\\QCOM0CCC\\\\19','Qualcomm(R) Spectra(TM) 395 SecureISP Device',
            '0x000000000ACCA000 - 0x000000000ACCDFFF','Status: Started',
            'qccamsecureisp8380.sys','qccamisp8380.sys'):
    need(tok in res,'resource proof '+tok)
summary['secureisp']={
 'device':'Qualcomm(R) Spectra(TM) 395 SecureISP Device',
 'acpi_instance':'ACPI\\\\QCOM0CCC\\\\19',
 'driver':'qccamsecureisp8380.sys',
 'status':'Started',
 'physical_window':'0x0acca000..0x0accdfff',
 'size_bytes':0x4000,
 'irq_resources':[392,391],
 'resource_proof_sha256':EXPECTED['resources'],
 'kd_direct_readable_during_live_frames':False,
 'kd_uncached_readable_during_live_frames':False,
}
need('===E004IR_LIVE2_SECUREISP_BEGIN===' in s,'secure live marker')
need('===E004IR_SECUREISP_UC_TEST===' in s,'secure UC marker')
for marker in ('===E004IR_LIVE2_SECUREISP_BEGIN===','===E004IR_SECUREISP_UC_TEST==='):
    pos=s.index(marker)
    tail=s[pos:pos+900]
    need('Physical memory read at acca000 failed' in tail,'secure read unexpectedly accessible')

for mod in ('qccamisp8380','qccamsecureisp8380','qccammipicsi8380','surfacecamauxsensor8380','surfacecamavs8380'):
    need(mod in s,'live module '+mod)
summary['secureisp']['live_modules_proved']=[
 'qccamisp8380','qccamsecureisp8380','qccammipicsi8380','surfacecamauxsensor8380','surfacecamavs8380'
]

summary['conclusion']={
 'standard_camss_csid_active':False,
 'standard_camss_vfe_active':False,
 'real_ir_frames_delivered':True,
 'secureisp_present_and_started':True,
 'secureisp_mmio_protected_from_kd':True,
 'parity_boundary':'A Linux normal-CAMSS IR route may be useful diagnostically, but cannot be called Windows 1:1 parity. Windows delivers real IR frames while observable standard CSID/VFE blocks stay in their inactive/default state and a started protected SecureISP device is present.',
 'secure_internal_route_proven':False,
}
OUT.write_text(json.dumps(summary,indent=2)+'\n')
print('E004Y_EXTRACT=PASS')
print('E004Y_REAL_IR_FRAMES=12 START=SUCCESS STOP=SUCCESS')
print('E004Y_STANDARD_CAMSS=INACTIVE LIVE1_EQUALS_LIVE2=YES')
print('E004Y_WRAPPER=CSID0:1 CSID1:1 CSID2:1 OUTPUT_IFE_EN=NO')
print('E004Y_CSID0_1_2=BYTE_EXACT_WINDOWS_INACTIVE_DEFAULT')
print('E004Y_VFE0_1=ALL_ZERO')
print('E004Y_SECUREISP=QCOM0CCC 0xACCA000..0xACCDFFF STARTED KD_READABLE=NO')
