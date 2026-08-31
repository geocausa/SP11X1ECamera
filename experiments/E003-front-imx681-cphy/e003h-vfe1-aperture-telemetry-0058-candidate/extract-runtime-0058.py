#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
REPO=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera'); NEW=REPO/'experiments/E003-front-imx681-cphy/e003h-vfe1-aperture-telemetry-0058-candidate'; sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
run=(NEW/'RUNTIME-VFEAP-0058-RUN.txt').read_text(); post=(NEW/'RUNTIME-VFEAP-0058-POST.txt').read_text(); dm=(NEW/'RUNTIME-VFEAP-0058-DMESG.txt').read_text(); ap=json.loads((NEW/'RUNTIME-VFEAP-0058-APERTURE.json').read_text())
assert run.count('HELPER_INVOCATION_COUNT=1')==1 and 'RUN_RC=1' in run and 'CAMERA_PROGRAMMING_DELTA=NONE_VS_0057' in run
assert 'fifo_seq=25' in post and 'faulted=0' in post and 'QC10C_OUTPUT=absent' in post and 'VFE_APERTURE_LOG=present' in post
assert 'VFE1 epoch0-timeout top=00000000/00030003 mask=0007f051/00000000 bus=00000000/00000000 bmask=d0000000/00000000' in dm
assert 'ipp-seq[3]=00000ee8/08700f00' in dm and 'line-error=00000000/00000000/00000000' in dm and 'ecc=00000000 crc=00000000' in dm
assert ap['read_only'] is True and ap['base']=='0x0ac71000' and ap['size']==0x4000 and ap['seen_active'] is False and ap['active_samples']==0 and set(bytes.fromhex(ap['snapshots'][0]['hex']))=={0}
files=['AUTHORIZATION.json','RUNTIME-VFEAP-0058-RUN.txt','RUNTIME-VFEAP-0058-POST.txt','RUNTIME-VFEAP-0058-DMESG.txt','RUNTIME-VFEAP-0058-RTCDM-STAGES.txt','RUNTIME-VFEAP-0058-APERTURE.json']
out={'schema':'sp11-e003h-runtime-0058-vfe-aperture-v1','accepted':True,'authorization_consumed':True,'execution':{'helper_invocations':1,'same_boot_retry':False,'run_rc':1,'golden_return_verified':True},'camera':{'camera_programming_delta':'none_vs_0057','rtcdm_fifo_final':25,'rtcdm_faulted':False,'csid_geometry':'3840x2160','csid_line_error':False,'csid_ecc_crc_errors':False,'vfe1_raw_epoch0':False,'qc10c_output':False},'external_aperture':{'base':'0x0ac71000','size':'0x4000','read_only':True,'samples':ap['samples'],'active_samples':0,'seen_active':False,'pre_snapshot_all_zero':True,'dt_vfe1_base_matches_sampler':True,'usable_for_windows_linux_value_comparison':False},'classification':{'external_devmem_transport_captured_live_vfe1':False,'vfe1_physical_address_assumption_wrong':False,'new_programming_write_justified':False,'next_telemetry':'in-driver read-only VFE680 config-cluster reads while timeout path is powered'},'evidence_sha256':{k:sha(NEW/k) for k in files}}
assert out==json.loads((NEW/'runtime-0058-analysis.json').read_text())
print(json.dumps(out,indent=2,sort_keys=True)); print('PASS: 0058 runtime analysis reproduced'); print('ANALYSIS_SHA256='+sha(NEW/'runtime-0058-analysis.json'))
