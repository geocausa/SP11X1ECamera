#!/usr/bin/env python3
import hashlib, json, struct
from pathlib import Path
ROOT=Path('/home/geoca/Documents/SP11-PROJECT')
REPO=ROOT/'06-camera/SP11X1ECamera'
STATIC=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static'
D=STATIC/'csid1-startup-companion-transport-0053'
CAMSS=ROOT/'02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss/camss.c'
CSID680=ROOT/'02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss/camss-csid-680.c'
CSIDH=ROOT/'02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss/camss-csid.h'
WIN=STATIC/'windows-csid1-ipp-start-oracle.json'
BL=STATIC/'windows-rtcdm-bl-boundaries/windows-rtcdm-bl-boundaries-oracle.json'
DRV=ROOT/'00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys'
EXPECTED={
 'windows_ipp':'01960da41376809d694c6aa2336ecef6ff4c010abfa29e4674b1a68d303c3cda',
 'windows_bl':'6741c46589c6bc976ad87a0aad566088e831c452e41961df309bda40f62dc45f',
 'qccamisp':'64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c',
 'camss':'5a920032e138eee1154c4b9ae1846a445e02fbac3e7626a4245797502e73b793',
 'csid680':'683c0d5c042d3a8f24be211cda7dc02d06befe31e42aeb29fcd14f117397c81c',
 'csidh':'5869c6721ebec550d5d3e21e6503fd1f580ebb1aa0991ea25532cfb12156b46d',
}
P0=[
 0x03000001,0x00000330,0x00000000,
 0x03000002,0x0000037c,0x00000001,0x00000000,
 0x03000002,0x0000035c,0x0eff0000,0x086f0000,
 0x03000002,0x00000384,0x0000001f,0x08700f00,
]
PC=[0x03000002,0x0000035c,0x0eff0000,0x086f0000]
USED_SHA=['1872731eaa3eb2233436029c2658682097c61ebf97e3facf46e31224ee25e2a2']+['45d059ec64587ea4f55eb8df64704520782801418c4a754f512831c7473fb5c7']*3
USED_LEN=[60,16,16,16]
WRITES0=[('0x330','0x00000000'),('0x37c','0x00000001'),('0x380','0x00000000'),('0x35c','0x0eff0000'),('0x360','0x086f0000'),('0x384','0x0000001f'),('0x388','0x08700f00')]
WRITESC=[('0x35c','0x0eff0000'),('0x360','0x086f0000')]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
def pack(words): return b''.join(struct.pack('<I',x) for x in words)
def extract_func(text, name, next_name):
 a=text.index(name); b=text.index(next_name,a); return text[a:b]
