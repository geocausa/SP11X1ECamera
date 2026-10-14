#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Extract only the existing own measured CCM parameter; never refit it."""
from pathlib import Path
import hashlib,json,sys
Q=Path(__file__).resolve().parent;R=Q.parents[3]
RUN=R.parents[1]/'02-kernel/front-ae-93/run-93.json'
PIN='a5f27787588c2bb0297b57ff672b912f96ec34e3628be0904bcdc12e37f7e0d1'
def main():
 assert hashlib.sha256(RUN.read_bytes()).hexdigest()==PIN
 data=json.loads(RUN.read_text())
 matches=[s for s in data['camss_params'] if s.startswith('native_front_ccm_q7=')]
 assert len(matches)==1
 matrix=[int(s) for s in matches[0].split('=',1)[1].split(',')]
 assert len(matrix)==9 and all(-2048<=v<=2047 for v in matrix)
 body="""/* SPDX-License-Identifier: GPL-2.0-only */
/* Existing own run93 measured GBR Q7 matrix, unchanged; no private tuning. */
#ifndef SP11_FRONT_CCM_MEASURED_H
#define SP11_FRONT_CCM_MEASURED_H

#include "sp11-front-ccm-config.h"

static const struct sp11_front_ccm_state sp11_front_ccm_run93 = {
\t.matrix = { """+', '.join(map(str,matrix))+""" },
\t.offset = { 0, 0, 0 },
\t.fractional_bits = 7,
};

static inline int
sp11_front_ccm_measured_config(u8 *out, size_t capacity,
\t\t\t       const struct sp11_front_cold_policy *policy)
{
\treturn sp11_front_ccm_config(out, capacity, policy,
\t\t\t\t     &sp11_front_ccm_run93);
}
#endif
"""
 target=Q/'sp11-front-ccm-measured.h'
 if '--check' in sys.argv:assert target.read_text()==body
 else:target.write_text(body)
 print(json.dumps({'status':'PASS_OWN_MEASURED_MATRIX_UNCHANGED','run93_sha256':PIN,'matrix_q7':matrix,'new_calibration':False}))
if __name__=='__main__':main()
