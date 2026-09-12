#!/usr/bin/env python3
from __future__ import annotations
import argparse,importlib.util,shutil,subprocess
from pathlib import Path
FRONT_SHA='34880dc20d349bf966ebf62d6d8bb3f0130f436c88d9e4838585624a869e04c7'
REAR_SHA='8cb5783fed2711758763aa81dc2f28c9f348259830ad6f57ffa18a6c5fd0d553'
UNION=[(0x800,0x60),(0x860,0x60),(0x1800,0x60),(0x1860,0x60),(0x18e0,0),(0x1980,0x20),(0x1900,0),(0x19a0,0x20),(0x820,0x60),(0x840,0x60),(0x18a0,0)]
REAR_SENSOR='/soc@0/cci@ac15000/i2c-bus@1/camera@10'
CAMSS='/soc@0/isp@acb7000'
def sha(p):
    import hashlib
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--front',type=Path,required=True); ap.add_argument('--rear',type=Path,required=True); ap.add_argument('--hv-builder',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
    if sha(a.front)!=FRONT_SHA: raise SystemExit('front DTB identity drift '+sha(a.front))
    if sha(a.rear)!=REAR_SHA: raise SystemExit('rear DTB identity drift '+sha(a.rear))
    spec=importlib.util.spec_from_file_location('hv',a.hv_builder); hv=importlib.util.module_from_spec(spec); spec.loader.exec_module(hv)
    ft=hv.parse_fdt(a.front); rt=hv.parse_fdt(a.rear); rear_only=sorted(set(rt)-set(ft),key=lambda p:(p.count('/'),p))
    expected=[REAR_SENSOR+'/port',REAR_SENSOR+'/port/endpoint',CAMSS+'/ports/port@1',CAMSS+'/ports/port@1/endpoint']
    if sorted(rear_only)!=sorted(expected): raise SystemExit('rear-only nodes drift '+repr(rear_only))
    rph,rpath=hv.phandle_map(rt); tph,tpath=hv.phandle_map(ft)
    remap={}
    for p in sorted(set(rt)&set(ft)):
        if p in rpath:
            if p not in tpath: raise SystemExit('common source phandle path absent in target '+p)
            remap[rpath[p]]=tpath[p]
    nextph=max(tph)+1; newph={}
    for p in rear_only:
        if p in rpath:
            newph[p]=nextph; remap[rpath[p]]=nextph; nextph+=1
    shutil.copyfile(a.front,a.out)
    for p in rear_only: hv.create_node(a.out,p)
    for p in rear_only:
        for prop,data in rt[p].items():
            if prop in ('phandle','linux,phandle'):
                if p not in newph: raise SystemExit('new phandle missing '+p)
                hv.set_raw(a.out,p,prop,hv.cells([newph[p]]))
            elif hv.is_list_ref(prop) or hv.seq_cellprop(prop):
                hv.set_raw(a.out,p,prop,hv.remap_ref_property(prop,data,rt,rph,remap))
            else:
                hv.set_raw(a.out,p,prop,data)
    # Enable accepted rear sensor: front-only authority carried status="disabled" solely as an isolation gate.
    subprocess.run(['fdtput','-d',str(a.out),REAR_SENSOR,'status'],check=True)
    # Replace front-only five-entry fwspec with IA conservative union, all on the same target apps_smmu provider.
    apps='/soc@0/iommu@15000000'
    if apps not in tpath: raise SystemExit('apps_smmu target phandle missing')
    ph=tpath[apps]; raw=[]
    for sid,mask in UNION: raw.extend([ph,sid,mask])
    hv.set_raw(a.out,CAMSS,'iommus',hv.cells(raw))
    out=hv.parse_fdt(a.out)
    print('IB_BUILD=PASS')
    print('FRONT_SHA256='+sha(a.front)); print('REAR_SHA256='+sha(a.rear)); print('OUTPUT_SHA256='+sha(a.out))
    print('NODES_FRONT='+str(len(ft))+' NODES_REAR='+str(len(rt))+' NODES_UNIFIED='+str(len(out))+' REAR_ONLY_ADDED='+str(len(rear_only)))
    print('NEW_PHANDLES='+(','.join(f'{p}={v:#x}' for p,v in sorted(newph.items())) if newph else 'none'))
    print('IOMMU_UNION='+','.join(f'{sid:#x}/{mask:#x}' for sid,mask in UNION))
if __name__=='__main__': main()
