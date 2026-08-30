#!/usr/bin/env python3
import hashlib,json,re
from pathlib import Path
REPO=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
P=REPO/'experiments/E003-front-imx681-cphy/e003h-vfe1-dal-start-prefix-0047-candidate'
P46=REPO/'experiments/E003-front-imx681-cphy/e003h-vfe1-timeout-readonly-0046-candidate'
EXPECTED={
 'run':'9d5cb8d1e67f2cacd794dcbc99a7b4e31c5f15a2219c1ce5064c0062cfffd7d2',
 'post':'c510245c31efc18c3e370a594f64469995e59f8fe3f0b5a8a4a0020ee40ae234',
 'dmesg':'5932b3b68397c4542b85c4eb57c82679c57a095693b78908a07125cfc631e829',
 'stages':'6117c7fda586ec3dff3e6513bc118e26479beafa610805f95c79d059090bb258',
 'pre':'3c99148cdaaf709f0fd64672d14fc1edfa90ed07a97c554572ccf81bbd29611d',
 'load':'0a1be25e490506267ebb4798a48d8d4de82c8ac3822cb069619a0c8d8cfc3985',
 'media':'f15ec70d7447992f718a709349313e75f5825ae9f1e60d3e39125ac83b6673c9',
 'golden':'36246b60a0e80bc18d21651ff87e92d05f0673c7e288076edb8b55475b9ab371',
 'auth':'98d8d7aeaaeddc01b7b8326da54a897b7dda31a233bafb1cb4b5b8cd95e6c91a',
 'package':'498937c1093375c8bb1204e8aed8604e1258cc4531428757b818649d7eaaf509',
 'aborted_stages':'608cc4339aca2cfbd7b35ea3b17ad2f19228f6d50ca405c33c0fc915052566e6',
 'aborted_ready':'3dfa3fb239f56c778a1e9b33eb31328349edd155a95806dac4378904e88527e5',
 'analysis46':'f43b743250a4172c2cebbc1e5f142d2ee7ea9b160b6769c315378060cf802ee7',
}
FILES={
 'run':'RUNTIME-VFE1-0047-RUN.txt','post':'RUNTIME-VFE1-0047-POST.txt',
 'dmesg':'RUNTIME-VFE1-0047-DMESG.txt','stages':'RUNTIME-VFE1-0047-RTCDM-STAGES.txt',
 'pre':'RUNTIME-VFE1-0047-PRE-RUN.txt','load':'RUNTIME-VFE1-0047-LOAD.txt',
 'media':'RUNTIME-VFE1-0047-MEDIA.txt','golden':'RUNTIME-VFE1-0047-GOLDEN-RETURN.txt',
 'auth':'AUTHORIZATION-CONSUMED.json','package':'package-inspection.json',
 'aborted_stages':'RUNTIME-VFE1-0047-OBSERVER-PRELAUNCH-ABORTED-STAGES.txt',
 'aborted_ready':'RUNTIME-VFE1-0047-OBSERVER-PRELAUNCH-ABORTED-READY.txt',
}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
def need(s,sub,name):
    if sub not in s: die(f'{name}: missing {sub!r}')
def one(text,pat,name):
    m=re.search(pat,text)
    if not m: die('missing '+name)
    return m.groups() if len(m.groups())>1 else m.group(1)
