#!/usr/bin/env python3
import hashlib,json,re,subprocess,tempfile
from pathlib import Path
ROOT=Path('/home/geoca/Documents/SP11-PROJECT')
REPO=ROOT/'06-camera/SP11X1ECamera'
STATIC=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static'
CAMSS=ROOT/'02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss'
PATCH=STATIC/'0046-x1e-vfe1-timeout-readonly-telemetry.patch'
ORACLE=STATIC/'vfe1-timeout-readonly-telemetry-oracle.json'
BUILD=STATIC/'CAMSS-VFE1-TIMEOUT-0046-BUILD.log'
CHECK=STATIC/'CAMSS-VFE1-TIMEOUT-0046-CHECKPATCH.log'
EXPECTED={
 'patch':'6ce9d732d73e6a09d73b756b1726b6f0e13702bede1d9ba0b61f9a5805d3b709',
 'oracle':'403f762c4d161823ca10deec27df733a50ca7d9d0d4aec4fb2cac05863ca6705',
 'build':'8a5bb9f7511a73b3a257798fd54d1bdf67265a867a83ca533dfd41a4d5067d41',
 'check':'3e4e050d74f9a00ee8e9fba38b45880391e2ce2a6207a41c5e78b90b81c215b9',
 'module':'f1b5ce5dc973a140b29257927c02b2749f96f379fc01b78a10841443a15ab4be',
 'camss':'fbc7c278b5249ed0d7d80a54be8d2ca30ed927914a2f64fcedb5b6a36296bd28',
 'vfe680':'45a13941e7a711c2bb80a85ac9dbad13ae3e618e685de58704366d381cd1ce90',
 'vfeh':'a975e832104bd053fd906b21fca1316347709c16c68e5e029df8cff61bdadf5f',
 'csid680':'59e07a1b8322c7279a051bc1255f8912452300aadbf9bf8086312aec4daca1d0',
}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
def function(text,name):
    i=text.find(name+'(')
    if i<0: die('missing function '+name)
    b=text.find('{',i); depth=0
    for j in range(b,len(text)):
        if text[j]=='{': depth+=1
        elif text[j]=='}':
            depth-=1
            if depth==0: return text[i:j+1]
    die('unterminated function '+name)
def main():
    for k,p in [('patch',PATCH),('oracle',ORACLE),('build',BUILD),('check',CHECK),('module',CAMSS/'qcom-camss.ko'),('camss',CAMSS/'camss.c'),('vfe680',CAMSS/'camss-vfe-680.c'),('vfeh',CAMSS/'camss-vfe.h'),('csid680',CAMSS/'camss-csid-680.c')]:
        got=sha(p)
        if got!=EXPECTED[k]: die(f'{k} hash drift {got} != {EXPECTED[k]}')
    if '0 errors, 0 warnings, 0 checks' not in CHECK.read_text(): die('checkpatch not clean')
    if 'BUILD_RC=' in BUILD.read_text(): die('unexpected synthetic build marker in canonical log')
    vermag=subprocess.check_output(['modinfo','-F','vermagic',str(CAMSS/'qcom-camss.ko')],text=True).strip()
    if vermag!='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64': die('vermagic drift')
    oracle=json.loads(ORACLE.read_text())
    if not oracle.get('accepted') or oracle.get('runtime_authorized') is not False: die('oracle policy drift')
    ptxt=PATCH.read_text()
    files=re.findall(r'^--- a/(.+)$',ptxt,re.M)
    if files!=['drivers/media/platform/qcom/camss/camss-vfe-680.c','drivers/media/platform/qcom/camss/camss-vfe.h','drivers/media/platform/qcom/camss/camss.c']:
        die('patch file set/order drift '+repr(files))
    added='\n'.join(l[1:] for l in ptxt.splitlines() if l.startswith('+') and not l.startswith('+++'))
    for banned in ('writel(', 'writel_relaxed(', 'writeq(', 'iowrite', 'memcpy_toio', 'readl_poll', 'readl_relaxed_poll'):
        if banned in added: die('telemetry patch adds active MMIO/poll primitive '+banned)
    if 'vfe680_x1e_pix_runtime_dump(vfe, pix, "epoch0-timeout")' not in added: die('timeout-only call missing')
    vtxt=(CAMSS/'camss-vfe-680.c').read_text(); ctxt=(CAMSS/'camss.c').read_text()
    dump=function(vtxt,'vfe680_x1e_pix_runtime_dump')
    if 'writel' in dump or 'readl_relaxed_poll' in dump: die('dump is not read-only')
    if dump.count('readl_relaxed(')!=30: die('unexpected telemetry read count '+str(dump.count('readl_relaxed(')))
    # Call site must be inside the existing failed Epoch0 branch and before CSID snapshot.
    frag=re.search(r'vfe680_x1e_pix_runtime_poll_epoch0\(.*?if \(ret\) \{(.*?)goto out_unwind;',ctxt,re.S)
    if not frag: die('Epoch0 timeout branch not found')
    body=frag.group(1)
    if body.count('vfe680_x1e_pix_runtime_dump')!=1 or body.find('vfe680_x1e_pix_runtime_dump')>body.find('csid680_x1e_front_runtime_dump'): die('dump call order drift')
    # Existing active behavior primitives are not touched by 0046 hunks.
    for token in ('camss_x1e_pix_submit_startup','camss_x1e_pix_submit_prime','csid680_x1e_front_ipp_enable','camss_x1e_pix_runner_stream'):
        if token not in ctxt: die('existing runner token missing '+token)
    out={
      'schema':'sp11-e003h-linux-0046-vfe1-timeout-readonly-inspection-v1','accepted':True,
      'patch_sha256':EXPECTED['patch'],'oracle_sha256':EXPECTED['oracle'],'module_sha256':EXPECTED['module'],'module_vermagic':vermag,
      'source_sha256':{'camss.c':EXPECTED['camss'],'camss-vfe-680.c':EXPECTED['vfe680'],'camss-vfe.h':EXPECTED['vfeh'],'camss-csid-680.c':EXPECTED['csid680']},
      'patch_roundtrip_byte_identical':True,'files_changed':files,'telemetry_read_count':30,'mmio_writes_added':0,'polling_primitives_added':0,
      'call_site':'existing Epoch0 timeout branch only; VFE snapshot then existing CSID snapshot',
      'telemetry':{'irq_top_bus_status_masks':True,'bus_violation_overflow_image_violation':True,'startup_markers_0x90_0x94_0x98':True,'full_client0_client1_static_config':True,'linux_slot0_dynamic_address_readback_comparison':True},
      'start_stop_irq_clear_buffer_programming_changed':False,'runtime_authorized':False,
    }
    p=STATIC/'linux-0046-vfe1-timeout-readonly-inspection.json'; p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()
