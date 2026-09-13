#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, re, sys

root = Path(__file__).resolve().parent
x = (root/'ghidra/SURFACECAMAVS-SECURE-XREFS.txt').read_text(errors='replace')
c = (root/'ghidra/SURFACECAMAVS-SECURE-CALLERS.txt').read_text(errors='replace')
r = json.loads((root/'RESULT.json').read_text())

checks = {
 'set_handler': 'FUN_140083120' in x and 'SetExtendedSecureMode => KSCAMERA_EXTENDEDPROP_SECUREMODE_ENABLED' in x,
 'get_handler': 'FUN_140083040' in x and 'GetExtendedSecureMode => KSCAMERA_EXTENDEDPROP_SECUREMODE_ENABLED' in x,
 'secure_state': "*(bool *)(param_1 + 0x2ad) = bVar3" in x,
 'aux_guard': 'SecureMode is only available for AUX camera, setting SecureMode to false' in x,
 'aux_literal_load': 'DAT_14001ec50' in x,
 'send_packet': 'FUN_140009b18' in x and 'Unable to send CSIInfo to secure KMDISP' in x,
 'secure_gate': "(*(char *)(param_1 + 0x2ad) == '\\x01')" in x,
 'secure_call_shape': '*plVar8 + 0x10,2,' in x and 'param_1 + 0x2b4,0xc' in x,
 'caller_wrappers': 'caller=FUN_14000b460' in c and 'caller=FUN_14000b490' in c,
 'result_status': r.get('status') == 'PASS_WINDOWS_SECUREMODE_OWNER_AND_SECURE_CSI_GATE_MAPPED',
}

bad=[k for k,v in checks.items() if not v]
if bad:
 print('E004ai VERIFY: FAIL', ', '.join(bad))
 sys.exit(1)
print('E004ai VERIFY: PASS')
print(' - surfacecamavs SecureMode setter/getter mapped')
print(' - AUX-only policy mapped')
print(' - +0x2ad secure state gates secure CSI KMDISP diversion')
print(' - next dynamic trigger is explicit SecureMode activation, not plain WinRT')
