#!/usr/bin/env python3
from __future__ import annotations
import base64,hashlib,importlib.util,json,struct,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
REPO=HERE.parents[3]
IQ=REPO/'src/front-imx681/userspace/iq'
V=IQ/'vendor'
ORIG=REPO/'experiments/E003-front-imx681-cphy/e003i-front-native-productionization'
ORIG_PROD=REPO/'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static'
OUT=IQ/'authority/authority.json'

def load(p,n):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;assert s.loader;s.loader.exec_module(m);return m
def sha_bytes(b):return hashlib.sha256(b).hexdigest()
def sha(p):return sha_bytes(Path(p).read_bytes())
def b64(b):return base64.b64encode(bytes(b)).decode('ascii')
def fbits(x):return struct.unpack('<I',struct.pack('<f',float(x)))[0]
def need(v,m):
    if not v: raise RuntimeError(m)

# Require prepared HG cache as the one-time extraction oracle.
marker=V/'local-authority/PREPARED.json';need(marker.is_file(),'run HG prepare-authority-cache.py first')
hgcache=json.loads(marker.read_text());need(hgcache['status']=='PASS','HG cache marker')

# --- Composer/static transport authority ---
E=load(ORIG/'e-template-free-capsule/build-template-free-0076-capsules.py','hh_e')
EM=load(ORIG/'em-r7-r9-template-free-composer/compose-em.py','hh_em')
J=load(ORIG/'j-cleanroom-gtm/generate-cleanroom-gtm-wire.py','hh_j')
_e,variant,main,raw4,slot4,startup,start_payloads,sp,pp=E.static_recipe(REPO)

def base_state(req):
    raw,slot,source=E.raw_request(REPO,req,raw4,slot4)
    values=[[0]*6 for _ in E.MODULES];vmask=[0]*len(E.MODULES)
    for r in variant['dynamic_register_fields']:
        off=int(r['field'],16);ro=int(r['register_offset'],16);mi,si=E.REG_SLOT[ro]
        values[mi][si]=struct.unpack_from('<I',raw,off)[0];vmask[mi]|=1<<si
    pay=[slot[o:o+n] for _,o,n in E.DMI_SOURCE];pmask=[0]*len(E.MODULES)
    for mi,indices in {1:[0],2:[1,2,3],4:[4],5:[5],6:[6],7:[7,8,9],8:[10,11,12,13]}.items():
        for j,_ in enumerate(indices):pmask[mi]|=1<<j
    module=bytearray()
    for i in range(len(E.MODULES)):module+=struct.pack('<BBH6I4x',vmask[i],pmask[i],0,*values[i])
    need(len(module)==0x120,'base module')
    return {'module_b64':b64(module),'payload_b64':[b64(x) for x in pay],'source':source,'module_sha256':sha_bytes(module),'payload_sha256':[sha_bytes(x) for x in pay]}
base5,base6=base_state(5),base_state(6)
ext_base=EM.base_payloads(E,raw4,slot4);gtm,tmc_sha=EM.build_gtm(J)
composer={
 'main_b64':b64(main),'main_sha256':sha_bytes(main),
 'startup_b64':[b64(x) for x in startup],'startup_sha256':[sha_bytes(x) for x in startup],
 'startup_payloads_b64':[b64(x) for x in start_payloads],'startup_payloads_sha256':[sha_bytes(x) for x in start_payloads],
 'startup_period':list(sp),'priming_period':list(pp),
 'dynamic_register_offsets':[int(r['register_offset'],16) for r in variant['dynamic_register_fields']],
 'pmask':{str(k):list(v) for k,v in EM.PMASK.items()},
 'base_states':{'5':base5,'6':base6},
 'extended_base_payloads_b64':[b64(x) for x in ext_base],
 'extended_base_payloads_sha256':[sha_bytes(x) for x in ext_base],
 'gtm_b64':b64(gtm),'gtm_sha256':sha_bytes(gtm),'tmc_dynamic_sha256':tmc_sha,
}

# --- LSC/Tintless authority distilled from the pinned tuning + physical OTP ---
X=load(ORIG/'x-native-live-lsc-deadline/prove-native-live-lsc-deadline.py','hh_x')
M=load(ORIG/'m-stats-only-lsc-request-state/generate-stats-only-front-lsc.py','hh_m')
CL=load(ORIG/'g-cleanroom-lsc-upstream/cleanroom-front-lsc.py','hh_cl')
D=load(ORIG_PROD/'decode_imx681_chromatix.py','hh_dec')
GOLD=load(ORIG_PROD/'prove-lsc-live-golden-authority.py','hh_gold')
blob=X.TUNING.read_bytes();need(sha_bytes(blob)==X.TUNING_SHA,'tuning identity')
h=D.parse_header(blob);recs,_=D.parse_symbol_table(blob,h['sections'][0],h['sections'][1]);obj=h['sections'][1]
leaves={sid:D.data_bytes(blob,obj,recs[sid]) for sid in (0x4b9,0x4bb,0x4bd,0x4bf,0x4c3)}
A,B,golden,otp=X.front_authority(D,CL,GOLD)
need(A==leaves[0x4bd] and B==leaves[0x4bf],'front authority leaf join')
x1,region_sha=M.build_front_x1()
solver=(ORIG/'i-cleanroom-tintless/solver-kernel-quadrant-33x17-f32le.bin').read_bytes()
lsc={
 'leaf_b64':{f'0x{sid:x}':b64(v) for sid,v in leaves.items()},
 'leaf_sha256':{f'0x{sid:x}':sha_bytes(v) for sid,v in leaves.items()},
 'golden_int':[int(v) for v in golden],
 'otp_int_channels':[[int(v) for v in ch] for ch in otp],
 'x1_b64':b64(x1),'x1_sha256':sha_bytes(x1),'tintless23_region_sha256':region_sha,
 'solver_kernel_b64':b64(solver),'solver_kernel_sha256':sha_bytes(solver),
}
need(len(lsc['golden_int'])==884 and sum(len(x) for x in lsc['otp_int_channels'])==884,'LSC calib shape')

