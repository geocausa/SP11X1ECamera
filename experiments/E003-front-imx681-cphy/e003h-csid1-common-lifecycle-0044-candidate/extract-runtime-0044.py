#!/usr/bin/env python3
import hashlib,json,re,sys
from pathlib import Path
REPO=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
P42=REPO/'experiments/E003-front-imx681-cphy/e003h-csid1-ipp-start-parity-candidate'
P43=REPO/'experiments/E003-front-imx681-cphy/e003h-csid1-prepare-rup-enable-parity-candidate'
P44=REPO/'experiments/E003-front-imx681-cphy/e003h-csid1-common-lifecycle-0044-candidate'
EXPECTED={
 'run':'bed32b2125dfb914eb1c4c254460d7c8a6d6d9d80a2d505b0a488125e9439212',
 'post':'8e981019a5c182c7d6cc221ebf9eda0f4b4aff2d8ad626d62eef557f2bfdbda6',
 'dmesg':'d848302d307e4b3c36da5fa3766a58721c13f4c2b4c65a0ef3e083fc4dd3f6db',
 'stages':'c1b1da6d3794af1fba6c432cbbc3e6df80089263bdc090daf51f963d7a564ad4',
 'auth':'2bfa23aacf53eb10be780b8b2317fb5e005663f9458b45bd9b7e245ca022eb25',
}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
def timeout(d):
    t=Path(d).read_text(errors='replace')
    lines=[x for x in t.splitlines() if 'CSID1 epoch0-timeout' in x]
    if len(lines)!=4: die(f'{d}: expected four timeout lines got {len(lines)}')
    blob='\n'.join(lines)
    def one(pat,name):
        m=re.search(pat,blob)
        if not m: die(f'{d}: missing {name}')
        return m.groups() if len(m.groups())>1 else m.group(1)
    return {
      'route':one(r'route=([0-9a-f]{8})','route'),
      'regupd':one(r'regupd=([0-9a-f]{8})','regupd'),
      'top':one(r'top=([0-9a-f]{8})/([0-9a-f]{8})','top'),
      'buf':one(r'buf=([0-9a-f]{8})/([0-9a-f]{8})','buf'),
      'rx':one(r'rx=([0-9a-f]{8})/([0-9a-f]{8})','rx'),
      'cfg_rx':one(r'cfg=([0-9a-f]{8})/([0-9a-f]{8}) pkts','cfg_rx'),
      'pkts':one(r'pkts=([0-9a-f]{8})','pkts'),
      'ecc':one(r'ecc=([0-9a-f]{8})','ecc'),
      'crc':one(r'crc=([0-9a-f]{8})','crc'),
      'ipp':one(r'ipp=([0-9a-f]{8})/([0-9a-f]{8})','ipp'),
      'ctrl':one(r'ctrl=([0-9a-f]{8})','ctrl'),
      'cfg_ipp':one(r'cfg=([0-9a-f]{8})/([0-9a-f]{8}) z324','cfg_ipp'),
      'z324':one(r'z324=([0-9a-f]{8})','z324'),'z330':one(r'z330=([0-9a-f]{8})','z330'),
      'epoch':one(r'epoch=([0-9a-f]{8})','epoch'),
      'crop':one(r'crop=([0-9a-f]{8})/([0-9a-f]{8})','crop'),
      'drop':one(r'drop=([0-9a-f]{8})/([0-9a-f]{8})/([0-9a-f]{8})/([0-9a-f]{8})/([0-9a-f]{8})/([0-9a-f]{8})','drop'),
      'measure':one(r'measure=([0-9a-f]{8})/([0-9a-f]{8})','measure'),
      'obs':one(r'obs=([0-9a-f]{8})/([0-9a-f]{8})/([0-9a-f]{8})','obs'),
      'lines':lines,
    }
