#!/usr/bin/env python3
import argparse, hashlib, json, shutil, subprocess, tempfile
from pathlib import Path

EXPECTED_ORACLE_SHA='d433307f97f97d2a1bdcf27b47fd9010e78b7fbb3ab75dfe78aad78c886cd19d'
EXPECTED_PATCH_SHA='ea0ecd2d3036a1fb735d1f95790518587d4ab8e808d6b989a4ae4ef3248284b9'
EXPECTED_MODULE_SHA='23cc63f742f70ca3f70e25d89b34c9e8cef531ed6f3c9562f2f7b0d3a7ac05a9'
EXPECTED_VERMAGIC='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
EXPECTED_SOURCE={
 'camss-csid-680.c':'1908ae6f07eebfd18623cc5b0ba7c2fd95273b663edcca098f865dd1240b71d2',
 'camss-csid.h':'d42cfeaeceb917f2cc045c1d4aa99818c5fb0ab69b785a955317772363014240',
 'camss.c':'de8d78ad95d538550511be4a5194cff9a5ca7eba438753afaf4ccf1957649112',
}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def die(m): raise SystemExit('FAIL: '+m)
def exactly(text, needle, label):
    n=text.count(needle)
    if n != 1: die(f'{label}: expected 1 occurrence, got {n}')
    return text.index(needle)
def order(text, needles, label):
    pos=[exactly(text,n,f'{label}/{i}') for i,n in enumerate(needles)]
    if pos != sorted(pos): die(label+': ordering drift')

