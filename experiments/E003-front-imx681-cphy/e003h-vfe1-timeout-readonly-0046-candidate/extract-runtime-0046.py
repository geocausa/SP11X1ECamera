#!/usr/bin/env python3
import hashlib,json,re
from pathlib import Path

REPO=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
P=REPO/'experiments/E003-front-imx681-cphy/e003h-vfe1-timeout-readonly-0046-candidate'
EXPECTED={
 'run':'6638ecb2aad847764ba5c34719584752537f22e9275a4050d4221b6f07c5efd3',
 'post':'d325970993c758f43b81078fd1f5a1469409c7e248ea25c73b21a2c402987728',
 'dmesg':'14e469dc0e93bef04595f10c4a880febea7e548a66fbc7065d45462e68443621',
 'stages':'ca739d19182d8ea7049fd86a2abf8bed7b8e617d58cd864f2970f6eb39481e81',
 'pre':'04124dd46c9fd9151989590bd1bcf775870ce8c75ba1aa39373102f3b6dd878b',
 'load':'8a62d17165d3cd0c956e4b0a5e8b1a7b3cf5900b7921b2920b7bbf3bec5fb600',
 'media':'e3ef135c67ca08b0cc6445193ee8c32a9b68ebdaa15a45b6c32e3a2557f328d0',
 'golden':'d4ad7bbdb83306c153dd5d6fabf1e24b70df0d3cb611beccda22dfc13553b16f',
 'auth':'f0fc250dbbb3eb83c288515faa0a634eb6f1ccd8bf399d269db7a035d2e99d96',
 'package':'70d9f0b2fdb7e835525c98807151922c113dbf026aaeec3d2445c505e2fd5571',
}
FILES={
 'run':'RUNTIME-VFE1-0046-RUN.txt','post':'RUNTIME-VFE1-0046-POST.txt',
 'dmesg':'RUNTIME-VFE1-0046-DMESG.txt','stages':'RUNTIME-VFE1-0046-RTCDM-STAGES.txt',
 'pre':'RUNTIME-VFE1-0046-PRE-RUN.txt','load':'RUNTIME-VFE1-0046-LOAD.txt',
 'media':'RUNTIME-VFE1-0046-MEDIA.txt','golden':'RUNTIME-VFE1-0046-GOLDEN-RETURN.txt',
 'auth':'AUTHORIZATION-CONSUMED.json','package':'package-inspection.json',
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
 run=(P/FILES['run']).read_text(errors='replace')
 post=(P/FILES['post']).read_text(errors='replace')
 dm=(P/FILES['dmesg']).read_text(errors='replace')
 stages=(P/FILES['stages']).read_text(errors='replace')
 pre=(P/FILES['pre']).read_text(errors='replace')
 golden=(P/FILES['golden']).read_text(errors='replace')
 for s in ('HELPER_INVOCATION_COUNT=1','RUN_RC=1','write trigger: Connection timed out'):
  need(run,s,'run')
 for s in ('QC10C_OUTPUT=absent','SENSOR_PM=suspended','CAMSS_PM=suspended','fifo_seq=17','faulted=0'):
  need(post,s,'post')
 for s in ('Pixel Format      : \'Q10C\'','Width/Height      : 2560/1440','Bytes per Line : 3584','Size Image     : 7778304'):
  need(pre,s,'pre')
 for s in ('MODE_SELECT=1 front transmission started','MODE_SELECT=0 front transmission stopped'):
  need(dm,s,'sensor lifecycle')
 for bad in ('WARNING:','BUG:','Oops:','Kernel panic','SError Interrupt'):
  if bad in dm: die('kernel fault marker '+bad)
 need(stages,'fifo_seq=17','stages'); need(stages,'name=stopped','stages')

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
 if top != ('00000000','00030003','00000000','00000000'): die('VFE top drift '+repr(top))
 if bus != ('00000000','00000000','00000000','00000000'): die('VFE bus drift '+repr(bus))
 if viol != ('00000000','00000000','00000000'): die('VFE bus fault '+repr(viol))
 if marker != ('00000001','00000001','00000001'): die('startup marker drift '+repr(marker))
 exp0=('00000011','ff806000','ff806000','ff800000','ff800000','004f2000','05a00a00','00000e00','0000000b','00000023')
 exp1=('00000011','ffcf5000','ffcf5000','ffcf2000','ffcf2000','00279000','02d00a00','00000e00','0000000b','00000033')
 if f0 != exp0: die('FULL0 drift '+repr(f0))
 if f1 != exp1: die('FULL1 drift '+repr(f1))

 pkts=one(cb,r'pkts=([0-9a-f]{8})','CSID packets')
 ecc=one(cb,r'ecc=([0-9a-f]{8})','CSID ECC'); crc=one(cb,r'crc=([0-9a-f]{8})','CSID CRC')
 ipp=one(cb,r'ipp=([0-9a-f]{8})/([0-9a-f]{8})','CSID IPP')
 buf=one(cb,r'buf=([0-9a-f]{8})/([0-9a-f]{8})','CSID BUF')
 if (pkts,ecc,crc)!=(('00009098'),('00000000'),('00000000')): die('CSI ingress drift')
 if ipp != ('00011e00','3cbc601c'): die('CSID IPP boundary drift '+repr(ipp))
 if buf != ('00000000','0001ffff'): die('CSID BUF mask drift '+repr(buf))

 for s in ('BOOT_IMAGE=/boot/sp11-7.1.5-audio-fullio-v19c/','saved_entry=sp11-audio-fullio-v19c','next_entry=','MODULE_qcom_camss=absent','MODULE_imx681=absent','MODULE_ov13858=absent'):
  need(golden,s,'golden')

 out={
  'schema':'sp11-e003h-vfe1-timeout-0046-runtime-result-v1','accepted':True,'date':'2026-08-30',
  'authorization_sha256':EXPECTED['auth'],'package_inspection_sha256':EXPECTED['package'],
  'helper_invocations':1,'same_boot_retry':False,'run_result':'ETIMEDOUT waiting VFE1 raw Epoch0; no QC10C userspace output',
  'golden_return_verified':True,'qc10c_output':False,
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
  'conclusions':[
   'VFE1 FULL client0/client1 static configuration and Linux-owned image/meta address programming are exact at timeout; all four dynamic FULL address readbacks equal the expected slot-0 IOVAs.',
   'VFE1 reports no BUS write violation, overflow, or image violation, and the three Windows-live-stable startup markers are all 1.',
   'Linux VFE1 TOP/BUS IRQ masks remain 0/0, unlike same-machine Windows TOP mask0 0x0007f051 and BUS mask0 0xd0000000; the private PIX path never performs the Windows DAL_ife_start mask callback.',
   'Same-machine Windows DAL_ife_start also writes VFE TOP +0x24=0 immediately before BUS start, creating a 0x6000 -> 0 -> BUS start -> 0x6000 transition between startup packets1 and2; Linux currently omits that transition.',
   'TOP status1 bit0 (Windows VIDEO event identity) is set while BUS status1 bit21 (Windows Epoch0 identity) is absent. Treat this as an early/spurious VIDEO-state anomaly, not a successful userspace frame: the Windows-proven Epoch0 -> BUS retarget -> replay2 -> VIDEO prefix did not execute and no QC10C buffer was returned.',
   'Do not repeat 0046. Next statically implement the complete Windows VFE start prefix immediately before existing bus_prepare: TOP/BUS mask pairs plus TOP +0x24=0, leaving packet order, CSID, sensor and RT-CDM payloads unchanged.'
  ],
  'evidence_sha256':{k:EXPECTED[k] for k in ('run','post','dmesg','stages','pre','load','media','golden')},
  'runtime_authorized':False,
  'next_gate':'E003h-0047 static VFE1 DAL_ife_start prefix: exact mask pairs and TOP +0x24 zero immediately before existing BUS prepare between startup packet1 and packet2.'
 }
 outp=P/'runtime-0046-analysis.json'; outp.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(json.dumps(out,indent=2,sort_keys=True))

if __name__=='__main__': main()
