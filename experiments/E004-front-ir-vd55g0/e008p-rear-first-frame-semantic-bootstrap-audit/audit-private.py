#!/usr/bin/env python3
import importlib.util,json
from pathlib import Path
D=Path(__file__).resolve().parent
R=D.parents[2]
P=R.parent/"private/e006a/E006A-PRIVATE-RECORDS-v2.json"
DEC=R/"experiments/E004-front-ir-vd55g0/e006a-windows-rear-rtcdm-targeted-corpus/decode_rear_rtcdm.py"
spec=importlib.util.spec_from_file_location("dec",DEC)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
records=json.load(open(P,encoding="utf-8-sig"))
maps=[]
for n in range(4):
    rec=next(x for x in records["records"] if x["n"]==n and x["idx"]==1 and x.get("complete"))
    parsed=m.decode(bytes.fromhex(rec["hex"]))
    maps.append({r:v for r,v,*_ in parsed["writes"]})
common=set.intersection(*(set(x) for x in maps))
vary=sorted(r for r in common if len({x[r] for x in maps})>1)
bf=[0xbc58,0xbc5c,0xbc60,*range(0xbc6c,0xbcd4,4)]
bf=[r for r in bf if r in common]
bf_vary=[r for r in bf if r in vary]
assert len(bf)==29 and len(bf_vary)==29
safe={
 "schema":"E008P-private-startup-variation-safe-v1",
 "startup_packets_compared":4,
 "common_registers":len(common),
 "varying_common_registers":len(vary),
 "bfstats25_common_words":len(bf),
 "bfstats25_varying_words":len(bf_vary),
 "all_bfstats25_words_vary_across_startup":True,
 "raw_register_values_emitted":False,
 "raw_packet_bytes_emitted":False
}
(D/"PRIVATE-STARTUP-VARIATION-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
print("E008P_PRIVATE_VARIATION_AUDIT_PASS")
