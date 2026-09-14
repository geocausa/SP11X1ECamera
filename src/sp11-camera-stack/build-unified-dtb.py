#!/usr/bin/env python3
from __future__ import annotations
import argparse,importlib.util,hashlib,shutil,subprocess
from pathlib import Path
IB_SHA='5e919d6bf778eb9eff5bf270447fa37f3c50ee16625c085c325e8d275d162321'
IR_SHA='dd54d71226b354e68164db7ad0d0985fb2d63fe584c4d0e1f647eb69ee3fe96b'
BUS='/soc@0/cci@ac15000/i2c-bus@0'
CSIPHY0_BASE=bytes.fromhex('000000000ace40000000000000001000')
CSIPHY0_WIDE=bytes.fromhex('000000000ace40000000000000002000')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--ib',type=Path,required=True);ap.add_argument('--ir',type=Path,required=True);ap.add_argument('--hv-builder',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 if sha(a.ib)!=IB_SHA:raise SystemExit('IB drift '+sha(a.ib))
 if sha(a.ir)!=IR_SHA:raise SystemExit('IR drift '+sha(a.ir))
 s=importlib.util.spec_from_file_location('hvdo',a.hv_builder);hv=importlib.util.module_from_spec(s);s.loader.exec_module(hv)
 ib=hv.parse_fdt(a.ib);ir=hv.parse_fdt(a.ir)
 added=sorted(set(ir)-set(ib),key=lambda p:(p.count('/'),p))
 expected={
 '/soc@0/pinctrl@f100000/front-ir-vd55g0-default-state',
 '/soc@0/cci@ac15000/i2c-bus@0/camera@60',
 '/soc@0/isp@acb7000/ports/port@0',
 '/soc@0/pinctrl@f100000/cci0-default-state/cci0-i2c0-pins',
 '/soc@0/pinctrl@f100000/cci0-sleep-state/cci0-i2c0-pins',
 '/soc@0/pinctrl@f100000/front-ir-vd55g0-default-state/mclk-pins',
 '/soc@0/pinctrl@f100000/front-ir-vd55g0-default-state/reset-pins',
 '/soc@0/rsc@17500000/regulators-8/ldo2',
 '/soc@0/rsc@17500000/regulators-8/ldo4',
 '/soc@0/rsc@17500000/regulators-8/ldo7',
 '/soc@0/cci@ac15000/i2c-bus@0/camera@60/port',
 '/soc@0/isp@acb7000/ports/port@0/endpoint',
 '/soc@0/cci@ac15000/i2c-bus@0/camera@60/port/endpoint'}
 if set(added)!=expected:raise SystemExit('IR added-node drift '+repr(added))
 # Common-node deltas must be only IR symbols + empty CCI0 bus0 clock authority.
 common=[]
 for p in sorted(set(ib)&set(ir)):
  ds=[k for k in sorted(set(ib[p])|set(ir[p])) if ib[p].get(k)!=ir[p].get(k)]
  if ds:common.append((p,ds))
 if common!=[('/__symbols__',['camss_csiphy0_ep','front_ir_vd55g0_default','vd55g0_ir','vd55g0_ir_ep','vreg_l2m_ir','vreg_l4m_ir','vreg_l7m_ir']), (BUS,['clock-frequency'])]:
  raise SystemExit('common delta drift '+repr(common))
 iph,ipath=hv.phandle_map(ib);rph,rpath=hv.phandle_map(ir);remap={}
 for p in sorted(set(ib)&set(ir)):
  if p in rpath:
   if p not in ipath:raise SystemExit('common phandle missing in IB '+p)
   remap[rpath[p]]=ipath[p]
 nextph=max(iph)+1;newph={}
 for p in added:
  if p in rpath:newph[p]=nextph;remap[rpath[p]]=nextph;nextph+=1
 shutil.copyfile(a.ib,a.out)
 for p in added:hv.create_node(a.out,p)
 for p in added:
  for prop,data in ir[p].items():
   if prop in ('phandle','linux,phandle'):
    hv.set_raw(a.out,p,prop,hv.cells([newph[p]]))
   elif hv.is_list_ref(prop) or hv.seq_cellprop(prop):hv.set_raw(a.out,p,prop,hv.remap_ref_property(prop,data,ir,rph,remap))
   else:hv.set_raw(a.out,p,prop,data)
 # Copy only the seven IR symbol aliases.
 for prop in common[0][1]:hv.set_raw(a.out,'/__symbols__',prop,ir['/__symbols__'][prop])
 # IR-only CCI0 bus0 is empty in IB; use the proven 400 kHz authority from E004l.
 hv.set_raw(a.out,BUS,'clock-frequency',ir[BUS]['clock-frequency'])
 raw=a.out.read_bytes()
 if raw.count(CSIPHY0_BASE)!=1:raise SystemExit('CSIPHY0 4K tuple not unique')
 off=raw.index(CSIPHY0_BASE);raw2=raw[:off]+CSIPHY0_WIDE+raw[off+16:];a.out.write_bytes(raw2)
 out=hv.parse_fdt(a.out)
 print('E004DO_DTB_BUILD=PASS');print('IB_SHA256='+sha(a.ib));print('IR_SHA256='+sha(a.ir));print('OUTPUT_SHA256='+sha(a.out));print('ADDED_IR_NODES='+str(len(added)));print('CCI0_BUS0_CLOCK=400000');print('CSIPHY0_APERTURE=0x2000');print('NEW_PHANDLE_RANGE='+hex(min(newph.values()))+'..'+hex(max(newph.values())))
if __name__=='__main__':main()
