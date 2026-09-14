#!/usr/bin/env python3
from pathlib import Path
import hashlib,importlib.util,json,os,re,struct,sys
D=Path(__file__).resolve().parent
R=D.parents[2]
SRC=R/'src/front-imx681/userspace/iq'
AUTH=SRC/'authority/authority.json'
os.environ['E003I_IQ_AUTHORITY']=str(AUTH)
MOD=SRC/'vendor/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/fy-calibrated-awb-selector-replay/dynamic_awb.py'

def load(p,n):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;assert s.loader;s.loader.exec_module(m);return m
FY=load(MOD,'e004dm_fy')
def need(v,m):
    if not v: raise AssertionError(m)
def kv(line): return dict(re.findall(r'(\w+)=([0-9A-Fa-f]+)',line))
def fb(h): return struct.unpack('<f',struct.pack('<I',int(h,16)))[0]
def bits(x): return FY.bits(x)

res=json.loads((D/'RESULT.json').read_text())
need(res['status']=='PASS_OFFLINE_WINDOWS_CTRIGLEADJV1_REACHABLE_FALLBACKS_PORTED','result status')
need(hashlib.sha256((D/'fixtures/E004DL-F1-AWB-G1-G21.json').read_bytes()).hexdigest()=='b463aaae86c7c3443b69fe6478f1266615f2572df800d1bc389a9a7688576ad4','fixture hash')

# 1) Production source must preserve every previously accepted Windows AWB oracle.
B=R/'experiments/E003-front-imx681-cphy/e003i-front-native-productionization'
sets=[
 ('EG',B/'eg-windows-awb-gain-adjust-oracle/ORACLE-PAIRS.txt','EG_GA ','EG_PUB ',list(range(4,12))),
 ('FA',B/'fa-windows-r12-awb-gain-adjust-oracle/ORACLE-PAIRS.txt','FA_GA ','FA_PUB ',list(range(4,13))),
 ('FH',B/'fh-recovered-windows-r18-awb-oracle/ORACLE-PAIRS.txt','FA_GA ','FA_PUB ',list(range(4,19))),
 ('FW',Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-fw/windows-r4-r21-20260911/capture/E003I-FW-oracle.log'),'FW_GA ','FW_PUB ',list(range(4,22))),
]
for name,path,gp,pp,reqs in sets:
    lines=path.read_text(errors='replace').replace('\r','').splitlines();ga=[kv(x) for x in lines if x.startswith(gp)];pub=[kv(x) for x in lines if x.startswith(pp)]
    need(len(ga)==len(pub)==len(reqs),f'{name} count');c=FY.DynamicCalibratedAWB()
    for a,p,req in zip(ga,pub,reqs):
        o=c.run(*[fb(a[k]) for k in ('rg','bg','lux','cct')],1.0);z=o['gain_adjust']
        need(z['selection_mode']=='triangle',f'{name} R{req} mode')
        need(z['triangle']==int(a['tri']),f'{name} R{req} triangle')
        need(z['vertices']==[int(a[k]) for k in ('v0','v1','v2')],f'{name} R{req} vertices')
        need([bits(x) for x in z['weights']]==[int(a[k],16) for k in ('w0','w1','w2')],f'{name} R{req} weights')
        need([bits(x) for x in z['cct_rgb']]==[int(a[k],16) for k in ('cctr','cctg','cctb')],f'{name} R{req} CCT')
        need([bits(x) for x in z['final_rgb']]==[int(a[k],16) for k in ('ar','ag','ab')],f'{name} R{req} GA')
        need([bits(o[k]) for k in ('R','G','B')]==[int(p[k],16) for k in ('R','G','B')],f'{name} R{req} publisher')
    print(f'E004dm {name}: {len(reqs)}/{len(reqs)} PASS')

# 2) Replay the compact E004dl F1 decision sequence through the patched production source.
fixture=json.loads((D/'fixtures/E004DL-F1-AWB-G1-G21.json').read_text());c=FY.DynamicCalibratedAWB()
for row in fixture['rows']:
    o=c.run(fb(row['rg_bits']),fb(row['bg_bits']),fb(row['lux_bits']),fb(row['cct_bits']),1.0);z=o['gain_adjust'];g=row['generation']
    need(o['calibration_slot']==row['selector_slot'] and o['calibration_region']==row['selector_region'],f'G{g} selector')
    need(z['selection_mode']==row['selection_mode'],f'G{g} mode {z["selection_mode"]}')
    need(z['triangle']==row['triangle'] and c.core.current_triangle==row['current_triangle'],f'G{g} triangle')
    need([f'0x{bits(o[k]):08x}' for k in ('R','G','B')]==row['published_gain_bits'],f'G{g} gains')
    if g==21:
        need(z['selector_visits']=={4:2,36:3},'G21 visits')
        need([f'0x{bits(x):08x}' for x in z['weights']]==row['weights_bits'],'G21 weights')
        need(z['final_bits']==row['gain_adjust_final_bits'],'G21 GA')
        need(z['actual_mesh_point_bits']==row['actual_mesh_point_bits'],'G21 actual mesh')
        need(z['mesh_point_bits']==row['interpolation_point_bits'],'G21 centroid')
print('E004dm E004dl G1..G21: 21/21 PASS; G21 centroid fallback PASS')

# 3) Reachable ordinary boundary-edge two-vertex path from real profile tuning.
core=FY.EL.CalibratedAWB();core.cal_rg=core.cal_bg=FY.GA.f32(1.0);core.current_triangle=0
out=core.run(fb('0x3f103665'),fb('0x3f3fb49f'),500.0,5000.0,1.0);z=out['gain_adjust']
need(z['selection_mode']=='two_vertex' and z['triangle']==0 and z['selector_return']==255,'boundary mode')
need(z['vertices']==[0,2,-1],'boundary vertices')
need(f'0x{bits(z["weights"][0]):08x}'=='0x3f01fc71','boundary weight')
need([f'0x{bits(out[k]):08x}' for k in ('R','G','B')]==['0x3fe33864','0x3f800000','0x3faaedc6'],'boundary published gains')
print('E004dm ordinary two-vertex boundary: PASS')

# 4) The generic two-boundary corner exists in code but is unreachable in this pinned profile.
counts=[sum(n==255 for n in tr.neighbors) for tr in core.tuning.triangles]
need(len(counts)==44 and counts.count(1)==18 and counts.count(0)==26 and max(counts)==1,'profile boundary topology')
src=(SRC/'vendor/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/el-calibrated-awb-scalar-join/awb_scalar.py').read_text()
need('visits[target]>2' in src and "'mode':'centroid'" in src and "'mode':'two_vertex'" in src,'source fallback markers')
need('awb_selection_mode' in (SRC/'live-iq-producer.py').read_text(),'producer fallback evidence')
print('E004dm topology: 18 one-boundary / 26 interior / no two-boundary triangle PASS')
print('E004dm VERIFY: PASS (all reachable Windows CTrigleAdjV1 paths for pinned IMX681 profile)')
