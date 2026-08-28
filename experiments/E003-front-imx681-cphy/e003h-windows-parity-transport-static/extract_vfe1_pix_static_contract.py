#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
BUS=HERE/'windows-vfe1-bus/vfe1-bus-oracle.json'
LAY=HERE/'vfe1-full-layout/vfe1-full-layout-summary.json'
IRQ=HERE/'windows-vfe1-video-completion-oracle.json'
EXPECTED={
 BUS:'126599031f6b8e611f7f9930b2239edbfccbcee2f2d988f47a78b46e5786d927',
 LAY:'299c1f34d31694fdca1a7811700346e49e22adabd04af6daf74c079bc8a04054',
 IRQ:'c8436846bb73082de504da00d0760280b347cd5b8fbbc5e9702197ed0509573c'}
def die(s): raise SystemExit('FAIL: '+s)
def load(p):
 raw=p.read_bytes(); sha=hashlib.sha256(raw).hexdigest()
 if sha!=EXPECTED[p]: die(f'{p.name} hash {sha}')
 return json.loads(raw),sha
bus,bsha=load(BUS); lay,lsha=load(LAY); irq,isha=load(IRQ)
full=bus['full_qc10c']
if [x['client'] for x in bus['enabled_clients']] != [0,1,2,3,11,12,13,14,18]: die('enabled client set drift')
if bus['inactive_parity_relevant_clients'] != {'PIXEL_RAW':10,'RDI0':24,'RDI1':25,'RDI2':26}: die('inactive path drift')
expect={'width':2560,'height':1440,'stride_bytes':3584,'surface_bytes':0x76b000}
for k,v in expect.items():
 if full[k]!=v: die(f'FULL {k} drift')
if full['offsets'] != {'y_meta':0,'y_data':0x6000,'c_meta':0x4f2000,'c_data':0x4f5000}: die('surface offset drift')
if irq['video_completion']['top_status_word']!='status1' or irq['video_completion']['top_status_bit']!=0 or irq['video_completion']['event_id']!=3: die('completion drift')
if irq['irq_masks']['top_mask0']!='0x0007f051' or irq['irq_masks']['bus_mask0']!='0xd0000000': die('mask drift')
# Exact public VFE680 layout facts used only for structural mapping, pinned to prior reviewed commit.
qstruct={'reference_commit':'0f16924ff6a7f9bb56a7e958016da2ed8a174f2f','full_num_wm':2,'full_wm_idx':[0,1],'full_comp_group':0,
         'ubwc_client0_offsets':{'meta_addr':'0x0e40','meta_cfg':'0x0e44','mode_cfg':'0x0e48','stats_ctrl':'0x0e4c','ctrl_2':'0x0e50','lossy_thresh0':'0x0e54','lossy_thresh1':'0x0e58','lossy_var_offset':'0x0e5c'},
         'ubwc_client1_offsets':{'meta_addr':'0x0f40','meta_cfg':'0x0f44','mode_cfg':'0x0f48','stats_ctrl':'0x0f4c','ctrl_2':'0x0f50','lossy_thresh0':'0x0f54','lossy_thresh1':'0x0f58','lossy_var_offset':'0x0f5c'}}
out={
 'schema':'sp11-e003h-vfe1-pix-qc10c-static-contract-v1','accepted':True,
 'inputs':{'bus_oracle_sha256':bsha,'full_layout_sha256':lsha,'video_completion_sha256':isha},
 'windows':{
  'input':{'csid1_ipp':'3840x2160 RAW10 VC0'},
  'video_output':{'pixelformat':'V4L2_PIX_FMT_QC10C','windows_family':'TP10 UBWC','width':2560,'height':1440,'stride_bytes':3584,'v4l2_memory_planes':1,'internal_regions':4,'surface_bytes':0x76b000,'offsets':full['offsets']},
  'full_clients':{'wm_idx':[0,1],'client0_full_y_static':full['client0_full_y_static'],'client1_full_c_static':full['client1_full_c_static']},
  'aux_clients':{'ds':bus['ds'],'stats':bus['stats']},
  'enabled_clients':[0,1,2,3,11,12,13,14,18],
  'forbidden_as_parity_output':[10,24,25,26],
  'irq':{'top_mask0':irq['irq_masks']['top_mask0'],'bus_mask0':irq['irq_masks']['bus_mask0'],'completion':'TOP status1 bit0 -> event 3 -> IFE VIDEO buf done'}},
 'public_layout_structure_only':qstruct,
 'linux_static_contract':{
  'x1e_nonlite_pix_mbus':'MEDIA_BUS_FMT_SRGGB10_1X10','x1e_nonlite_pix_memory':'V4L2_PIX_FMT_QC10C',
  'qc10c_only_accepted_size':'2560x1440','qc10c_bytesperline':3584,'qc10c_sizeimage':0x76b000,
  'surface_address_derivation':'base + {0,0x6000,0x4f2000,0x4f5000}; reject 32-bit overflow',
  'stream_policy':'reject X1E non-lite PIX stream-on until FULL+DS+stats+IQ/RT-CDM+VIDEO completion are connected as one parity path',
  'rear_policy':'RDI lines and X1E lite instances unchanged'},
 'next_blocker':'compile a fail-closed X1E PIX/QC10C format/surface/two-WM contract without any reachable PIX hardware programming; then integrate exact Windows BUS/aux/IQ state behind a still-blocked gate'}
(HERE/'vfe1-pix-qc10c-static-contract.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True))
print('PASS: VFE1 PIX/QC10C static contract closed from Windows BUS/layout/completion oracles')
