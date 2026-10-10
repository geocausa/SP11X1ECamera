#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Whole-frame scalar diagnostic gates. No patch geometry or quality calibration."""
import math
def cci_sequence_matches(commits, readbacks, stream_index):
    expected=list(range(stream_index*6,(stream_index+1)*6))
    return len(commits)==6 and len(readbacks)==6 and [p[0] for p in commits]==expected and [p[0] for p in readbacks]==expected

def evaluate(streams):
    if len(streams)!=5 or any(len(p)!=6 for p in streams):
        raise ValueError("five streams/six plateaus required")
    keys=("green_median","Y_median","U_median","V_median")
    if any(not math.isfinite(p[k]) for st in streams for p in st for k in keys):
        raise ValueError("nonfinite diagnostic")
    stable=[];responses=[]
    for j in range(6):
        a,b=streams[0][j],streams[4][j]
        stable.append(abs(b["green_median"]-a["green_median"])<=0.05*max(a["green_median"],1)
                      and abs(b["Y_median"]-a["Y_median"])<=max(2,0.1*a["Y_median"])
                      and abs(b["U_median"]-a["U_median"])<=2
                      and abs(b["V_median"]-a["V_median"])<=2)
    for channel,index in zip(("red","green","blue"),(1,2,3)):
        groups=[]
        for j in range(5):
            p=streams[index][j];a,b=streams[0][j],streams[4][j]
            baseline={k:a[k]+(b[k]-a[k])*index/4 for k in keys}
            y,u,v=[p[k]-baseline[k] for k in keys[1:]]
            raw_ratio=p["green_median"]/max(baseline["green_median"],1)
            # Direction under ordinary positive RGB-to-YUV matrices; magnitudes
            # are engineering diagnostics, not calibrated colour coefficients.
            direction={"red":y>0.5 and v>0.5 and u<-0.1,
                       "green":y>0.5 and u<-0.5 and v<-0.5,
                       "blue":y>0.1 and u>0.5 and v<-0.05}[channel]
            accepted=stable[j] and 0.95<=raw_ratio<=1.05 and direction
            groups.append({"plateau":j,"delta_Y":y,"delta_U":u,"delta_V":v,
                           "raw_green_ratio":raw_ratio,"baseline_stable":stable[j],
                           "channel_direction_matches":direction,"qualified":accepted})
        count=sum(p["qualified"] for p in groups)
        responses.append({"channel":channel,"qualified_plateaus":count,"qualified":count>=2,"groups":groups})
    return {"qualified":all(r["qualified"] for r in responses),
            "baseline_stable_plateaus":sum(stable),"channels":responses,
            "scope":"Independent single-channel gamma causes output response with stable raw-green and baseline recovery; no calibrated curve, per-pixel match, full encoding accuracy or Windows parity",
            "scalar_only":True,"spatial_registration_required_for_calibration":True}

if __name__=="__main__":
    import json,sys
    print(json.dumps(evaluate(json.load(open(sys.argv[1]))),indent=2))
