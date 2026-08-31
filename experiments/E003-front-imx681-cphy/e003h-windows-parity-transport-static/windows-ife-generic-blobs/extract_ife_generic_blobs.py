#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re, struct
from pathlib import Path

REPO=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
ROOT=Path('/home/geoca/Documents/SP11-PROJECT')
HERE=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/windows-ife-generic-blobs'
STATIC=HERE.parent
RAW=STATIC/'windows-ife-cdm/raw/E003H_IFE_CDM_DMI_FULL_EXACT_20260828.log'
QMEDIA=ROOT/'00-RE-archive/qcom-camera-kernel-KleeUI/include/uapi/camera/media'
BIN=ROOT/'00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys'
KS=ROOT/'02-kernel/sp11-camera-e002k-d-src'
CAMSS=KS/'drivers/media/platform/qcom/camss'
CAMCC=KS/'drivers/clk/qcom/camcc-x1e80100.c'
SENSOR=REPO/'experiments/E003-front-imx681-cphy/e003h-imx681-mode2-parity-0054-static/imx681.c'
BUS=STATIC/'windows-vfe1-bus/vfe1-bus-oracle.json'
RT=REPO/'experiments/E003-front-imx681-cphy/e003h-imx681-mode2-parity-0054-candidate/runtime-0054-analysis.json'
OUT=HERE/'windows-ife-generic-blobs-oracle.json'

EXPECTED={
 'raw':'7555716caa88769aedfbf478c80bd1ff9d14d3fb2512ac368b7f2fb9cb4a17b2',
 'qccamisp':'64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c',
 'cam_isp_h':'b1ff9ff107830d0e2173d66479584a062ca3992a176857f57c6bd212534e5087',
 'cam_defs_h':'534178168e97e52e43b29b48074fd4e0987be8c14884add423691721bae67c2f',
 'cam_cpas_h':'02e4b061dde6e4f0ee33867f5b31eeaaa0f5a198d396c50b7b2d0d3b1bdfc57e',
 'bus_oracle':'126599031f6b8e611f7f9930b2239edbfccbcee2f2d988f47a78b46e5786d927',
 'runtime0054':'a77d1ec6876710ce3d885dcdf3063969558643555b72534f09cef11d6ffd7d6e',
 'camss_c':'c5e01fbf9b4e9ae6c687e1adbbb64e1450a9a677ac2ae15d2b5779ffc3a6a24c',
 'vfe_c':'98474729d5036a4e1770e3ab7d275ccaaba143b22202468e4ad8b93c0cbec2cb',
 'vfe680_c':'0dc6269d8b7c0e57e1442dfea374f0e90bdf14b8e8ef58117a505cda6d643036',
 'camcc_c':'c9d0c54bbfd4de4d27e814a06332c950f23b75dbaac327180a3a245628c01477',
 'sensor_c':'0f05fc8d368456921939f71d96fc3f5ada80f6e62c5275c6bc24a3d7f8083b35',
}
STREAM_SHA=[
 '87fae329e604e001be6b13ffd717da0d4ada0d5c690b439c5786908f557941ff',
 'f2b428ab5f7e192abbc273cf92968672961a42a2ecadd63a775b8a7c70528b7e',
 '8daf514a44d3ae84f341fc323cd5b7f8622f2d188c087eef4be57bafaf0554db',
 'a5859a650913f474499b7f3e9cda59593bf4bc2d1d3c0c473f4c252e2434f1a9',
]
USED=[0xabc,0x8e0,0x8e0,0x8cc]
TYPES=[[10,0,1,17,9,4,6],[9,17],[9,17],[9]]
NAMES={0:'HFR_CONFIG',1:'CLOCK_CONFIG',2:'BW_CONFIG',3:'UBWC_CONFIG',4:'CSID_CLOCK_CONFIG',5:'FE_CONFIG',6:'UBWC_CONFIG_V2',7:'IFE_CORE_CONFIG',8:'VFE_OUT_CONFIG',9:'BW_CONFIG_V2',10:'DISCARD_INITIAL_FRAMES',11:'SENSOR_DIMENSION_CONFIG',12:'CSID_QCFA_CONFIG',13:'SENSOR_BLANKING_CONFIG',14:'TPG_CORE_CONFIG',15:'DYNAMIC_MODE_SWITCH',16:'BW_LIMITER_CFG',17:'FPS_CONFIG',18:'INIT_CONFIG'}
PATHS={0:'IFE_LINEAR',1:'IFE_VID',2:'IFE_DISP',3:'IFE_STATS',4:'IFE_RDI0',5:'IFE_RDI1',6:'IFE_RDI2',7:'IFE_RDI3',8:'IFE_PDAF',9:'IFE_PIXEL_RAW',96:'SFE_NRDI',97:'SFE_RDI0',98:'SFE_RDI1',99:'SFE_RDI2',100:'SFE_RDI3',101:'SFE_RDI4',102:'SFE_STATS'}
USAGE={0:'INVALID',1:'LEFT_PX',2:'RIGHT_PX',3:'RDI',4:'SFE_LEFT',5:'SFE_RIGHT',6:'SFE_RDI'}
OUTRES={0x3000:'FULL',0x3001:'DS4',0x3002:'DS16',0x300c:'TL_BG',0x300e:'AWB_BG',0x300f:'BHIST',0x3010:'RS',0x301c:'AEC_BE'}

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def die(s):raise SystemExit('FAIL: '+s)
def check(p,k):
 g=sha(p)
 if g!=EXPECTED[k]:die(f'{k} hash {g}')
 return g

