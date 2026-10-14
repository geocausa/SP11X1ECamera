#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
from pathlib import Path
import re,json,hashlib,subprocess,sys
Q=Path(__file__).resolve().parent;S,O=map(Path,sys.argv[1:3]);O.mkdir(parents=True,exist_ok=False)
def body(s,n):
 matches=list(re.finditer(r'^(?:static\s+)?(?:int|void|bool|struct \w+\s*\*)\s*'+n+r'\([^;]*?\)\n\{',s,re.M))
 if len(matches)!=1:raise RuntimeError((n,len(matches)))
 a=matches[0].start();b=s.index('{',a);i=b+1;depth=1
 while depth:depth+=(s[i]=='{')-(s[i]=='}');i+=1
 return s[a:i]
files=[S/'drivers/phy/qualcomm/phy-qcom-mipi-csi2-core.c',S/'drivers/phy/qualcomm/phy-qcom-mipi-csi2.h',S/'drivers/phy/phy-core.c',S/'drivers/media/platform/qcom/camss/camss-csiphy.c']
core=files[0].read_text();text=''
for n in ['phy_qcom_mipi_csi2_set_clock_rates','phy_qcom_mipi_csi2_release_owned','phy_qcom_mipi_csi2_power_on','phy_qcom_mipi_csi2_power_off','phy_qcom_mipi_csi2_configure','phy_qcom_mipi_csi2_set_mode']:text+=body(core,n)+'\n'
text+=body(files[2].read_text(),'phy_power_off')+'\n'
for n in ['csiphy_stream_off','csiphy_set_stream']:text+=body(files[3].read_text(),n)+'\n'
(O/'actual-phy.h').write_bytes(files[1].read_bytes())
(O/'stubs/linux/phy').mkdir(parents=True)
(O/'stubs/linux/interrupt.h').write_text('/* API model types are defined by the harness. */\n')
(O/'stubs/linux/phy/phy.h').write_text('/* API model types are defined by the harness. */\n')
(O/'actual-test.c').write_text((Q/'test-power.c.in').read_text().replace('/* ACTUAL_FUNCTIONS */',text))
result={'status':'PASS_ACTUAL_PHY_REFERENCE_AND_PROPAGATION_MODEL','source_sha256':{str(p.relative_to(S)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},'runs':[],'scope':'API ownership and error model; no physical/electrical/IRQ concurrency proof'}
for compiler in ['gcc','clang']:
 exe=O/compiler
 args=[compiler,'-std=gnu11','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-Wno-sign-compare','-fsanitize=address,undefined','-fno-omit-frame-pointer','-g','-I',str(O/'stubs'),'-I',str(O),str(O/'actual-test.c'),'-o',str(exe)]
 p=subprocess.run(args,capture_output=True,text=True);(O/(compiler+'-compile.log')).write_text(p.stdout+p.stderr)
 if p.returncode:print(p.stdout+p.stderr);raise SystemExit(p.returncode)
 p=subprocess.run([str(exe)],capture_output=True,text=True);(O/(compiler+'-run.log')).write_text(p.stdout+p.stderr)
 if p.returncode:print(p.stdout+p.stderr);raise SystemExit(p.returncode)
 result['runs'].append({'compiler':compiler,'output':p.stdout.strip()})
(O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
