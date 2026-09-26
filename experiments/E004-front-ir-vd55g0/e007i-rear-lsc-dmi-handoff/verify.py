#!/usr/bin/env python3
from pathlib import Path
import json
D=Path(__file__).resolve().parent
s=(D/'camss-e007i-rear-lsc-handoff.inc').read_text()
h=json.load(open(D.parent/'e007h-rear-lsc-clean-runtime/RESULT.json'))
assert h['classification']=='USERSPACE_PRODUCER_PASS_15_OF_15_BYTE_EXACT'
assert h['all_wire_exact'] is True
assert h['runtime_outputs']['lsc_selector1_bytes']==884
assert h['runtime_outputs']['lsc_selector2_bytes']==884
for token in (
 'struct e007i_rear_lsc_wire_state','u64 request_id;',
 'u8 selector1[E006G_LSC_BYTES];','u8 selector2[E006G_LSC_BYTES];',
 'bytes != E006G_LSC_BYTES','s->lsc.request_id != expected_request_id',
 'return -EPROTO;','E007I_LSC_VALID_ALL','.lsc = e007i_rear_lsc',
 'return e007f_rear_prepare_dynamic(&s->dmi, out);',
 'return e007f_rear_fill_slot(&s->dmi, dyn, slot, out);',
 'e007i_rear_lsc_handoff_recipe'):
    assert token in s
for bad in ('writel(', 'readl(', 'dma_alloc', 'tintless_core_mode2_native', 'ctypes.CDLL'):
    assert bad not in s
print('E007I_VERIFY_PASS lsc_selectors=2x884 request_tagged=true stale_rejected=true')
print('userspace_solver=true gic_alias=e006g-derived runtime_submission=none')
