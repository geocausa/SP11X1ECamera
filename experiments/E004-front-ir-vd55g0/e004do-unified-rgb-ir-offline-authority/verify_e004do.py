#!/usr/bin/env python3
from __future__ import annotations
import hashlib,importlib.util,json,shutil,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent; R=HERE.parents[2]
IB=R/'experiments/E003-front-imx681-cphy/e003i-front-native-productionization/ib-unified-current-golden-rear-front-dtb/x1e80100-microsoft-denali-sp11-ib-unified-rear-front.dtb'
IR=R/'experiments/E004-front-ir-vd55g0/e004l-native-bind-only-authority/x1e80100-microsoft-denali-sp11-e004l-native-bind.dtb'
OUT=HERE/'x1e80100-microsoft-denali-sp11-e004do-unified-rgb-ir.dtb'
BUILDER=HERE/'build-e004do-dtb.py'
HVB=R/'experiments/E003-front-imx681-cphy/e003i-front-native-productionization/hv-current-golden-camera-dtb-merge/build-hv-dtb.py'
PATCH=R/'experiments/E004-front-ir-vd55g0/e004k-csiphy0-dphy-parity-module/0001-sp11-e004j-csiphy0-dphy-windows-parity.patch'
CAMSS=R/'src/front-imx681/kernel/camss'; SENSOR=R/'src/front-ir-vd55g0/sp11-vd55g0-native'
KBUILD=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826')
IB_SHA='5e919d6bf778eb9eff5bf270447fa37f3c50ee16625c085c325e8d275d162321';IR_SHA='dd54d71226b354e68164db7ad0d0985fb2d63fe584c4d0e1f647eb69ee3fe96b';OUT_SHA='3d56fd6f610576dee5fc97da809f9c48da16952af9a48a5053ea864b94855beb';PATCH_SHA='1fc0f918a2f00e79918cf8bf7164f49cb8df395b8b05c949dc424a7b3824a869';SENSOR_C_SHA='20bca88eb4333f386e76e17d800268511dcf30fbc0b642d39e425e00703d6745'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
 if not v:raise AssertionError(m)
s=importlib.util.spec_from_file_location('hvdoverify',HVB);hv=importlib.util.module_from_spec(s);s.loader.exec_module(hv)
need(sha(IB)==IB_SHA,'IB identity');need(sha(IR)==IR_SHA,'IR identity');need(sha(OUT)==OUT_SHA,'output identity');need(sha(PATCH)==PATCH_SHA,'patch identity');need(sha(SENSOR/'sp11-vd55g0.c')==SENSOR_C_SHA,'sensor source')
with tempfile.TemporaryDirectory(prefix='e004do-dtb-') as td:
 q=Path(td)/'x.dtb';subprocess.run(['python3',str(BUILDER),'--ib',str(IB),'--ir',str(IR),'--hv-builder',str(HVB),'--out',str(q)],check=True,stdout=subprocess.DEVNULL);need(q.read_bytes()==OUT.read_bytes(),'deterministic DT rebuild')
a=hv.parse_fdt(IB);o=hv.parse_fdt(OUT); added=sorted(set(o)-set(a))
need(len(added)==13,'IR node count');need(not(set(a)-set(o)),'lost RGB node')
# Existing RGB sensor/ports remain byte-identical property-for-property.
for p in ['/soc@0/cci@ac15000/i2c-bus@1/camera@10','/soc@0/cci@ac15000/i2c-bus@1/camera@10/port','/soc@0/cci@ac15000/i2c-bus@1/camera@10/port/endpoint','/soc@0/cci@ac16000/i2c-bus@1/camera@10','/soc@0/cci@ac16000/i2c-bus@1/camera@10/port','/soc@0/cci@ac16000/i2c-bus@1/camera@10/port/endpoint','/soc@0/isp@acb7000/ports/port@1','/soc@0/isp@acb7000/ports/port@1/endpoint','/soc@0/isp@acb7000/ports/port@2','/soc@0/isp@acb7000/ports/port@2/endpoint']:
 need(a[p]==o[p],'RGB node changed '+p)
# All common deltas are exactly symbols, empty bus0 clock, and CAMSS reg aperture.
deltas=[]
for p in sorted(set(a)&set(o)):
 ds=[k for k in sorted(set(a[p])|set(o[p])) if a[p].get(k)!=o[p].get(k)]
 if ds:deltas.append((p,ds))
