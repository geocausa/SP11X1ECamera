#!/usr/bin/env python3
import json, math
from pathlib import Path
import gain_adjust as g

def need(x,msg):
    if not x: raise AssertionError(msg)

t=g.GainAdjustTuning()
need(t.enable==1,'GA disabled')
need(len(t.triangles)==44 and len(t.vertices)==32 and len(t.outer)==2,'topology counts')
# Neighbor topology must be reciprocal for every non-sentinel edge.
for i,tr in enumerate(t.triangles):
    for n in tr.neighbors:
        if n!=255: need(i in t.triangles[n].neighbors,f'neighbor reciprocity {i}->{n}')
# Every triangle centroid must select that triangle (no overlap at centroid) and yield 1/3-ish exact weights.
for i,tr in enumerate(t.triangles):
    pts=[t.vertices[v] for v in tr.v]; rg=sum(v.rg for v in pts)/3; bg=sum(v.bg for v in pts)/3
    got,_,w=g.find_triangle(t,rg,bg); need(got==i,f'centroid triangle {i} selected {got}')
    need(abs(sum(w)-1.0)<2e-6,f'weights sum T{i}')
# Known all-unity point: V0, Lux 100, CCT 5000.
v0=t.vertices[0]; a=g.adjust(t,v0.rg,v0.bg,100.0,5000.0)
need(a['final_bits']==['0x3f800000']*3,'unity fixture')
# V28 has an exact non-unity Lux-band vector at 180..203; top CCT branch is unity for Lux<290.
v=t.vertices[28]; a=g.adjust(t,v.rg,v.bg,190.0,5000.0)
need(a['final_bits']==['0x3f828f5c','0x3f800000','0x3f71eb85'],f'V28 fixture {a["final_bits"]}')
# V0 is unity in the triangle table; at Lux=400/CCT=2000 the top CCT adjustment is exact second child.
a=g.adjust(t,v0.rg,v0.bg,400.0,2000.0)
need(a['final_bits']==['0x3f82d0e5','0x3f800000','0x3f770a3d'],f'CCT fixture {a["final_bits"]}')
# Outer Lux gap 290..330: Lux 310 is midpoint between unity branch and low-CCT adjusted branch.
a=g.adjust(t,v0.rg,v0.bg,310.0,2000.0)
exp=[g.bits(g.f32((1.0+1.0219999551773071)/2)),g.bits(1.0),g.bits(g.f32((1.0+0.9649999737739563)/2))]
need([int(x,16) for x in a['final_bits']]==exp,'outer gap midpoint')
out={'schema':'sp11-e003i-ef-clean-awb-gain-adjust-replay-v1','status':'PASS_OFFLINE_STATIC_CORE',
     'tuning_sha256':g.TUNING_SHA256,'triangles':44,'vertices':32,'outer_trigger':'LuxIndex',
     'inner_trigger':'CCT_from_RG_BG_temperature_converter','contained_triangle_path':True,
     'windows_differential_same_request':False,'continuous_aec':False}
Path(__file__).with_name('RESULT.json').write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,indent=2))
