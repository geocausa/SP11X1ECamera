#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess
REPO=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
SRC=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss/camss-vfe-680.c')
OUT=REPO/'experiments/E003-front-imx681-cphy/e003h-vfe1-lowtop-readonly-0059-static'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
new=SRC.read_text()
macro="""
/* 0059 read-only VFE680 low-TOP parity telemetry offsets. */
#define VFE680_X1E_CORE_CFG2			0x002c
#define VFE680_X1E_CORE_CFG3			0x0068
#define VFE680_X1E_STATS_THROTTLE0		0x0070
#define VFE680_X1E_STATS_THROTTLE1		0x0074
#define VFE680_X1E_STATS_THROTTLE2		0x0078
#define VFE680_X1E_CORE_CFG4			0x0080
#define VFE680_X1E_CORE_CFG5			0x0084
#define VFE680_X1E_CORE_CFG6			0x0088
#define VFE680_X1E_PERIOD_CFG			0x008c
#define VFE680_X1E_EPOCH_HEIGHT_CFG		0x009c
"""
tele="""	dev_info(vfe->camss->dev,
		 "E003h VFE1 %s cfg=%08x/%08x/%08x diag=%08x core3=%08x throttle=%08x/%08x/%08x\\n",
		 why, readl_relaxed(vfe->base + VFE680_X1E_SP11_DAL_CORE_CFG0),
		 readl_relaxed(vfe->base + VFE680_X1E_SP11_DAL_CORE_CFG1),
		 readl_relaxed(vfe->base + VFE680_X1E_CORE_CFG2),
		 readl_relaxed(vfe->base + VFE_TOP_DIAG_CONFIG),
		 readl_relaxed(vfe->base + VFE680_X1E_CORE_CFG3),
		 readl_relaxed(vfe->base + VFE680_X1E_STATS_THROTTLE0),
		 readl_relaxed(vfe->base + VFE680_X1E_STATS_THROTTLE1),
		 readl_relaxed(vfe->base + VFE680_X1E_STATS_THROTTLE2));
	dev_info(vfe->camss->dev,
		 "E003h VFE1 %s core456=%08x/%08x/%08x period=%08x epoch_height=%08x\\n",
		 why, readl_relaxed(vfe->base + VFE680_X1E_CORE_CFG4),
		 readl_relaxed(vfe->base + VFE680_X1E_CORE_CFG5),
		 readl_relaxed(vfe->base + VFE680_X1E_CORE_CFG6),
		 readl_relaxed(vfe->base + VFE680_X1E_PERIOD_CFG),
		 readl_relaxed(vfe->base + VFE680_X1E_EPOCH_HEIGHT_CFG));
"""
assert macro in new and tele in new
old=new.replace(macro,'',1).replace(tele,'',1)
h=lambda s:hashlib.sha256(s.encode()).hexdigest()
assert h(old)=='204162bf1296f41a7e0999fd37b243ef0944fd9edd3c3fba93f37037e3974a12'
assert h(new)=='bcc889a8e91627c670dda14d371eb037c1a5833aa41d333ca0174223fb492310'
assert new.count('readl_relaxed(')-old.count('readl_relaxed(')==13
assert new.count('writel_relaxed(')==old.count('writel_relaxed(')
assert new.count('writel(')==old.count('writel(')
old_w=[x.strip() for x in old.splitlines() if 'writel' in x]
new_w=[x.strip() for x in new.splitlines() if 'writel' in x]
assert old_w==new_w
patch=(OUT/'0059-vfe1-lowtop-readonly-telemetry.patch').read_text()
for line in patch.splitlines():
    if line.startswith('-') and not line.startswith('---'):
        raise AssertionError('patch removes source line: '+line)
cp=(OUT/'CHECKPATCH.raw.txt').read_text(); assert '0 errors, 0 warnings, 0 checks' in cp
assert sha(OUT/'qcom-camss.ko')=='e714330b3f2d32a18d51e5fb7577242b7e34f96f9af889afaf1e658d4bf752f0'
vm=subprocess.check_output(['modinfo','-F','vermagic',str(OUT/'qcom-camss.ko')],text=True).strip()
assert vm=='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
o=json.loads((OUT/'0059-static-oracle.json').read_text())
assert o['accepted'] and o['runtime_authorized'] is False
assert o['windows_live1_lowtop']['0x0050']=='0x00400000'
out={'schema':'sp11-e003h-vfe1-lowtop-0059-static-inspection-v1','accepted':True,'base_source_sha256':h(old),'source_sha256':h(new),'module_sha256':sha(OUT/'qcom-camss.ko'),'patch_sha256':sha(OUT/'0059-vfe1-lowtop-readonly-telemetry.patch'),'oracle_sha256':sha(OUT/'0059-static-oracle.json'),'new_direct_mmio_reads':13,'new_mmio_writes':0,'existing_mmio_write_lines_unchanged':True,'camera_programming_changed':False,'checkpatch_errors':0,'checkpatch_warnings':0,'golden_vermagic_exact':True,'scope':'existing bounded X1E80100 VFE1 runtime dump only','runtime_authorized':False}
(OUT/'0059-static-inspection.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True)); print('INSPECTION_SHA256='+sha(OUT/'0059-static-inspection.json'))
