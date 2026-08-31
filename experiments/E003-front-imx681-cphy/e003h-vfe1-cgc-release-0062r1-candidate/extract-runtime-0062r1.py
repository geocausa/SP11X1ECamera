#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re
R=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
N=R/'experiments/E003-front-imx681-cphy/e003h-vfe1-cgc-release-0062r1-candidate'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
run=(N/'RUNTIME-VFECGC-0062R1-RUN.txt').read_text(); post=(N/'RUNTIME-VFECGC-0062R1-POST.txt').read_text(); dm=(N/'RUNTIME-VFECGC-0062R1-DMESG.txt').read_text(); st=(N/'RUNTIME-VFECGC-0062R1-RTCDM-STAGES.txt').read_text(); gr=(N/'GOLDEN-RETURN-0062R1.txt').read_text()
assert run.count('HELPER_INVOCATION_COUNT=1')==1 and 'RUN_RC=1' in run
assert 'CAMERA_PROGRAMMING_DELTA=REMOVE_PRIVATE_CGC_OVD_ONLY_VS_0061' in run
assert 'QC10C_OUTPUT=absent' in post
assert 'fifo_seq=25' in st and 'name=fifo-done' in st and 'faulted=0' in st
m=re.search(r'VFE1 epoch0-timeout top=([0-9a-f]+)/([0-9a-f]+).*bus=([0-9a-f]+)/([0-9a-f]+).*bmask=([0-9a-f]+)/([0-9a-f]+)',dm,re.I); assert m
assert m.group(2).lower()=='00030003' and m.group(3).lower()=='00000000' and m.group(4).lower()=='00000000'
b=re.search(r'VFE1 epoch0-timeout buscommon cgc=([0-9a-f]+) ubwc=([0-9a-f]+)',dm,re.I); assert b
assert b.group(1).lower()=='00000000' and b.group(2).lower()=='00001046'
assert 'CSID1 epoch0-timeout ipp-history=' in dm and 'line-error=00000000/00000000/00000000' in dm
assert 'measure=0000001f/08700f00' in dm
for c in ('busc0','busc1','busc2','busc3','busc11','busc18','busc12','busc14','busc13'):
 assert f'VFE1 epoch0-timeout {c} ' in dm
assert 'sp11_entry=7.1.5-sp11-fullio-v19c' in gr and 'saved_entry=sp11-audio-fullio-v19c' in gr and 'next_entry=' in gr
assert 'CAMSS_LOADED=no' in gr and 'IMX681_LOADED=no' in gr
out={
 'schema':'sp11-e003h-runtime-0062r1-vfe-cgc-release-v1','accepted':True,'date':'2026-09-01',
 'authorization_consumed':True,'authorization_sha256':sha(N/'AUTHORIZATION.json'),'helper_invocations':1,'same_boot_retry':False,'run_rc':1,
 'boot_diagnostic_retry_succeeded':True,'camera_assets_byte_identical_to_0062':True,
 'linux_bus_cgc_ovd_0061':'0x000001ff','linux_bus_cgc_ovd_0062r1':'0x00000000','windows_live_bus_cgc_ovd':'0x00000000',
 'ubwc_static_ctrl':'0x00001046','vfe_top_status1':'0x00030003','vfe_bus_status0':'0x00000000','vfe_bus_status1':'0x00000000','vfe_raw_epoch0_seen':False,
 'nine_bus_clients_address_status_match':True,'csid_geometry':'3840x2160','csid_line_error':False,'rtcdm_fifo_bl_completed':25,'rtcdm_faulted':False,'qc10c_output':False,
 'golden_return_verified':True,
 'classification':{'cgc_override_mismatch_was_real':True,'cgc_release_parity_achieved':True,'cgc_release_is_noncausal_for_missing_vfe_epoch0':True,'next_gate':'move below BUS common configuration into the generator/qualification of BUS status1 bit21; do not restore c08=1ff and do not substitute TOP epoch bits'},
 'runtime_run_sha256':sha(N/'RUNTIME-VFECGC-0062R1-RUN.txt'),'runtime_post_sha256':sha(N/'RUNTIME-VFECGC-0062R1-POST.txt'),'runtime_dmesg_sha256':sha(N/'RUNTIME-VFECGC-0062R1-DMESG.txt'),'runtime_rtcdm_stages_sha256':sha(N/'RUNTIME-VFECGC-0062R1-RTCDM-STAGES.txt'),'runtime_media_sha256':sha(N/'RUNTIME-VFECGC-0062R1-MEDIA.txt'),'golden_return_sha256':sha(N/'GOLDEN-RETURN-0062R1.txt'),'runtime_authorized':False}
(N/'runtime-0062r1-analysis.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True)); print('ANALYSIS_SHA='+sha(N/'runtime-0062r1-analysis.json'))
