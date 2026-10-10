#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Register four coded markers; keep every spatial/patch measurement on SP11."""
import importlib.util, pathlib, sys
import cv2
import numpy as np
_spec=importlib.util.spec_from_file_location("chart_base",pathlib.Path(__file__).with_name("register-healthy-chart.py"))
base=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(base)
IDS=[17,83,211,509]
XY=[(.008,.04),(.932,.04),(.932,.58),(.008,.58)]
D=cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_1000)
def layout(width=1200,height=800):
    size=round(width*.06)
    return [np.float32([[round(width*x),round(height*y)],
                       [round(width*x)+size-1,round(height*y)],
                       [round(width*x)+size-1,round(height*y)+size-1],
                       [round(width*x),round(height*y)+size-1]]) for x,y in XY]
def template():
    t=base.template();size=round(base.W*.06);quiet=round(size/6)
    for n,box in zip(IDS,layout()):
        x,y=box[0].astype(int)
        cv2.rectangle(t,(x-quiet,y-quiet),(x+size+quiet-1,y+size+quiet-1),255,-1)
        t[y:y+size,x:x+size]=cv2.aruco.generateImageMarker(D,n,size)
    return t
def detect(y):
    par=cv2.aruco.DetectorParameters();par.cornerRefinementMethod=cv2.aruco.CORNER_REFINE_SUBPIX
    detector=cv2.aruco.ArucoDetector(D,par)
    # Mirroring is resolved from decoded IDs; photometry uses the matching original view.
    candidates=[]
    for mirror in [False,True]:
        view=np.fliplr(y).copy() if mirror else y
        corners,ids,_=detector.detectMarkers(view)
        if ids is None:continue
        ids=ids.ravel().tolist()
        if all(ids.count(n)==1 for n in IDS):
            candidates.append((mirror,view,[corners[ids.index(n)].reshape(4,2) for n in IDS]))
    return candidates
def locate(y,uv=None):
    out={"qualified":False,"reason":"four_unique_fiducials_not_visible"}
    candidates=detect(y)
    if len(candidates)!=1:return out
    mirror,view,boxes=candidates[0]
    if uv is not None and mirror:uv=np.fliplr(uv).copy()
    src=np.concatenate(layout());dst=np.concatenate(boxes)
    mat,_=cv2.findHomography(src,dst,0)
    if mat is None:return out
    # Every held-out marker must agree with a transform fit to the other three.
    errors=[]
    for i in range(4):
        indices=np.array([j for j in range(16) if j//4!=i])
        held,_=cv2.findHomography(src[indices],dst[indices],0)
        if held is None:return out
        pred=cv2.perspectiveTransform(src[i*4:i*4+4].reshape(-1,1,2),held).reshape(-1,2)
        errors.extend(np.linalg.norm(pred-dst[i*4:i*4+4],axis=1))
    out["private_max_heldout_reprojection_px"]=float(max(errors))
    if max(errors)>3:
        out["reason"]="heldout_marker_geometry_failed";return out
    patches=[]
    for row,top,bottom in [("gray",.17,.32),("color",.47,.61)]:
        for i in range(6):
            box=np.float32([[base.W*(.10+i*.14),base.H*top],[base.W*(.18+i*.14),base.H*top],
                            [base.W*(.18+i*.14),base.H*bottom],[base.W*(.10+i*.14),base.H*bottom]])
            poly=cv2.perspectiveTransform(box.reshape(-1,1,2),mat).reshape(-1,2)
            if not (np.isfinite(poly).all() and cv2.isContourConvex(poly) and
                    (poly[:,0]>=0).all() and (poly[:,0]<view.shape[1]).all() and
                    (poly[:,1]>=0).all() and (poly[:,1]<view.shape[0]).all() and
                    abs(cv2.contourArea(poly))>=64):
                out["reason"]="healthy_patch_bounds_failed";return out
            mask=np.zeros_like(view);cv2.fillConvexPoly(mask,np.rint(poly).astype(np.int32),255)
            values=view[mask>0]
            patches.append({"row":row,"index":i,"median_Y":float(np.median(values)),
                            "mean_Y":float(values.mean()),"std_Y":float(values.std()),
                            "p01_Y":float(np.percentile(values,1)),"p99_Y":float(np.percentile(values,99))})
            if uv is not None:
                uv_mask=np.zeros(uv.shape[:2],np.uint8)
                cv2.fillConvexPoly(uv_mask,np.rint(poly/2).astype(np.int32),255)
                color=uv[uv_mask>0]
                patches[-1].update(mean_U=float(color[:,0].mean()),mean_V=float(color[:,1].mean()),
                                   range_and_color_matrix_unqualified=True)
    out.update(qualified=True,reason="PASS_FOUR_FIDUCIAL_GEOMETRY",
               private_mirror=mirror,private_homography=mat.tolist(),private_patches=patches,
               photometric_gray_order_qualified=bool(np.all(np.diff([p["median_Y"] for p in patches[:6]])>1)))
    return out
def selftest():
    t=template()
    src=np.float32([[0,0],[1199,0],[1199,799],[0,799]])
    dst=np.float32([[70,40],[1130,60],[1090,750],[50,710]])
    m=cv2.getPerspectiveTransform(src,dst)
    warped=cv2.warpPerspective(t,m,(1200,800),borderValue=90)
    for image in [t,warped,np.fliplr(warped).copy(),np.rot90(warped).copy()]:
        r=locate(image);assert r["qualified"],r;assert r["photometric_gray_order_qualified"],r
    damaged=t.copy();damaged[round(base.H*.71):]=0
    assert locate(damaged)["qualified"]
    missing=t.copy();missing[:200,:150]=128
    assert not locate(missing)["qualified"]
    assert not locate(base.template())["qualified"]
    assert not locate(np.full_like(t,128))["qualified"]
    # One displaced tag must fail the held-out transform even though all IDs decode.
    moved=t.copy();box=layout()[2];x,y=box[0].astype(int);size=72;q=12
    moved[y-q:y+size+q,x-q:x+size+q]=128
    nx=x-90;ny=y-80
    moved[ny-q:ny+size+q,nx-q:nx+size+q]=255
    moved[ny:ny+size,nx:nx+size]=cv2.aruco.generateImageMarker(D,211,size)
    assert not locate(moved)["qualified"]
    print("PASS_CODED_CHART_REGISTRATION tests=9 no_camera_access=true")
if __name__=="__main__":
    if "--self-test" in sys.argv:selftest()
    else:
        base.locate=locate
        base.main()
