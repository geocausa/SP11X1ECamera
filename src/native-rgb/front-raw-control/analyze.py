#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Camera-free aggregate RAW plateau analysis. Never accepts an SOF delay."""
import math
import statistics

def median(v):
    return statistics.median(v)

def noise(v):
    m=median(v)
    return max(1e-5, 1.4826*median([abs(x-m) for x in v]))

def analyze(frames):
    if len(frames)!=320 or [f["sequence"] for f in frames]!=list(range(320)):
        raise ValueError("complete sequential 320-frame metrology required")
    for f in frames:
        if len(f["channels"])!=4:
            raise ValueError("four Bayer phases required")
        for i,c in enumerate(f["channels"]):
            if c["phase"]!=i or c["samples"]<=0 or not all(
                math.isfinite(c[k]) and c[k]>=0 for k in
                ["mean","variance","zero_fraction","storage_saturation_fraction"]):
                raise ValueError("invalid raw channel")
    def window(step,ch,key="mean"):
        return [f["channels"][ch][key] for f in frames[step*16+8:step*16+16]]
    result={"analysis":"raw_code_value_response_above_temporal_noise",
        "calibrated_brightness":False, "gain_law_optically_verified":False,
        "sensor_application_delay_qualified":False,
        "frame_sync_reference_available":False, "fields":{}}
    for field,first in [("exposure",1),("analogue_gain",7),("digital_gain",13)]:
        cycles=[]
        for step in range(first,first+6,2):
            channels=[]
            for ch in range(4):
                low=window(step-1,ch);high=window(step,ch);restore=window(step+1,ch)
                baseline=median(low);raised=median(high);restored=median(restore)
                n=max(noise(low),noise(high),noise(restore))
                up=raised-baseline;down=raised-restored
                # No absolute-luma percentage threshold and no assumed black pedestal.
                returned=abs(restored-baseline)<=max(8*n,0.25*min(up,down))
                clipped=max(window(step-1,ch,"storage_saturation_fraction")+
                    window(step,ch,"storage_saturation_fraction")+
                    window(step+1,ch,"storage_saturation_fraction"))
                response=up>8*n and down>8*n and returned and clipped<0.001
                channels.append({"phase":ch,"baseline":baseline,"raised":raised,
                    "restored":restored,"increase":up,"decrease":down,
                    "temporal_noise":n,"restored_baseline_accepted":returned,
                    "max_storage_saturation_fraction":clipped,
                    "reversible_positive_response":response})
            cycles.append({"raised_step":step,"channels":channels})
        accepted=[all(c["channels"][ch]["reversible_positive_response"] for c in cycles)
                  for ch in range(4)]
        result["fields"][field]={"cycles":cycles,
            "phase_response_repeatable":accepted,
            "all_four_phases_repeatable":all(accepted)}
    return result