def extract_streams():
 text=RAW.read_bytes().decode('utf-16',errors='strict'); lines=text.splitlines(); marker='===E003H_DMI_FULL_803==='
 marks=[i for i,l in enumerate(lines) if l==marker]
 if len(marks)!=4:die(f'expected 4 packet markers, got {len(marks)}')
 DD=re.compile(r'^([0-9a-f]{8})`([0-9a-f]{8})\s+((?:[0-9a-f]{8}\s+){3}[0-9a-f]{8})$',re.I)
 DB=re.compile(r'^([0-9a-f]{8})`([0-9a-f]{8})\s+((?:[0-9a-f]{2}\s+){7}[0-9a-f]{2})-((?:[0-9a-f]{2}\s+){7}[0-9a-f]{2})',re.I)
 EV=re.compile(r'Evaluate expression: .* = ([0-9a-f]{8})`([0-9a-f]{8})',re.I)
 out=[]
 for pi,mi in enumerate(marks):
  block=lines[mi:marks[pi+1] if pi+1<len(marks) else len(lines)]; dw={}
  for l in block:
   m=DD.match(l)
   if m:
    a=int(m.group(1)+m.group(2),16)
    for j,v in enumerate(m.group(3).split()):dw[a+4*j]=int(v,16)
  xline=next((l for l in block if l.startswith('x2=')),None)
  if not xline:die(f'packet{pi} x2 absent')
  x2=int(re.search(r'x2=([0-9a-f]+)',xline,re.I).group(1),16); d=x2+0xb4
  try:doff,size,used,typ,meta=[dw[d+o] for o in (8,0xc,0x10,0x14,0x18)]
  except KeyError as e:die(f'packet{pi} descriptor2 dwords incomplete {e}')
  if typ!=9 or meta!=12:die(f'packet{pi} descriptor2 cmd_type/meta_data drift {typ}/{meta}')
  if used!=USED[pi]:die(f'packet{pi} used {used:x}')
  ev=[int(m.group(1)+m.group(2),16) for l in block if (m:=EV.search(l))]
  if len(ev)<2:die(f'packet{pi} mapped desc2 expression absent')
  cpu=ev[1]; buf=bytearray(0x9000); seen=bytearray(0x9000)
  for l in block:
   m=DB.match(l)
   if not m:continue
   a=int(m.group(1)+m.group(2),16)
   if cpu<=a<cpu+0x9000:
    ch=bytes(int(x,16) for x in (m.group(3)+' '+m.group(4)).split()); o=a-cpu
    if o+16>len(buf):die(f'packet{pi} desc2 dump overflow')
    buf[o:o+16]=ch;seen[o:o+16]=b'\1'*16
  if not all(seen):die(f'packet{pi} desc2 dump incomplete {sum(seen)}/{len(seen)}')
  stream=bytes(buf[:used]) # KD expression already resolves allocation base + descriptor offset
  if sha_bytes(stream)!=STREAM_SHA[pi]:die(f'packet{pi} stream sha drift {sha_bytes(stream)}')
  blobs=[];pos=0
  while pos<used:
   if pos+4>used:die(f'packet{pi} truncated generic header')
   h=struct.unpack_from('<I',stream,pos)[0];bt=h&0xff;bsz=h>>8;blk=4+((bsz+3)//4)*4
   if not bsz or pos+blk>used:die(f'packet{pi} invalid blob at {pos:x}')
   payload=stream[pos+4:pos+4+bsz]
   blobs.append({'offset':pos,'type':bt,'name':NAMES.get(bt,'UNKNOWN'),'size':bsz,'payload_sha256':sha_bytes(payload),'payload':payload})
   pos+=blk
  if [b['type'] for b in blobs]!=TYPES[pi]:die(f'packet{pi} type sequence drift {[b["type"] for b in blobs]}')
  out.append({'packet':pi,'descriptor':{'offset':doff,'size':size,'used_length':used,'type':typ,'meta':meta},'stream_sha256':STREAM_SHA[pi],'blobs':blobs})
 return out

def sha_bytes(b):return hashlib.sha256(b).hexdigest()

def decode_hfr(p):
 num,res=struct.unpack_from('<II',p)
 if len(p)!=8+24*num:die('HFR size mismatch')
 ports=[]
 for i in range(num):
  r,sp,sper,fp,fper,rsv=struct.unpack_from('<6I',p,8+24*i)
  ports.append({'resource':hex(r),'name':OUTRES.get(r,'UNKNOWN'),'subsample_pattern':sp,'subsample_period':sper,'framedrop_pattern':fp,'framedrop_period':fper,'reserved':rsv})
 return {'num_ports':num,'reserved':res,'ports':ports}

def decode_clock(p):
 if len(p)!=0x38:die('CLOCK size')
 usage,n=struct.unpack_from('<II',p); left,right=struct.unpack_from('<QQ',p,8); rdi=list(struct.unpack_from('<'+('Q'*n),p,24))
 return {'usage_type':usage,'num_rdi':n,'left_pix_hz':left,'right_pix_hz':right,'rdi_hz':rdi}

def decode_bw(p):
 if len(p)!=0x8c8:die('BW_V2 fixed payload size')
 usage,n=struct.unpack_from('<II',p);fmt='<IIIIQQQQQ';vs=struct.calcsize(fmt)
 if n!=20 or 8+40*vs!=len(p):die('BW_V2 shape')
 votes=[];sums=[0]*5
 for i in range(n):
  u,t,pt,r,*bw=struct.unpack_from(fmt,p,8+i*vs)
  for j,v in enumerate(bw):sums[j]+=v
  votes.append({'index':i,'usage_data':u,'usage_name':USAGE.get(u,str(u)),'transaction':t,'transaction_name':'WRITE' if t==1 else 'READ','path_data_type':pt,'path_name':PATHS.get(pt,str(pt)),'reserved':r,'camnoc_bw':bw[0],'mnoc_ab_bw':bw[1],'mnoc_ib_bw':bw[2],'ddr_ab_bw':bw[3],'ddr_ib_bw':bw[4]})
 tail=p[8+n*vs:]
 if any(tail):die('BW_V2 fixed unused path slots not zero')
 return {'usage_type':usage,'num_paths':n,'votes':votes,'sum':{'camnoc_bw':sums[0],'mnoc_ab_bw':sums[1],'mnoc_ib_bw':sums[2],'ddr_ab_bw':sums[3],'ddr_ib_bw':sums[4]},'unused_fixed_slots':20,'unused_slots_zero':True}

def decode_ubwc(p):
 if len(p)!=0xa8:die('UBWC_V2 size')
 api,n=struct.unpack_from('<II',p)
 if api!=2 or n!=1:die('UBWC_V2 api/ports')
 fields=['port_type','meta_stride','meta_size','meta_offset','packer_config','mode_config_0','mode_config_1','tile_config','h_init','v_init','static_ctrl','ctrl_2','stats_ctrl_2','lossy_threshold_0','lossy_threshold_1','lossy_var_offset','bandwidth_limit','reserved0','reserved1','reserved2']
 planes=[]
 for i in range(2):planes.append(dict(zip(fields,struct.unpack_from('<20I',p,8+i*80))))
 return {'api_version':api,'num_ports':n,'planes':planes}

def main():
 hashes={
  'raw':check(RAW,'raw'),'qccamisp':check(BIN,'qccamisp'),'cam_isp_h':check(QMEDIA/'cam_isp.h','cam_isp_h'),'cam_defs_h':check(QMEDIA/'cam_defs.h','cam_defs_h'),'cam_cpas_h':check(QMEDIA/'cam_cpas.h','cam_cpas_h'),
  'bus_oracle':check(BUS,'bus_oracle'),'runtime0054':check(RT,'runtime0054'),'camss_c':check(CAMSS/'camss.c','camss_c'),'vfe_c':check(CAMSS/'camss-vfe.c','vfe_c'),'vfe680_c':check(CAMSS/'camss-vfe-680.c','vfe680_c'),'camcc_c':check(CAMCC,'camcc_c'),'sensor_c':check(SENSOR,'sensor_c')}
 packets=extract_streams()
 by={}
 for p in packets:
  for b in p['blobs']:
   by.setdefault(b['type'],[]).append((p['packet'],b['payload']))
 if 7 in by:die('unexpected IFE_CORE_CONFIG type7 present')
 hfr=decode_hfr(by[0][0][1]); clock=decode_clock(by[1][0][1]); bw=decode_bw(by[9][0][1]); ubwc=decode_ubwc(by[6][0][1])
 if len(by[9])!=4 or len({sha_bytes(x[1]) for x in by[9]})!=1:die('BW V2 not identical across four startup packets')
 if clock != {'usage_type':0,'num_rdi':4,'left_pix_hz':432000000,'right_pix_hz':0,'rdi_hz':[432000000,0,0,0]}:die('Windows IFE clock decode drift')
 if hfr['num_ports']!=8 or any((x['subsample_pattern'],x['subsample_period'],x['framedrop_pattern'],x['framedrop_period'])!=(1,0,1,0) for x in hfr['ports']):die('HFR contract drift')
 nonzero=[v for v in bw['votes'] if any(v[k] for k in ('camnoc_bw','mnoc_ab_bw','mnoc_ib_bw','ddr_ab_bw','ddr_ib_bw'))]
 if [(v['path_data_type'],v['camnoc_bw'],v['mnoc_ab_bw']) for v in nonzero] != [(0,838800000,118830000),(1,2516400000,1280610770),(3,450000000,450000000)]:die('BW active path drift')
 if bw['sum']!={'camnoc_bw':3805200000,'mnoc_ab_bw':1849440770,'mnoc_ib_bw':1849440770,'ddr_ab_bw':0,'ddr_ib_bw':0}:die('BW sum drift')
 # Linux clock path proof.
 camssc=(CAMSS/'camss.c').read_text();vfec=(CAMSS/'camss-vfe.c').read_text();sens=SENSOR.read_text();v680=(CAMSS/'camss-vfe-680.c').read_text();camcc=CAMCC.read_text()
 for q in ('v4l2_pipeline_pm_get(&req->video[0]->entity)','vfe_get(vfe)'):
  # vfe_get is reached via VFE s_power, not textually in camss.c; below source anchors prove both sides.
  pass
 if 'ret = v4l2_pipeline_pm_get(video_entity);' not in camssc:die('runner pipeline PM ownership drift')
 if 'ret = vfe_get(vfe);' not in vfec or 'ret = vfe_set_clock_rates(vfe);' not in vfec:die('VFE power/clock path drift')
 if '548570000' not in sens:die('mode2 pixel rate drift')
 rates=[345600000,432000000,594000000,675000000,727000000]; margin=548570000*105//100; selected=next(r for r in rates if margin<r)
 if selected!=594000000:die('Linux VFE selection calculation drift')
 if 'F(240000000' not in camcc or 'F(300000000' not in camcc or 'F(400000000' not in camcc:die('X1E CAMNOC RT source table drift')
 if '/* IFE1 */' not in camssc:die('X1E IFE1 resource block absent')
 ife1_block=camssc.split('/* IFE1 */',1)[1].split('/* IFE_LITE_0 */',1)[0]
 if '"camnoc_rt_axi"' not in ife1_block or '.clock_rate = { { 0 },' not in ife1_block:die('CAMSS IFE1 camnoc_rt_axi no-rate representation drift')
 if '.irq_subsample_pattern = 1, .framedrop_pattern = 1' not in v680:die('Linux HFR BUS representation drift')
 bus=json.loads(BUS.read_text()); rt=json.loads(RT.read_text())
 if not bus.get('active_writable_configuration_stable_across_two_passes'):die('BUS final MMIO oracle not stable')
 if not rt['classification']['csid_first_completed_frame_geometry_fixed'] or rt['classification']['vfe1_raw_epoch0_advanced']:die('0054 boundary drift')
 # Strip bytes from public JSON; retain hashes and decodes only.
 pub=[]
 for p in packets:
  pub.append({'packet':p['packet'],'descriptor':p['descriptor'],'stream_sha256':p['stream_sha256'],'blobs':[{k:v for k,v in b.items() if k!='payload'} for b in p['blobs']]})
 fps=[struct.unpack_from('<I',x[1])[0] for x in by[17]]
 csid_clk=struct.unpack_from('<Q',by[4][0][1])[0]
 linux_mnoc_bytes=2097152*1000
 out={
  'schema':'sp11-e003h-windows-ife-generic-blobs-v1','accepted':True,'date':'2026-08-31','runtime_authorized':False,'hashes':hashes,
  'descriptor2':{'cmd_buffer_type':9,'meta_data':12,'meta_name':'CAM_ISP_PACKET_META_GENERIC_BLOB_COMMON','packet_count':4,'packets':pub,'ife_core_config_type7_present':False},
  'decoded':{'hfr':hfr,'clock':clock,'fps_first_u32':fps,'csid_clock_blob_hz':csid_clk,'bandwidth_v2':bw,'ubwc_v2':ubwc},
  'linux_comparison':{
   'hfr_output_subsample_and_framedrop_represented':True,
   'windows_ife_clock_request_hz':432000000,'linux_mode2_vfe_pixel_rate_hz':548570000,'linux_vfe_clock_min_with_margin_hz':margin,'linux_vfe1_selected_rate_hz':selected,'linux_ife_clock_under_voted':False,
   'windows_mnoc_ab_bw_bytes_per_s':bw['sum']['mnoc_ab_bw'],'linux_hf_mnoc_fixed_vote_icc_kbytes_per_s':2097152,'linux_hf_mnoc_equivalent_bytes_per_s':linux_mnoc_bytes,'linux_hf_mnoc_vote_lower_than_windows_mnoc_ab':linux_mnoc_bytes < bw['sum']['mnoc_ab_bw'],
   'windows_camnoc_bw_bytes_per_s':bw['sum']['camnoc_bw'],'x1e_camnoc_rt_available_rates_hz':[240000000,300000000,400000000],'linux_camss_sets_explicit_camnoc_rt_rate':False,
   'applied_camnoc_rt_rate_in_0054_evidence':None,'camnoc_rate_parity_closed':False,
   'ubwc_final_mmio_authority':'accepted two-pass same-machine windows-vfe1-bus oracle; Linux BUS recipe is bound to that final hardware state, not raw portable blob fields',
  },
  'classification':{
   'previous_linux_model_omitted_descriptor2_semantics':True,'descriptor2_contains_ife_core_config':False,'hfr_missing_programming_proven':False,'ubwc_missing_final_bus_programming_proven':False,'ife_clock_underclock_proven':False,'external_mnoc_undervote_proven':False,
   'request_specific_camnoc_bw_semantics_not_represented_by_linux':True,'applied_camnoc_rate_mismatch_proven':False,'causal_link_to_missing_vfe1_epoch0_proven':False,'speculative_camnoc_rate_write_authorized':False,'production_parity_reached':False},
  'next_gate':'Recover or statically prove the applied same-machine Windows CAMNOC RT AXI rate / control-camnoc-axi-clk semantics for the accepted front start, then compare against X1E Linux CAM_CC source behavior. Do not authorize a Linux CAMNOC rate change or new camera runtime from the generic-blob request alone.'}
 OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
