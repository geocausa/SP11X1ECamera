#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Offline same-geometry sparse luminance measurement. No pixel output/hash."""
import statistics
def sparse_y(data,width=2560,height=1440):
    if width<=0 or height<=0 or width%64 or height%2 or len(data)!=width*height*3//2:
        raise ValueError("exact contiguous NV12 geometry required")
    sampled=data[:width*height:64]
    return {"width":width,"height":height,"format":"NV12","y_mean":sum(sampled)/len(sampled),
        "y_min":min(sampled),"y_max":max(sampled),"y_zero_fraction":sampled.count(0)/len(sampled),
        "y_255_fraction":sampled.count(255)/len(sampled),"sampled_values":len(sampled),
        "horizontal_stride":64,"all_rows":True}
def temporal_summary(samples):
    if not samples:raise ValueError("samples required")
    values=[s["y_mean"] for s in samples]
    median=statistics.median(values)
    return {"samples":len(values),"median_y_mean":median,"min_y_mean":min(values),
        "max_y_mean":max(values),"temporal_mad_sigma":1.4826*statistics.median(abs(x-median) for x in values),
        "max_y_255_fraction":max(s["y_255_fraction"] for s in samples)}
def self_test():
    data=bytes([37])*128+bytes([128])*64
    a=sparse_y(data,64,2)
    assert a["y_mean"]==37 and a["sampled_values"]==2
    mixed=bytearray(data);mixed[0]=0;mixed[64]=255
    a=sparse_y(mixed,64,2)
    assert a["y_mean"]==127.5 and a["y_zero_fraction"]==a["y_255_fraction"]==0.5
    for data,w,h in [(data[:-1],64,2),(data,63,2),(data,64,3)]:
        try:sparse_y(data,w,h)
        except ValueError:pass
        else:raise AssertionError("invalid geometry accepted")
    print("PASS_SAME_STRIDE_Y_SAMPLING_BLACK_WHITE_SHORT_GEOMETRY_NO_CAMERA")
if __name__=="__main__":self_test()
