#!/usr/bin/env python3
import hashlib, json, re, subprocess, tempfile
from pathlib import Path

REPO=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
KS=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src')
D=REPO/'experiments/E003-front-imx681-cphy/e003h-vfe1-sp11-active-start-prefix-0057-static'
V=KS/'drivers/media/platform/qcom/camss/camss-vfe-680.c'
CAMSS=KS/'drivers/media/platform/qcom/camss/camss.c'
VH=KS/'drivers/media/platform/qcom/camss/camss-vfe.h'
PATCH=D/'0057-x1e-vfe1-sp11-active-start-prefix.patch'
MOD=D/'qcom-camss.ko'
ORACLE=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/windows-vfe1-sp11-active-start-prefix/windows-vfe1-sp11-active-start-prefix-oracle.json'
BASE_SHA='0dc6269d8b7c0e57e1442dfea374f0e90bdf14b8e8ef58117a505cda6d643036'
NEW_SHA='204162bf1296f41a7e0999fd37b243ef0944fd9edd3c3fba93f37037e3974a12'
CAMSS_SHA='945a5765667ab6a2bada9395079cd519e7afc038afaa8d57d99926dd38c50795'
VH_SHA='1029c3d353e93209d212729be238f9665308ba97eb659d8c6648c86c238d1bbd'
ORACLE_SHA='aeac1c99783427fc0bafdda7e57df73ecedf02f63881c6118871288aea9e6b02'
MOD_SHA='3fd0ebdc8a3f17fdc49e117d77fa10e03711dfbd27bc552e79230540f1cef80c'
VERMAGIC='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(c,m):
    if not c: raise SystemExit('FAIL: '+m)
need(sha(V)==NEW_SHA,'0057 source hash')
need(sha(CAMSS)==CAMSS_SHA,'camss.c drift')
need(sha(VH)==VH_SHA,'camss-vfe.h drift')
need(sha(ORACLE)==ORACLE_SHA,'active Windows oracle drift')
need(sha(MOD)==MOD_SHA,'module drift')
need(subprocess.check_output(['modinfo','-F','vermagic',str(MOD)],text=True).strip()==VERMAGIC,'vermagic')
check=(D/'CHECKPATCH.raw.txt').read_text()
need('total: 0 errors, 0 warnings, 0 checks' in check,'checkpatch')

patch=PATCH.read_text()
changed=re.findall(r'^--- a/(.+)$',patch,re.M)
need(changed==['drivers/media/platform/qcom/camss/camss-vfe-680.c'],f'patch scope {changed}')
need('camss.c' not in '\n'.join(changed),'runner changed')

# Reverse and forward reconstruction against the exact current source.
with tempfile.TemporaryDirectory() as td:
    t=Path(td); target=t/'drivers/media/platform/qcom/camss/camss-vfe-680.c'; target.parent.mkdir(parents=True); target.write_bytes(V.read_bytes())
    subprocess.run(['patch','-s','-R','-p1','-i',str(PATCH)],cwd=t,check=True)
    rev=sha(target); need(rev==BASE_SHA,f'reverse source {rev}')
    subprocess.run(['patch','-s','-p1','-i',str(PATCH)],cwd=t,check=True)
    fwd=sha(target); need(fwd==NEW_SHA,f'forward source {fwd}')

src=V.read_text()
# Preserve steady-state Windows contract separately from transient active callback.
need('#define VFE680_X1E_WINDOWS_BUS_MASK0    0xd0000000' in src,'steady BUS mask contract changed')
vals={
 'core_cfg0_off':'#define VFE680_X1E_SP11_DAL_CORE_CFG0   0x00000024',
 'core_cfg1_off':'#define VFE680_X1E_SP11_DAL_CORE_CFG1   0x00000028',
 'bus_cgc_off':'#define VFE680_X1E_SP11_DAL_BUS_CGC_OVD 0x00000c08',
 'core_cfg0':'#define VFE680_X1E_SP11_DAL_CORE_CFG0_VALUE 0x00000007',
 'core_cfg1':'#define VFE680_X1E_SP11_DAL_CORE_CFG1_VALUE 0x00000010',
 'bus_mask0':'#define VFE680_X1E_SP11_DAL_BUS_MASK0   0xdc000000',
 'bus_cgc':'#define VFE680_X1E_SP11_DAL_BUS_CGC_OVD_VALUE 0x000001ff',
}
for k,v in vals.items(): need(v in src,k)