def main():
 for k,p in [('windows_ipp',WIN),('windows_bl',BL),('qccamisp',DRV),('camss',CAMSS),('csid680',CSID680),('csidh',CSIDH)]:
  g=sha(p)
  if g!=EXPECTED[k]: die(f'{k} hash drift {g}')
 w=json.loads(WIN.read_text()); bl=json.loads(BL.read_text())
 if not w.get('accepted') or not bl.get('accepted'): die('Windows oracle not accepted')
 if w['source']['sha256']!=EXPECTED['qccamisp'] or bl['driver']['sha256']!=EXPECTED['qccamisp']: die('driver identity drift')
 ps=w['captured_csid1_companion_0x803']['packets']
 if len(ps)!=4: die('Windows companion packet count drift')
 reconstructed=[]
 for i,p in enumerate(ps):
  if p['descriptor']['type']!=18: die(f'packet{i} descriptor type drift')
  if p['descriptor']['used_length']!=USED_LEN[i]: die(f'packet{i} used length drift')
  if p['used_sha256']!=USED_SHA[i]: die(f'packet{i} oracle SHA drift')
  words=P0 if i==0 else PC
  got=hashlib.sha256(pack(words)).hexdigest()
  if got!=USED_SHA[i]: die(f'packet{i} reconstructed byte SHA drift {got}')
  want=WRITES0 if i==0 else WRITESC
  got_w=[(x['register_offset'],x['value']) for x in p['writes']]
  if got_w!=want: die(f'packet{i} writes drift {got_w!r}')
  reconstructed.append({'packet':i,'bytes':len(pack(words)),'sha256':got,'words':[f'0x{x:08x}' for x in words]})
 if bl['physical_crosscheck']['csid1_change_base']!='0x00057000': die('CSID1 change-base drift')
 if bl['physical_crosscheck']['csid1_physical']!='0x0acb9000': die('CSID1 physical drift')
 if bl['qccamisp_static_commit']['function_rva']!='0x28480': die('RT-CDM submit function drift')
 if not bl['first_start_pre_enable']['adjacent_0x0803c000_submitted'] is False: die('BL boundary correction drift')
 cam=CAMSS.read_text(); cs=CSID680.read_text(); ch=CSIDH.read_text()
 run=extract_func(cam,'static int camss_x1e_pix_runner_once','static int camss_x1e_pix_trigger_buffer')
 startup=extract_func(cam,'static int camss_x1e_pix_submit_startup','static int camss_x1e_pix_submit_prime')
 if run.count('csid680_x1e_front_ipp_companion(csid,')!=4: die('Linux CPU companion call count drift')
 if startup.count('camss_rtcdm1_windows_fifo0_commit')!=2: die('Linux startup RT-CDM commit count drift')
 for q in ('wrapper->bl_dma[packet]','corpus->packet_dma[packet]'):
  if q not in startup: die('Linux startup submit path drift '+q)
 if '0x08057000' in startup or '0x00057000' in startup: die('Linux startup already changes to CSID1')
 if 'int csid680_x1e_front_ipp_companion' not in cs or 'int csid680_x1e_front_ipp_companion' not in ch: die('CPU companion helper missing')
 comp=extract_func(cs,'int csid680_x1e_front_ipp_companion','int csid680_x1e_front_ipp_enable')
 for q in ('writel(SP11_IPP_HCROP_MODE0','writel(SP11_IPP_VCROP_MODE0','CSID_IPP_FORMAT_MEASURE_CFG0','CSID_IPP_FORMAT_MEASURE_CFG1'):
  if q not in comp: die('CPU companion helper behavior drift '+q)
 # Existing priming materializer proves the Linux-owned CDM encoding/submit machinery already exists.
 for q in ('0x08057000','0x03000002, 0x0000035c, 0x0eff0000, 0x086f0000','0x03000001, 0x00000330, 0x00000000'):
  if q not in cam: die('existing CDM companion materializer evidence missing '+q)
 out={
  'schema':'sp11-e003h-csid1-startup-companion-transport-0053-oracle-v1','accepted':True,
  'evidence_sha256':EXPECTED,
  'windows':{
   'device':'same SP11 X1E80100','csid1_change_base':'0x00057000','csid1_physical':'0x0acb9000',
   'companion_descriptor_type':'0x12','packet_count':4,'reconstructed_packets':reconstructed,
   'transport':'RT-CDM FIFO0 block-list submission after CHANGE_BASE(CSID1)',
   'register_values_changed_by_0053':False,
  },
  'linux_0052_baseline':{
   'startup_rtcdm_commits_per_packet':2,
   'startup_rtcdm_sequence':['CHANGE_BASE(VFE1)','IFE startup main'],
   'startup_csid_companion_transport':'CPU MMIO via csid680_x1e_front_ipp_companion()',
   'cpu_companion_calls':4,
   'same_companion_values_already_materializable_as_cdm':True,
  },
  'classification':{
   'transport_ownership_mismatch_proven':True,
   'register_value_mismatch_proven':False,
   'host_order_mismatch_proven':False,
   'active_shadow_latch_causality_proven':False,
   'crop_failure_causality_proven':False,
   '0053_static_delta_justified':True,
   'reason':'restore the exact captured Windows owner/transport for the already-proven startup CSID companion command bytes without introducing a new register or value',
  },
  'allowed_0053_delta':[
   'materialize exact captured packet0 and packet1..3 CSID companion CDM bytes in Linux-owned coherent DMA',
   'after each startup VFE main BL, submit CHANGE_BASE 0x08057000 then the exact matching CSID companion BL through the existing RT-CDM FIFO0 commit path',
   'remove the four startup-path calls that replay those companion writes through CPU MMIO',
  ],
  'forbidden_0053_delta':[
   'new CSID register values','new crop coordinates','new RUP/AUP value','new LUT/bank write','new sensor/CSIPHY/VFE programming','runtime authorization','same-machine hardware execution',
  ],
  'runtime_authorized':False,
  'next_gate':'implement the static transport-only delta, build qcom-camss.ko, strict-checkpatch and fail-closed inspect; no runtime/package authorization until that checkpoint is public'
 }
 blob=json.dumps(out,indent=2,sort_keys=True)+'\n'
 (D/'startup-companion-transport-0053-oracle.json').write_text(blob)
 (D/'EXTRACT.txt').write_text(blob)
 md='''# E003h 0053 startup CSID companion transport oracle\n\nThe same-machine Windows descriptor-1 companion bytes are now reconstructed and hash-verified exactly: packet0 is 60 bytes and packets1..3 are 16 bytes each. Windows submits them to CSID1 through RT-CDM after `CHANGE_BASE 0x00057000`; current Linux 0052 instead submits only the VFE startup base/main through RT-CDM and then applies the matching CSID companion values through CPU `writel()` calls.\n\nThis proves a **transport/ownership mismatch**, not causality. Register values and host order already match; no claim is made that RT-CDM transport is the crop fix. The only justified 0053 experiment is to preserve the exact Windows CDM transport for these already-proven bytes and remove the four startup CPU-companion calls. Runtime remains unauthorized.\n'''
 (D/'README.md').write_text(md)
 print(blob,end='')
if __name__=='__main__': main()