def main():
    files={'run':P44/'RUNTIME-CSID1-0044-RUN.txt','post':P44/'RUNTIME-CSID1-0044-POST.txt','dmesg':P44/'RUNTIME-CSID1-0044-DMESG.txt','stages':P44/'RUNTIME-CSID1-0044-RTCDM-STAGES.txt','auth':P44/'AUTHORIZATION-BOOT3-CONSUMED.json'}
    for k,p in files.items():
        if not p.is_file(): die(f'missing {p}')
        if sha(p)!=EXPECTED[k]: die(f'{k} hash drift {sha(p)} != {EXPECTED[k]}')
    run=files['run'].read_text(); post=files['post'].read_text(); stages=files['stages'].read_text(); d44=files['dmesg'].read_text(errors='replace')
    for s in ('HELPER_INVOCATION_COUNT=1','RUN_RC=1','write trigger: Connection timed out'):
        if s not in run: die('run missing '+s)
    for s in ('QC10C_OUTPUT=absent','SENSOR_PM=suspended','CAMSS_PM=suspended','fifo_seq=13','faulted=0'):
        if s not in post: die('post missing '+s)
    if 'MODE_SELECT=1 front transmission started' not in d44 or 'MODE_SELECT=0 front transmission stopped' not in d44: die('sensor lifecycle missing')
    if 'call_s_stream' in d44 or 'WARNING:' in d44: die('0044 teardown warning unexpectedly present')
    if len(re.findall(r'name=fifo-done',stages)) < 2 or 'fifo_seq=13' not in stages or 'name=stopped' not in stages: die('RT-CDM stage evidence incomplete')
    t42=timeout(P42/'RUNTIME-CSID1-0042-DMESG.txt'); t43=timeout(P43/'RUNTIME-CSID1-0043-DMESG.txt'); t44=timeout(files['dmesg'])
    stable=('route','regupd','top','rx','cfg_rx','pkts','ecc','crc','ipp','ctrl','cfg_ipp','z324','z330','epoch','crop','drop','measure')
    diffs={k:[t42[k],t43[k],t44[k]] for k in stable if not (t42[k]==t43[k]==t44[k])}
    if diffs: die('stable timeout state drift: '+repr(diffs))
    if t42['buf'] != ('00000000','0001ffff'): die('0042 BUF_DONE baseline drift '+repr(t42['buf']))
    if t43['buf'] != ('00000000','00000001') or t44['buf'] != ('00000000','00000001'): die('0043/0044 BUF_DONE drift expectation failed')
    if t44['pkts']!='00009098' or int(t44['pkts'],16)!=37016 or t44['ecc']!='00000000' or t44['crc']!='00000000': die('CSI ingress boundary drift')
    if t44['ipp'] != ('00011e00','3cbc601c'): die('IPP boundary drift')
    out={
      'schema':'sp11-e003h-csid1-0044-runtime-result-v1','accepted':True,'date':'2026-08-30',
      'authorization_sha256':EXPECTED['auth'],'helper_invocations':1,'same_boot_retry':False,
      'run_result':'ETIMEDOUT waiting VFE1 raw Epoch0; no QC10C output','qc10c_output':False,
      'rtcdm':{'pre_csid_fifo_bl_completed':13,'faulted':False,'final_stage':'stopped'},
      'sensor':{'stream_on_seen':True,'stream_off_seen':True,'post_runtime_status':'suspended'},
      'camss_post_runtime_status':'suspended',
      'csid1_timeout':{'packets':37016,'ecc_errors':0,'crc_errors':0,'ipp_irq_status':'0x00011e00','ipp_irq_mask':'0x3cbc601c','ctrl':'0x1','cfg0':'0x802b2000','cfg1':'0x00007241','epoch':'0x00130013'},
      'comparison':{
        '0042_0043_0044_stable_boundary_identical':True,
        'stable_fields_compared':list(stable),
        'volatile_observation_word_excluded':True,
        '0042_buf_done_status_mask':['0x'+x for x in t42['buf']],
        '0043_buf_done_status_mask':['0x'+x for x in t43['buf']],
        '0044_buf_done_status_mask':['0x'+x for x in t44['buf']],
        'buf_done_mask_parity_drift':'Windows/0042 final mask 0x0001ffff; 0043/0044 final mask 0x00000001',
      },
      'conclusions':[
        '0044 exact common reset/config/companion/private-stop lifecycle does not unlock CSID CAMIF/RUP/Epoch or VFE1 Epoch0.',
        'The 0043 teardown-only V4L2 call_s_stream warning is eliminated by 0044 private stop.',
        'Do not repeat 0044 runtime or blindly rewrite BUF_DONE mask late; statically determine why the Windows-builder value 0x0001ffff becomes 0x00000001 in 0043/0044 and whether that transition is a symptom of a broader CSID state/lifecycle mismatch.'
      ],
      'evidence_sha256':{k:EXPECTED[k] for k in ('run','post','dmesg','stages')},
      'runtime_authorized':False,
      'next_gate':'Trace every CPU/RT-CDM/hardware lifecycle effect that can change CSID1 +0x90 after the full builder; compare exact same-machine Windows reset/ISR/start state before proposing any write.'
    }
    outp=P44/'runtime-0044-analysis.json'; outp.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()