m=re.search(r'int vfe680_x1e_pix_runtime_start_prefix\(struct vfe_device \*vfe\)\n\{(.*?)\n\}\n\nint vfe680_x1e_pix_runtime_bus_prepare',src,re.S)
need(m,'start prefix body'); body=m.group(1)
# Three retained prerequisites are explicitly outside the active callback block.
pre=[
 'writel_relaxed(VFE680_X1E_WINDOWS_TOP_MASK0,',
 'writel_relaxed(0, vfe->base + VFE_TOP_IRQn_MASK(vfe, 1));',
 'writel_relaxed(0, vfe->base + VFE_BUS_IRQn_MASK(vfe, 1));',
]
active=[
 'writel_relaxed(VFE680_X1E_SP11_DAL_CORE_CFG0_VALUE,',
 'writel_relaxed(VFE680_X1E_SP11_DAL_CORE_CFG1_VALUE,',
 'writel_relaxed(VFE680_X1E_SP11_DAL_BUS_MASK0,',
 'writel_relaxed(VFE680_X1E_SP11_DAL_BUS_CGC_OVD_VALUE,',
]
pos=[]
for s in pre+active:
    i=body.find(s); need(i>=0,'missing '+s); pos.append(i)
need(pos==sorted(pos),'write order drift')
need('VFE680_X1E_WINDOWS_BUS_MASK0,' not in body,'steady-state d0000000 still used in DAL prefix')
need('VFE680_X1E_DAL_START_TOP_ZERO' not in src,'old top-zero path remains')

# New direct reads are forbidden; the delta adds exactly two writel callsites.
base=Path('/tmp/camss-vfe-680.0056-base.c')
# /tmp is convenient during creation; reconstruction above is authoritative if this disappears.
base_text=base.read_text() if base.exists() and sha(base)==BASE_SHA else None
if base_text is not None:
    need(src.count('readl_relaxed(')==base_text.count('readl_relaxed('),'new direct read')
    need(src.count('writel_relaxed(')==base_text.count('writel_relaxed(')+2,'direct write callsite count')

oracle=json.loads(ORACLE.read_text()); need(oracle['accepted'],'oracle not accepted')
need(oracle['active_callback_pair']=={'second_callback_semantics':'ret/no MMIO','slot_0x6b690':'0x1be80','slot_0x6b698':'0x1c0e0'},'callback pair drift')
expected=[('0x24','0x00000007'),('0x28','0x00000010'),('0xc18','0xdc000000'),('0xc08','0x000001ff')]
got=[(x['offset'],x['value']) for x in oracle['active_first_callback']['writes_in_order'] if x['space']!='software shadow']
need(got==expected,f'active oracle values {got}')

out={
 'schema':'sp11-e003h-vfe1-active-start-prefix-0057-static-inspection-v1','accepted':True,
 'base_vfe680_sha256':BASE_SHA,'vfe680_sha256':NEW_SHA,'camss_c_sha256':CAMSS_SHA,'vfe_h_sha256':VH_SHA,
 'oracle_sha256':ORACLE_SHA,'patch_sha256':sha(PATCH),'module_sha256':MOD_SHA,'vermagic':VERMAGIC,
 'patch_scope':['camss-vfe-680.c'],'reverse_patch_exact':True,'forward_patch_exact':True,
 'retained_linux_irq_visibility_prerequisites':['TOP +0x34=0x0007f051','TOP +0x38=0','BUS +0xc1c=0'],
 'active_sp11_callback_write_order':['TOP +0x24=0x00000007','TOP +0x28=0x00000010','BUS +0xc18=0xdc000000','BUS +0xc08=0x000001ff'],
 'changed_existing_write_values':{'TOP +0x24':['0x00000000','0x00000007'],'BUS +0xc18':['0xd0000000','0xdc000000']},
 'new_write_offsets':['0x28','0xc08'],'new_direct_mmio_write_calls':2,'new_direct_mmio_reads':0,
 'steady_state_windows_bus_mask0_retained':'0xd0000000',
 'unchanged':['camss.c runner/order','camss-vfe.h ABI','sensor','CSID','RT-CDM command bytes','CSIPHY','DT','BUS client recipe','CAMNOC 300MHz correction'],
 'runtime_authorized':False,
}
(D/'0057-static-inspection.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True))
print('PASS: 0057 active SP11 IFE1 DAL-start static correction')
