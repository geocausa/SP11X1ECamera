#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, re, struct, subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OEM=ROOT/'experiments/E001-windows-oracle-map/oracle-local/qccamisp8380.sys'
QROOT=Path('/home/geoca/.cache/qualcomm-camera-driver')
QHDR=QROOT/'camera/drivers/cam_isp/isp_hw_mgr/isp_hw/vfe_hw/vfe17x/cam_vfe680.h'
QBUS=QROOT/'camera/drivers/cam_isp/isp_hw_mgr/isp_hw/vfe_hw/vfe_bus/cam_vfe_bus_ver3.c'
OEM_SHA='64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c'
QHDR_SHA='a31f6fe84cbd2b544fe504e9099ea6adc6bbe846628999742d9fb6024add2505'
QBUS_SHA='dbe53691b46f912d59a5848a7c3e039601088430fd2e3efc992d9100dcc36b44'

def req(v,m):
    if not v: raise AssertionError('E005T_FAIL_CLOSED '+m)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

d=json.loads((HERE/'RESULT.json').read_text())
s=json.loads((ROOT/'experiments/E004-front-ir-vd55g0/e005s-windows-live-300d-composite-group-minimal/RESULT.json').read_text())
req(sha(OEM)==OEM_SHA,'OEM SHA')
req(sha(QHDR)==QHDR_SHA,'VFE680 SHA')
req(sha(QBUS)==QBUS_SHA,'BUSv3 SHA')
req(s['live_oem_output_resource']['same_sp11_oem_live_composite_group']==3,'E005s live group3')

raw=OEM.read_bytes()
# PE .text: RVA 0x1000 -> raw 0x400 for this pinned image.
lit_off=0x400+(0x1dc18-0x1000)
req(struct.unpack_from('<I',raw,lit_off)[0]==0x20001,'OEM 0x300d cfg literal')

dis=subprocess.check_output(['llvm-objdump','-d','--no-show-raw-insn',str(OEM)],text=True,errors='replace')
for pat in (
 r'14001d850:.*mov\s+w8, #0x300d',
 r'14001d864:.*ldr\s+w8, 0x14001dc18',
 r'14001d888:.*csel\s+w21, w8, wzr, eq',
 r'14001da6c:.*ldr\s+x8, \[x19, #0x150\].*?14001da70:.*mov\s+x1, #0x1200.*?14001da74:.*str\s+w21, \[x8, #0x1200\]',
 r'1400280a0:.*mov\s+w13, #0x300d.*?140028124:.*orr\s+w9, w8, #0x100.*?140028128:.*cmp\s+w10, w13',
):
    req(re.search(pat,dis,re.S) is not None,'OEM anchor '+pat)

# Reuse the already fail-closed source-lock for BUS base VFE+0xc00.
p=subprocess.run(['python3',str(ROOT/'experiments/E004-front-ir-vd55g0/e005p-original-oem-vfe-bus-tophalf-source-lock-static/verify.py')],capture_output=True,text=True)
req(p.returncode==0,'E005p BUS base/register source-lock')
h=QHDR.read_text()
b=QBUS.read_text()
req(re.search(r'/\* BUS Client 16 STATS BAF \*/.*?\.cfg\s*=\s*0x00001E00.*?\.addr_status_0\s*=\s*0x00001E70.*?\.comp_group\s*=\s*CAM_VFE_BUS_VER3_COMP_GRP_7',h,re.S),'WM16 BAF group7')
req(re.search(r'/\* BUS Client 10 PIXEL RAW \*/.*?\.comp_group\s*=\s*CAM_VFE_BUS_VER3_COMP_GRP_3',h,re.S),'group3 negative control')
req(re.search(r'\.comp_done_mask\s*=\s*\{.*?BIT\(7\)',h,re.S),'VFE680 comp mask includes bit7')
for needle in (
    '*comp_grp_id = rsrc_data->hw_regs->comp_group;',
    'rsrc_data->comp_done_mask = ver3_hw_info->comp_done_mask[index];',
    'if (status_0 & rsrc_data->comp_done_mask)',
):
    req(needle in b,'BUS-v3 semantics '+needle)

req(d['oem_hardware_programming']['resource_0x300d_to_wm16_cfg0_proven'] is True,'saved WM16 link')
req(d['namespace_conclusion']['software_group8_equals_oem_output_group3'] is False,'namespace 8!=3')
req(d['namespace_conclusion']['oem_output_group3_may_be_assumed_equal_to_upstream_wm16_group7'] is False,'namespace 3!=assumed7')
req(d['namespace_conclusion']['exact_oem_group3_to_physical_completion_bit_translation_proven'] is False,'no invented translation')
req(all(d['not_proven'].values()),'unproven boundary')
req(d['e005n_loaded'] is False and d['protected_golden_modified'] is False,'Golden/E005n safety')
req(d['native_rear_hardware_isp_runtime_authorized'] is False,'rear denied')
print('PASS_E005T_300D_TO_WM16_CFG0_GROUP_NAMESPACES_8_3_7_SEPARATED_DMA_RETIRE_UNPROVEN_REAR_DENIED')
