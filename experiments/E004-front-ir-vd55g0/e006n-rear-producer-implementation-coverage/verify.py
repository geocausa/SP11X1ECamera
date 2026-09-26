#!/usr/bin/env python3
from pathlib import Path
import json
D=Path(__file__).resolve().parent
j=json.loads((D/"COVERAGE.json").read_text())
assert j["schema"]=="E006n-rear-producer-implementation-coverage-v1"
assert len(j["steady_dynamic"])==10
assert len(j["startup_extra"])==15
assert j["safe_value_providers"]["steady_singleton"]["register_count"]==468
assert j["safe_value_providers"]["steady_dynamic"]["register_count"]==25
assert j["safe_value_providers"]["startup_differs"]["register_count"]==37
assert j["safe_value_providers"]["startup_only"]["register_count"]==184
assert sum(j["safe_value_providers"][x]["register_count"] for x in ("steady_singleton","steady_dynamic","startup_differs","startup_only"))==714
assert j["steady_dynamic"]["GIC"]["status"]=="DERIVED_FROM_LSC_ALIAS_REUSABLE"
assert j["startup_extra"]["VFE680_PERIOD_CFG"]["status"]=="TRANSPORT_STATE_EXISTING_LINUX_CONTRACT"
assert j["native_rear_linux_isp_authorized"] is False
print("E006N_VERIFY_PASS")
print("steady_families=10 startup_extra=15 startup_partition=714")
print("immediately_safe_singletons=468")
