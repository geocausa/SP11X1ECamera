#!/usr/bin/env python3
from pathlib import Path
import json

D=Path(__file__).resolve().parent
safe=json.loads((D/"STARTUP-VS-STEADY-SAFE.json").read_text(encoding="utf-8-sig"))

def seq(a,b):
    return list(range(a,b+1,4))

owners={}
def add(owner, regs):
    for r in regs:
        if r in owners:
            raise SystemExit(f"duplicate owner 0x{r:x}: {owners[r]} vs {owner}")
        owners[r]=owner

add("BC101", seq(0x3f60,0x3f68))
add("BAYER_GTM101", [0x4d60])
add("BAYER_LTM101", [0x5260])
add("LCAC111", [0x5460])
add("CST12", [0x6160]+seq(0x6168,0x61ac))
add("UV_GAMMA101", [0x6360])
add("MNDS23", seq(0x9860,0x9884)+seq(0x9a60,0x9a84))

for base in (0x9c00,0x9e00,0xa400,0xa600,0xac00,0xae00):
    add("ROUND_CLAMP12", [base+0x60]+seq(base+0x70,base+0x94))
    add("CROP12", [base+0x68,base+0x6c])

add("AEC_BE_STATS17", seq(0xb060,0xb0a4))
add("BHIST_STATS16", [0xb258,0xb25c])
add("TINTLESS_BG_STATS17", seq(0xb660,0xb6a4))
add("AWB_BG_STATS17", seq(0xb860,0xb8a4))
add("RS_STATS14", [0xbe60]+seq(0xbe68,0xbe70))

startup_only={int(x,16) for x in safe["startup_only_offsets"]}
if set(owners)!=startup_only:
    miss=sorted(startup_only-set(owners))
    extra=sorted(set(owners)-startup_only)
    raise SystemExit(f"startup-only owner mismatch miss={[hex(x) for x in miss]} extra={[hex(x) for x in extra]}")

steady_dynamic={
  0x3b70:"DEMUX_BLS",0x3b74:"DEMUX_BLS",
  0x3d58:"PDPC",0x3d5c:"PDPC",0x3d7c:"PDPC",0x3d84:"PDPC",
  0x4358:"LSC",0x435c:"LSC",
  0x456c:"WB",
  0x4758:"GIC",0x475c:"GIC",
  0x4958:"BPC_ABF",0x495c:"BPC_ABF",0x49b8:"BPC_ABF",0x49bc:"BPC_ABF",
  0x5a58:"GTM",0x5a5c:"GTM",
  0x5f58:"GAMMA",0x5f5c:"GAMMA",
  0xa058:"DSX",0xa05c:"DSX",0xa258:"DSX",0xa25c:"DSX",
  0xbc58:"BFSTATS25",0xbc5c:"BFSTATS25",
}
# The 25-entry steady dynamic owner table is source-locked by E006j.
if len(steady_dynamic)!=25:
    raise SystemExit("steady dynamic table count drift")

startup_diff={
  0x008c:"VFE680_PERIOD_CFG",
  0x3d78:"PDPC",0x3d80:"PDPC",
  0x4570:"WB",
  0x49d0:"BPC_ABF",0x49d4:"BPC_ABF",0x49d8:"BPC_ABF",0x49dc:"BPC_ABF",0x49e0:"BPC_ABF",
  0xb26c:"BHIST_STATS16",
}
for r in [0xbc60]+seq(0xbc6c,0xbcd0):
    startup_diff[r]="BFSTATS25"

expected_diff={int(x,16) for x in safe["startup_differs_from_steady_offsets"]}
if set(startup_diff)!=expected_diff:
    miss=sorted(expected_diff-set(startup_diff)); extra=sorted(set(startup_diff)-expected_diff)
    raise SystemExit(f"startup-diff owner mismatch miss={[hex(x) for x in miss]} extra={[hex(x) for x in extra]}")

reuse={int(x,16) for x in safe["reusable_steady_singleton_offsets"]}
phase={int(x,16) for x in safe["startup_phase_variant_offsets"]}

# Four disjoint categories must cover exactly 714 unique startup registers.
cats={
 "STEADY_SINGLETON_REUSABLE":reuse,
 "STEADY_DYNAMIC_PRODUCER":set(steady_dynamic),
 "STARTUP_DIFFERS_FROM_STEADY":set(startup_diff),
 "STARTUP_ONLY":set(owners),
}
all_regs=set()
for name,regs in cats.items():
    if all_regs & regs:
        raise SystemExit(f"category overlap {name}: {[hex(x) for x in sorted(all_regs & regs)]}")
    all_regs |= regs
if len(all_regs)!=safe["startup_register_count"]:
    raise SystemExit(f"coverage {len(all_regs)} != {safe['startup_register_count']}")

out={
 "schema":"E006l-rear-startup-register-owner-map-v1",
 "source_safe_schema":safe["schema"],
 "startup_register_count":safe["startup_register_count"],
 "partition_counts":{k:len(v) for k,v in cats.items()},
 "phase_variant_count":len(phase),
 "period_cfg":{
   "register":"0x8c",
   "owner":"VFE680_PERIOD_CFG",
   "classification":"stream-local transport state; not IQ; do not transplant Windows value",
 },
 "startup_differs_from_steady":[
   {"register":hex(r),"owner":startup_diff[r],"phase_variant":r in phase}
   for r in sorted(startup_diff)
 ],
 "startup_only":[
   {"register":hex(r),"owner":owners[r],"phase_variant":r in phase}
   for r in sorted(owners)
 ],
 "steady_dynamic":[
   {"register":hex(r),"owner":steady_dynamic[r],"phase_variant":r in phase}
   for r in sorted(steady_dynamic)
 ],
 "reusable_steady_singleton_offsets":[hex(r) for r in sorted(reuse)],
 "unresolved_owner_count":0,
 "raw_values_committed":False,
 "private_bytes_committed":False,
}
(D/"STARTUP-REGISTER-OWNER-MAP.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print("E006L_OWNER_MAP_PASS")
print("partition",out["partition_counts"])
print("startup_only_owners",len(set(owners.values())))
print("startup_diff_owners",len(set(startup_diff.values())))
print("unresolved",out["unresolved_owner_count"])
