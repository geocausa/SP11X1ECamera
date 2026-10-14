#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Reuse pinned own register measurements; no private profile or optical input."""
from pathlib import Path
import hashlib,json
Q=Path(__file__).resolve().parent;R=Q.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 audit=json.loads((Q/'baseline-audit.json').read_text())
 name='src/native-rgb/front-ae/tuning/imx681-front-open-regs.txt'
 source=R/name
 if sha(source)!=audit['repository_pins'][name]:raise RuntimeError('measurement source changed')
 rows=[]
 for line in source.read_text().splitlines():
  line=line.split('#',1)[0].strip()
  if not line:continue
  row=tuple(int(v,0) for v in line.split(','))
  if len(row)!=3 or any(v<0 or v>0xffffffff for v in row) or row[0]&3 or row[0]>0xffffff:
   raise RuntimeError('malformed measurement row')
  rows.append(row)
 if len({r for r,_,_ in rows})!=len(rows):raise RuntimeError('duplicate register measurement')
 if len(rows)!=30:raise RuntimeError('measurement shape changed')
 activation={0x4960}
 config=[(r,o) for r,a,o in rows if (a&~o&0xffffffff)==0 and r not in activation]
 deferred=[{'register':r,'reason':'activation_requires_owned_ABF_DMI_and_complete_setup' if r in activation else 'preserves_prior_word_bits','unresolved_bits':a&~o&0xffffffff} for r,a,o in rows if r in activation or a&~o&0xffffffff]
 if len(config)!=24 or len(deferred)!=6:raise RuntimeError('coverage shape changed')
 header="""/* SPDX-License-Identifier: GPL-2.0-only */
/* Generated from our existing measured register overrides, not a vendor file.
 * Source, native baseline and exact extraction: baseline-audit.json.
 * Configuration only: no activation, DMI, private carrier, MMIO or ownership.
 * Parent must establish the actual calibrated native processing domain and
 * complete surrounding BLS/ABF setup. Geometry/tag alone are not that proof.
 */
#ifndef SP11_FRONT_MEASURED_CONFIG_H
#define SP11_FRONT_MEASURED_CONFIG_H
#include "sp11-cdm.h"

#define SP11_FRONT_MEASURED_CONFIG_WORDS 24U
#define SP11_FRONT_MEASURED_CONFIG_BYTES (12U * SP11_FRONT_MEASURED_CONFIG_WORDS)
#define SP11_FRONT_MEASURED_NATIVE_AE74_93 1U

struct sp11_front_measured_domain {
	u32 calibration;
	u32 sensor_width;
	u32 sensor_height;
	u32 output_width;
	u32 output_height;
};

static const struct {
	u32 reg;
	u32 value;
} sp11_front_measured_words[SP11_FRONT_MEASURED_CONFIG_WORDS] = {
"""
 header+=''.join('\t{ 0x%04xU, 0x%08xU },\n'%(r,o) for r,o in config)
 header+="""};

/* Reuse exactly the native 2160 -> 1440 domain; reject the newer 2640 mode.
 * Unknown preserved bits and the ABF activation are deliberately absent.
 * Immutable caller domain/output extents; publish atomically after validation.
 */
static inline int sp11_front_measured_config(
	u8 *out, size_t capacity, const struct sp11_front_measured_domain *domain)
{
	u8 tmp[SP11_FRONT_MEASURED_CONFIG_BYTES];
	unsigned int i;
	int ret;

	if (!out || !domain)
		return -EINVAL;
	if (capacity < sizeof(tmp))
		return -ENOSPC;
	if (sp11_cdm_overlap(out, sizeof(tmp), domain, sizeof(*domain)))
		return -EINVAL;
	if (domain->calibration != SP11_FRONT_MEASURED_NATIVE_AE74_93 ||
	    domain->sensor_width != 3840 || domain->sensor_height != 2160 ||
	    domain->output_width != 2560 || domain->output_height != 1440)
		return -EOPNOTSUPP;
	for (i = 0; i < SP11_FRONT_MEASURED_CONFIG_WORDS; i++) {
		ret = sp11_cdm_reg_cont(tmp + 12 * i, 12,
					sp11_front_measured_words[i].reg,
					&sp11_front_measured_words[i].value, 1);
		if (ret)
			return ret;
	}
	memcpy(out, tmp, sizeof(tmp));
	return 0;
}
#endif
"""
 (Q/'sp11-front-measured-config.h').write_text(header)
 result={'schema':'sp11-own-measured-configuration-fragment-v1','source_pin':sha(source),
 'source_rows':30,'full_configuration_words':24,'bytes':288,'dmi':0,'activation_writes':0,
 'deferred':deferred,'header_sha256':sha(Q/'sp11-front-measured-config.h'),
 'baseline':'native-ae74/93 3840x2160->2560x1440','new_calibration':False,
 'private_profile_read':False,'complete_startup':False,'hardware_qualified':False}
 (Q/'GENERATED.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['source_rows','full_configuration_words','bytes','activation_writes','new_calibration','complete_startup']}))
if __name__=='__main__':main()
