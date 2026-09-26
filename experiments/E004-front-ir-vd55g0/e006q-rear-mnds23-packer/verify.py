#!/usr/bin/env python3
from pathlib import Path
import json

D=Path(__file__).resolve().parent
safe=json.loads((D/"PRIVATE-VALIDATION-SAFE.json").read_text(encoding="utf-8-sig"))
src=(D/"camss-e006q-mnds23.inc").read_text()

assert safe["schema"]=="E006q-mnds23-private-validation-v1"
assert safe["raw_private_values_committed"] is False
assert safe["titan680_static"]["phase_scale"]==1<<21
assert safe["titan680_static"]["interpolation_thresholds"]==[64,32,16]
assert len(safe["startup"])==2
for st in safe["startup"]:
    assert st["input"]=={"width":4064,"height":2286}
    assert st["luma_output"]=={"width":3840,"height":2160}
    assert st["chroma_output"]=={"width":1920,"height":1080,"h_div":2,"v_div":2}
    assert st["pre_crop"]=={"firstPixel":0,"firstLine":0,"lastPixel":4063,"lastLine":2285}
    assert st["enabled"] is True and st["stripe_override"] is False
    assert st["luma_ratio"]["horizontal"]=="127/120"
    assert st["luma_ratio"]["vertical"]=="127/120"
    assert st["chroma_ratio"]["horizontal"]=="127/60"
    assert st["chroma_ratio"]["vertical"]=="127/60"
    assert st["exact_semantic_packer_match"]=={"matched_words":20,"total_words":20}

assert "e006q_mnds23_phase" in src
assert "e006q_mnds23_phase_init" in src
assert "e006q_mnds23_frac" in src
assert "e006q_mnds23_lookup" in src
assert "e006q_mnds23_recipe" in src
assert "(u64)input << 21" in src
assert "output * 64U" in src and "output * 32U" in src and "output * 16U" in src
assert "s->stripe_override" in src and "-EOPNOTSUPP" in src

owner=json.loads((D.parent/"e006l-rear-startup-register-ownership"/"STARTUP-REGISTER-OWNER-MAP.json").read_text())
regs={int(x["register"],16) for x in owner["startup_only"] if x["owner"]=="MNDS23"}
expected=set(range(0x9860,0x9888,4)) | set(range(0x9a60,0x9a88,4))
assert regs==expected,(sorted(regs),sorted(expected))
assert len(regs)==20

print("E006Q_VERIFY_PASS")
print("mnds23_regs=20 video_full_luma=10 video_full_chroma=10")
print("private_validation=startup0,startup1 semantic 20/20 exact")
print("geometry=4064x2286 -> Y3840x2160 C1920x1080")
print("raw_private_values=false stripe_override=false")
