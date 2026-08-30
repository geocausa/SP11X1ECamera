#!/usr/bin/env python3
import hashlib,json,re
from pathlib import Path
REPO=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
P42=REPO/'experiments/E003-front-imx681-cphy/e003h-csid1-ipp-start-parity-candidate'
P44=REPO/'experiments/E003-front-imx681-cphy/e003h-csid1-common-lifecycle-0044-candidate'
P45=REPO/'experiments/E003-front-imx681-cphy/e003h-ife-startup-base-wrapper-0045-candidate'
EXPECTED={
 'run':'aef7acf30e924b880b03403e266db9aee002c7bb522f78277c0921e3541b4626',
 'post':'635ce37d3d582f15d143cc6eaf3ca53d2a8346fc655a93f0de68ca2c5dc7893b',
 'dmesg':'69f50865fa51bd996956ad93c294c947cee453409add6f1b3d66b31cbb3d9ee6',
 'stages':'a515ed7828833f35cdf20261af85cd6f6627b4338e8eab3d856bfb52fce82882',
 'pre':'8faa7bd2569d9ad8372be47e95b9caf50bb75c9e3e8d760dfe55b9ec9f47e88f',
 'load':'667728d5d4ab48d62f1928e920265a5e3025749d4c287581983c557fb801adde',
 'auth':'75870317b1bae8fe5ac74b0e766bdf86628ea9732d78ffe98048771ff8d68e29',
 'golden':'d416e8b727128a213df28a59658430e47349b94e24e532c87e2d9fa8e8d0cb32',
}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
def timeout(p):
    t=Path(p).read_text(errors='replace')
    ls=[x for x in t.splitlines() if 'CSID1 epoch0-timeout' in x]
    if len(ls)!=4: die(f'{p}: expected four timeout lines got {len(ls)}')
    b='\n'.join(ls)
    def one(pat,n):
        m=re.search(pat,b)
        if not m: die(f'{p}: missing {n}')
        return m.groups() if len(m.groups())>1 else m.group(1)
    return {
      'route':one(r'route=([0-9a-f]{8})','route'), 'regupd':one(r'regupd=([0-9a-f]{8})','regupd'),
      'top':one(r'top=([0-9a-f]{8})/([0-9a-f]{8})','top'), 'buf':one(r'buf=([0-9a-f]{8})/([0-9a-f]{8})','buf'),
      'rx':one(r'rx=([0-9a-f]{8})/([0-9a-f]{8})','rx'), 'cfg_rx':one(r'cfg=([0-9a-f]{8})/([0-9a-f]{8}) pkts','cfg_rx'),
      'pkts':one(r'pkts=([0-9a-f]{8})','pkts'), 'ecc':one(r'ecc=([0-9a-f]{8})','ecc'), 'crc':one(r'crc=([0-9a-f]{8})','crc'),
      'ipp':one(r'ipp=([0-9a-f]{8})/([0-9a-f]{8})','ipp'), 'ctrl':one(r'ctrl=([0-9a-f]{8})','ctrl'),
      'cfg_ipp':one(r'cfg=([0-9a-f]{8})/([0-9a-f]{8}) z324','cfg_ipp'), 'z324':one(r'z324=([0-9a-f]{8})','z324'),
      'z330':one(r'z330=([0-9a-f]{8})','z330'), 'epoch':one(r'epoch=([0-9a-f]{8})','epoch'),
      'crop':one(r'crop=([0-9a-f]{8})/([0-9a-f]{8})','crop'),
      'drop':one(r'drop=([0-9a-f]{8})/([0-9a-f]{8})/([0-9a-f]{8})/([0-9a-f]{8})/([0-9a-f]{8})/([0-9a-f]{8})','drop'),
      'measure':one(r'measure=([0-9a-f]{8})/([0-9a-f]{8})','measure'),
      'obs':one(r'obs=([0-9a-f]{8})/([0-9a-f]{8})/([0-9a-f]{8})','obs'),
    }
