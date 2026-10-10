#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Private Windows08/native08 registered chart comparison; prints aggregate scalars only."""
import argparse,importlib.util,json,os,stat,subprocess
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
NATIVE=Path("/var/lib/sp11-camera-native-front-param-queue-20261010-08")
OUTPUT=Path("/var/lib/sp11-camera-windows-front-quality-20261010-08")
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--windows-root",required=True);args=ap.parse_args()
    assert os.geteuid()==0
    assert "BOOT_IMAGE=/boot/sp11-7.1.5-audio-fullio-v19c/" in Path("/proc/cmdline").read_text()
    windows=Path(args.windows_root)
    assert str(windows).startswith("/run/sp11-windows-")
    assert "ro" in subprocess.check_output(["findmnt","-rn","-T",str(windows),"-o","OPTIONS"],text=True).strip().split(",")
    result=json.loads((windows/"RESULT.json").read_text())
    assert result["identity"]=="E-WINDOWS-FRONT-QUALITY-20261010-08"
    assert result["status"]=="PASS_WINDOWS_FRONT_NATIVE_NV12_PRIVATE_CAPTURE" and result["clean_stop_release"]
    assert len(result["samples"])==8 and result["private_native_frames_saved"]==3
    assert len({p["system_relative_ticks"] for p in result["samples"]})==8
    assert (windows/"CONSUMED.txt").is_file()
    assert json.loads((windows/"RETIREMENT.json").read_text())["task_unregistered"]
    spec=importlib.util.spec_from_file_location("strict",ROOT/"src/native-rgb/front-windows-quality/register-fiducial-chart.py")
    f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
    rows=[]
    for seq in (1,4,7):
        path=windows/("frame-"+str(seq)+".nv12")
        assert not path.is_symlink() and path.stat().st_uid==0 and stat.S_IMODE(path.stat().st_mode)==0o600 and path.stat().st_size==5529600
        data=np.fromfile(path,np.uint8);y=data[:3686400].reshape(1440,2560);uv=data[3686400:].reshape(720,1280,2)
        saved=result["samples"][seq]
        for name,values in (("Y",y.ravel()),("U",uv[:,:,0].ravel()),("V",uv[:,:,1].ravel())):
            v=values.astype(np.float64);stats=saved[name]
            assert abs(v.mean()-stats["mean"])<1e-8 and abs(v.std()-stats["std"])<1e-8
            assert int(v.min())==stats["min"] and int(v.max())==stats["max"]
            for p in (1,50,99):assert int(np.percentile(values,p,method="lower"))==stats["p"+str(p).zfill(2)]
        rows.append({"sequence":seq,"private_registration":f.locate(y,uv)})
    native=json.loads((NATIVE/"PRIVATE-CHART-REGISTRATION.json").read_text())
    qualified=[x for x in native["private_rows"] if x["private_registration"]["qualified"] and x["private_registration"].get("photometric_gray_order_qualified",False)]
    geometry=sum(bool(x["private_registration"]["qualified"]) for x in rows)
    gray=sum(bool(x["private_registration"].get("photometric_gray_order_qualified",False)) for x in rows)
    summary={"identity":result["identity"],"native_identity":native["summary"]["identity"],
        "original_whole_frame_metrics_reproduced":True,"Windows_geometry_passes":geometry,"Windows_gray_order_passes":gray,
        "Windows_frames_assessed":3,"native_qualified_frames":len(qualified),
        "geometry_reasons":{reason:sum(x["private_registration"]["reason"]==reason for x in rows) for reason in sorted({x["private_registration"]["reason"] for x in rows})},
        "registered_comparison_possible":geometry==3 and gray==3 and len(qualified)>=3,
        "same_sensor_controls_proven":False,"same_cross_boot_illumination_proven":False,
        "color_space_and_range_qualified":False,"automatic_feedback_enabled":False,
        "Windows_quality_parity_proven":False,"spatial_patch_results_exported":False}
    errors=[]
    if summary["registered_comparison_possible"]:
        wp=[x["private_registration"]["private_patches"] for x in rows]
        reference=np.median(np.array([[p["mean_Y"],p["mean_U"],p["mean_V"]] for patches in wp for p in patches]).reshape(3,12,3),axis=0)
        for plateau in sorted({x["plateau"] for x in qualified}):
            npatches=[x["private_registration"]["private_patches"] for x in qualified if x["plateau"]==plateau]
            candidate=np.median(np.array([[[p["mean_Y"],p["mean_U"],p["mean_V"]] for p in patches] for patches in npatches]),axis=0)
            delta=candidate-reference
            errors.append({"native_plateau":plateau,"native_frames":len(npatches),
                "gray_luma_mean_absolute_difference_8bit":float(np.mean(np.abs(delta[:6,0]))),
                "color_luma_mean_absolute_difference_8bit":float(np.mean(np.abs(delta[6:,0]))),
                "color_U_mean_absolute_difference_8bit":float(np.mean(np.abs(delta[6:,1]))),
                "color_V_mean_absolute_difference_8bit":float(np.mean(np.abs(delta[6:,2])))})
        summary["registered_aggregate_errors"]=errors
    summary["status"]="PASS_REGISTERED_COMPARISON_MEASUREMENTS_PARITY_UNPROVEN" if summary["registered_comparison_possible"] else "FAILED_WINDOWS07_STRICT_GEOMETRY_GATE"
    os.umask(0o077)
    with (OUTPUT/"PRIVATE-WINDOWS-NATIVE07-COMPARISON.json").open("x") as out:
        json.dump({"summary":summary,"private_Windows_registration":rows,"private_native_registration":native},out,indent=2);out.write("\n")
    print(json.dumps(summary,sort_keys=True))
if __name__=="__main__":main()
