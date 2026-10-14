#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Reject unsafe resource-release and error-propagation mutations."""
from pathlib import Path
import subprocess,json,sys,resource
Q=Path(__file__).resolve().parent;I,O=map(Path,sys.argv[1:3]);O.mkdir(exist_ok=False)
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
original=(I/'actual-test.c').read_text()
mutations={
 'drop_camss_phy_stop_error':('return phy_power_off(csiphy->phy);','(void)phy_power_off(csiphy->phy);\n\treturn 0;'),
 'force_parent_suspend_with_active_child':('pm_runtime_put_noidle(csi2phy->dev);','(void)pm_runtime_put_sync(csi2phy->dev);'),
 'leak_owned_parent_reference':('pm_runtime_put_noidle(csi2phy->dev);','if (csi2phy->power_fault) pm_runtime_put_noidle(csi2phy->dev);'),
 'lose_opp_ownership':('csi2phy->opp_owned = true;','csi2phy->opp_owned = false;'),
 'lose_partial_pstate_ownership':('csi2phy->perf_owned |= BIT(i);','csi2phy->perf_owned |= 0 * BIT(i);'),
 'hide_failed_start_cleanup_fault':('return -EUCLEAN;\n\t}\n\treturn ret;','return ret;\n\t}\n\treturn ret;'),
}
result={'status':'PASS_UNSAFE_PHY_MUTATIONS_REJECTED','mutations':[]}
for name,(before,after) in mutations.items():
 if original.count(before)!=1:raise RuntimeError((name,original.count(before)))
 p=O/(name+'.c');p.write_text(original.replace(before,after))
 exe=O/name
 command=['gcc','-std=gnu11','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-Wno-sign-compare','-Wno-unused-function','-fsanitize=address,undefined','-fno-omit-frame-pointer','-g','-I',str(I/'stubs'),'-I',str(I),str(p),'-o',str(exe)]
 r=subprocess.run(command,capture_output=True,text=True);(O/(name+'-compile.log')).write_text(r.stdout+r.stderr)
 if r.returncode:raise RuntimeError(r.stdout+r.stderr)
 r=subprocess.run([str(exe)],capture_output=True,text=True);(O/(name+'-run.log')).write_text(r.stdout+r.stderr)
 if not r.returncode:raise RuntimeError('unsafe mutation survived: '+name)
 result['mutations'].append({'name':name,'compiled':True,'returncode':r.returncode,'rejected':True})
(O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
