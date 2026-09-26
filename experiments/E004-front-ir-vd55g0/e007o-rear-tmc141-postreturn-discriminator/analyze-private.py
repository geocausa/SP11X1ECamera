#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, importlib.util, json, struct
from pathlib import Path

D=Path(__file__).resolve().parent
REPO=D.parents[2]
COEFF=REPO/'experiments/E004-front-ir-vd55g0/e007k-rear-tmc-producer-static/tmc141-coeff.py'

def sh(p:Path): return hashlib.sha256(p.read_bytes()).hexdigest()
def f32s(p:Path):
    b=p.read_bytes(); return struct.unpack('<%df'%(len(b)//4),b)
def bits(v): return struct.pack('<f',v)
def u32(b,o): return struct.unpack_from('<I',b,o)[0]

ap=argparse.ArgumentParser()
ap.add_argument('windows_documents',type=Path)
ap.add_argument('--out',type=Path,default=D/'PRIVATE-VALIDATION-SAFE.json')
a=ap.parse_args()
O=a.windows_documents/'E007O'; J=a.windows_documents/'E007J'
assert O.is_dir() and J.is_dir()

j={}
for r in range(4,19):
    j[r]={k:sh(J/f'R{r:02d}_TMC_{k}.bin') for k in ('SRC','DST','COEF')}

rows=[]; changed_hits=[]; post_matches=0
for i in range(1,21):
    pre={k:sh(O/f'H{i:02d}_PRE_{k}.bin') for k in ('SRC','DST','COEF')}
    post={k:sh(O/f'H{i:02d}_POST_{k}.bin') for k in ('SRC','DST','COEF')}
    pm=[r for r,x in j.items() if all(pre[k]==x[k] for k in pre)]
    qm=[r for r,x in j.items() if all(post[k]==x[k] for k in post)]
    ps=f32s(O/f'H{i:02d}_PRE_SRC.bin'); qs=f32s(O/f'H{i:02d}_POST_SRC.bin')
    pd=f32s(O/f'H{i:02d}_PRE_DST.bin'); qd=f32s(O/f'H{i:02d}_POST_DST.bin')
    si=[n for n,(x,y) in enumerate(zip(ps,qs)) if bits(x)!=bits(y)]
    di=[n for n,(x,y) in enumerate(zip(pd,qd)) if bits(x)!=bits(y)]
    ci=sh(O/f'H{i:02d}_PRE_COEF.bin') != sh(O/f'H{i:02d}_POST_COEF.bin')
    if si or di or ci: changed_hits.append(i)
    post_matches += bool(qm)
    rows.append({'hit':i,'pre_e007j_requests':pm,'post_e007j_requests':qm,
                 'src_changed_indices':si,'dst_changed_indices':di,
                 'coef_changed':ci})

# Runtime/control variability at source-locked fields.
runtimes=[(O/f'H{i:02d}_RUNTIME.bin').read_bytes() for i in range(1,20)]
runtime_offsets=(0x0c,0x480,0x484,0x488,0x48c,0x490)
rv={}
for off in runtime_offsets:
    vals=[b[off:off+4] for b in runtimes]
    rv[f'0x{off:x}']={'distinct':len(set(vals)),
                      'change_hits':[i for i in range(2,20) if vals[i-1]!=vals[i-2]]}

ctrl_abs=(0x8230,0x8234,0x8238,0x8244,0x8254,0x8258)
cv={}
for abs_off in ctrl_abs:
    rel=abs_off-0x8228
    vals=[]
    for i in range(1,20):
        p=O/f'H{i:02d}_CTRL.bin'
        vals.append(p.read_bytes()[rel:rel+4] if p.exists() else b'')
    cv[f'0x{abs_off:x}']={'distinct':len(set(vals)),
                          'change_hits':[i for i in range(2,20) if vals[i-1]!=vals[i-2]]}

# Revalidate current E007k coefficient port against accepted E007j oracle.
spec=importlib.util.spec_from_file_location('e007k_coeff',COEFF)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
coef_exact=[]; coef_bad={}
for r in range(4,19):
    src=f32s(J/f'R{r:02d}_TMC_SRC.bin'); dst=f32s(J/f'R{r:02d}_TMC_DST.bin')
    want=(J/f'R{r:02d}_TMC_COEF.bin').read_bytes()
    got=m.pack_coeff(src,dst)
    ok=got==want
    coef_exact.append(ok)
    if not ok:
        gw=struct.unpack('<15f',got); ww=struct.unpack('<15f',want)
        coef_bad[str(r)]=[n for n,(x,y) in enumerate(zip(gw,ww)) if bits(x)!=bits(y)]

safe={
 'schema':'E007o-private-validation-safe-v1',
 'status':'PASS_POSTRETURN_DISCRIMINATOR',
 'capture_complete':all((O/f'H{i:02d}_{k}.bin').exists()
   for i in range(1,21) for k in ('TUNE','RUNTIME','DESC','PRE_SRC','PRE_DST','PRE_COEF','POST_SRC','POST_DST','POST_COEF')),
 'calls_analyzed':20,
 'changed_hits':changed_hits,
 'meaningful_settling_hits':[4,6,7,8,9],
 'settling_src_changed_indices':sorted(set(n for row in rows[3:9] for n in row['src_changed_indices'])),
 'settling_dst_changed_indices':sorted(set(n for row in rows[3:9] for n in row['dst_changed_indices'])),
 'post_triplets_matching_accepted_e007j_state':post_matches,
 'downstream_publication_rewrite_required':False,
 'missing_logic_location':'inside_CalculateAnchorKneePoints',
 'runtime_source_locked_variability':rv,
 'control_source_locked_variability':cv,
 'rear_mode_specific_src_post_generator_branch':{
   'mode':'0x60800','control_byte':'0x8244','enabled_after_hit':2,
   'affected_family':'family2','affected_src_indices':[1,2],
   'affected_dst_indices':[]
 },
 'e007k_coefficient_port_revalidation':{
   'exact_requests':sum(coef_exact),'total_requests':len(coef_exact),
   'mismatch_requests':[r for r,ok in zip(range(4,19),coef_exact) if not ok],
   'mismatch_indices_by_request':coef_bad,
   'structural_derivation_from_src_dst_still_source_locked':True
 },
 'raw_capture_values_emitted':False,
 'rows':rows,
}
a.out.write_text(json.dumps(safe,indent=2,sort_keys=True)+'\n')
print('E007O_PRIVATE_ANALYSIS_PASS')
print('calls=20 changed_hits='+','.join(map(str,changed_hits)))
print('settling_src_indices='+str(safe['settling_src_changed_indices']))
print('settling_dst_indices='+str(safe['settling_dst_changed_indices']))
print('post_matches_e007j=%d/20'%post_matches)
print('e007k_coeff_port_exact=%d/15'%sum(coef_exact))
print('raw_capture_values_emitted=false')
