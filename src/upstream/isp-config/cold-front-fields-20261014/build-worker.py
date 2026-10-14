#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Synthetic host checks and a compile-only native ABI probe; no installation."""
from pathlib import Path
import hashlib,json,subprocess,resource,re,sys
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
Q=Path(__file__).resolve().parent;R=Q.parents[3]
C=R.parents[1]/'02-kernel/front-cold-fields-20261014-01'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 tag=sys.argv[1] if len(sys.argv)>1 else '01'
 assert re.fullmatch(r'[0-9]{2}',tag)
 O=C/('host'+tag);O.mkdir()
 headers={
 'sp11-front-cold-fields.h':Q/'sp11-front-cold-fields.h',
 'sp11-front-measured-config.h':R/'src/upstream/isp-config/measured-front-reuse-20261014/sp11-front-measured-config.h',
 'sp11-cdm.h':R/'src/upstream/isp-config/sp11-cdm.h'}
 for name,p in headers.items():(O/name).write_bytes(p.read_bytes())
 source=(Q/'test-host.c').read_text();(O/'test-host.c').write_text(source)
 actual=(Q/'sp11-front-cold-fields.h').read_text()
 mutants={
  'wrong_offset_shift':actual.replace('offset18 << 14','offset18 << 16'),
  'admit_unqualified_fraction':actual.replace('policy->bls_fraction != 0','policy->bls_fraction > 3'),
  'admit_wrong_layout':actual.replace('policy->bls_selector != SP11_BLS121_IFE18_SELECTOR','policy->bls_selector == 0'),
  'publish_before_validation':actual.replace('\tif (!out || !policy)','\tif (out)\n\t\tout[0] = 0;\n\tif (!out || !policy)')}
 assert all(h!=actual for h in mutants.values())
 runs=[]
 for cc in ['gcc','clang']:
  for label,h in [('actual',actual),*mutants.items()]:
   (O/'sp11-front-cold-fields.h').write_text(h)
   exe=O/(cc+'-'+label)
   p=subprocess.run([cc,'-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror',
    '-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+str(O),str(O/'test-host.c'),'-o',str(exe)],capture_output=True,text=True)
   assert p.returncode==0,p.stderr[-1500:]
   p=subprocess.run([str(exe)],capture_output=True,text=True,timeout=15)
   (O/(cc+'-'+label+'.log')).write_text(p.stdout+p.stderr)
   if label=='actual':
    assert p.returncode==0,p.stderr[-1500:]
    runs.append({'compiler':cc,'ASan_UBSan':True,'result':json.loads(p.stdout)})
   else:assert p.returncode!=0,'unsafe mutation survived '+label
 (O/'sp11-front-cold-fields.h').write_text(actual)
 host={'status':'PASS','runs':runs,'compiled_mutations_rejected_each':list(mutants),
       'source_pins':{name:digest(p) for name,p in headers.items()}}
 (O/'RESULT.json').write_text(json.dumps(host,indent=2)+'\n')
 B=C/('native-compile'+tag);B.mkdir()
 for name,p in headers.items():(B/name).write_bytes(p.read_bytes())
 (B/'Makefile').write_text('obj-m += sp11_cold_compile.o\n')
 (B/'sp11_cold_compile.c').write_text("""// SPDX-License-Identifier: GPL-2.0-only
#include <linux/module.h>
#include "sp11-front-cold-fields.h"
static int __init cold_compile_init(void)
{
 struct sp11_front_cold_policy p = {
  { SP11_FRONT_MEASURED_NATIVE_AE74_93, 3840, 2160, 2560, 1440 },
  SP11_BLS121_IFE18_SELECTOR, 0
 };
 u8 out[SP11_FRONT_COLD_BYTES];
 int ret = sp11_front_cold_fields(out, sizeof(out), &p);
 return ret ? ret : -EOPNOTSUPP;
}
static void __exit cold_compile_exit(void) { }
module_init(cold_compile_init);
module_exit(cold_compile_exit);
MODULE_LICENSE("GPL");
""")
 anchor=Path('/lib/modules/7.1.5-sp11-render-parity-v4+/build').resolve()
 p=subprocess.run(['make','-C',str(anchor),'M='+str(B),'ARCH=arm64','W=1','KCFLAGS=-Werror','modules'],capture_output=True,text=True)
 (C/('native-compile'+tag+'.log')).write_text(p.stdout+p.stderr)
 assert p.returncode==0 and not re.search(r'\b(?:warning|error):',p.stdout+p.stderr),p.stderr[-1500:]
 m=B/'sp11_cold_compile.ko'
 vermagic=subprocess.check_output(['modinfo','-F','vermagic',str(m)],text=True).strip()
 assert vermagic.startswith('7.1.5-sp11-render-parity-v4+ ')
 assert 'AArch64' in subprocess.check_output(['readelf','-h',str(m)],text=True)
 result={'status':'PASS_NATIVE_ABI_COMPILE_ONLY','host_result_path':str(O/'RESULT.json'),'module_sha256':digest(m),'module_path':str(m),
 'vermagic':vermagic,'warnings':0,'errors':0,'header_sha256':digest(Q/'sp11-front-cold-fields.h'),
 'installed':False,'loaded':False,'CAMSS_or_kernel_rebuilt':False,'runtime_changed':False,'hardware':False}
 (C/'BUILD.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'host':host,'native_compile':result}))
if __name__=='__main__':main()
