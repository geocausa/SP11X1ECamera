#!/usr/bin/env python3
import hashlib,json,pathlib,subprocess,tempfile
D=pathlib.Path(__file__).resolve().parent
R=json.loads((D/'RESULT.json').read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assert R['authority'].startswith('Windows live oracle')
assert sha(D/'oracle/windows-live/SWABF-derived-from-live-cache.bin')==R['windows_oracle']['swabf_payload_sha256']
assert sha(D/'oracle/windows-live/SWASF-derived-from-live-cache.bin')==R['windows_oracle']['swasf_payload_sha256']
assert sha(D/'oracle/windows-live/E004DH-pInputData-iq-window.bin')==R['windows_oracle']['pinputdata_window_sha256']
assert sha(D/'scaffold/sp11-swabf-reference.hexagon-v73.o')==R['swabf']['hexagon_object_sha256']
assert sha(D/'oracle/windows-sync-oracle/windows-trustlet-sync-swabf-644x604.bin')==R['windows_shipping_trustlet_oracle']['synchronized_swabf_sha256']
assert sha(D/'oracle/windows-sync-oracle/windows-trustlet-sync-swasf-644x604-stable.bin')==R['windows_shipping_trustlet_oracle']['swasf_stable_candidate_sha256']
assert subprocess.check_output(['llvm-nm','-u',str(D/'scaffold/sp11-swabf-reference.hexagon-v73.o')],text=True).strip()==''
with tempfile.TemporaryDirectory() as td:
    exe=pathlib.Path(td)/'t'
    subprocess.check_call(['cc','-std=c11','-Wall','-Wextra','-Werror','-O2',str(D/'scaffold/sp11-swabf-reference.c'),str(D/'scaffold/test_swabf_reference.c'),'-o',str(exe)])
    out=subprocess.check_output([str(exe)],text=True)
    assert 'PASS' in out
assert not R['swasf']['pixel_transform_port_complete']
print('E004dh VERIFY: PASS (partial gate; SWASF pixel port pending)')
