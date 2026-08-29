#!/usr/bin/env python3
import argparse, hashlib, subprocess
from pathlib import Path
NODE='/soc@0/isp@acb7000'
def get(dt,prop,t='x'):
 return subprocess.check_output(['fdtget','-t',t,str(dt),NODE,prop],text=True).strip().split()
def put(dt,prop,vals,t='x'):
 subprocess.run(['fdtput','-t',t,str(dt),NODE,prop,*vals],check=True)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--base',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
 a.out.write_bytes(a.base.read_bytes())
 reg=get(a.out,'reg'); names=get(a.out,'reg-names','s'); irq=get(a.out,'interrupts'); inames=get(a.out,'interrupt-names','s')
 if len(reg)!=17*4 or names[-4:]!=['vfe0','vfe1','vfe_lite0','vfe_lite1']: raise SystemExit('base CAMSS resource layout drift')
 # resource groups 13/14 are vfe0/vfe1: <0 base 0 size>
 reg[13*4+3]='f000'; reg[14*4+3]='f000'; reg += ['0','ac26000','0','1000']; names += ['rt_cdm1']
 if len(irq)!=13*3 or inames[-4:]!=['vfe0','vfe1','vfe_lite0','vfe_lite1']: raise SystemExit('base CAMSS IRQ layout drift')
 irq += ['0','11f','1']; inames += ['rt_cdm1']
 put(a.out,'reg',reg); put(a.out,'reg-names',names,'s'); put(a.out,'interrupts',irq); put(a.out,'interrupt-names',inames,'s')
 # Front-only invariant inherited from accepted RDI candidate.
 ports=subprocess.check_output(['fdtget','-l',str(a.out),NODE+'/ports'],text=True).split()
 if ports != ['port@2']: raise SystemExit('front-only ports drift: '+repr(ports))
 rear='/soc@0/cci@ac15000/i2c-bus@1/camera@10'
 subprocess.run(['fdtget',str(a.out),rear,'status'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 print('base_sha256='+sha(a.base)); print('candidate_sha256='+sha(a.out)); print('vfe_span=0xf000'); print('rt_cdm1=0x0ac26000/0x1000 irq=GIC_SPI_287'); print('ports=port@2 only')
if __name__=='__main__': main()
