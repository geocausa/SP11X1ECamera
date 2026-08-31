#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess
R=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
O=R/'experiments/E003-front-imx681-cphy/e003h-vfe1-ubwc-static-0061-static'
S=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss/camss-vfe-680.c')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest(); h=lambda s:hashlib.sha256(s.encode()).hexdigest()
new=S.read_text()
defs='''/* Same-machine qccamisp computes and writes this exact SP11 VFE1 value. */
#define VFE680_X1E_WINDOWS_UBWC_STATIC_CTRL\t0x00001046
'''
write='''\t/* Exact SP11 qccamisp BUS-common UBWC static programming. */
\twritel_relaxed(VFE680_X1E_WINDOWS_UBWC_STATIC_CTRL,
\t\t       vfe->base + VFE680_X1E_BUS_UBWC_STATIC_CTRL);

'''
assert new.count(defs)==1 and new.count(write)==1
old=new.replace(defs,'',1).replace(write,'',1)
assert h(old)=='77544e3aa12bd9c374409ffdb436bc75f0325684c4f5046cb98704debb540527'
assert h(new)=='090b00419096d27214985d3b957ef7942e9455c6d8ab148af2afd25954f1cdd9'
assert new.count('writel_relaxed(')-old.count('writel_relaxed(')==1
assert new.count('readl_relaxed(')==old.count('readl_relaxed(')
oldw=[l.strip() for l in old.splitlines() if 'writel' in l]
neww=[l.strip() for l in new.splitlines() if 'writel' in l]
extra=neww.copy()
for l in oldw: extra.remove(l)
assert extra==['writel_relaxed(VFE680_X1E_WINDOWS_UBWC_STATIC_CTRL,']
# It must be in the bounded X1E VFE1 bus_prepare after address validation and before client config.
pos=new.index(write); assert new.rfind('ret = vfe680_x1e_bus_build_addresses(iovas, &addr);',0,pos)>new.rfind('static int vfe680_x1e_bus_prepare',0,pos)
assert new.index('vfe680_x1e_bus_config_client(vfe, c);',pos)>pos
assert 'if (!vfe680_x1e_bus_target(vfe))\n\t\treturn -ENODEV;' in new[new.rfind('static int vfe680_x1e_bus_prepare',0,pos):pos]
cp=(O/'CHECKPATCH.raw.txt').read_text(); assert '0 errors, 0 warnings' in cp
assert sha(O/'qcom-camss.ko')=='6b23dc7f41cd675107d81d89d61ae341807954b6649df03e7e1ac7a465d827b3'
vm=subprocess.check_output(['modinfo','-F','vermagic',str(O/'qcom-camss.ko')],text=True).strip(); assert vm=='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
oracle=json.loads((O/'0061-static-oracle.json').read_text()); assert oracle['accepted'] and not oracle['runtime_authorized'] and oracle['target']['windows_value']=='0x00001046'
own=R/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/windows-vfe1-ubwc-static-ownership/windows-vfe1-ubwc-static-ownership.json'
assert sha(own)==oracle['windows_ownership_oracle_sha256']; assert json.loads(own.read_text())['classification']['qccamisp_owns_bus_ubwc_static_write']
run=R/'experiments/E003-front-imx681-cphy/e003h-vfe1-bus-progress-readonly-0060-candidate/runtime-0060-analysis.json'
assert sha(run)==oracle['consumed_0060_analysis_sha256']; assert json.loads(run.read_text())['authorization_consumed']
expected={
 'camss.c':'945a5765667ab6a2bada9395079cd519e7afc038afaa8d57d99926dd38c50795',
 'camss-csid-680.c':'6171b255cfdc6372f46702c150338c6921fa326f3997267e83a4ae47b284955d',
 'camss-csid.c':'fc316d35114a23e29333b22a6fb10f9af2f5dfb15ae829a963ecd05c53d6b229',
 'camss-csiphy-3ph-1-0.c':'418fe18845e1d57e2de5f2c9ece4bdd78d817d59ca71b25b00eb4259581464a8'}
root=S.parent
for n,v in expected.items(): assert sha(root/n)==v,(n,sha(root/n),v)
out={'schema':'sp11-e003h-vfe1-ubwc-static-0061-inspection-v1','accepted':True,'base_source_sha256':h(old),'source_sha256':h(new),'module_sha256':sha(O/'qcom-camss.ko'),'patch_sha256':sha(O/'0061-vfe1-ubwc-static-parity.patch'),'oracle_sha256':sha(O/'0061-static-oracle.json'),'windows_ownership_oracle_sha256':sha(own),'consumed_0060_analysis_sha256':sha(run),'new_mmio_writes':1,'new_direct_mmio_reads':0,'existing_mmio_write_lines_unchanged':True,'write_offset':'0x0c58','write_value':'0x00001046','write_before_bus_client_config_and_enable':True,'bounded_x1e80100_vfe1_only':True,'retains_0060_telemetry':True,'camera_programming_delta_only_ubwc_static':True,'checkpatch_errors':0,'checkpatch_warnings':0,'golden_vermagic_exact':True,'frozen_source_sha256':expected,'runtime_authorized':False}
(O/'0061-static-inspection.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True)); print('INSPECTION_SHA='+sha(O/'0061-static-inspection.json'))
