#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Compile-only native ABI probe; never install/load or rebuild CAMSS/kernel."""
from pathlib import Path
import subprocess,json,hashlib,sys,re
Q=Path(__file__).resolve().parent;R=Q.parents[3]
C=R.parents[1]/'02-kernel/front-measured-reuse-20261014-01';O=C/'native-compile01'
def main():
 O.mkdir()
 for n in ['sp11-front-measured-config.h']:(O/n).write_bytes((Q/n).read_bytes())
 (O/'sp11-cdm.h').write_bytes((R/'src/upstream/isp-config/sp11-cdm.h').read_bytes())
 (O/'Makefile').write_text('obj-m += sp11_measured_compile.o\n')
 (O/'sp11_measured_compile.c').write_text('''// SPDX-License-Identifier: GPL-2.0-only
#include <linux/module.h>
#include "sp11-front-measured-config.h"
static int __init measured_compile_init(void)
{
 struct sp11_front_measured_domain d = {
  SP11_FRONT_MEASURED_NATIVE_AE74_93, 3840, 2160, 2560, 1440
 };
 u8 out[SP11_FRONT_MEASURED_CONFIG_BYTES];
 int ret = sp11_front_measured_config(out, sizeof(out), &d);
 return ret ? ret : -EOPNOTSUPP;
}
static void __exit measured_compile_exit(void) { }
module_init(measured_compile_init);
module_exit(measured_compile_exit);
MODULE_LICENSE("GPL");
''')
 anchor=Path('/lib/modules/7.1.5-sp11-render-parity-v4+/build').resolve()
 p=subprocess.run(['make','-C',str(anchor),'M='+str(O),'ARCH=arm64','W=1','KCFLAGS=-Werror','modules'],capture_output=True,text=True)
 (C/'native-compile.log').write_text(p.stdout+p.stderr)
 assert not p.returncode and not re.search(r'\b(?:warning|error):',p.stdout+p.stderr),p.stderr[-2000:]
 module=O/'sp11_measured_compile.ko';vermagic=subprocess.check_output(['modinfo','-F','vermagic',str(module)],text=True).strip()
 assert vermagic.startswith('7.1.5-sp11-render-parity-v4+ ')
 machine=subprocess.check_output(['readelf','-h',str(module)],text=True);assert 'AArch64' in machine
 result={'status':'PASS_NATIVE_ABI_ARM64_COMPILE_ONLY','header_sha256':hashlib.sha256((Q/'sp11-front-measured-config.h').read_bytes()).hexdigest(),
 'module_sha256':hashlib.sha256(module.read_bytes()).hexdigest(),'module_path':str(module),'vermagic':vermagic,'warnings':0,'errors':0,
 'installed':False,'loaded':False,'CAMSS_or_kernel_rebuilt':False,'hardware':False}
 (C/'BUILD.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
