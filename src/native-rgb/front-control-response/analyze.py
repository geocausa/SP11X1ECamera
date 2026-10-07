#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Pure diagnostic analysis: control response, not optical quality or 3A tuning."""
import math
import statistics


def median(values):
    return statistics.median(values)


def noise(values):
    center = median(values)
    return 1.4826 * median([abs(v-center) for v in values])


def analyze_field(luma, output, commands, field):
    """Require three restored cycles and six sharp, consistent transitions."""
    observed = []
    reasons = []
    for command in commands:
        n = command["sof"]
        before = luma[n-8:n-2]
        after = luma[n+6:n+14]
        old, new = median(before), median(after)
        sigma = max(noise(before), noise(after), 1e-6)
        delta = new-old
        rising = command["step"] % 2 == 1
        threshold = (old+new)/2
        separation = max(8*sigma, abs(old)*0.15, 1e-4)
        error = []
        if (delta > 0) != rising or abs(delta) <= separation:
            error.append("insufficient directional statistics response")
        tolerance = max(abs(delta)*0.1, 4*sigma, 1e-5)
        def crossed(value):
            return value > threshold if rising else value < threshold
        candidates = [i for i in range(n,n+7)
                      if all(crossed(v) for v in luma[i:i+3])]
        stable = [i for i in range(n,n+7)
                  if all(abs(v-new)<=tolerance for v in luma[i:i+3])]
        start = candidates[0] if candidates else None
        settled = stable[0] if stable else None
        if not candidates or not stable or start != settled:
            error.append("ambiguous or gradual statistics transition")
        if candidates and (crossed(luma[n-1]) or
                           any(abs(v-old)>tolerance for v in luma[n:start])):
            error.append("pre-command drift or intermediate transition")
        old_y = median(output[n-8:n-2])
        new_y = median(output[n+6:n+14])
        y_sigma = max(noise(output[n-8:n-2]), noise(output[n+6:n+14]), 1e-6)
        if ((new_y>old_y) != rising or
            abs(new_y-old_y) <= max(4*y_sigma, abs(old_y)*0.005, 1e-4)):
            error.append("processed-output response not corroborated")
        observed.append({"step":command["step"],"command_sof":n,"field":field,
            "statistics_before":old,"statistics_after":new,
            "statistics_noise_estimate":sigma,"statistics_response":delta,
            "processed_y_before":old_y,"processed_y_after":new_y,
            "threshold_crossing_sequence":start,"stable_response_sequence":settled,
            "response_offset":None if start is None else start-n,
            "sharp_transition_screen_passed":not error,"reasons":error})
    cycles = []
    for index in range(0,len(commands),2):
        up,down = commands[index],commands[index+1]
        before = luma[up["sof"]-8:up["sof"]-2]
        restored = luma[down["sof"]+6:down["sof"]+14]
        low,returned = median(before),median(restored)
        uncertainty = max(noise(before),noise(restored),1e-6)
        drift = abs(returned-low)
        stable = drift <= max(abs(low)*0.05, 8*uncertainty, 1e-4)
        if not stable:
            reasons.append("baseline changed across restored cycle")
        cycles.append({"cycle":index//2,"baseline_before":low,"baseline_restored":returned,
                       "baseline_absolute_change":drift,"baseline_screen_passed":stable})
    reasons.extend(reason for item in observed for reason in item["reasons"])
    offsets = [x["response_offset"] for x in observed]
    if len(set(offsets)) != 1 or offsets[0] is None:
        reasons.append("response offset inconsistent across six changes")
    return {"field":field,"three_restored_cycles":cycles,"transitions":observed,
        "response_timing_qualified":not reasons,
        "observed_response_delay_frames":offsets[0] if not reasons else None,
        "reasons":sorted(set(reasons)),"lighting_reference_instrumented":False,
        "lighting_screen":"repeated restored-baseline comparison only"}


def analyze(luma, output, commands, frame_association):
    if len(luma)<324 or len(output)!=320 or len(commands)!=18:
        raise ValueError("response analysis needs complete ordered capture")
    if any(not math.isfinite(v) or v<0 for v in luma+output):
        raise ValueError("response samples must be finite and nonnegative")
    # App pixels cover hardware sequences4..323; startup remains private/internal.
    pixels = [output[0]]*4+output
    fields = [analyze_field(luma,pixels,commands[i:i+6],field)
              for i,field in [(0,"exposure"),(6,"analogue"),(12,"digital")]]
    if not frame_association:
        for field in fields:
            field["response_timing_qualified"] = False
            field["observed_response_delay_frames"] = None
            field["reasons"].append("receiver/video source association changed")
    return {"fields":fields,"all_fields_response_timing_qualified":all(
                x["response_timing_qualified"] for x in fields),
            "source_frame_association_observed":frame_association,
            "sensor_exposure_timestamp_proven":False,
            "DelayedControls_parameters_qualified":False,
            "automatic_feedback_enabled":False,"optical_quality_parity_proven":False,
            "metering_domain_optically_qualified":False}
