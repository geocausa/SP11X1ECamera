#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess
R=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
N=R/'experiments/E003-front-imx681-cphy/e003h-vfe1-bus-progress-readonly-0060-candidate'
S=R/'experiments/E003-front-imx681-cphy/e003h-vfe1-bus-progress-readonly-0060-static'
def bytes_(p):
    p=Path(p)
    try: return p.read_bytes()
    except PermissionError: return subprocess.check_output(['sudo','-n','cat',str(p)])
sha=lambda p:hashlib.sha256(bytes_(p)).hexdigest()
def die(x): raise SystemExit('FAIL: '+x)
run=(N/'RUNTIME-VFEBUS-0060-RUN.txt').read_text(); post=(N/'RUNTIME-VFEBUS-0060-POST.txt').read_text(); dm=(N/'RUNTIME-VFEBUS-0060-DMESG.txt').read_text(); stages=bytes_(N/'RUNTIME-VFEBUS-0060-RTCDM-STAGES.txt').decode(); auth=json.loads((N/'AUTHORIZATION.json').read_text()); oracle=json.loads((S/'0060-static-oracle.json').read_text())
if run.count('HELPER_INVOCATION_COUNT=1')!=1 or 'RUN_RC=1' not in run or 'TELEMETRY=IN_DRIVER_VFE1_BUS_PROGRESS_0060' not in run: die('run contract')
if 'QC10C_OUTPUT=absent' not in post or 'fifo_seq=25' not in post or 'faulted=0' not in post: die('post/rtcdm')
if 'ipp-seq[3]=00000ee8/08700f00' not in dm or 'line-error=00000000/00000000/00000000' not in dm: die('csid health')
if 'E003h VFE1 epoch0-timeout top=' not in dm: die('vfe timeout')
m=re.search(r'buscommon cgc=([0-9a-f]{8}) ubwc=([0-9a-f]{8}) piso=([0-9a-f]{8}) dbgcfg=([0-9a-f]{8}) dbg=([0-9a-f]{8}) test=([0-9a-f]{8})',dm)
if not m: die('buscommon')
cgc,ubwc,piso,dbgcfg,dbg,test=[int(x,16) for x in m.groups()]
clients={}
for mm in re.finditer(r'busc(\d+) cfg=([0-9a-f]{8}) image=([0-9a-f]{8}) stat=([0-9a-f]{8})/([0-9a-f]{8})/([0-9a-f]{8})/([0-9a-f]{8}) dbg=([0-9a-f]{8})/([0-9a-f]{8})',dm):
    cid=int(mm.group(1)); vals=[int(x,16) for x in mm.groups()[1:]]; clients[cid]=vals
order=[0,1,2,3,11,18,12,14,13]
if list(clients)!=order: die('client order '+str(list(clients)))
for cid,v in clients.items():
    cfg,image,s0,s1,s2,s3,d0,d1=v
    if s0!=image or s3!=image or s1 or s2 or d0 or d1: die('client progression '+str(cid))
win=int(oracle['windows_same_machine_live']['bus_common']['ubwc_static_0x0c58'],16)
if win!=0x1046 or ubwc!=0x6 or (win^ubwc)!=0x1040: die('ubwc delta')
env=subprocess.check_output(['grub-editenv','list'],text=True,stderr=subprocess.DEVNULL).splitlines()
cmdline=Path('/proc/cmdline').read_text()
golden='sp11_entry=7.1.5-sp11-fullio-v19c' in cmdline and 'saved_entry=sp11-audio-fullio-v19c' in env and not any(x.startswith('next_entry=') and x!='next_entry=' for x in env)
mods=all(not Path('/sys/module/'+x).exists() for x in ('qcom_camss','imx681','ov13858'))
if not golden or not mods: die('golden return')
out={
 'schema':'sp11-e003h-runtime-0060-vfe-bus-progress-v1','accepted':True,'date':'2026-08-31','authorization_consumed':True,'helper_invocations':1,'same_boot_retry':False,'run_rc':1,'qc10c_output':False,'golden_return_verified':True,'rtcdm_fifo_bl_completed':25,'rtcdm_faulted':False,'csid_geometry':'3840x2160','csid_line_error':False,'vfe_raw_epoch0_seen':False,
 'linux_bus_common':{'cgc_override':f'0x{cgc:08x}','ubwc_static_ctrl':f'0x{ubwc:08x}','power_iso_cfg':f'0x{piso:08x}','debug_cfg':f'0x{dbgcfg:08x}','debug_status':f'0x{dbg:08x}','test_bus_ctrl':f'0x{test:08x}'},
 'windows_bus_common':{'ubwc_static_ctrl':f'0x{win:08x}'},'ubwc_static_ctrl_xor_delta':f'0x{win^ubwc:08x}','nine_bus_clients_programmed':True,'nine_bus_clients_addr_status0_matches_image':True,'nine_bus_clients_addr_status3_matches_image':True,'nine_bus_clients_debug_zero':True,
 'classification':{'missing_clients_disproven':True,'bus_client_address_latch_absent_disproven':True,'ubwc_static_ctrl_mismatch_proven':True,'ubwc_static_ctrl_write_causality_proven':False,'new_programming_write_justified':False,'next_gate':'static ownership/provenance of Windows/VFE680 UBWC_STATIC_CTRL 0x1046 and missing 0x1040 bits'},
 'runtime_run_sha256':sha(N/'RUNTIME-VFEBUS-0060-RUN.txt'),'runtime_post_sha256':sha(N/'RUNTIME-VFEBUS-0060-POST.txt'),'runtime_dmesg_sha256':sha(N/'RUNTIME-VFEBUS-0060-DMESG.txt'),'runtime_rtcdm_stages_sha256':sha(N/'RUNTIME-VFEBUS-0060-RTCDM-STAGES.txt'),'authorization_sha256':sha(N/'AUTHORIZATION.json'),'static_oracle_sha256':sha(S/'0060-static-oracle.json'),'runtime_authorized':False}
(N/'runtime-0060-analysis.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
(N/'RESULT.md').write_text('# E003h 0060 result\n\nPASS as a consumed read-only diagnostic. Golden return is verified. All nine Windows-active BUS clients are enabled and reflect their programmed image addresses in ADDR_STATUS0/3 with zero debug status. The concrete remaining BUS-common delta is UBWC_STATIC_CTRL: Linux 0x00000006 versus successful Windows 0x00001046 (missing bits 0x00001040). This proves the mismatch, not its write ownership or causality. No programming write is authorized yet.\n')
(N/'GOLDEN-RETURN-0060.txt').write_text('Golden return verified after the single consumed 0060 helper invocation.\n'+cmdline+'\n'+'\n'.join(env)+'\n')
cons={'schema':'sp11-e003h-vfebus-0060-authorization-consumed-v1','accepted':True,'authorization_sha256':sha(N/'AUTHORIZATION.json'),'consumed':True,'helper_invocations':1,'same_boot_retry':False,'analysis_sha256':sha(N/'runtime-0060-analysis.json')}
(N/'AUTHORIZATION-CONSUMED.json').write_text(json.dumps(cons,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True)); print('ANALYSIS_SHA='+sha(N/'runtime-0060-analysis.json')); print('EXTRACTOR_SHA='+sha(N/'extract-runtime-0060.py')); print('GOLDEN_SHA='+sha(N/'GOLDEN-RETURN-0060.txt')); print('CONSUMED_SHA='+sha(N/'AUTHORIZATION-CONSUMED.json'))