need(deltas==[('/__symbols__',['camss_csiphy0_ep','front_ir_vd55g0_default','vd55g0_ir','vd55g0_ir_ep','vreg_l2m_ir','vreg_l4m_ir','vreg_l7m_ir']),('/soc@0/cci@ac15000/i2c-bus@0',['clock-frequency']),('/soc@0/isp@acb7000',['reg'])],'common DT delta '+repr(deltas))
need(subprocess.check_output(['fdtget','-t','x',str(OUT),'/soc@0/cci@ac15000/i2c-bus@0','clock-frequency'],text=True).strip()=='61a80','CCI0 bus0 400k')
# Three external CAMSS ports coexist and IR identity is exact.
for n in (0,1,2):need(f'/soc@0/isp@acb7000/ports/port@{n}' in o,'missing port '+str(n))
irn='/soc@0/cci@ac15000/i2c-bus@0/camera@60';need(o[irn]['compatible'].rstrip(b'\0')==b'microsoft,sp11-vd55g0','IR compatible')
# IOMMU authority from IB remains exact.
need(o['/soc@0/isp@acb7000']['iommus']==a['/soc@0/isp@acb7000']['iommus'],'CAMSS iommus changed')
# Compile baseline + guarded CAMSS from identical source snapshots.
with tempfile.TemporaryDirectory(prefix='e004do-build-') as td:
 td=Path(td);base=td/'base';pat=td/'patch';shutil.copytree(CAMSS,base);shutil.copytree(CAMSS,pat)
 subprocess.run(['patch','-p6','-d',str(pat)],stdin=PATCH.open('rb'),check=True,stdout=subprocess.DEVNULL)
 hashes={}
 for name,w in [('base',base),('patch',pat)]:
  mp=f'-ffile-prefix-map={w}=/usr/src/e004do-camss -fdebug-prefix-map={w}=/usr/src/e004do-camss -fmacro-prefix-map={w}=/usr/src/e004do-camss'
  subprocess.run(['make','-C',str(KBUILD),f'M={w}','clean'],check=True,stdout=subprocess.DEVNULL)
  subprocess.run(['make','-C',str(KBUILD),f'M={w}','W=1',f'KCFLAGS={mp}',f'KCPPFLAGS={mp}','-j4'],check=True,stdout=subprocess.DEVNULL)
  ko=w/'qcom-camss.ko';hashes[name]=sha(ko);need(subprocess.check_output(['modinfo','-F','vermagic',str(ko)],text=True).strip().startswith('7.1.5-sp11-render-parity-v4+'),'CAMSS vermagic')
 mi=subprocess.check_output(['modinfo',str(pat/'qcom-camss.ko')],text=True);need('e004j_ir_dphy_windows_parity' in mi,'IR parity parameter missing')
 ps=(pat/'camss-csiphy-3ph-1-0.c').read_text();need('csiphy->id == 0' in ps and 'c->phy_cfg == V4L2_MBUS_CSI2_DPHY' in ps and 'CAMSS_X1E80100' in ps,'IR gate scope')
 # Compile accepted native sensor source from a disposable copy. Generate the
 # exact Windows-derived header through the real source-tree generator, copy it,
 # then remove the transient source-tree artifact.
 sd=td/'sensor';shutil.copytree(SENSOR,sd);gen_header=SENSOR/'surface-windows.generated.h'
 try:
  subprocess.run(['python3',str(SENSOR/'generate_windows_header.py')],check=True,stdout=subprocess.DEVNULL)
  need(sha(gen_header)=='40f9731061ba327c423da3322abdc9a20e07251073c39c266027dac55de1fd9e','generated sensor header')
  shutil.copy2(gen_header,sd/'surface-windows.generated.h')
 finally:
  gen_header.unlink(missing_ok=True)
 smap=f'-ffile-prefix-map={sd}=/usr/src/e004do-vd55g0 -fdebug-prefix-map={sd}=/usr/src/e004do-vd55g0 -fmacro-prefix-map={sd}=/usr/src/e004do-vd55g0'
 subprocess.run(['make','-C',str(KBUILD),f'M={sd}','clean'],check=True,stdout=subprocess.DEVNULL)
 # make clean removes generated build outputs, not the copied authority header.
 subprocess.run(['make','-C',str(KBUILD),f'M={sd}','modules',f'KCFLAGS={smap}',f'KCPPFLAGS={smap}','-j4'],check=True,stdout=subprocess.DEVNULL)
 sko=sd/'sp11-vd55g0.ko';need(subprocess.check_output(['modinfo','-F','vermagic',str(sko)],text=True).strip().startswith('7.1.5-sp11-render-parity-v4+'),'sensor vermagic');sensor_ko_sha=sha(sko)
 Path(HERE/'evidence/BUILD-HASHES.json').write_text(json.dumps({'camss_baseline_sha256':hashes['base'],'camss_ir_gated_sha256':hashes['patch'],'sensor_disposable_build_sha256':sensor_ko_sha},indent=2,sort_keys=True)+'\n')
# Offline safety.
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'not Golden');env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True);need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'GRUB state')
for m in ('qcom_camss','imx681','ov13858','sp11_vd55g0'):need(not Path('/sys/module',m).exists(),'module loaded '+m)
print('E004do VERIFY: PASS (unified rear+front RGB+IR offline DT + guarded CSIPHY0 compile)')