# --- AWB/GainAdjust authority as decoded topology/tables; no tuning blob at runtime ---
EF=load(ORIG/'ef-clean-awb-gain-adjust-replay/gain_adjust.py','hh_ef')
FY=load(ORIG/'fy-calibrated-awb-selector-replay/dynamic_awb.py','hh_fy')
t=EF.GainAdjustTuning()
daw=FY.DynamicCalibratedAWB()
def rec3(r):return {'start_bits':f'0x{fbits(r.start):08x}','end_bits':f'0x{fbits(r.end):08x}','value_bits':[f'0x{fbits(v):08x}' for v in r.value]}
awb={
 'enable':int(t.enable),'triangle_count':int(t.triangle_count),'vertex_count':int(t.vertex_count),'outer_count':int(t.outer_count),
 'triangles':[{'v':list(x.v),'neighbors':list(x.neighbors)} for x in t.triangles],
 'vertices':[{'rg_bits':f'0x{fbits(x.rg):08x}','bg_bits':f'0x{fbits(x.bg):08x}','lux':[rec3(r) for r in x.lux]} for x in t.vertices],
 'outer':[{'start_bits':f'0x{fbits(s):08x}','end_bits':f'0x{fbits(e):08x}','table':[rec3(r) for r in tab]} for s,e,tab in t.outer],
 'selector_points_bits':[[f'0x{fbits(a):08x}',f'0x{fbits(b):08x}'] for a,b in daw.selector.points],
 'selector_scales_bits':[[f'0x{fbits(a):08x}',f'0x{fbits(b):08x}'] for a,b in daw.scales],
 'active_reciprocal_bits':[f'0x{fbits(daw.core.cal_rg):08x}',f'0x{fbits(daw.core.cal_bg):08x}'],
 'f_intersection_bits':[f'0x{fbits(x):08x}' for x in daw.selector.f_intersection],
 'f_distance_bits':f'0x{fbits(daw.selector.f_distance):08x}',
 'seed_triangles':[5,19,38,41],
}
need(len(awb['triangles'])==44 and len(awb['vertices'])==32 and len(awb['selector_points_bits'])==10,'AWB shape')

# --- CCT/AGW authority: preserve tiny clean-room tables, not the vendor tuning blob. ---
AC=ORIG/'ac-clean-cct-reconstruction/fixtures'
cct_files=['E003I-AC31-CCTENGINE.bin','E003I-AC31-CCTANCHORS.bin']
cct_files += [f'E003I-AC36-P04-C{ci}.bin' for ci in range(3)]
cct_files += [f'E003I-AC36-P04-C{ci}-R{ri}.bin' for ci in range(3) for ri in range(6)]
cct_files += [f'E003I-AC36-P05-C{ci}.bin' for ci in range(10)]
cct={name:{'b64':b64((AC/name).read_bytes()),'sha256':sha(AC/name),'bytes':(AC/name).stat().st_size} for name in cct_files}

out={
 'schema':'sp11-front-imx681-clean-runtime-authority-v1',
 'status':'PASS_DERIVED_CLEAN_RUNTIME_AUTHORITY',
 'derived_from':{'hg_commit':'44eb147ae2f70a9c16982f96642135657453cbf9','hg_cache_manifest_sha256':hgcache['manifest_sha256'],'front_tuning_sha256':X.TUNING_SHA},
 'composer':composer,'lsc':lsc,'awb':awb,'cct_tables':cct,
 'policy':{'proprietary_tuning_bytes_embedded':False,'raw_windows_log_embedded':False,'raw_request_slots_embedded':False,'runtime_state_is_decoded_or_derived':True,'camera_runtime_performed':False}
}
OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print('HH_AUTHORITY='+str(OUT))
print('HH_AUTHORITY_BYTES='+str(OUT.stat().st_size))
print('HH_AUTHORITY_SHA256='+sha(OUT))
print('HH_COMPOSER_GTM='+composer['gtm_sha256'])
print('HH_LSC_X1='+lsc['x1_sha256'])
print('HH_AWB_TRIANGLES='+str(len(awb['triangles'])))
print('HH_CCT_TABLES='+str(len(cct)))
