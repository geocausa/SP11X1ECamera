#!/usr/bin/env python3
from pathlib import Path
import json,re

D=Path(__file__).resolve().parent
safe=json.loads((D/"PRIVATE-VALIDATION-SAFE.json").read_text(encoding="utf-8-sig"))
s=(D/"camss-e006p-crop-roundclamp.inc").read_text()

assert safe["schema"]=="E006p-video-geometry-private-validation-v1"
assert len(safe["startup"])==2
expected={
 "full":((3840,2160),(1920,1080)),
 "ds4":((960,540),(480,270)),
 "ds16":((240,136),(120,68)),
}
for st in safe["startup"]:
    for p in st["paths"]:
        name=p["path"]; assert name in expected
        assert (p["luma_crop"]["width"],p["luma_crop"]["height"])==expected[name][0]
        assert (p["chroma_crop"]["width"],p["chroma_crop"]["height"])==expected[name][1]
        assert p["luma_crop"]["firstPixel"]==0 and p["luma_crop"]["firstLine"]==0
        assert p["chroma_crop"]["firstPixel"]==0 and p["chroma_crop"]["firstLine"]==0
        assert p["roundclamp_matches"]==[{"bit_width":10,"enabled":True}]

assert "e006p_crop12_pack" in s
assert "e006p_roundclamp_word" in s
assert "e006p_crop12_recipe" in s
assert "e006p_roundclamp12_recipe" in s
assert "0x3c01" in s and "0x0c01" in s
assert "path->bit_width < 11 ? 10 - path->bit_width : 0" in s

# Exact E006l ownership coverage: 12 Crop12 + 66 RoundClamp12.
l=json.loads((D.parent/"e006l-rear-startup-register-ownership"/"STARTUP-REGISTER-OWNER-MAP.json").read_text())
crop={int(x["register"],16) for x in l["startup_only"] if x["owner"]=="CROP12"}
rnd={int(x["register"],16) for x in l["startup_only"] if x["owner"]=="ROUND_CLAMP12"}
assert len(crop)==12 and len(rnd)==66 and not (crop & rnd)
expected_crop=set()
expected_rnd=set()
for lbase,cbase in ((0x9c60,0x9e60),(0xa460,0xa660),(0xac60,0xae60)):
    for base in (lbase,cbase):
        expected_crop |= {base+8,base+12}
        expected_rnd.add(base)
        expected_rnd |= {base+0x10+4*i for i in range(10)}
assert crop==expected_crop,(sorted(crop),sorted(expected_crop))
assert rnd==expected_rnd,(sorted(rnd),sorted(expected_rnd))

print("E006P_VERIFY_PASS")
print("crop12_regs=12 roundclamp12_regs=66 total=78")
print("private_validation=startup0,startup1 exact semantic matches")
print("inputs=semantic_geometry+bit_width+enable raw_private_values=false")
