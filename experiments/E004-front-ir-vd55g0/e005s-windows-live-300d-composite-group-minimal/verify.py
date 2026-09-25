#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, re, subprocess
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OEM=ROOT/'experiments/E001-windows-oracle-map/oracle-local/qccamisp8380.sys'
SHA='64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c'
def req(v,m):
    if not v: raise AssertionError('E005S_FAIL_CLOSED '+m)
p=json.loads((HERE/'PLAN.json').read_text())
d=json.loads((HERE/'RESULT.json').read_text())
req(p['breakpoint_count']==3,'bp count')
req(p['load_e005n'] is False and d['e005n_loaded'] is False,'no E005n')
req(OEM.is_file() and hashlib.sha256(OEM.read_bytes()).hexdigest()==SHA,'OEM SHA')
dis=subprocess.check_output(['llvm-objdump','-d','--no-show-raw-insn',str(OEM)],text=True,errors='replace')
for pat in (r'140016de8:.*ldr\s+w2, \[x21, #0x8c0\]', r'14001fc98:.*mov\s+x23, x0', r'14001fce8:.*mov\s+w9, #0x300d'):
    req(re.search(pat,dis) is not None,pat)
req(d['run_consumed_no_retry'] is True,'consumed')
req(d['capture']['acceptance_passed'] is True and d['capture']['valid_frame_handles']==30,'capture acceptance')
req(d['live_oem_output_resource']['same_sp11_oem_live_composite_group']==3,'live OEM group')
req(d['bf_fifo_matcher']['fifo8_nonnull_count']==56,'FIFO count')
req(d['bf_fifo_matcher']['matcher_nonnull_count']==56,'matcher count')
req(d['bf_fifo_matcher']['key_tag_sequences_identical'] is True,'key/tag identity')
req(d['bf_fifo_matcher']['keys_consecutive_1_through_56'] is True,'key sequence')
req(d['bf_fifo_matcher']['all_tags_zero'] is True,'tags')
req(d['wm16_bounded_state']['addr_status0_samples']==56 and d['wm16_bounded_state']['unique_values']==10,'WM16 movement')
req(d['wm16_bounded_state']['raw_values_private'] is True,'raw privacy')
req(d['wm16_bounded_state']['exact_per_key_dma_identity_proven'] is False,'no DMA identity overclaim')
req(all(d['cleanup'].values()),'cleanup')
req(all(d['not_proven'].values()),'unproven boundary')
req(d['native_rear_hardware_isp_runtime_authorized'] is False,'rear denied')
print('PASS_E005S_LIVE_OEM_300D_GROUP3_FIFO56_MATCH56_WM16_MOVES_DMA_RETIRE_UNPROVEN_REAR_DENIED')
