#!/usr/bin/env python3
from pathlib import Path
import importlib.util, json

D=Path(__file__).resolve().parent
R=D.parents[2]
safe=json.loads((D/"TUNING-SAFE.json").read_text())
out=json.loads((D/"PRIVATE-VALIDATION-SAFE.json").read_text())
decpath=D.parent/"e006a-windows-rear-rtcdm-targeted-corpus"/"decode_rear_rtcdm.py"
spec=importlib.util.spec_from_file_location("e006a_dec",decpath)
dec=importlib.util.module_from_spec(spec); spec.loader.exec_module(dec)
private=Path("/home/geoca/Documents/SP11-PROJECT/06-camera/private/e006a/E006A-PRIVATE-RECORDS-v2.json")
j=json.loads(private.read_text(encoding="utf-8-sig"))

q=safe["reserve"]["m_q10_roundf"]
cx0=safe["reserve"]["c_x0"]; cx1=safe["reserve"]["c_x1"]
o=safe["reserve"]["o"]; ss=safe["reserve"]["s"]
state={
 "enabled":True,
 "c00":cx0[0],"c10":cx0[1],"c20":cx0[2],
 "c01":cx1[0],"c11":cx1[1],"c21":cx1[2],
 "m00":q[0],"m01":q[1],"m02":q[2],
 "m10":q[3],"m11":q[4],"m12":q[5],
 "m20":q[6],"m21":q[7],"m22":q[8],
 "o0":o[0],"o1":o[1],"o2":o[2],
 "s0":ss[0],"s1":ss[1],"s2":ss[2],
}
def s13(v): return v & 0x1fff
def pair(a,b): return s13(a)|(s13(b)<<16)
def hi13(v): return s13(v)<<19
def clamp(v): return (v&0xfff)<<20
model=[
 1 if state["enabled"] else 0,
 pair(state["m00"],state["m01"]),s13(state["m02"]),hi13(state["o0"]),hi13(state["s0"]),clamp(state["c00"]),clamp(state["c01"]),
 pair(state["m10"],state["m11"]),s13(state["m12"]),hi13(state["o1"]),hi13(state["s1"]),clamp(state["c10"]),clamp(state["c11"]),
 pair(state["m20"],state["m21"]),s13(state["m22"]),hi13(state["o2"]),hi13(state["s2"]),clamp(state["c20"]),clamp(state["c21"]),
]
regs=[0x6160]+list(range(0x6168,0x61b0,4))
assert len(model)==len(regs)==19
for expected,n in zip(out["startup"],(0,1)):
    rec=next(x for x in j["records"] if x["n"]==n and x["idx"]==1)
    d=dec.decode(bytes.fromhex(rec["hex"]))
    values={r:v for r,v,_,_ in d["writes"]}
    actual=[values[r] for r in regs]
    assert actual==model
    assert expected["capture"]==n
    assert expected["matched_words"]==19 and expected["total_words"]==19
print("E006R_PRIVATE_VALIDATION_PASS")
print("startup_samples=2 cst12_semantic_match=19/19_each raw_values_printed=false")