def main():
    for k,n in FILES.items():
        p=P/n
        if not p.is_file(): die(f'missing {p}')
        got=sha(p)
        if got!=EXPECTED[k]: die(f'{k} hash drift {got} != {EXPECTED[k]}')
    if sha(P46/'runtime-0046-analysis.json')!=EXPECTED['analysis46']: die('0046 analysis drift')
    a46=json.loads((P46/'runtime-0046-analysis.json').read_text())
    run=(P/FILES['run']).read_text(errors='replace'); post=(P/FILES['post']).read_text(errors='replace')
    dm=(P/FILES['dmesg']).read_text(errors='replace'); stages=(P/FILES['stages']).read_text(errors='replace')
    pre=(P/FILES['pre']).read_text(errors='replace'); load=(P/FILES['load']).read_text(errors='replace')
    media=(P/FILES['media']).read_text(errors='replace'); golden=(P/FILES['golden']).read_text(errors='replace')
    for s in ('HELPER_INVOCATION_COUNT=1','RUN_RC=1','write trigger: Connection timed out'): need(run,s,'run')
    for s in ('QC10C_OUTPUT=absent','SENSOR_PM=suspended','CAMSS_PM=suspended','fifo_seq=17','faulted=0'): need(post,s,'post')
    need(pre,'PASS: 0047 authorization-aware runtime preflight is clean before module load','pre')
    for s in ('PASS: 0047 CAMSS + IMX681 loaded; trigger present and still unused','SENSOR=imx681 5-0010','VIDEO=/dev/video7'): need(load+media,s,'load/media')
    for s in ('msm_csiphy2','msm_csid1','msm_vfe1_pix','msm_vfe1_video3','imx681 5-0010','[ENABLED]','[ENABLED,IMMUTABLE]'): need(media,s,'media')
    for s in ('MODE_SELECT=1 front transmission started','MODE_SELECT=0 front transmission stopped'): need(dm,s,'sensor lifecycle')
    for bad in ('WARNING:','BUG:','Oops:','Kernel panic','SError Interrupt'):
        if bad in dm: die('kernel fault marker '+bad)
    need(stages,'fifo_seq=17','stages'); need(stages,'name=stopped','stages')
    need(golden,'BOOT_IMAGE=/boot/sp11-7.1.5-audio-fullio-v19c/','golden')
    for s in ('saved_entry=sp11-audio-fullio-v19c','next_entry=','qcom_camss=absent','imx681=absent','ov13858=absent','GENERAL.CONNECTION:GEOCA','MultiMedia1 Playback','MultiMedia3 Capture','Microsoft Surface G6 Touch','Touchpad'):
        need(golden,s,'golden')
    vfe=[x for x in dm.splitlines() if 'E003h VFE1 epoch0-timeout' in x]
    csid=[x for x in dm.splitlines() if 'E003h CSID1 epoch0-timeout' in x]
    if len(vfe)!=4: die(f'expected 4 VFE timeout lines, got {len(vfe)}')
    if len(csid)!=4: die(f'expected 4 CSID timeout lines, got {len(csid)}')
    vb='\n'.join(vfe); cb='\n'.join(csid)
    top=one(vb,r'top=([0-9a-f]{8})/([0-9a-f]{8}) mask=([0-9a-f]{8})/([0-9a-f]{8})','VFE top')
    bus=one(vb,r'bus=([0-9a-f]{8})/([0-9a-f]{8}) bmask=([0-9a-f]{8})/([0-9a-f]{8})','VFE bus')
    viol=one(vb,r'viol=([0-9a-f]{8})/([0-9a-f]{8})/([0-9a-f]{8})','VFE violations')
    marker=one(vb,r'marker=([0-9a-f]{8})/([0-9a-f]{8})/([0-9a-f]{8})','VFE markers')
    f0=one(vb,r'full0=([0-9a-f]{8}) addr=([0-9a-f]{8})/([0-9a-f]{8}) meta=([0-9a-f]{8})/([0-9a-f]{8}) incr=([0-9a-f]{8}) cfg0=([0-9a-f]{8}) cfg2=([0-9a-f]{8}) pack=([0-9a-f]{8}) mode=([0-9a-f]{8})','FULL0')
    f1=one(vb,r'full1=([0-9a-f]{8}) addr=([0-9a-f]{8})/([0-9a-f]{8}) meta=([0-9a-f]{8})/([0-9a-f]{8}) incr=([0-9a-f]{8}) cfg0=([0-9a-f]{8}) cfg2=([0-9a-f]{8}) pack=([0-9a-f]{8}) mode=([0-9a-f]{8})','FULL1')
    if top != ('00000000','00030003','0007f051','00000000'): die('VFE top drift '+repr(top))
    if bus != ('00000000','00000000','d0000000','00000000'): die('VFE bus drift '+repr(bus))
    if viol != ('00000000','00000000','00000000'): die('VFE bus fault '+repr(viol))
    if marker != ('00000001','00000001','00000001'): die('startup marker drift '+repr(marker))
    exp0=('00000011','ff806000','ff806000','ff800000','ff800000','004f2000','05a00a00','00000e00','0000000b','00000023')
    exp1=('00000011','ffcf5000','ffcf5000','ffcf2000','ffcf2000','00279000','02d00a00','00000e00','0000000b','00000033')
    if f0!=exp0: die('FULL0 drift '+repr(f0))
    if f1!=exp1: die('FULL1 drift '+repr(f1))
    pkts=one(cb,r'pkts=([0-9a-f]{8})','CSID packets'); ecc=one(cb,r'ecc=([0-9a-f]{8})','CSID ECC'); crc=one(cb,r'crc=([0-9a-f]{8})','CSID CRC')
    ipp=one(cb,r'ipp=([0-9a-f]{8})/([0-9a-f]{8})','CSID IPP'); buf=one(cb,r'buf=([0-9a-f]{8})/([0-9a-f]{8})','CSID BUF')
    if (pkts,ecc,crc)!=('00009098','00000000','00000000'): die('CSI ingress drift')
    if ipp!=('00011e00','3cbc601c'): die('CSID IPP boundary drift '+repr(ipp))
    if buf!=('00000000','0001ffff'): die('CSID BUF mask drift '+repr(buf))
    v46=a46['vfe1_timeout']; c46=a46['csid1_timeout']
    if (v46['top_status1'],v46['bus_status1'],v46['top_mask0'],v46['bus_mask0']) != ('0x00030003','0x00000000','0x00000000','0x00000000'): die('0046 VFE baseline drift')
    if (c46['ipp_irq_status'],c46['packets']) != ('0x00011e00',37016): die('0046 CSID baseline drift')
    out={
      'schema':'sp11-e003h-vfe1-dal-start-0047-runtime-result-v1','accepted':True,'date':'2026-08-30',
      'authorization_sha256':EXPECTED['auth'],'package_inspection_sha256':EXPECTED['package'],
      'helper_invocations':1,'same_boot_retry':False,'run_result':'ETIMEDOUT waiting VFE1 raw Epoch0; no QC10C userspace output',
      'golden_return_verified':True,'qc10c_output':False,
      'observer_relaunch':{'occurred':True,'reason':'initial foreground observer was terminated by orchestration timeout before RUN','initial_capture_preserved':True,'run_observer_ready':True},
      'rtcdm':{'fifo_bl_completed':17,'faulted':False,'final_stage':'stopped'},
      'vfe1_timeout':{
       'top_status0':'0x'+top[0],'top_status1':'0x'+top[1],'top_mask0':'0x'+top[2],'top_mask1':'0x'+top[3],
       'bus_status0':'0x'+bus[0],'bus_status1':'0x'+bus[1],'bus_mask0':'0x'+bus[2],'bus_mask1':'0x'+bus[3],
       'bus_violation':'0x'+viol[0],'bus_overflow':'0x'+viol[1],'bus_image_violation':'0x'+viol[2],
       'startup_markers':['0x'+x for x in marker],
       'full0':{'cfg':'0x'+f0[0],'image_readback':'0x'+f0[1],'image_expected':'0x'+f0[2],'meta_readback':'0x'+f0[3],'meta_expected':'0x'+f0[4],'frame_incr':'0x'+f0[5],'image_cfg0':'0x'+f0[6],'image_cfg2':'0x'+f0[7],'packer':'0x'+f0[8],'mode':'0x'+f0[9]},
       'full1':{'cfg':'0x'+f1[0],'image_readback':'0x'+f1[1],'image_expected':'0x'+f1[2],'meta_readback':'0x'+f1[3],'meta_expected':'0x'+f1[4],'frame_incr':'0x'+f1[5],'image_cfg0':'0x'+f1[6],'image_cfg2':'0x'+f1[7],'packer':'0x'+f1[8],'mode':'0x'+f1[9]},
       'linux_owned_full_addresses_match_expected':True,
       'windows_video_bit_top_status1_bit0_set':bool(int(top[1],16)&1),
       'windows_epoch0_bit_bus_status1_bit21_set':bool(int(bus[1],16)&(1<<21)),
      },
      'csid1_timeout':{'packets':int(pkts,16),'ecc_errors':0,'crc_errors':0,'ipp_irq_status':'0x'+ipp[0],'ipp_irq_mask':'0x'+ipp[1],'buf_done_mask':'0x'+buf[1]},
      'differential_vs_0046':{
       'top_mask0':['0x00000000','0x0007f051'],'bus_mask0':['0x00000000','0xd0000000'],
       'top_status1_unchanged':True,'bus_status1_unchanged':True,'csid_ipp_status_unchanged':True,'csid_packet_count_unchanged':True,
       'full_client_state_unchanged':True,'qc10c_output_unchanged_absent':True,
      },
      'conclusions':[
       '0047 mechanically fixes the VFE1 IRQ-mask parity gap: timeout readback now exactly matches same-machine Windows TOP mask0 0x0007f051/TOP mask1 0 and BUS mask0 0xd0000000/BUS mask1 0.',
       'The failure boundary does not move: raw BUS Epoch0 remains absent, TOP status1 remains 0x00030003 with the early Windows VIDEO identity bit set, and no QC10C userspace buffer is returned.',
       'CSID1 remains byte-for-byte at the prior clean-ingress/no-CAMIF boundary: 37,016 packets, zero ECC/CRC, IPP status 0x00011e00, exact final masks/config, and no CAMIF/RUP/Epoch progression.',
       'Therefore the VFE DAL_ife_start mask/+0x24 prefix was a real parity correction but is not sufficient to unlock CSID CAMIF/VFE Epoch0. Do not repeat 0047.',
       'Next close the remaining Windows first-start lifecycle after BUS start and before sensor-on, focusing on any direct VFE/CSID start callbacks or state transitions not represented by the current packet/callback model; prefer existing same-machine KD/static evidence before another Linux run.'
      ],
      'evidence_sha256':{k:EXPECTED[k] for k in ('run','post','dmesg','stages','pre','load','media','golden','aborted_stages','aborted_ready')},
      'runtime_authorized':False,
      'next_gate':'E003h-Windows first-start post-BUS/pre-sensor lifecycle closure; no further Linux runtime until a new exact parity delta or phase telemetry is statically justified.'
    }
    outp=P/'runtime-0047-analysis.json'; outp.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    (P/'RUNTIME-VFE1-0047-ANALYSIS.log').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()
