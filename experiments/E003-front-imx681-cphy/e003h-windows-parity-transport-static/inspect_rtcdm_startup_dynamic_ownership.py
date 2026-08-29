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
    for x in ('source','vfe-source','object','module','patch','ownership-oracle','static-proof'):
        ap.add_argument('--'+x,type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True); a=ap.parse_args()
    src=a.source.read_text(); vfe=a.vfe_source.read_text(); patch=a.patch.read_text()
    own=json.loads(a.ownership_oracle.read_text()); proof=json.loads(a.static_proof.read_text())
    if not own.get('accepted') or not proof.get('accepted'): die('oracle/proof not accepted')
    if proof['ownership_oracle_sha256']!=sha(a.ownership_oracle): die('proof/oracle hash mismatch')
    c=own['closure']
    if (c['previous_dynamic_holes'],c['refined_dynamic_holes'],c['dmi_address_holes'],c['total_normalized_holes']) != (20,4,46,50): die('ownership closure drift')
    if not c['dmi_plus_period_only_normalization_equal_across_independent_windows_captures'] or c['qccamisp_0x26838_changes_these_fields']: die('Windows ownership proof drift')

    for x in [
      '#define CAMSS_RTCDM1_CORPUS_DYNAMIC_COUNT\t4',
      '#define CAMSS_RTCDM1_CORPUS_DYNAMIC_VALID\tGENMASK(3, 0)',
      'u32 dynamic[CAMSS_RTCDM1_CORPUS_DYNAMIC_COUNT];',
      'input->dynamic_valid != CAMSS_RTCDM1_CORPUS_DYNAMIC_VALID',
      'Only start-dependent period_cfg values are caller inputs, never template data.',
      'put_unaligned_le32(input->dynamic[i], field);',
      'camss_rtcdm1_corpus_recipe __used = {'
    ]: need(src,x,'source contract drift')

    body=block(src,'camss_rtcdm1_corpus_dynamic')
    got=[(int(p),int(f,16),int(r,16)) for p,f,r in re.findall(r'\.packet = (\d+), \.field = 0x([0-9a-fA-F]+), \.reg = 0x([0-9a-fA-F]+)',body)]
    exp=[(x['packet'],int(x['value_field_offset'],16),0x8c) for x in own['period_fields']]
    if got!=exp or len(got)!=4: die('period-only dynamic table drift')
    if any(r!=0x8c for _,_,r in got): die('non-period register remains caller dynamic')

    # The 16 invariant startup words are template-owned: none of their captured
    # values may be introduced by the 0020 source delta as a kernel constant.
    pl=patch.lower()
    for x in own['startup_template_fields']:
        for key in ('initial_value','final_value'):
            if x[key].lower() in pl: die('0020 freezes startup-template value '+x[key])
    for x in own['period_fields']:
        for key in ('initial_value','final_value'):
            if x[key].lower() in pl: die('0020 freezes captured period value '+x[key])

    if patch.count('--- a/drivers/media/platform/qcom/camss/camss.c')!=1 or patch.count('--- a/')!=1: die('0020 path set drift')
    for bad in ('writel_relaxed(', 'readl_relaxed(', 'enable_irq(', 'disable_irq(',
                'camss_rtcdm1_windows_fifo0_commit(', 'camss_rtcdm1_windows_start(',
                'camss_rtcdm1_windows_open_init(', 'vfe_enable_v2(', 'vfe_buf_done('):
        if bad in patch: die('0020 connects runtime path: '+bad)

    start=vfe.find('vfe_enable_v2(')
    if start<0: die('vfe_enable_v2 missing')
    end=vfe.find('\n}',start)
    if end<0: die('vfe_enable_v2 body end missing')
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

    out={'schema':'sp11-e003h-linux-rtcdm-startup-dynamic-ownership-inspection-v1','accepted':True,
         'source_sha256':sha(a.source),'object_sha256':sha(a.object),'module_sha256':sha(a.module),'patch_sha256':sha(a.patch),
         'ownership_oracle_sha256':sha(a.ownership_oracle),'static_proof_sha256':sha(a.static_proof),
         'dynamic_policy':{'caller_dynamic_values':4,'caller_dynamic_register':'0x8c period_cfg','valid_mask':'0x0000000f',
                           'startup_template_invariant_live_mutable_values':16,'dmi_address_holes':46,'total_template_holes':50},
         'runtime_isolation':{'helper_relocations':hrel,'recipe_relocation_present':False,'mmio_irq_fifo_or_stream_added':False,
                              'pix_stream_gate':'-EOPNOTSUPP before stream lock/IRQ/output'},
         'captured_values_embedded_by_0020':False,'runtime_authorized':False,'fifo0_submission_authorized':False}
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('PASS: 0020 narrows RT-CDM caller dynamics to four period_cfg words; invariant startup words remain template-owned and runtime stays disconnected')

if __name__=='__main__': main()
