#!/usr/bin/env python3
from pathlib import Path
import importlib.util,json,re,struct,sys,hashlib
HERE=Path(__file__).resolve().parent;BASE=HERE.parent

def load(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
EL=load(HERE/'awb_scalar.py','el_core');F=load(BASE/'f-native-iq-backends/generate-steady-scalar-state.py','el_f')
def need(x,m):
 if not x: raise AssertionError(m)
def fb(h): return struct.unpack('<f',struct.pack('<I',int(h,16)))[0]
def kv(s): return dict(re.findall(r'(\w+)=([0-9A-Fa-f]+)',s))
# 1) Same-request Windows EG differential over R4..R11.
lines=[x.strip() for x in (BASE/'eg-windows-awb-gain-adjust-oracle/ORACLE-PAIRS.txt').read_text().splitlines() if x.strip()]
ga=[kv(x) for x in lines if x.startswith('EG_GA ')]; pub=[kv(x) for x in lines if x.startswith('EG_PUB ')]
need(len(ga)==len(pub)==8,'EG pair count');core=EL.CalibratedAWB();wr=[]
for i,(a,p) in enumerate(zip(ga,pub)):
 rg,bg,lux,cct=[fb(a[k]) for k in ('rg','bg','lux','cct')];o=core.run(rg,bg,lux,cct,1.0)
 got=[EL.bits(o[k]) for k in ('R','G','B')];exp=[int(p[k],16) for k in ('R','G','B')]
 need(o['gain_adjust']['triangle']==int(a['tri']),f'EG R{i+4} triangle state')
 need(got==exp,f'EG R{i+4} gains')
 # Cross-implementation scalar pack against pre-existing F backend.
 fr={};fr.update(F.pdpc(o['G'],o['B'],o['R']));fr.update(F.wb(o['G'],o['B'],o['R'],1.0))
 need(o['registers']==fr,f'F scalar pack R{i+4}')
 wr.append({'request':i+4,'triangle':o['gain_adjust']['triangle'],'gain_bits':[f'0x{x:08x}' for x in got],
            'registers':{f'0x{k:04x}':f'0x{v:08x}' for k,v in sorted(o['registers'].items())}})
# 2) Preserved EA live G1..G6 replay summary, generated from byte-exact archived STATS3A hashes.
ea=json.loads((HERE/'EA-LIVE-REPLAY.json').read_text())
need(ea['source_capture']=='EA_attempt1_pass_20260911T0348','EA source')
need(ea['all_generations_hold_previous'] is True,'EA hold classification')
expected={0x3d78:0x1c80,0x3d7c:0x1efc,0x3d80:0x08fc,0x3d84:0x0843,0x4568:0x08000000,0x456c:0x0f7e0000,0x4570:0x0e400000}
for r in ea['rows']:
 need([int(x,16) for x in r['decision_bits']]==[0x3f1129ca,0x3f00e486],f"EA G{r['generation']} decision")
 o=core.run(fb(r['decision_bits'][0]),fb(r['decision_bits'][1]),fb(r['lux_bits']),fb(r['cct_bits']),1.0)
 need(o['registers']==expected,f"EA G{r['generation']} scalars")
 need({f'0x{k:04x}':f'0x{v:08x}' for k,v in sorted(expected.items())}==r['registers'],f"EA G{r['generation']} summary")
out={'schema':'sp11-e003i-el-calibrated-awb-scalar-join-v1','status':'PASS_OFFLINE_JOIN',
 'windows_gain_differential':'8/8','triangle_state_differential':'8/8','windows_requests':list(range(4,12)),'scalar_pack_crosscheck':'8/8',
 'ea_live_generations_replayed':6,'ea_g1_g6_awb_hold':'6/6','ea_scalar_regression':'7/7 words x 6 generations',
 'predictive_gain_profile':'exact 1.0 normal-preview authority BM/BP','calibration_source':'EJ <- EK Linux physical EEPROM',
 'out_of_mesh_fallback_proven':False,'linux_camera_runtime_performed_by_el':False,'continuous_aec_claimed':False,
 'windows_rows':wr}
(HERE/'RESULT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
