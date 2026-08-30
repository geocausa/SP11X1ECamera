#!/usr/bin/env python3
import hashlib, json, re, shutil, subprocess, tempfile
from pathlib import Path

REPO=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
STATIC=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static'
SRC=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss')
PATCH=STATIC/'0047-x1e-vfe1-dal-start-prefix-windows-parity.patch'
ORACLE=STATIC/'windows-vfe1-dal-start-prefix-oracle.json'
MODULE=SRC/'qcom-camss.ko'
EXPECTED={
 'patch':'f5192c50c15e1ab8d92659b3735d70f5dfeeff0bbae961d90e1dbf27486ffee4',
 'oracle':'75738af53bf5845f28e8c279dad573b0e8e052c4aa2fed9e11d0685fc9455cd7',
 'checkpatch':'e9dcb470ce2a2832dff5b0b9d372297bd4f08de45aaa165dea953abc2c0ea4f1',
 'build':'8a5bb9f7511a73b3a257798fd54d1bdf67265a867a83ca533dfd41a4d5067d41',
 'module':'5e7bdadf76f293b48e4efb54a69c011cb00ff9af75806e9558176cd925dd5007',
 'camss.c':'5a920032e138eee1154c4b9ae1846a445e02fbac3e7626a4245797502e73b793',
 'camss-vfe-680.c':'0dc6269d8b7c0e57e1442dfea374f0e90bdf14b8e8ef58117a505cda6d643036',
 'camss-vfe.h':'1029c3d353e93209d212729be238f9665308ba97eb659d8c6648c86c238d1bbd',
}
BASE={
 'camss.c':'fbc7c278b5249ed0d7d80a54be8d2ca30ed927914a2f64fcedb5b6a36296bd28',
 'camss-vfe-680.c':'45a13941e7a711c2bb80a85ac9dbad13ae3e618e685de58704366d381cd1ce90',
 'camss-vfe.h':'a975e832104bd053fd906b21fca1316347709c16c68e5e029df8cff61bdadf5f',
}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
def check(p,h,n):
 g=sha(p)
 if g!=h: die(f'{n} hash {g} != {h}')

