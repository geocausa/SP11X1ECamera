#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess
D=Path(__file__).resolve().parent; repo=D.parents[3]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest(); m=json.load(open(D/'asset-manifest.json')); errors=[]
for r,h in m['assets'].items():
    if sha(D/r)!=h: errors.append(f'hash:{r}')
if sha(D/'WINDOWS-E003H-CAMNOC-RATE-20260831.log')!=m['windows_camnoc_kd_sha256']: errors.append('windows_log_hash')
for name in ['install-candidate.sh','runtime-preflight.sh','load-candidate.sh','start-observer.sh','run-once.sh','camnoc-watch.py']:
    if not (D/name).exists(): errors.append('missing:'+name)
install=(D/'install-candidate.sh').read_text(); run=(D/'run-once.sh').read_text()
if 'grub-reboot' in install: errors.append('installer_arms_boot')
if run.count('"$HELPER"')!=1: errors.append('helper_invocation_not_exactly_one')
if 'camera_programming_changes": 0' not in (D/'asset-manifest.json').read_text(): errors.append('manifest_not_zero_delta')
out={'schema':'sp11-e003h-camnoc-rate-0055-package-inspection-v1','accepted':not errors,'errors':errors,'telemetry_only':True,'camera_programming_delta':0,'windows_expected_cfg':'0x00000203','windows_expected_rate_hz':300000000,'assets_sha256':m['assets']}
(D/'package-inspection.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2)); raise SystemExit(0 if out['accepted'] else 1)
