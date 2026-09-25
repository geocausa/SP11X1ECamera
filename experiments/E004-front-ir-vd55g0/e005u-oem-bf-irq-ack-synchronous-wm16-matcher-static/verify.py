#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, re, subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OEM=ROOT/'experiments/E001-windows-oracle-map/oracle-local/qccamisp8380.sys'
OEM_SHA='64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c'

def req(v,m):
    if not v: raise AssertionError('E005U_FAIL_CLOSED '+m)

d=json.loads((HERE/'RESULT.json').read_text())
req(hashlib.sha256(OEM.read_bytes()).hexdigest()==OEM_SHA,'OEM SHA')
dis=subprocess.check_output(['llvm-objdump','-d','--no-show-raw-insn',str(OEM)],text=True,errors='replace')

patterns=(
    r'14001b67c:.*ldr\s+w8, \[x8, #0x8c\].*?14001b684:.*str\s+w8, \[x20, #0xc\]',
    r'14001b72c:.*ldr\s+w9, \[x20, #0xc\].*?14001b734:.*str\s+w9, \[x8, #0x94\]',
    r'14001b7f0:.*ldr\s+w8, \[x1, #0xc\].*?14001b7f4:.*str\s+w8, \[x2, #0x8\]',
    r'14001f048:.*ubfx\s+w15, w2, #7, #1.*?14001f190:.*mov\s+w15, #0xf',
    r'14001fc8c:.*mov\s+w1, #0x8.*?14001fc94:.*bl\s+0x140026460.*?14001fc9c:.*cbz\s+x23',
    r'14001fca4:.*mov\s+w2, #0xf.*?14001fcc4:.*blr\s+x15.*?14001fcc8:.*ldrb\s+w8, \[x19, #0x1c0\].*?14001fce4:.*bl\s+0x140025078',
    r'14001d714:.*ldr\s+w8, \[x8, #0x1270\].*?14001d718:.*str\s+w8, \[x1, #0x4c\].*?14001d720:.*ldr\s+w8, \[x8, #0x1200\].*?14001d724:.*and\s+w8, w8, #0x1.*?14001d728:.*strb\s+w8, \[x1, #0x48\]',
    r'140024f7c:.*mov\s+x20, x1.*?140024fbc:.*add\s+x9, x8, #0x173.*?140024fc0:.*lsl\s+x9, x9, #5.*?140024fe0:.*str\s+x20, \[x9, x19\]',
    r'14001f0ec:.*ldr\s+x2, \[x23, #0x30\].*?14001f0f4:.*str\s+x2, \[sp, #0x40\].*?14001f29c:.*ldr\s+x1, \[sp, #0x40\].*?14001f2a4:.*bl\s+0x140024f60',
    r'1400250e0:.*add\s+x8, x19, #0x173.*?1400250f4:.*ldr\s+x23, \[x26, x21\]'
)
for p in patterns:
    req(re.search(p,dis,re.S) is not None,'anchor '+p)

req(d['type1_bf_hardware_status']['same_word_status_ack_source_locked'] is True,'BF ack')
req(d['bf_synchronous_wm16_sample']['sample_occurs_after_fifo8_pop_before_matcher'] is True,'ordering')
req(d['bf_synchronous_wm16_sample']['selector_tests_bus_completion_irq'] is False,'no fake IRQ predicate')
req(d['bf_synchronous_wm16_sample']['selector_acks_bus_completion_irq'] is False,'no fake BUS ack')
req(d['matcher_object']['installer_stores_argument_x1_as_object_pointer'] is True,'installer provenance')
req(d['matcher_object']['matcher_returns_same_installed_object_pointer'] is True,'matcher pointer')
req(d['matcher_object']['object_dma_address_field_source_proven'] is False,'no fake DMA field')
req(all(d['not_proven'].values()),'unproven boundary')
req(d['e005n_loaded'] is False and d['protected_golden_modified'] is False,'Golden safety')
req(d['native_rear_hardware_isp_runtime_authorized'] is False,'rear denied')
print('PASS_E005U_BF_CSID_STATUS_ACK_SYNCHRONOUS_WM16_SAMPLE_MATCHER_OBJECT_PROVEN_EXACT_DMA_FENCE_UNPROVEN_REAR_DENIED')
