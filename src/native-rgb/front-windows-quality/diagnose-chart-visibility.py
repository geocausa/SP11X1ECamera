#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Same-SP11 marker visibility diagnostics; never authorize calibration."""
import importlib.util,json,os,pathlib,stat,subprocess
import cv2,numpy as np
_spec=importlib.util.spec_from_file_location("chart",pathlib.Path(__file__).with_name("register-fiducial-chart.py"))
f=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(f)
def assess(y):
    par=cv2.aruco.DetectorParameters();par.minMarkerPerimeterRate=.005
    par.adaptiveThreshWinSizeMax=63;par.adaptiveThreshWinSizeStep=4
    detector=cv2.aruco.ArucoDetector(f.D,par)
    models=[]
    for mirror in [False,True]:
        view=np.fliplr(y).copy() if mirror else y
        for enhance in [False,True]:
            search=cv2.createCLAHE(clipLimit=3,tileGridSize=(16,16)).apply(view) if enhance else view
            corners,ids,_=detector.detectMarkers(search)
            if ids is None:continue
            ids=ids.ravel().tolist()
            known={n:corners[ids.index(n)].reshape(4,2) for n in f.IDS if ids.count(n)==1}
            if len(known)<2:continue
            src=np.concatenate([f.layout()[f.IDS.index(n)] for n in known]);dst=np.concatenate(list(known.values()))
            hom,_=cv2.findHomography(src,dst,0)
            if hom is None:continue
            error=float(np.max(np.linalg.norm(cv2.perspectiveTransform(src.reshape(-1,1,2),hom).reshape(-1,2)-dst,axis=1)))
            if error>3:continue
            records=[]
            for n,box in zip(f.IDS,f.layout()):
                points=np.float32([[box[0,0]+(c+.5)*72/6,box[0,1]+(r+.5)*72/6] for r in range(6) for c in range(6)])
                pos=cv2.perspectiveTransform(points.reshape(-1,1,2),hom).reshape(-1,2)
                inside=bool(np.isfinite(pos).all() and (pos[:,0]>=2).all() and (pos[:,0]<view.shape[1]-2).all() and (pos[:,1]>=2).all() and (pos[:,1]<view.shape[0]-2).all())
                rec={"id":n,"independently_decoded":n in known,"centers_inside_frame":inside,"private_centers":pos.tolist()}
                if inside:
                    values=np.array([float(cv2.getRectSubPix(view,(3,3),tuple(p)).mean()) for p in pos])
                    code=(cv2.aruco.generateImageMarker(f.D,n,60).reshape(6,10,6,10).mean(axis=(1,3)).ravel()>127)
                    black=float(np.median(values[~code]));white=float(np.median(values[code]))
                    bits=values>(black+white)/2
                    rec.update(private_black=black,private_white=white,private_bit_errors=int((bits!=code).sum()),
                               expected_code_supported=bool(white-black>=12 and (bits!=code).sum()<=1))
                else:rec["expected_code_supported"]=False
                records.append(rec)
            models.append({"private_mirror":mirror,"private_enhance":enhance,"private_homography":hom.tolist(),"private_seed_error":error,"markers":records})
    return {"models":models,"diagnostic_only":True,"calibration_authorized":False}
def summary(rows):
    models=[m for r in rows for m in r["models"]]
    return {"partial_model_available":bool(models),
            "all_expected_codes_supported_under_any_partial_model":any(all(p["expected_code_supported"] for p in m["markers"]) for m in models),
            "all_expected_codes_inside_under_any_partial_model":any(all(p["centers_inside_frame"] for p in m["markers"]) for m in models),
            "diagnostic_only":True,"calibration_authorized":False,"pixels_and_spatial_metrics_exported":False}
def selftest():
    t=f.template()
    assert summary([assess(t)])["all_expected_codes_supported_under_any_partial_model"]
    assert not summary([assess(np.full_like(t,128))])["partial_model_available"]
    # Two absent codes must remain unsupported even though the other pair defines a plane.
    damaged=t.copy()
    for box in f.layout()[2:]:
        x,y=box[0].astype(int);damaged[y-12:y+84,x-12:x+84]=128
    assert not summary([assess(damaged)])["all_expected_codes_supported_under_any_partial_model"]
    print("PASS_MARKER_VISIBILITY_DIAGNOSTICS tests=3 no_camera_access=true")
if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument("--self-test",action="store_true")
    ap.add_argument("--private-manifest");args=ap.parse_args()
    if args.self_test:selftest();raise SystemExit
    if os.geteuid()!=0:raise RuntimeError("root required")
    path=pathlib.Path(args.private_manifest)
    if path.is_symlink() or stat.S_IMODE(path.stat().st_mode)!=0o600:raise RuntimeError("private manifest required")
    data=json.loads(path.read_text());root=pathlib.Path(data["private_output_directory"])
    if root.is_symlink() or root.parent!=pathlib.Path("/var/lib") or not root.name.startswith("sp11-camera-") or root.stat().st_uid!=0 or stat.S_IMODE(root.stat().st_mode)!=0o700:raise RuntimeError("same-SP11 private root required")
    rows=[]
    for item in data["frames"]:
        p=pathlib.Path(item["path"])
        if p.is_symlink() or not p.is_file() or p.stat().st_uid!=0 or stat.S_IMODE(p.stat().st_mode)!=0o600:raise RuntimeError("private original required")
        if str(p).startswith("/run/sp11-windows-"):
            opt=subprocess.check_output(["findmnt","-rn","-T",str(p),"-o","OPTIONS"],text=True).strip().split(",")
            if "ro" not in opt:raise RuntimeError("read-only Windows original required")
        elif not str(p).startswith("/var/lib/sp11-camera-native-"):raise RuntimeError("same-SP11 originals only")
        w,h=item["width"],item["height"]
        if p.stat().st_size!=w*h*3//2:raise RuntimeError("NV12 extent mismatch")
        y=np.fromfile(p,np.uint8,count=w*h).reshape(h,w)
        r=assess(y);r["label"]=item["label"];rows.append(r)
    fd=os.open(root/"MARKER-VISIBILITY-PRIVATE.json",os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    try:os.write(fd,(json.dumps(rows,indent=2)+"\n").encode());os.fsync(fd)
    finally:os.close(fd)
    print(json.dumps(summary(rows)))