def main():
 check(PATCH,EXPECTED['patch'],'patch'); check(ORACLE,EXPECTED['oracle'],'oracle')
 check(STATIC/'CAMSS-VFE1-DAL-START-0047-CHECKPATCH.log',EXPECTED['checkpatch'],'checkpatch')
 check(STATIC/'CAMSS-VFE1-DAL-START-0047-BUILD.log',EXPECTED['build'],'build')
 check(MODULE,EXPECTED['module'],'module')
 for f in ('camss.c','camss-vfe-680.c','camss-vfe.h'): check(SRC/f,EXPECTED[f],f)
 o=json.loads(ORACLE.read_text())
 if not o.get('accepted') or o.get('runtime_authorized') is not False: die('oracle acceptance/runtime gate')
 writes=o['irq_mask_callback']['writes']
 expect=[('VFE TOP','0x34','0x0007f051'),('VFE TOP','0x38','0x00000000'),('VFE BUS','0x18','0xd0000000'),('VFE BUS','0x1c','0x00000000')]
 if [(x['base'],x['offset'],x['value']) for x in writes]!=expect: die('oracle mask write drift')
 opt=o['irq_mask_callback']['optional_write']
 if opt['offset']!='0x08' or not opt['linux_status'].startswith('not authorized'): die('optional path classification drift')
 if o['pre_bus_top_callback']['write']['offset']!='0x24' or o['pre_bus_top_callback']['write']['value']!='0x00000000': die('top zero drift')
 if o['top_0x24_transition']!='packet0/1 leave 0x6000 -> DAL_ife_start writes 0 -> BUS start -> packet2/3 restore 0x6000': die('transition drift')

 v=(SRC/'camss-vfe-680.c').read_text(); c=(SRC/'camss.c').read_text(); h=(SRC/'camss-vfe.h').read_text()
 a=v.index('int vfe680_x1e_pix_runtime_start_prefix(struct vfe_device *vfe)')
 b=v.index('\nint vfe680_x1e_pix_runtime_bus_prepare(',a)
 body=v[a:b]
 if body.count('writel_relaxed(')!=5: die(f'prefix write count {body.count("writel_relaxed(")}')
 required=[
  'writel_relaxed(VFE680_X1E_WINDOWS_TOP_MASK0,',
  'writel_relaxed(0, vfe->base + VFE_TOP_IRQn_MASK(vfe, 1));',
  'writel_relaxed(VFE680_X1E_WINDOWS_BUS_MASK0,',
  'writel_relaxed(0, vfe->base + VFE_BUS_IRQn_MASK(vfe, 1));',
  'writel_relaxed(0, vfe->base + VFE680_X1E_DAL_START_TOP_ZERO);']
 for x in required:
  if x not in body: die('missing helper write '+x)
 if '0xfffffff' in body or '+ 8' in body or '+ 0x08' in body: die('optional BUS +0x08 path leaked into helper')
 if '#define VFE680_X1E_DAL_START_TOP_ZERO  0x00000024' not in v: die('top zero offset define drift')
 if h.count('vfe680_x1e_pix_runtime_start_prefix')!=1: die('header declaration drift')
 if c.count('vfe680_x1e_pix_runtime_start_prefix(vfe)')!=1: die('runner call count drift')
 p1=c.index('csid680_x1e_front_ipp_companion(csid, 1)')
 prefix=c.index('vfe680_x1e_pix_runtime_start_prefix(vfe)',p1)
 bus=c.index('vfe680_x1e_pix_runtime_bus_prepare(vfe, pix)',prefix)
 prime1=c.index('camss_x1e_pix_submit_prime(camss, &materialized->prime, 1)',bus)
 packet2=c.index('&materialized->startup, 2)',prime1)
 if not p1 < prefix < bus < prime1 < packet2: die('runner ordering drift')

 # Patch reverse must reconstruct exact 0046 bytes; forward must recover live 0047.
 with tempfile.TemporaryDirectory() as td:
  root=Path(td); d=root/'drivers/media/platform/qcom/camss'; d.mkdir(parents=True)
  for f in BASE: shutil.copy2(SRC/f,d/f)
  subprocess.check_call(['patch','-d',str(root),'-p1','-R','--batch','--silent'],stdin=PATCH.open('rb'))
  for f,hsh in BASE.items():
   if sha(d/f)!=hsh: die('reverse baseline drift '+f)
  subprocess.check_call(['patch','-d',str(root),'-p1','--batch','--silent'],stdin=PATCH.open('rb'))
  for f,hsh in EXPECTED.items():
   if f in BASE and sha(d/f)!=hsh: die('forward source drift '+f)

 cp=(STATIC/'CAMSS-VFE1-DAL-START-0047-CHECKPATCH.log').read_text()
 if '0 errors, 0 warnings, 0 checks' not in cp: die('strict checkpatch not clean')
 modinfo=subprocess.check_output(['modinfo',str(MODULE)],text=True)
 vermagic=next(x.split(':',1)[1].strip() for x in modinfo.splitlines() if x.startswith('vermagic:'))
 if vermagic!='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64': die('vermagic drift')

 out={
  'schema':'sp11-e003h-linux-0047-vfe1-dal-start-prefix-inspection-v1','accepted':True,
  'oracle_sha256':EXPECTED['oracle'],'patch_sha256':EXPECTED['patch'],
  'module_sha256':EXPECTED['module'],'module_vermagic':vermagic,
  'source_sha256':{f:EXPECTED[f] for f in BASE},'base_0046_source_sha256':BASE,
  'patch_roundtrip_byte_identical':True,
  'write_count':5,
  'write_order':['TOP mask0=0x0007f051','TOP mask1=0','BUS mask0=0xd0000000','BUS mask1=0','VFE TOP +0x24=0'],
  'optional_bus_0x08_added':False,
  'runner_order':['startup packet1','CSID companion1','VFE DAL start prefix','existing BUS prepare','prime1','startup packet2'],
  'captured_rtcdm_bytes_changed':False,'csid_changed':False,'sensor_changed':False,
  'runtime_authorized':False,
 }
 op=STATIC/'linux-0047-vfe1-dal-start-prefix-inspection.json'; op.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(json.dumps(out,indent=2,sort_keys=True))

if __name__=='__main__': main()
