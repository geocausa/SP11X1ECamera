#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Small compile-only probe of the original native ABI; no driver rebuild."""
from pathlib import Path
import json,subprocess,hashlib,re
Q=Path(__file__).resolve().parent;R=Q.parents[3]
C=R.parents[1]/'02-kernel/front-channel-bayer0-20261014-01'
def main():
 O=C/'native-compile02';O.mkdir()
 headers={
  'sp11-front-channel-bayer0.h':Q/'sp11-front-channel-bayer0.h',
  'sp11-front-channel-gain.h':R/'src/upstream/isp-config/front-channel-gain-20261014/sp11-front-channel-gain.h',
  'sp11-front-cold-fields.h':R/'src/upstream/isp-config/cold-front-fields-20261014/sp11-front-cold-fields.h',
  'sp11-front-measured-config.h':R/'src/upstream/isp-config/measured-front-reuse-20261014/sp11-front-measured-config.h',
  'sp11-cdm.h':R/'src/upstream/isp-config/sp11-cdm.h'}
 for n,p in headers.items():(O/n).write_bytes(p.read_bytes())
 (O/'Makefile').write_text('obj-m += sp11_channel_bayer0_compile.o\n')
 (O/'sp11_channel_bayer0_compile.c').write_text("""// SPDX-License-Identifier: GPL-2.0-only
#include <linux/module.h>
#include "sp11-front-channel-bayer0.h"
static int __init channel_bayer0_compile_init(void)
{
 struct sp11_front_cold_policy p = {
  { SP11_FRONT_MEASURED_NATIVE_AE74_93, 3840, 2160, 2560, 1440 },
  SP11_BLS121_IFE18_SELECTOR, 0
 };
 u8 out[SP11_FRONT_CHANNEL_GAIN_CONFIG_BYTES];
 int ret = sp11_front_channel_bayer0_cold_config(out, sizeof(out), &p);
 return ret ? ret : -EOPNOTSUPP;
}
static void __exit channel_bayer0_compile_exit(void) { }
module_init(channel_bayer0_compile_init);
module_exit(channel_bayer0_compile_exit);
MODULE_LICENSE("GPL");
""")
 anchor=Path('/lib/modules/7.1.5-sp11-render-parity-v4+/build').resolve()
 p=subprocess.run(['make','-C',str(anchor),'M='+str(O),'ARCH=arm64','W=1','KCFLAGS=-Werror','modules'],capture_output=True,text=True)
 (C/'native-compile.log').write_text(p.stdout+p.stderr)
 assert p.returncode==0 and not re.search(r'\b(?:warning|error):',p.stdout+p.stderr),p.stderr[-2000:]
 module=O/'sp11_channel_bayer0_compile.ko';vermagic=subprocess.check_output(['modinfo','-F','vermagic',str(module)],text=True).strip()
 assert vermagic.startswith('7.1.5-sp11-render-parity-v4+ ')
 assert 'AArch64' in subprocess.check_output(['readelf','-h',str(module)],text=True)
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 result={'status':'PASS_NATIVE_ABI_COMPILE_ONLY','module_path':str(module),'module_sha256':sha(module),
 'vermagic':vermagic,'warnings':0,'errors':0,'header_pins':{n:sha(p) for n,p in headers.items()},
 'installed':False,'loaded':False,'CAMSS_or_kernel_rebuilt':False,'runtime_changed':False,'hardware':False}
 (C/'BUILD.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
