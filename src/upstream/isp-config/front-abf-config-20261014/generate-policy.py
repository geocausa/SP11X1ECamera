#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Extract only the existing own complete ABF control replacement."""
from pathlib import Path
import hashlib,json
Q=Path(__file__).resolve().parent;R=Q.parents[3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 audit=json.loads((R/'src/upstream/isp-config/measured-front-reuse-20261014/baseline-audit.json').read_text())
 name='src/native-rgb/front-ae/tuning/imx681-front-open-regs.txt';p=R/name
 assert sha(p)==audit['repository_pins'][name]
 rows=[]
 for line in p.read_text().splitlines():
  text=line.split('#',1)[0].strip()
  if text:
   row=tuple(int(x,0) for x in text.split(','));assert len(row)==3
   if row[0]==0x4960:rows.append(row)
 assert rows==[(0x4960,0,0x101)]
 (Q/'sp11-front-abf-measured.h').write_text("""/* SPDX-License-Identifier: GPL-2.0-only */
/* Generated from existing own full-word run93 control replacement.
 * No vendor tuning/profile, table, pixel input or new filter calibration.
 */
#ifndef SP11_FRONT_ABF_MEASURED_H
#define SP11_FRONT_ABF_MEASURED_H

#define SP11_FRONT_ABF_MEASURED_MODULE 0x101U

#endif
""")
 result={'status':'PASS_REUSED_OWN_COMPLETE_ABF_MODULE','source':name,'source_sha256':sha(p),
 'and_mask':0,'own_module_word':257,'private_tuning_or_profile_read':False,'new_calibration':False}
 (Q/'GENERATED.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