def main():
    here=Path(__file__).resolve().parent
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,default=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src'))
    ap.add_argument('--oracle',type=Path,default=here/'windows-csid1-config-rup-enable-order-oracle.json')
    ap.add_argument('--patch',type=Path,default=here/'0043-x1e-csid1-ipp-prepare-rup-enable-order.patch')
    ap.add_argument('--module',type=Path,default=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss/qcom-camss.ko'))
    ap.add_argument('--build-log',type=Path,default=here/'CAMSS-CSID1-PREP-RUP-ENABLE-BUILD.log')
    ap.add_argument('--checkpatch-log',type=Path,default=here/'CAMSS-CSID1-PREP-RUP-ENABLE-CHECKPATCH.log')
    ap.add_argument('-o','--output',type=Path,default=here/'csid1-prepare-rup-enable-linux-inspection.json')
    a=ap.parse_args()

    if sha(a.oracle)!=EXPECTED_ORACLE_SHA: die('Windows order oracle hash drift')
    o=json.loads(a.oracle.read_text())
    if not o.get('accepted') or o.get('runtime_authorized') is not False: die('oracle acceptance/runtime gate invalid')
    if o['configure_phase']['ctrl']!='0x00000000' or o['configure_phase']['ipp_irq_mask']!='0x3c1c7004': die('configure phase drift')
    if o['rup_aup_phase']['value']!='0x01f501f5': die('RUP/AUP value drift')
    if o['enable_phase']['ctrl_after']!='0x00000001' or o['enable_phase']['ipp_irq_mask_after']!='0x3cbc601c': die('enable phase drift')

    if sha(a.patch)!=EXPECTED_PATCH_SHA: die('0043 patch hash drift')
    patch=a.patch.read_text()
    added=[x[1:] for x in patch.splitlines() if x.startswith('+') and not x.startswith('+++')]
    if any('CSID_REG_UPDATE_CMD' in x and 'writel' in x for x in added): die('0043 adds a new RUP/AUP MMIO write')
    if any('0x01f501f5' in x for x in added): die('0043 duplicates the already-existing RUP/AUP payload')

    d=a.source/'drivers/media/platform/qcom/camss'
    csid=(d/'camss-csid-680.c').read_text(); hdr=(d/'camss-csid.h').read_text(); camss=(d/'camss.c').read_text()
    for f,h in EXPECTED_SOURCE.items():
        if sha(d/f)!=h: die(f'{f} hash drift')

    exactly(csid,'#define SP11_CSID_IPP_IRQ_MASK_PREP_MODE0\t\t\t0x3c1c7004','pre-RUP IPP mask')
    exactly(csid,'#define SP11_CSID_IPP_IRQ_MASK_MODE0\t\t\t\t0x3cbc601c','final IPP mask')
    prepare='int csid680_x1e_front_ipp_prepare(struct csid_device *csid)'
    enable='int csid680_x1e_front_ipp_enable(struct csid_device *csid)'
    p0=exactly(csid,prepare,'prepare helper'); p1=exactly(csid,enable,'enable helper')
    prep=csid[p0:p1]
    if '__csid_ctrl_ipp(csid, true)' in prep: die('prepare helper enables IPP before RUP')
    order(prep,[
        '__csid_configure_top(csid);',
        '__csid_configure_ipp_stream(csid, true)',
        '__csid_configure_rx(csid, &csid->phy, 0);',
        'writel(SP11_CSID_IPP_IRQ_MASK_PREP_MODE0,',
        'writel(SP11_CSID_TOP_IRQ_MASK_MODE0, csid->base + CSID_TOP_IRQ_MASK);',
    ],'prepare order')
    en_end=csid.index('static void csid_configure_stream',p1)
    en=csid[p1:en_end]
    order(en,[
        '__csid_ctrl_ipp(csid, true);',
        'writel(SP11_CSID_IPP_IRQ_MASK_MODE0, csid->base + CSID_IPP_IRQ_MASK);',
        'writel(SP11_CSID_TOP_IRQ_MASK_MODE0, csid->base + CSID_TOP_IRQ_MASK);',
    ],'enable order')
    exactly(hdr,'int csid680_x1e_front_ipp_prepare(struct csid_device *csid);','prepare prototype')
    exactly(hdr,'int csid680_x1e_front_ipp_enable(struct csid_device *csid);','enable prototype')

    # The bounded runner must place prepare before the existing prime1 batch and enable after it.
    runner=camss[camss.index('static int camss_x1e_pix_runner_once'):]
    order(runner,[
        'ret = csid680_x1e_front_ipp_prepare(csid);',
        'ret = camss_x1e_pix_submit_prime(camss, &materialized->prime, 1);',
        'ret = camss_x1e_pix_submit_startup(camss, &materialized->startup, 2);',
        'ret = camss_x1e_pix_submit_startup(camss, &materialized->startup, 3);',
        'ret = csid680_x1e_front_ipp_enable(csid);',
        'ret = camss_x1e_pix_runner_stream(&csiphy->subdev, true);',
        'ret = camss_x1e_pix_runner_stream(req->sensor, true);',
    ],'bounded runner Windows order')
    if 'camss_x1e_pix_runner_stream(&csid->subdev, true)' in runner: die('runner still invokes combined CSID stream-on')
    if runner.count('if (csid_streaming || csid_prepared) {') != 2: die('prepared-state rollback/teardown gate drift')

    # Prove prime materializer still owns the exact Windows RUP/AUP payload; 0043 must only reorder around it.
    exactly(camss,'0x04000001, 0x00000018, 0x01f501f5, 0x06000000,','existing prime RUP/AUP payload')

    if sha(a.module)!=EXPECTED_MODULE_SHA: die('module hash drift')
    modinfo=subprocess.check_output(['modinfo',str(a.module)],text=True)
    vm=next((l.split(':',1)[1].strip() for l in modinfo.splitlines() if l.startswith('vermagic:')),None)
    if vm!=EXPECTED_VERMAGIC: die('vermagic drift')
    cp=a.checkpatch_log.read_text(); bl=a.build_log.read_text()
    if 'total: 0 errors, 0 warnings' not in cp or 'CHECKPATCH_RC=0' not in cp: die('checkpatch not clean')
    if 'BUILD_RC=0' not in bl or EXPECTED_MODULE_SHA not in bl or EXPECTED_VERMAGIC not in bl: die('build provenance drift')

    # Current source must be exactly describable by reversing and re-applying 0043.
    touched=['camss-csid-680.c','camss-csid.h','camss.c']
    with tempfile.TemporaryDirectory(prefix='e003h-0043-roundtrip-') as td:
        t=Path(td)/'drivers/media/platform/qcom/camss'; t.mkdir(parents=True)
        for f in touched: shutil.copy2(d/f,t/f)
        root=Path(td); subprocess.check_call(['git','-C',str(root),'init','-q'])
        subprocess.check_call(['git','-C',str(root),'apply','--check','--reverse',str(a.patch)])
        subprocess.check_call(['git','-C',str(root),'apply','--reverse',str(a.patch)])
        subprocess.check_call(['git','-C',str(root),'apply','--check',str(a.patch)])
        subprocess.check_call(['git','-C',str(root),'apply',str(a.patch)])
        for f in touched:
            if sha(t/f)!=EXPECTED_SOURCE[f]: die('patch roundtrip mismatch '+f)

    out={
      'status':'PASS','schema':'sp11-e003h-linux-csid1-prepare-rup-enable-inspection-v1',
      'windows_oracle_sha256':sha(a.oracle),'patch_sha256':sha(a.patch),
      'module':{'sha256':sha(a.module),'vermagic':vm},
      'proved':{
        'front_mode0_only':True,
        'prepare_ctrl_remains_zero':True,
        'pre_rup_ipp_irq_mask':'0x3c1c7004','pre_rup_top_irq_mask':'0x00000001',
        'existing_prime1_rup_aup':'offset 0x18 = 0x01f501f5',
        'duplicate_rup_aup_added':False,
        'enable_order':['CTRL=1','IPP_IRQ_MASK=0x3cbc601c','TOP_IRQ_MASK=0x1'],
        'runner_order':['prepare','prime1 RUP/AUP','startup2','startup3','enable','CSIPHY','sensor'],
        'rollback_covers_prepared_state':True,
        'patch_roundtrip_byte_identical':True,
      },
      'runtime_authorized':False,
      'next_gate':'Update durable state, commit/push static 0043 checkpoint, then package and separately authorize one bounded diagnostic only if all package/provenance gates remain green.'
    }
    a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__': main()
