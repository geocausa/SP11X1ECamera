#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, re, subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OEM=ROOT/'experiments/E001-windows-oracle-map/oracle-local/qccamisp8380.sys'
Q=Path('/home/geoca/.cache/qualcomm-camera-driver/camera/drivers/cam_isp/isp_hw_mgr/isp_hw/ife_csid_hw/cam_ife_csid680.h')
OEM_SHA='64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c'

def req(v,m):
    if not v:
        raise AssertionError('E005V_FAIL_CLOSED '+m)

d=json.loads((HERE/'RESULT.json').read_text())
req(hashlib.sha256(OEM.read_bytes()).hexdigest()==OEM_SHA,'OEM SHA')
q=Q.read_text()
req(re.search(r'timestamp_curr0_sof_addr\s*=\s*0x398',q),'QCOM SOF low')
req(re.search(r'timestamp_curr1_sof_addr\s*=\s*0x39[Cc]',q),'QCOM SOF high')

dis=subprocess.check_output(['llvm-objdump','-d','--no-show-raw-insn',str(OEM)],text=True,errors='replace')
anchors=(
 r'14001b7f8:.*ldr\s+x8, \[x0, #0x8\]',
 r'14001b7fc:.*ldr\s+w9, \[x8, #0x398\]',
 r'14001b804:.*ldr\s+w8, \[x8, #0x39c\]',
 r'14001b808:.*bfi\s+x9, x8, #32, #24',
 r'14001b80c:.*str\s+x9, \[x2, #0x30\]',
 r'14001f0ec:.*ldr\s+x2, \[x23, #0x30\]',
 r'14001f29c:.*ldr\s+x1, \[sp, #0x40\].*?14001f2a4:.*bl\s+0x140024f60',
 r'140024f7c:.*mov\s+x20, x1.*?140024fe0:.*str\s+x20, \[x9, x19\]',
 r'1400250f4:.*ldr\s+x23, \[x26, x21\]'
)
for a in anchors:
    req(re.search(a,dis,re.S), 'anchor '+a)

req(d['matcher']['slot_value_is_pointer'] is False,'not pointer')
req(d['matcher']['slot_value_is_dma_address'] is False,'not DMA')
req(d['matcher']['slot_value_is_csid_current_sof_timestamp'] is True,'SOF token')
req(d['retained_from_e005u']['wm16_status_sample_is_independent_bus_completion_fence'] is False,'no fake fence')
req(all(d['not_proven'].values()),'unproven boundary')
req(d['e005n_loaded'] is False and d['protected_golden_modified'] is False,'Golden safety')
req(d['native_rear_hardware_isp_runtime_authorized'] is False,'rear denied')
print('PASS_E005V_MATCHER_RETURN_IS_CSID_CURRENT_SOF_TIMESTAMP_NOT_POINTER_NOT_DMA_EXACT_WM16_FENCE_UNPROVEN_REAR_DENIED')
