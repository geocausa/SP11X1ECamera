#!/usr/bin/env python3
import argparse, hashlib, json, re, subprocess
from pathlib import Path

def die(s): raise SystemExit('FAIL: '+s)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(*a): return subprocess.check_output(a,text=True,stderr=subprocess.STDOUT)
def need(s,x,label):
    if x not in s: die(label+': '+x)
def block(src,name):
    m=re.search(rf'{re.escape(name)}\s*\[[^]]+\]\s*=\s*\{{(.*?)\n\}};',src,re.S)
    if not m: die('table missing '+name)
    return m.group(1)

def main():
    ap=argparse.ArgumentParser()
    for x in ('source','vfe-source','object','module','patch','period-contract','static-proof'):
        ap.add_argument('--'+x,type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True); a=ap.parse_args()
    src=a.source.read_text(); vfe=a.vfe_source.read_text(); patch=a.patch.read_text()
    pc=json.loads(a.period_contract.read_text()); proof=json.loads(a.static_proof.read_text())
    if not pc.get('accepted') or not proof.get('accepted'): die('oracle/proof not accepted')
    if proof['period_contract_sha256']!=sha(a.period_contract): die('proof/period contract hash mismatch')
    c=pc['contract']
    if c['logical_values_per_start']!=2 or not c['packets_1_2_3_equal_in_every_observed_start'] or c['qccamisp_0x26838_mutates_period_cfg']:
        die('Windows two-value period contract drift')

    required=[
      '#define CAMSS_RTCDM1_CORPUS_DYNAMIC_VALUE_COUNT\t2',
      '#define CAMSS_RTCDM1_CORPUS_DYNAMIC_PATCH_COUNT\t4',
      '#define CAMSS_RTCDM1_CORPUS_DYNAMIC_VALID\tGENMASK(1, 0)',
      'u32 dynamic[CAMSS_RTCDM1_CORPUS_DYNAMIC_VALUE_COUNT];',
      'input->dynamic_valid != CAMSS_RTCDM1_CORPUS_DYNAMIC_VALID',
      'put_unaligned_le32(input->dynamic[patch->value], field);',
      'camss_rtcdm1_corpus_recipe __used = {'
    ]
    for x in required: need(src,x,'source contract drift')
    body=block(src,'camss_rtcdm1_corpus_dynamic')
    got=[(int(p),int(v),int(f,16),int(r,16)) for p,v,f,r in re.findall(r'\.packet = (\d+), \.value = (\d+), \.field = 0x([0-9a-fA-F]+), \.reg = 0x([0-9a-fA-F]+)',body)]
    exp=[(0,0,0xe84,0x8c),(1,1,0xe24,0x8c),(2,1,0x8f4,0x8c),(3,1,0x4d8,0x8c)]
    if got!=exp: die('period patch/value mapping drift: '+repr(got))

    # 0021 is a relation-only refinement; no observed Windows period literal is allowed.
    pl=patch.lower()
    for rec in pc['observed_starts'].values():
        for val in rec.values():
            if val.lower() in pl: die('0021 freezes captured Windows period value '+val)
    if patch.count('--- a/drivers/media/platform/qcom/camss/camss.c')!=1 or patch.count('--- a/')!=1: die('0021 path set drift')
    for bad in ('writel_relaxed(', 'readl_relaxed(', 'enable_irq(', 'disable_irq(',
                'camss_rtcdm1_windows_fifo0_commit(', 'camss_rtcdm1_windows_start(',
                'camss_rtcdm1_windows_open_init(', 'vfe_enable_v2(', 'vfe_buf_done('):
        if bad in patch: die('0021 connects runtime path: '+bad)

    start=vfe.find('vfe_enable_v2('); end=vfe.find('\n}',start)
    if start<0 or end<0: die('vfe_enable_v2 missing')
    b=vfe[start:end]; gate=b.find('return -EOPNOTSUPP;'); lock=b.find('mutex_lock(&vfe->stream_lock)')
    if gate<0 or lock<0 or gate>=lock: die('PIX fail-close moved after runtime setup')

    rel=run('aarch64-linux-gnu-objdump','-r',str(a.object))
    helpers=['camss_rtcdm1_corpus_materialize','camss_rtcdm1_corpus_release']
    hrel=[ln.strip() for ln in rel.splitlines() if any(x in ln for x in helpers)]
    if len(hrel)!=2 or any('R_AARCH64_ABS64' not in x for x in hrel): die('retained helper relocation drift: '+repr(hrel))
    if 'camss_rtcdm1_corpus_recipe' in rel: die('compiled relocation references private recipe')
    if src.count('camss_rtcdm1_corpus_recipe')!=1: die('private recipe source ref count drift')
    nm=run('aarch64-linux-gnu-nm','-an',str(a.module))
    for x in helpers+['camss_rtcdm1_corpus_recipe']:
        if x not in nm: die('retained symbol missing '+x)
    vermagic=run('modinfo','-F','vermagic',str(a.module)).strip()
    if vermagic!='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64': die('Golden vermagic drift: '+vermagic)

    out={'schema':'sp11-e003h-linux-rtcdm-period-cfg-two-value-contract-inspection-v1','accepted':True,
         'source_sha256':sha(a.source),'object_sha256':sha(a.object),'module_sha256':sha(a.module),'patch_sha256':sha(a.patch),
         'period_contract_sha256':sha(a.period_contract),'static_proof_sha256':sha(a.static_proof),
         'dynamic_policy':{'logical_caller_values':2,'patch_sites':4,'mapping':[0,1,1,1],'caller_dynamic_register':'0x8c period_cfg','valid_mask':'0x00000003'},
         'runtime_isolation':{'helper_relocations':hrel,'recipe_relocation_present':False,'mmio_irq_fifo_or_stream_added':False,'pix_stream_gate':'-EOPNOTSUPP before stream lock/IRQ/output'},
         'captured_period_values_embedded_by_0021':False,'runtime_authorized':False,'fifo0_submission_authorized':False}
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('PASS: 0021 enforces two logical upstream period_cfg values across four packet sites; runtime stays disconnected')
if __name__=='__main__': main()
