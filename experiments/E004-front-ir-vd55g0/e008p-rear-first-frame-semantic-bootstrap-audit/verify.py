#!/usr/bin/env python3
import json,subprocess
from pathlib import Path
D=Path(__file__).resolve().parent
R=D.parents[2]
subprocess.run(["python3",str(D/"audit-private.py")],check=True)
cov=json.loads((D/"SAFE-BOOTSTRAP-COVERAGE.json").read_text())
var=json.loads((D/"PRIVATE-STARTUP-VARIATION-SAFE.json").read_text())
need={
 "camss-e006z-clean-scalar-bank.inc":"struct e006z_rear_scalar_state",
 "camss-e007a-bpcabf411.inc":"struct e007a_bpcabf411_calc_state",
 "camss-e007b-bfstats25.inc":"struct e007b_bfstats25_calc_state",
 "camss-e007e-bfstats25-dmi.inc":"struct e007e_bf_dmi_state"
}
paths={
 "camss-e006z-clean-scalar-bank.inc":R/"experiments/E004-front-ir-vd55g0/e006z-rear-clean-scalar-bank-providers/camss-e006z-clean-scalar-bank.inc",
 "camss-e007a-bpcabf411.inc":R/"experiments/E004-front-ir-vd55g0/e007a-rear-bpcabf411-calculated-provider/camss-e007a-bpcabf411.inc",
 "camss-e007b-bfstats25.inc":R/"experiments/E004-front-ir-vd55g0/e007b-rear-bfstats25-calculated-provider/camss-e007b-bfstats25.inc",
 "camss-e007e-bfstats25-dmi.inc":R/"experiments/E004-front-ir-vd55g0/e007e-rear-bfstats25-dmi-provider/camss-e007e-bfstats25-dmi.inc"
}
for k,n in need.items(): assert n in paths[k].read_text(),(k,n)
assert len(cov["closed_clean_families"])==8
assert len(cov["seed_handoffs_required"])==11
assert cov["windows_value_replay_required"] is False
assert var["startup_packets_compared"]==4
assert var["bfstats25_common_words"]==29 and var["bfstats25_varying_words"]==29
assert not var["raw_register_values_emitted"]
print("E008p VERIFY PASS")
