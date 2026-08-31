#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, subprocess

R = Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
O = R / 'experiments/E003-front-imx681-cphy/e003h-vfe1-cgc-release-0062-static'
W = R / 'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/windows-vfe1-cgc-cold-path'
S = Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss/camss-vfe-680.c')
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
h = lambda s: hashlib.sha256(s.encode()).hexdigest()

new = S.read_text()
new_comment = '\t/* Retain the proven active SP11 IFE1 TOP/BUS mask writes. */\n'
old_comment = '\t/* Exact active SP11 IFE1 callback RVA 0x1be80 write order. */\n'
anchor = '''\twritel_relaxed(VFE680_X1E_SP11_DAL_BUS_MASK0,\n\t\t       vfe->base + VFE_BUS_IRQn_MASK(vfe, 0));\n'''
removed = '''\twritel_relaxed(VFE680_X1E_SP11_DAL_BUS_CGC_OVD_VALUE,\n\t\t       vfe->base + VFE680_X1E_SP11_DAL_BUS_CGC_OVD);\n'''
assert new.count(new_comment) == 1
assert new.count(old_comment) == 0
assert new.count(anchor) == 1
assert removed not in new
old = new.replace(new_comment, old_comment, 1).replace(anchor, anchor + removed, 1)
assert h(old) == '090b00419096d27214985d3b957ef7942e9455c6d8ab148af2afd25954f1cdd9'
assert h(new) == '36a07ad05f2ea5fdb5d1fcb168eb730cc8fe640b14a21dcb8bb22427c5398d81'
assert old.count('writel_relaxed(') - new.count('writel_relaxed(') == 1
assert new.count('readl_relaxed(') == old.count('readl_relaxed(')
oldw = [l.strip() for l in old.splitlines() if 'writel' in l]
neww = [l.strip() for l in new.splitlines() if 'writel' in l]
removed_lines = oldw.copy()
for line in neww:
    removed_lines.remove(line)
assert removed_lines == ['writel_relaxed(VFE680_X1E_SP11_DAL_BUS_CGC_OVD_VALUE,']
assert 'writel_relaxed(VFE680_X1E_WINDOWS_UBWC_STATIC_CTRL,' in new
assert 'readl_relaxed(vfe->base + VFE680_X1E_SP11_DAL_BUS_CGC_OVD)' in new
assert '#define VFE680_X1E_SP11_DAL_BUS_CGC_OVD_VALUE 0x000001ff' in new

cp = (O / 'CHECKPATCH.raw.txt').read_text()
assert '0 errors, 0 warnings' in cp
assert sha(O / 'qcom-camss.ko') == '71a7338ff2aa89c69e8e695989e154120dbef07ed1b91f64417796fb92bb6e19'
vm = subprocess.check_output(['modinfo','-F','vermagic',str(O/'qcom-camss.ko')], text=True).strip()
assert vm == '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'

oracle = json.loads((O / '0062-static-oracle.json').read_text())
assert oracle['accepted'] and not oracle['runtime_authorized']
assert oracle['differential']['removed_mmio_writes'] == 1
assert oracle['differential']['new_mmio_writes'] == 0
assert not oracle['differential']['replacement_zero_write']
assert oracle['windows_cold_path']['holder_start_status'] == 'Success'
assert oracle['windows_cold_path']['live_bus_c08'] == '0x00000000'
assert sha(W / 'E003H_VFE1_CGC_COLD_ENTRY_20260831.log') == oracle['windows_cold_kd_sha256']
assert sha(W / 'HOLDER-SUCCESS.txt') == oracle['windows_holder_record_sha256']

expected = {
    'camss.c':'945a5765667ab6a2bada9395079cd519e7afc038afaa8d57d99926dd38c50795',
    'camss-csid-680.c':'6171b255cfdc6372f46702c150338c6921fa326f3997267e83a4ae47b284955d',
    'camss-csid.c':'fc316d35114a23e29333b22a6fb10f9af2f5dfb15ae829a963ecd05c53d6b229',
    'camss-csiphy-3ph-1-0.c':'418fe18845e1d57e2de5f2c9ece4bdd78d817d59ca71b25b00eb4259581464a8'
}
root = S.parent
for name, digest in expected.items():
    assert sha(root / name) == digest, (name, sha(root / name), digest)

out = {
    'schema':'sp11-e003h-vfe1-cgc-release-0062-inspection-v1',
    'accepted':True,
    'base_source_sha256':h(old),
    'source_sha256':h(new),
    'module_sha256':sha(O/'qcom-camss.ko'),
    'patch_sha256':sha(O/'0062-vfe1-cgc-release.patch'),
    'oracle_sha256':sha(O/'0062-static-oracle.json'),
    'windows_cold_kd_sha256':sha(W/'E003H_VFE1_CGC_COLD_ENTRY_20260831.log'),
    'windows_holder_record_sha256':sha(W/'HOLDER-SUCCESS.txt'),
    'removed_mmio_writes':1,
    'new_mmio_writes':0,
    'new_direct_mmio_reads':0,
    'replacement_zero_write':False,
    'removed_offset':'0x0c08',
    'removed_value':'0x000001ff',
    'retains_ubwc_static_0x1046':True,
    'retains_bus_cgc_readback_telemetry':True,
    'bounded_x1e80100_vfe1_only':True,
    'checkpatch_errors':0,
    'checkpatch_warnings':0,
    'golden_vermagic_exact':True,
    'frozen_source_sha256':expected,
    'runtime_authorized':False
}
(O / '0062-static-inspection.json').write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
print(json.dumps(out, indent=2, sort_keys=True))
print('INSPECTION_SHA=' + sha(O/'0062-static-inspection.json'))