def main():
    files={
      'run':P45/'RUNTIME-IFE-BASE-0045-RUN.txt','post':P45/'RUNTIME-IFE-BASE-0045-POST.txt',
      'dmesg':P45/'RUNTIME-IFE-BASE-0045-DMESG.txt','stages':P45/'RUNTIME-IFE-BASE-0045-RTCDM-STAGES.txt',
      'pre':P45/'RUNTIME-IFE-BASE-0045-PRE-RUN.txt','load':P45/'RUNTIME-IFE-BASE-0045-LOAD.txt',
      'auth':P45/'AUTHORIZATION-CONSUMED.json','golden':P45/'RUNTIME-IFE-BASE-0045-GOLDEN-RETURN.txt'}
    for k,p in files.items():
        if not p.is_file(): die(f'missing {p}')
        got=sha(p)
        if got!=EXPECTED[k]: die(f'{k} hash drift {got} != {EXPECTED[k]}')
    run=files['run'].read_text(); post=files['post'].read_text(); stages=files['stages'].read_text(); d45=files['dmesg'].read_text(errors='replace'); golden=files['golden'].read_text()
    for s in ('HELPER_INVOCATION_COUNT=1','RUN_RC=1','write trigger: Connection timed out'):
        if s not in run: die('run missing '+s)
    for s in ('QC10C_OUTPUT=absent','SENSOR_PM=suspended','CAMSS_PM=suspended','fifo_seq=17','faulted=0'):
        if s not in post: die('post missing '+s)
    if 'MODE_SELECT=1 front transmission started' not in d45 or 'MODE_SELECT=0 front transmission stopped' not in d45: die('sensor lifecycle missing')
    if any(x in d45 for x in ('WARNING:', 'BUG:', 'Oops:', 'SError:', 'Kernel panic')): die('kernel warning/fault in 0045 evidence')
    if 'fifo_seq=17' not in stages or 'name=stopped' not in stages: die('RT-CDM final stage evidence incomplete')
    if 'KERNEL=7.1.5-sp11-render-parity-v4+' not in golden or 'saved_entry=sp11-audio-fullio-v19c' not in golden or 'next_entry=' not in golden: die('Golden boot identity missing')
    for s in ('MODULE_qcom_camss=absent','MODULE_imx681=absent','MODULE_ov13858=absent','GENERAL.STATE:100 (connected)','List of PLAYBACK Hardware Devices','List of CAPTURE Hardware Devices','Touchpad'):
        if s not in golden: die('Golden health missing '+s)
    t42=timeout(P42/'RUNTIME-CSID1-0042-DMESG.txt'); t44=timeout(P44/'RUNTIME-CSID1-0044-DMESG.txt'); t45=timeout(files['dmesg'])
    stable=('route','regupd','top','rx','cfg_rx','pkts','ecc','crc','ipp','ctrl','cfg_ipp','z324','z330','epoch','crop','drop','measure')
    diffs={k:[t42[k],t44[k],t45[k]] for k in stable if not (t42[k]==t44[k]==t45[k])}
    if diffs: die('stable CSID timeout state drift: '+repr(diffs))
    if t42['buf'] != ('00000000','0001ffff') or t44['buf'] != ('00000000','00000001') or t45['buf'] != ('00000000','0001ffff'):
        die('BUF_DONE differential drift')
    if t45['pkts']!='00009098' or int(t45['pkts'],16)!=37016 or t45['ecc']!='00000000' or t45['crc']!='00000000': die('CSI ingress boundary drift')
    if t45['ipp'] != ('00011e00','3cbc601c'): die('IPP boundary drift')
    out={
      'schema':'sp11-e003h-ife-startup-base-0045-runtime-result-v1','accepted':True,'date':'2026-08-30',
      'authorization_sha256':EXPECTED['auth'],'helper_invocations':1,'same_boot_retry':False,
      'run_result':'ETIMEDOUT waiting VFE1 raw Epoch0; no QC10C output','qc10c_output':False,
      'rtcdm':{'fifo_bl_completed':17,'baseline_0044_fifo_bl_completed':13,'added_startup_wrapper_bls_completed':4,'faulted':False,'final_stage':'stopped'},
      'sensor':{'stream_on_seen':True,'stream_off_seen':True,'post_runtime_status':'suspended'},
      'camss_post_runtime_status':'suspended','golden_return_verified':True,
      'csid1_timeout':{'packets':37016,'ecc_errors':0,'crc_errors':0,'ipp_irq_status':'0x00011e00','ipp_irq_mask':'0x3cbc601c','ctrl':'0x1','cfg0':'0x802b2000','cfg1':'0x00007241','buf_done_mask':'0x0001ffff'},
      'comparison':{
        'stable_0042_0044_0045_fields_identical':True,'stable_fields_compared':list(stable),
        '0044_buf_done_mask':'0x00000001','0045_buf_done_mask':'0x0001ffff','windows_and_0042_buf_done_mask':'0x0001ffff',
        'startup_wrapper_repairs_buf_done_clobber':True,
        'readback_0x398_0x39c_excluded_as_configuration':True,
        'readback_reason':'same-machine Windows static oracle classifies +0x398/+0x39c as timestamp/readback state; +0x398 varies between live passes'
      },
      'conclusions':[
        'The four Linux-owned 0x0800f000 startup wrappers execute successfully and increase the completed RT-CDM FIFO count from 13 to 17 without a fault.',
        'The wrapper restores CSID1 BUF_DONE_IRQ_MASK from the malformed 0043/0044 value 0x00000001 to the Windows/0042 value 0x0001ffff, proving the missing startup CHANGE_BASE caused that clobber.',
        'Despite corrected startup base context, CSID1 still receives 37,016 clean packets and remains at IPP_IRQ_STATUS 0x00011e00 with no CAMIF/RUP/Epoch progression; VFE1 raw Epoch0 still never arrives.',
        'Do not add a late CSID BUF_DONE repair write. The remaining blocker is distinct from the base-wrapper bug and should be localized with read-only VFE1 state at the timeout boundary.'
      ],
      'evidence_sha256':{k:EXPECTED[k] for k in ('run','post','dmesg','stages','pre','load','golden')},
      'runtime_authorized':False,
      'next_gate':'Build read-only VFE1 timeout telemetry for exact Windows-owned IRQ masks/status and selected startup/bus configuration registers; no behavior change and no new runtime until statically inspected and separately authorized.'
    }
    p=P45/'runtime-0045-analysis.json'; p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()
