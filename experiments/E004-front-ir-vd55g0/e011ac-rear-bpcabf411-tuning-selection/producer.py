#!/usr/bin/env python3
"""Resolve BPC authority and derive selected common output from explicit leaves.
The upstream interval/ratio decision is caller-owned, not inferred here.
"""
from pathlib import Path
import importlib.util
HERE=Path(__file__).resolve().parent
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
I=load("interpolation",HERE/"interpolate.py")
P=load("bpc_common",HERE.parent/"e011aa-rear-bpcabf411-common-producer"/"producer.py")
def selected_terms(region):
 if len(region)!=107:raise ValueError("full region required")
 return (list(region[82:84]),[[region[84],region[86]],[region[85],region[87]]],
         [list(region[88:93]),list(region[93:98])])
def produce(authority,modes,lower_leaf,upper_leaf,ratio):
 root=authority.resolve(modes)
 lower=authority.region(root,lower_leaf)
 upper=lower if upper_leaf==lower_leaf else authority.region(root,upper_leaf)
 region=I.interpolate(lower,upper,ratio)
 state=P.calculate(*selected_terms(region),authority.anchors(root))
 return {"root":root,"region":region,"state":state,"registers":P.pack(state)}
def cold_seed(authority):
 root=authority.resolve([(0,0)])
 leaves=authority.leaves(root)
 region=authority.equivalent(root,leaves) # All six Default leaves are identical.
 state=P.calculate(*selected_terms(region),authority.anchors(root))
 return {"root":root,"region":region,"state":state,"registers":P.pack(state)}
