#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess
REPO=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
KS=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss')
SRC=KS/'camss-vfe-680.c'
OUT=REPO/'experiments/E003-front-imx681-cphy/e003h-vfe1-bus-progress-readonly-0060-static'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
h=lambda s:hashlib.sha256(s.encode()).hexdigest()
new=SRC.read_text()
macro='''/* 0060 read-only VFE680 BUS progression telemetry offsets. */
#define VFE680_X1E_BUS_UBWC_STATIC_CTRL\t\t0x0c58
#define VFE680_X1E_BUS_PWR_ISO_CFG\t\t0x0c5c
#define VFE680_X1E_BUS_DEBUG_TOP_CFG\t\t0x0cd4
#define VFE680_X1E_BUS_DEBUG_TOP\t\t0x0cd8
#define VFE680_X1E_BUS_TEST_BUS_CTRL\t\t0x0cdc
#define VFE680_X1E_BUS_ADDR_STATUS0\t\t0x70
#define VFE680_X1E_BUS_ADDR_STATUS1\t\t0x74
#define VFE680_X1E_BUS_ADDR_STATUS2\t\t0x78
#define VFE680_X1E_BUS_ADDR_STATUS3\t\t0x7c
#define VFE680_X1E_BUS_DEBUG_STATUS0\t\t0x84
#define VFE680_X1E_BUS_DEBUG_STATUS1\t\t0x88

'''
tele='''\tdev_info(vfe->camss->dev,
\t\t "E003h VFE1 %s buscommon cgc=%08x ubwc=%08x piso=%08x dbgcfg=%08x dbg=%08x test=%08x\\n",
\t\t why, readl_relaxed(vfe->base + VFE680_X1E_SP11_DAL_BUS_CGC_OVD),
\t\t readl_relaxed(vfe->base + VFE680_X1E_BUS_UBWC_STATIC_CTRL),
\t\t readl_relaxed(vfe->base + VFE680_X1E_BUS_PWR_ISO_CFG),
\t\t readl_relaxed(vfe->base + VFE680_X1E_BUS_DEBUG_TOP_CFG),
\t\t readl_relaxed(vfe->base + VFE680_X1E_BUS_DEBUG_TOP),
\t\t readl_relaxed(vfe->base + VFE680_X1E_BUS_TEST_BUS_CTRL));
\tfor (i = 0; i < ARRAY_SIZE(vfe680_x1e_windows_bus_client_order); i++) {
\t\tu8 client = vfe680_x1e_windows_bus_client_order[i];
\t\tvoid __iomem *cfg = vfe680_x1e_bus_reg(vfe, client, 0);

\t\tdev_info(vfe->camss->dev,
\t\t\t "E003h VFE1 %s busc%u cfg=%08x image=%08x stat=%08x/%08x/%08x/%08x dbg=%08x/%08x\\n",
\t\t\t why, client, readl_relaxed(cfg + VFE680_X1E_BUS_CFG),
\t\t\t readl_relaxed(cfg + VFE680_X1E_BUS_IMAGE_ADDR),
\t\t\t readl_relaxed(cfg + VFE680_X1E_BUS_ADDR_STATUS0),
\t\t\t readl_relaxed(cfg + VFE680_X1E_BUS_ADDR_STATUS1),
\t\t\t readl_relaxed(cfg + VFE680_X1E_BUS_ADDR_STATUS2),
\t\t\t readl_relaxed(cfg + VFE680_X1E_BUS_ADDR_STATUS3),
\t\t\t readl_relaxed(cfg + VFE680_X1E_BUS_DEBUG_STATUS0),
\t\t\t readl_relaxed(cfg + VFE680_X1E_BUS_DEBUG_STATUS1));
\t}
'''
assert macro in new and tele in new and '\tunsigned int i;\n' in new
old=new.replace(macro,'',1).replace('\tconst char *why = reason ? reason : \"snapshot\";\n\tunsigned int i;\n\tint ret;\n','\tconst char *why = reason ? reason : \"snapshot\";\n\tint ret;\n',1).replace(tele,'',1)
assert h(old)=='bcc889a8e91627c670dda14d371eb037c1a5833aa41d333ca0174223fb492310'
assert h(new)=='77544e3aa12bd9c374409ffdb436bc75f0325684c4f5046cb98704debb540527'
assert new.count('readl_relaxed(')-old.count('readl_relaxed(')==14
assert new.count('writel_relaxed(')==old.count('writel_relaxed(')
assert new.count('writel(')==old.count('writel(')
assert [x.strip() for x in new.splitlines() if 'writel' in x]==[x.strip() for x in old.splitlines() if 'writel' in x]
patch=OUT/'0060-vfe1-bus-progress-readonly-telemetry.patch'
for line in patch.read_text().splitlines():
    if line.startswith('-') and not line.startswith('---'):
        raise AssertionError('patch removes source line: '+line)
cp=(OUT/'CHECKPATCH.raw.txt').read_text(); assert '0 errors, 0 warnings, 0 checks' in cp
assert sha(OUT/'qcom-camss.ko')=='00da9fd6510ed01455f4b2349d6730fcf8ce81571e94dbbdbade526b77cae8d6'
vm=subprocess.check_output(['modinfo','-F','vermagic',str(OUT/'qcom-camss.ko')],text=True).strip()
assert vm=='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
# Freeze unrelated camera programming owners.
expected={
 'camss.c':'945a5765667ab6a2bada9395079cd519e7afc038afaa8d57d99926dd38c50795',
 'camss-csid-680.c':'6171b255cfdc6372f46702c150338c6921fa326f3997267e83a4ae47b284955d',
 'camss-csid.c':'fc316d35114a23e29333b22a6fb10f9af2f5dfb15ae829a963ecd05c53d6b229',
 'camss-csiphy-3ph-1-0.c':'418fe18845e1d57e2de5f2c9ece4bdd78d817d59ca71b25b00eb4259581464a8'}
for f,s in expected.items(): assert sha(KS/f)==s,(f,sha(KS/f))
o=json.loads((OUT/'0060-static-oracle.json').read_text())
assert o['accepted'] and o['runtime_authorized'] is False
assert o['linux_current_path']['nine_windows_active_clients_already_configured'] is True
assert o['vendor_reference']['vfe680_comp_cfg_needed'] is False
assert o['windows_same_machine_live']['bus_common']['ubwc_static_0x0c58']=='0x00001046'
out={'schema':'sp11-e003h-vfe1-bus-progress-0060-static-inspection-v1','accepted':True,'base_source_sha256':h(old),'source_sha256':h(new),'module_sha256':sha(OUT/'qcom-camss.ko'),'patch_sha256':sha(patch),'oracle_sha256':sha(OUT/'0060-static-oracle.json'),'new_direct_mmio_read_callsites':14,'new_mmio_writes':0,'existing_mmio_write_lines_unchanged':True,'camera_programming_changed':False,'nine_windows_bus_clients_already_present':True,'vfe680_comp_cfg_needed':False,'windows_live_ubwc_static_ctrl':'0x00001046','checkpatch_errors':0,'checkpatch_warnings':0,'golden_vermagic_exact':True,'runtime_authorized':False,'frozen_source_sha256':expected}
(OUT/'0060-static-inspection.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True)); print('INSPECTION_SHA256='+sha(OUT/'0060-static-inspection.json'))
