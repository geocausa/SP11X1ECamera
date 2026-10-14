#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Exercise the actual observer's scalar gates with retained topology."""
from pathlib import Path
import json,runpy,sys
sys.dont_write_bytecode=True
Q=Path(__file__).resolve().parent
m=runpy.run_path(str(Q/'run-once.py'))
text=Path('/var/lib/sp11-camera-upstream-front-20261014-08/PRIVATE-MEDIA.txt').read_text()
assert m['check_raw_route'](text,False)
on=text.replace('-> "msm_csid1":0 []','-> "msm_csid1":0 [ENABLED]',1)
a=on.index('- entity 16: msm_csid1');b=on.index('\n- entity',a+1)
on=on[:a]+on[a:b].replace('-> "msm_vfe1_rdi0":0 []','-> "msm_vfe1_rdi0":0 [ENABLED]',1)+on[b:]
assert m['check_raw_route'](on,True)
fmt="Width/Height : 3840/2640\nPixel Format : 'pRAA'\nBytes per Line : 4800\nSize Image : 12672000\n"
assert m['check_raw_format'](fmt)
capture='\n'.join(f'cap dqbuf: {i%3} seq: {i} bytesused: 12672000 ts: {100+i/30:.6f} flags: done' for i in range(8))
assert m['check_raw_capture'](capture)['frames']==8
negative=[
 ('extra_edge','check_raw_route',(on.replace('-> "msm_csid0":0 []','-> "msm_csid0":0 [ENABLED]',1),True)),
 ('missing_edge','check_raw_route',(text,True)),
 ('duplicate_edge','check_raw_route',(on+'\n- entity 900: msm_csiphy2 (2 pads)\n pad1: SOURCE\n -> "msm_csid1":0 [ENABLED]\n',True)),
 ('wrong_height','check_raw_format',(fmt.replace('3840/2640','3840/2160'),)),
 ('wrong_stride','check_raw_format',(fmt.replace('4800','4799'),)),
 ('short_size','check_raw_format',(fmt.replace('12672000','10368000'),)),
 ('short_frame','check_raw_capture',(capture.replace('12672000','12671999',1),)),
 ('gap','check_raw_capture',(capture.replace('seq: 4','seq: 44'),)),
 ('missing_frame','check_raw_capture',('\n'.join(capture.splitlines()[:-1]),)),
 ('timestamp_regression','check_raw_capture',(capture.replace('100.133333','100.000000'),)),
 ('error_flag','check_raw_capture',(capture.replace('flags: done','flags: error',1),))]
for n,fn,args in negative:
 try:m[fn](*args)
 except RuntimeError:pass
 else:raise AssertionError(n)
print(json.dumps(dict(status='PASS_RAW09_SCALAR_ROUTE_FORMAT_CAPTURE_GATES',positive=4,
                     negative=len(negative),retained_topology='08',hardware_access=False)))
