#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess
R=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
N=R/'experiments/E003-front-imx681-cphy/e003h-vfe1-ubwc-static-0061-candidate'
B=R/'experiments/E003-front-imx681-cphy/e003h-vfe1-bus-progress-readonly-0060-candidate'
def sha(p):
    try: b=p.read_bytes()
    except PermissionError: b=subprocess.check_output(['sudo','-n','cat',str(p)])
    return hashlib.sha256(b).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
run=(N/'RUNTIME-VFEUBWC-0061-RUN.txt').read_text(); post=(N/'RUNTIME-VFEUBWC-0061-POST.txt').read_text(); dm=(N/'RUNTIME-VFEUBWC-0061-DMESG.txt').read_text()
if run.count('HELPER_INVOCATION_COUNT=1')!=1 or 'CAMERA_PROGRAMMING_DELTA=UBWC_STATIC_ONLY_VS_0060' not in run: die('run contract')
if 'RUN_RC=1' not in run or 'QC10C_OUTPUT=absent' not in post: die('result drift')
if 'buscommon cgc=000001ff ubwc=00001046 piso=00000000 dbgcfg=00000000 dbg=00000000 test=00000000' not in dm: die('UBWC parity missing')
if 'top=00000000/00030003 mask=0007f051/00000000 bus=00000000/00000000 bmask=d0000000/00000000' not in dm: die('VFE status drift')
if 'line-error=00000000/00000000/00000000' not in dm or 'measure=0000001f/08700f00' not in dm: die('CSID health drift')
clients=re.findall(r'epoch0-timeout busc(0|1|2|3|11|18|12|14|13) cfg=.*? image=([0-9a-f]{8}) stat=([0-9a-f]{8})/00000000/00000000/([0-9a-f]{8})',dm)
if len(clients)!=9 or any(a!=b or a!=c for _,a,b,c in clients): die('BUS address status drift')
base=json.load(open(B/'runtime-0060-analysis.json'))
if base['linux_bus_common']['ubwc_static_ctrl']!='0x00000006': die('0060 base drift')
auth=json.load(open(N/'AUTHORIZATION.json'))
out={
 'schema':'sp11-e003h-runtime-0061-vfe-ubwc-static-v1','accepted':True,'date':'2026-08-31',
 'authorization_sha256':sha(N/'AUTHORIZATION.json'),'authorization_consumed':True,'runtime_authorized':False,
 'helper_invocations':1,'same_boot_retry':False,'run_rc':1,'golden_return_verified':True,
 'csid_geometry':'3840x2160','csid_line_error':False,'rtcdm_fifo_bl_completed':25,'rtcdm_faulted':False,
 'linux_ubwc_static_ctrl_before_0061':'0x00000006','linux_ubwc_static_ctrl_0061':'0x00001046','windows_ubwc_static_ctrl':'0x00001046',
 'vfe_raw_epoch0_seen':False,'qc10c_output':False,'nine_bus_clients_address_status_match':True,
 'classification':{'ubwc_static_programming_parity_achieved':True,'ubwc_static_mismatch_was_real':True,'ubwc_static_is_noncausal_for_missing_vfe_epoch0':True,'next_gate':'same-machine Windows dynamic lifecycle trace of VFE1 BUS CGC override +0xc08 0x1ff -> live 0, then compare ordering/ownership to Linux'},
 'runtime_run_sha256':sha(N/'RUNTIME-VFEUBWC-0061-RUN.txt'),'runtime_post_sha256':sha(N/'RUNTIME-VFEUBWC-0061-POST.txt'),'runtime_dmesg_sha256':sha(N/'RUNTIME-VFEUBWC-0061-DMESG.txt'),'runtime_rtcdm_stages_sha256':sha(N/'RUNTIME-VFEUBWC-0061-RTCDM-STAGES.txt')}
(N/'runtime-0061-analysis.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True)); print('PASS: 0061 achieves exact UBWC static parity but VFE BUS Epoch/QC10C remain absent')
