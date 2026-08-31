#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess
REPO=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
P=REPO/'experiments/E003-front-imx681-cphy/e003h-vfe1-sp11-active-start-prefix-0057-candidate'
B=REPO/'experiments/E003-front-imx681-cphy/e003h-camnoc-rate-parity-0056-candidate'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def txt(p): return Path(p).read_text(errors='replace')
def sh(c): return subprocess.check_output(c,shell=True,text=True).strip()
files={
 'RUN':P/'RUNTIME-VFEACTIVE-0057-RUN.txt',
 'POST':P/'RUNTIME-VFEACTIVE-0057-POST.txt',
 'DMESG':P/'RUNTIME-VFEACTIVE-0057-DMESG.txt',
 'STAGES':P/'RUNTIME-VFEACTIVE-0057-RTCDM-STAGES.txt',
 'AUTH':P/'AUTHORIZATION.json',
 'STATIC':REPO/'experiments/E003-front-imx681-cphy/e003h-vfe1-sp11-active-start-prefix-0057-static/0057-static-inspection.json',
 'BASE':B/'runtime-0056-analysis.json',
}
for k,p in files.items():
    if not p.is_file(): raise SystemExit(f'missing {k}: {p}')
run,post,dmesg,stages=(txt(files[x]) for x in ['RUN','POST','DMESG','STAGES'])
auth=json.loads(txt(files['AUTH'])); static=json.loads(txt(files['STATIC'])); base=json.loads(txt(files['BASE']))
assert auth['accepted'] and auth['runtime_authorized']
assert static['accepted'] and base['accepted']
assert run.count('HELPER_INVOCATION_COUNT=1')==1
assert 'CAMERA_PROGRAMMING_DELTA=VFE1_SP11_ACTIVE_DAL_PREFIX_0057_ONLY' in run
assert 'RUN_RC=1' in run and 'Connection timed out' in run
assert 'QC10C_OUTPUT=absent' in post
assert 'fifo_seq=25' in post and 'faulted=0' in post
assert 'SENSOR_PM=suspended' in post and 'CAMSS_PM=suspended' in post
assert 'name=stopped fifo_seq=25' in stages
# Healthy CSID mode2 boundary retained.
assert 'ipp-history=00e11ff8/00000ee8/' in dmesg
assert 'line-error=00000000/00000000/00000000' in dmesg
assert '/08700f00' in dmesg
assert 'ecc=00000000 crc=00000000' in dmesg
# VFE still has no raw IRQ status and no BUS status.
needle='E003h VFE1 epoch0-timeout top=00000000/00030003 mask=0007f051/00000000 bus=00000000/00000000 bmask=d0000000/00000000'
assert needle in dmesg
# Compare the four stable VFE timeout records to 0056 ignoring timestamps.
base_d=txt(B/'RUNTIME-CAMNOC300-0056-DMESG.txt')
labels=['VFE1 epoch0-timeout top=','VFE1 epoch0-timeout viol=','VFE1 epoch0-timeout full0=','VFE1 epoch0-timeout full1=']
def payloads(s):
    out={}
    for lab in labels:
        lines=[ln.split('E003h ',1)[1] for ln in s.splitlines() if 'E003h '+lab in ln]
        assert len(lines)==1,(lab,len(lines))
        out[lab]=lines[0]
    return out
p57=payloads(dmesg); p56=payloads(base_d)
assert p57==p56,(p57,p56)
# Golden return invariants.
cmd=txt('/proc/cmdline') if Path('/proc/cmdline').exists() else ''
grub=sh('sudo -n grub-editenv /boot/grub/grubenv list')
mods=sh("lsmod | grep -E 'qcom_camss|imx681' || true")
assert 'sp11_entry=7.1.5-sp11-fullio-v19c' in cmd
assert 'saved_entry=sp11-audio-fullio-v19c' in grub and 'next_entry=' in grub
assert not [x for x in grub.splitlines() if x.startswith('next_entry=') and x!='next_entry=']
assert mods==''
out={
 'schema':'sp11-e003h-runtime-0057-active-vfe-prefix-v1',
 'accepted':True,
 'authorization_consumed':True,
 'execution':{'helper_invocations':1,'same_boot_retry':False,'run_rc':1,'golden_return_verified':True},
 'camera':{'csid_geometry':'3840x2160','csid_line_error':False,'csid_ecc_crc_errors':False,'rtcdm_fifo_final':25,'rtcdm_faulted':False,'vfe1_raw_epoch0':False,'qc10c_output':False},
 'comparison_0056':{'vfe_timeout_snapshot_identical':True,'vfe_top_bus':'00000000/00030003 mask=0007f051/00000000 bus=00000000/00000000 bmask=d0000000/00000000'},
 'classification':{'wrong_generation_prefix_was_real_parity_bug':True,'active_prefix_causal_for_vfe1_stall':False,'retain_0057_prefix_correction':True,'new_speculative_register_write_justified':False},
 'remaining_failure_boundary':'after healthy CSID1 3840x2160, parity clocks, corrected active SP11 IFE1 DAL prefix and configured BUS clients; before VFE1 raw Epoch0 / FULL output',
 'evidence_sha256':{k:sha(p) for k,p in files.items()},
}
(P/'runtime-0057-analysis.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True))
print('ANALYSIS_SHA256='+sha(P/'runtime-0057-analysis.json'))
