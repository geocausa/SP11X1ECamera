#!/usr/bin/env python3
"""Source-only bounded BPC exposure interval selection; no hardware access."""
from pathlib import Path
import importlib.util,math,struct
HERE=Path(__file__).resolve().parent
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
AC=load("bpc_ac",HERE.parent/"e011ac-rear-bpcabf411-tuning-selection"/"producer.py")
f32=AC.I.f32

def select(intervals,value):
    """Choose a plateau or blend only in a strict gap between two plateaus."""
    rows=tuple((f32(start),f32(end)) for start,end in intervals)
    value=f32(value)
    if not 1<=len(rows)<=6:raise ValueError("one to six intervals supported")
    if any(start>end for start,end in rows):raise ValueError("reversed interval")
    if any(end>next_start for (_,end),(next_start,_) in zip(rows,rows[1:])):
        raise ValueError("overlapping or unordered intervals unsupported")
    for index,(_,end) in enumerate(rows):
        if value<=end or index==len(rows)-1:return index,index,0.0
        next_start=rows[index+1][0]
        if value<next_start:
            # Native FCVT uses binary64 subtraction/division, then one f32 rounding.
            return index,index+1,f32((float(value)-float(end))/(float(next_start)-float(end)))
    raise AssertionError("validated nonempty interval list exhausted")

def source_intervals(authority,root,*,with_prefix=False):
    """Decode the proven 1 -> 1 -> 6 serialized trigger shape, retaining leaf IDs."""
    def data(sid,kind):
        symbol=authority.symbols[sid]
        if symbol["type"]!=kind:raise ValueError("trigger symbol type")
        return authority.d.data_bytes(authority.b,authority.h["sections"][1],symbol)
    if root not in authority.module_by_branch.values():raise ValueError("unproven root")
    raw=data(root,"bpcabf41_ife_v2")
    if len(raw)!=136:raise ValueError("root layout changed")
    count,sid=struct.unpack_from("<2I",raw,128)
    if count!=1:raise ValueError("root must have one outer trigger")
    prefix=[]
    for kind,expected_children in (("mod_bpcabf41_trigger_data",1),("trigger",6)):
        raw=data(sid,kind)
        if len(raw)!=24:raise ValueError("singleton trigger layer changed")
        start,end,children,child,regions,region=struct.unpack("<2f4I",raw)
        if not all(math.isfinite(x) for x in (start,end)) or start>end:
            raise ValueError("outer interval domain")
        if children!=expected_children or regions!=0:raise ValueError("singleton shape changed")
        prefix.append((start,end))
        sid=child
    raw=data(sid,"trigger")
    if len(raw)!=6*24:raise ValueError("six-terminal-trigger layout changed")
    intervals=[];leaves=[]
    for offset in range(0,len(raw),24):
        start,end,children,child,regions,region=struct.unpack_from("<2f4I",raw,offset)
        if children!=0 or data(child,"trigger") or regions!=1:
            raise ValueError("terminal trigger shape changed")
        if region not in authority.leaves(root):raise ValueError("terminal leaf ownership")
        authority.region(root,region)
        intervals.append((start,end));leaves.append(region)
    # Exercise the domain checks without introducing a selection policy.
    select(intervals,intervals[0][0])
    if len(set(leaves))!=6:raise ValueError("duplicate terminal leaf")
    result=(tuple(intervals),tuple(leaves))
    return (*result,tuple(prefix)) if with_prefix else result

def produce(authority,modes,exposure_value):
    """Exposure scalar is caller-owned until request provenance is verified."""
    root=authority.resolve(modes)
    intervals,leaves=source_intervals(authority,root)
    lower,upper,ratio=select(intervals,exposure_value)
    result=AC.produce(authority,modes,leaves[lower],leaves[upper],ratio)
    result["interval"]={"lower":lower,"upper":upper,"ratio":ratio}
    return result
