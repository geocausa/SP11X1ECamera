#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Use the retained05 real kernel formatter output to validate the corrected reader."""
from pathlib import Path
import re,sys,json
sys.dont_write_bytecode=True
Q=Path(__file__).resolve().parent
namespace={'__name__':'observer_test'}
exec(compile((Q/'run-once.py').read_text(),str(Q/'run-once.py'),'exec'),namespace)
summary=Path('/var/lib/sp11-camera-upstream-front-20261014-05/PRIVATE-GENPD.txt').read_text()
check=namespace['check_top_membership']
result=check(summary,'8-0010')
assert result['runtime_status']=='suspended'
row=next(x for x in summary.splitlines() if x.split() and x.split()[0]=='8-0010')
cases={
 'missing_sensor':summary.replace(row+'\n',''),
 'similar_name':summary.replace('8-0010','18-0010'),
 'duplicate_sensor':summary.replace(row,row+'\n'+row),
 'duplicate_top_header':summary+'\ncam_cc_titan_top_gdsc off-0\n'+row+'\n',
 'missing_top_header':summary.replace('cam_cc_titan_top_gdsc ','other_top '),
 'sensor_active':summary.replace(row,re.sub(r'\bsuspended\b','active',row)),
 'sensor_other_domain':summary.replace(row+'\n','')+'\nother_domain off-0\n'+row+'\n',
}
for label,value in cases.items():
 try:check(value,'8-0010')
 except RuntimeError:pass
 else:raise AssertionError('Malformed genpd admitted: '+label)
print(json.dumps({'status':'PASS_ACTUAL_GENPD_FORMAT_REGRESSION','real_retained_positive':result,'negative_controls':list(cases)}))
