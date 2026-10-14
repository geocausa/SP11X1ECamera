#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
from pathlib import Path
import json,hashlib,subprocess,re,sys
Q=Path(__file__).resolve().parent;R=Q.parents[1];B=R.parents[1]/'02-kernel/upstream-ife-base-build-20261011-01';C=B/'candidate-33/matched-route-qual01';S=C/'source';O=C/'build01';ATTEMPT=sys.argv[1] if len(sys.argv)==2 else '01';MO=C/('diag-module11-'+ATTEMPT)
assert not MO.exists();MO.mkdir()
args=['make','-C',str(S),'O='+str(O),'ARCH=arm64','LOCALVERSION=-sp11-upstream-front26','-j4','M='+str(Q/'kmod'),'MO='+str(MO),'W=1','KCFLAGS=-Werror -I'+str(S/'drivers/media/platform/qcom/camss'),'sp11_rdi_idle_probe.ko']
p=subprocess.run(args,capture_output=True,text=True);(C/('DIAG11-BUILD-'+ATTEMPT+'.log')).write_text(p.stdout+p.stderr)
if p.returncode:raise RuntimeError(p.stdout+p.stderr)
assert re.search(r'\b(?:warning|error):',p.stdout+p.stderr) is None
module=MO/'sp11_rdi_idle_probe.ko';vermagic=subprocess.check_output(['modinfo','-F','vermagic',str(module)],text=True).strip()
assert vermagic.startswith('7.2.0-sp11-upstream-front26 ')
r=dict(status='PASS_READ_ONLY_RDI_DIAGNOSTIC_ARM64_W1_WERROR',module_path=str(module),sha256=hashlib.sha256(module.read_bytes()).hexdigest(),bytes=module.stat().st_size,vermagic=vermagic,source_sha256=hashlib.sha256((Q/'kmod/sp11_rdi_idle_probe.c').read_bytes()).hexdigest(),camera_driver_unchanged=True,installed=False)
(C/'DIAG11.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
