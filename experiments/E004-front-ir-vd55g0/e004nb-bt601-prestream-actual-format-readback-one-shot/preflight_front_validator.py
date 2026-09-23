#!/usr/bin/env python3
"""Pre-arm test: reuse ONLY previous physical E004mx text/aggregate evidence.

Distinct new source-defined boot token emits E004NB_ metric labels, so
relabel JUST the previous text event prefix in a TEMPORARY isolated
directory (never alter original evidence, numeric values or photos).
No sensor camera/image network or native controls. Only four exact
scalar JSON/txt files are read, all text output transient.
"""
from pathlib import Path
import json,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parent
PREV=ROOT.parent/"e004mx-front-gain-tone-guarded-one-shot"/"evidence"
TEXT=("FRONT-DAYLIGHT-PROBE.json","FRONT-GAIN-PROBE.json",
      "RGB-SELECTOR-ACCEPTANCE.json","front-SERVICE-STDERR.txt")
def verify()->dict:
    source=(ROOT/"validate_front_tone_live.py").read_text()
    assert not any(ord(c)<32 and ord(c) not in (9,10,13) for c in source)
    assert chr(92)+"bframe=" in source
    assert "E004NB_PAIRED_RAW_NV12" in source
    originals={name:(PREV/name).read_text() for name in TEXT}
    assert '"status": "PASS_REAL_OPT_IN_RGB_SELECTOR_UID1000_FRONT1080_REAR4K"' in originals["RGB-SELECTOR-ACCEPTANCE.json"]
    assert originals["front-SERVICE-STDERR.txt"].count("E004MX_PAIRED_RAW_NV12 camera=front frame=")>=10
    assert originals["front-SERVICE-STDERR.txt"].count("E004MX_FRONT_PREVIEW_TONE frame=")>=12
    with tempfile.TemporaryDirectory(prefix="sp11-e004nb-front-preflight-") as td:
        d=Path(td)
        for name in TEXT:
            text=originals[name]
            if name=="front-SERVICE-STDERR.txt":
                text=text.replace("E004MX_PAIRED_RAW_NV12 camera=front frame=",
                                  "E004NB_PAIRED_RAW_NV12 camera=front frame=")
                text=text.replace("E004MX_FRONT_PREVIEW_TONE frame=",
                                  "E004NB_FRONT_PREVIEW_TONE frame=")
                assert "E004NB_FRONT_PREVIEW_TONE frame=600" in text
            (d/name).write_text(text)
        result=subprocess.run((sys.executable,str(ROOT/"validate_front_tone_live.py"),str(d)),
                  check=True,capture_output=True,text=True,timeout=12)
        parsed=json.loads(result.stdout)
    assert parsed["status"]=="PASS_REAL_FRONT_OPTIN_GAIN_ONLY_TONE_1080P_WITH_UID1000_APP_FPS"
    assert len(parsed["four_30_frame_real_gain_window_fps"])==4
    assert all(x>=29 for x in parsed["four_30_frame_real_gain_window_fps"])
    return {"status":"E004NB_PREFLIGHT_CORRECTED_VALIDATOR_PREVIOUS_REAL_FRONT_SCALAR_ONLY_PASS",
        "event_labels_rewritten_only_in_temporary_nonoptical_text":True,
        "original_private_images_and_physical_boot_untouched":True,
        "actual_real_previous_source_and_ordinary_app_evidence":True,
        "real_source_test_not_new_E004nb_physical_acceptance":True,
        "native_front_source_fps_previous_trial":parsed["actual_front_native_full_session_fps"],
        "four_previous_30frame_gain_source_fps":parsed["four_30_frame_real_gain_window_fps"],
        "new_E004nb_full_independent_physical_one_shot_passed":False}

if __name__=="__main__":
    print(json.dumps(verify(),sort_keys=True,indent=2))
