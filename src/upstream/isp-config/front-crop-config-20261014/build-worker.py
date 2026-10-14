#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
from pathlib import Path
import hashlib,json,re,subprocess
Q=Path(__file__).resolve().parent;R=Q.parents[3]
C=R.parents[1]/'02-kernel/front-crop-config-20261014-01'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 O=C/'native-compile01';O.mkdir()
 closure={
 'sp11-front-crop-config.h':Q/'sp11-front-crop-config.h',
 'sp11-geometry-stats.h':R/'src/upstream/isp-config/sp11-geometry-stats.h',
 'sp11-front-cold-fields.h':R/'src/upstream/isp-config/cold-front-fields-20261014/sp11-front-cold-fields.h',
 'sp11-front-measured-config.h':R/'src/upstream/isp-config/measured-front-reuse-20261014/sp11-front-measured-config.h',
 'sp11-cdm.h':R/'src/upstream/isp-config/sp11-cdm.h'}
 for n,p in closure.items():(O/n).write_bytes(p.read_bytes())
 (O/'Makefile').write_text('obj-m += sp11_crop_compile.o\n')
 (O/'sp11_crop_compile.c').write_text("""// SPDX-License-Identifier: GPL-2.0-only
#include <linux/module.h>
#include "sp11-front-crop-config.h"
static int __init crop_compile_init(void)
{
 const struct sp11_front_cold_policy p = {
  { SP11_FRONT_MEASURED_NATIVE_AE74_93,3840,2160,2560,1440 },
  SP11_BLS121_IFE18_SELECTOR,0
 };
 u8 out[SP11_FRONT_CROP_CONFIG_BYTES];
 int ret = sp11_front_crop_config(out,sizeof(out),&p);
 return ret ? ret : -EOPNOTSUPP;
}
static void __exit crop_compile_exit(void) { }
module_init(crop_compile_init);
module_exit(crop_compile_exit);
MODULE_LICENSE("GPL");
""")
 anchor=Path('/lib/modules/7.1.5-sp11-render-parity-v4+/build').resolve()
 p=subprocess.run(['make','-C',str(anchor),'M='+str(O),'ARCH=arm64','W=1','KCFLAGS=-Werror','modules'],capture_output=True,text=True)
 (C/'native-compile.log').write_text(p.stdout+p.stderr)
 assert p.returncode==0 and not re.search(r'\b(?:warning|error):',p.stdout+p.stderr),p.stderr[-2500:]
 module=O/'sp11_crop_compile.ko'
 vermagic=subprocess.check_output(['modinfo','-F','vermagic',str(module)],text=True).strip()
 assert vermagic.startswith('7.1.5-sp11-render-parity-v4+ ')
 assert 'AArch64' in subprocess.check_output(['readelf','-h',str(module)],text=True)
 checkpatch=R.parents[1]/'02-kernel/upstream-ife-base-build-20261011-01/candidate-35/cdm-owner-qual01/source/scripts/checkpatch.pl'
 p=subprocess.run(['perl',str(checkpatch),'--no-tree','--strict','--file',str(Q/'sp11-front-crop-config.h')],capture_output=True,text=True)
 (C/'header-style.log').write_text(p.stdout+p.stderr)
 assert p.returncode==0 and '0 errors, 0 warnings, 0 checks' in p.stdout,p.stdout[-2500:]
 result={'status':'PASS_NATIVE_ABI_COMPILE_ONLY','module_path':str(module),'module_sha256':sha(module),
 'vermagic':vermagic,'warnings':0,'errors':0,'style':{'errors':0,'warnings':0,'checks':0},
 'header_pins':{n:sha(p) for n,p in closure.items()},
 'installed':False,'loaded':False,'CAMSS_or_kernel_rebuilt':False,'runtime_changed':False,'hardware':False}
 (C/'BUILD.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
