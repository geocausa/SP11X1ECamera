#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Locate the independent SP7 chart. Camera originals and spatial results stay on SP11.
Geometry enhancement is for registration only; photometry uses original NV12 Y.
A successful geometry check is not Windows/Linux image-quality parity.
"""
import argparse, json, pathlib, os, stat, subprocess
import cv2
import numpy as np

W,H=1200,800
def template():
    a=np.full((H,W),128,np.uint8)
    for i,v in enumerate([0,32,64,128,192,255]):
        cv2.rectangle(a,(round(W*(.08+i*.14)),round(H*.12)),
                      (round(W*(.20+i*.14)),round(H*.37)),int(v),-1)
    for i,v in enumerate([54,182,18,237,201,73]):
        cv2.rectangle(a,(round(W*(.08+i*.14)),round(H*.43)),
                      (round(W*(.20+i*.14)),round(H*.65)),int(v),-1)
    cv2.rectangle(a,(round(W*.04),round(H*.04)),
                  (round(W*.96),round(H*.70)),255,4)
    cv2.line(a,(round(W*.07),round(H*.07)),
             (round(W*.20),round(H*.07)),0,4)
    return a

def locate(y,uv=None):
    # Exclude the known damaged lower LCD area from template keypoints.
    t=template()
    mask=np.zeros_like(t);mask[:round(.71*H)]=255
    sift=cv2.SIFT_create(nfeatures=4000,contrastThreshold=.008)
    ka,da=sift.detectAndCompute(t,mask)
    enhanced=cv2.createCLAHE(clipLimit=2,tileGridSize=(16,16)).apply(y)
    kb,db=sift.detectAndCompute(enhanced,None)
    out={"qualified":False,"reason":"insufficient_unique_chart_features",
         "template_features":len(ka),"frame_features":len(kb)}
    if da is None or db is None:return out
    pairs=cv2.BFMatcher().knnMatch(da,db,k=2)
    good=[m for p in pairs if len(p)==2 for m,n in [p] if m.distance<.75*n.distance]
    out["unique_matches"]=len(good)
    if len(good)<16:return out
    # Held-out matches independently check repeated-patch ambiguity.
    train=good[::2];hold=good[1::2]
    p=np.float32([ka[m.queryIdx].pt for m in train])
    q=np.float32([kb[m.trainIdx].pt for m in train])
    mat,inliers=cv2.findHomography(p,q,cv2.RANSAC,3.0)
    if mat is None:return out
    sel=inliers.ravel().astype(bool)
    out["training_inliers"]=int(sel.sum())
    if sel.sum()<8:return out
    hp=np.float32([ka[m.queryIdx].pt for m in hold]).reshape(-1,1,2)
    hq=np.float32([kb[m.trainIdx].pt for m in hold])
    err=np.linalg.norm(cv2.perspectiveTransform(hp,mat).reshape(-1,2)-hq,axis=1)
    out["heldout_inliers"]=int((err<=3).sum())
    out["heldout_error_median_px"]=float(np.median(err))
    # Verify support spans the chart, rather than one repeated rectangle.
    support=p[sel]
    out["support_width_fraction"]=float(np.ptp(support[:,0])/W)
    out["support_height_fraction"]=float(np.ptp(support[:,1])/H)
    corners=cv2.perspectiveTransform(np.float32([[0,0],[W,0],[W,H*.7],[0,H*.7]]).reshape(-1,1,2),mat).reshape(-1,2)
    safe=bool(np.isfinite(corners).all() and cv2.isContourConvex(corners.astype(np.float32))
              and abs(cv2.contourArea(corners))>y.size*.03
              and (corners[:,0]>=0).all() and (corners[:,0]<y.shape[1]).all()
              and (corners[:,1]>=0).all() and (corners[:,1]<y.shape[0]).all())
    qualified=bool(out["heldout_inliers"]>=6 and out["heldout_error_median_px"]<=3
                   and out["support_width_fraction"]>.6 and out["support_height_fraction"]>.3 and safe)
    if not qualified:
        out["reason"]="heldout_geometry_or_coverage_failed"
        return out
    vals=[]
    for i in range(6):
        box=np.float32([[W*(.10+i*.14),H*.17],[W*(.18+i*.14),H*.17],
                        [W*(.18+i*.14),H*.32],[W*(.10+i*.14),H*.32]])
        poly=cv2.perspectiveTransform(box.reshape(-1,1,2),mat).reshape(-1,2)
        m=np.zeros_like(y);cv2.fillConvexPoly(m,np.rint(poly).astype(np.int32),255)
        vals.append(float(np.median(y[m>0])))
    # Reject wrong patch order, clipping or unresolved exposure before calibration.
    out["private_gray_medians"]=vals
    out["private_homography"]=mat.tolist()
    out["qualified"]=qualified
    out["photometric_gray_order_qualified"]=bool(np.all(np.diff(vals)>1))
    out["reason"]="PASS_GEOMETRY" if qualified else out["reason"]
    return out

def selftest():
    t=template()
    # Reject featureless and unrelated scenes. Neither can authorize tuning.
    assert not locate(np.full((H,W),128,np.uint8))["qualified"]
    rng=np.random.default_rng(721)
    assert not locate(rng.integers(0,256,(H,W),dtype=np.uint8))["qualified"]
    # Check known perspective using the same source fixture.
    m=cv2.getPerspectiveTransform(np.float32([[0,0],[W-1,0],[W-1,H-1],[0,H-1]]),
        np.float32([[70,40],[1130,60],[1090,750],[50,710]]))
    result=locate(cv2.warpPerspective(t,m,(W,H),borderValue=90))
    assert result["qualified"],result
    assert result["photometric_gray_order_qualified"],result
    print("PASS_CHART_REGISTRATION_SYNTHETIC tests=3 no_camera_access=true")

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--self-test",action="store_true")
    ap.add_argument("--private-manifest");args=ap.parse_args()
    if args.self_test:selftest();return
    if os.geteuid()!=0:raise RuntimeError("root required for private original analysis")
    manifest_path=pathlib.Path(args.private_manifest)
    if manifest_path.is_symlink() or stat.S_IMODE(manifest_path.stat().st_mode)!=0o600:
        raise RuntimeError("private regular manifest required")
    manifest=json.loads(manifest_path.read_text())
    root=pathlib.Path(manifest["private_output_directory"])
    if root.is_symlink() or not root.is_dir() or root.stat().st_uid!=0 or stat.S_IMODE(root.stat().st_mode)!=0o700:
        raise RuntimeError("root-owned private output directory required")
    if root.parent!=pathlib.Path("/var/lib") or not root.name.startswith("sp11-camera-"):
        raise RuntimeError("same-SP11 camera evidence root required")
    results=[]
    for item in manifest["frames"]:
        path=pathlib.Path(item["path"])
        if path.is_symlink() or not path.is_file() or path.stat().st_uid!=0 or stat.S_IMODE(path.stat().st_mode)!=0o600:
            raise RuntimeError("root-owned private regular originals required")
        if str(path).startswith("/run/sp11-windows-"):
            options=subprocess.check_output(["findmnt","-rn","-T",str(path),"-o","OPTIONS"],text=True).strip().split(",")
            if "ro" not in options:raise RuntimeError("Windows originals must be read only")
        elif not str(path).startswith("/var/lib/sp11-camera-native-"):
            raise RuntimeError("original is outside same-SP11 camera roots")
        w,h=item["width"],item["height"]
        assert path.stat().st_size==w*h*3//2
        raw=np.fromfile(path,dtype=np.uint8)
        y=raw[:w*h].reshape(h,w);uv=raw[w*h:].reshape(h//2,w//2,2)
        # Photometric measurements use original native-resolution bytes.
        r=locate(y,uv);r["label"]=item["label"];results.append(r)
    destination=root/"CHART-REGISTRATION-PRIVATE.json"
    fd=os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    try:os.write(fd,(json.dumps(results,indent=2)+"\n").encode());os.fsync(fd)
    finally:os.close(fd)
    public={"frame_count":len(results),"geometry_qualified_count":sum(r["qualified"] for r in results),
            "all_geometry_qualified":all(r["qualified"] for r in results),
            "all_gray_order_qualified":all(r.get("photometric_gray_order_qualified",False) for r in results),
            "calibration_authorized":False,"quality_parity_proven":False,
            "spatial_results_exported":False}
    print(json.dumps(public))
if __name__=="__main__":main()
