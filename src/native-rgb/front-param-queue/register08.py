#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Private offline strict chart assessment. Never prints spatial/image data."""
import importlib.util,json,os,re,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
D=Path("/var/lib/sp11-camera-native-front-param-queue-20261010-08")
def main():
    assert os.geteuid()==0
    assert "BOOT_IMAGE=/boot/sp11-7.1.5-audio-fullio-v19c/" in Path("/proc/cmdline").read_text()
    result=json.loads((D/"RESULT.json").read_text())
    assert result["identity"]=="E-NATIVE-FRONT-PARAM-QUEUE-20261010-08"
    assert result["status"]=="PASS_FRONT_CHART_CAPTURE_CLEAN"
    assert (D/"ATTEMPT-CONSUMED").is_file()
    target=D/"PRIVATE-CHART-REGISTRATION.json"
    assert not target.exists()
    source=ROOT/"src/native-rgb/front-windows-quality/register-fiducial-chart.py"
    spec=importlib.util.spec_from_file_location("strict_chart",source)
    f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
    stream=result["streams"][0]
    series=stream["observation"]["whole_frame_scalar_series"]
    assert len(series)==96
    files={int(re.search(r"-(\d+)\.bin$",p.name)[1]):p for p in (D/"lift-all").glob("frame-*.bin")}
    assert set(files)=={p["sequence"] for p in series}
    rows=[]
    # Three predetermined settled frames per distinct manual plateau.
    # No selection by measured spatial/image response.
    for plateau in range(5):
        for offset in (8,12,15):
            request=plateau*16+offset
            p=files[series[request]["sequence"]]
            assert p.stat().st_size==5529600 and p.stat().st_mode&0o077==0
            data=np.fromfile(p,np.uint8)
            y=data[:3686400].reshape(1440,2560)
            uv=data[3686400:].reshape(720,1280,2)
            registration=f.locate(y,uv)
            rows.append({"request":request,"plateau":plateau,"sequence":series[request]["sequence"],"private_registration":registration})
    summary={"identity":result["identity"],"frames_assessed":len(rows),
       "four_marker_geometry_passes":sum(bool(p["private_registration"]["qualified"]) for p in rows),
       "gray_order_passes":sum(bool(p["private_registration"].get("photometric_gray_order_qualified",False)) for p in rows),
       "reasons":{reason:sum(p["private_registration"]["reason"]==reason for p in rows) for reason in sorted({p["private_registration"]["reason"] for p in rows})},
       "automatic_feedback_enabled":False,"optical_quality_parity_proven":False,
       "private_pixels_and_spatial_measurements_same_SP11":True}
    summary["qualified"]=summary["four_marker_geometry_passes"]>=3 and summary["gray_order_passes"]>=3
    summary["status"]="PASS_PRIVATE_CHART_REGISTRATION_GATE" if summary["qualified"] else "FAILED_PRIVATE_CHART_REGISTRATION_GATE"
    os.umask(0o077)
    with target.open("x") as out:json.dump({"summary":summary,"private_rows":rows},out,indent=2);out.write("\n")
    print(json.dumps(summary,sort_keys=True))
if __name__=="__main__":main()
