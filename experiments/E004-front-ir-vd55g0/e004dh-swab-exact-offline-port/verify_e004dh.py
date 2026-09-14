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

# Windows-authoritative SWASF helper closure.
assert sha(D/'oracle/windows-helper-oracle/HELPERS.txt') == '9523aeafa7139bcf02f7c8251867d9f5094449de5b59edf57bffd1f0db60e573'
assert (D/'oracle/windows-c078-basis/C078-BASIS.txt').exists()
assert R['swasf']['helper_local_extrema_exact']
assert R['swasf']['helper_c078_activity_exact']
assert not R['swasf']['pixel_transform_port_complete']
with tempfile.TemporaryDirectory() as td:
    exe=pathlib.Path(td)/'swasf_helpers'
    subprocess.check_call(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(D/'scaffold/sp11-swasf-helpers.c'),str(D/'scaffold/test_swasf_helpers.c'),'-o',str(exe)])
    out=subprocess.check_output([str(exe)],text=True)
    assert 'SWASF helper vectors: PASS' in out
with tempfile.TemporaryDirectory() as td:
    obj=pathlib.Path(td)/'swasf_helpers.o'
    subprocess.check_call(['clang','--target=hexagon','-mcpu=hexagonv73','-O2','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(D/'scaffold/sp11-swasf-helpers.c'),'-o',str(obj)])
    assert sha(obj)==R['swasf']['helper_hexagon_object_sha256']
    assert subprocess.check_output(['llvm-nm','-u',str(obj)],text=True).strip()==''

# Windows-authoritative C230 nested-filter basis closure.
assert R['swasf']['c230_scalar_basis_exact']
assert R['swasf']['c230_windows_basis_cases'] == 232
out=subprocess.check_output([str(D/'verify_c230_windows_basis.py')],text=True)
assert 'PASS (232 direct oracle cases)' in out
with tempfile.TemporaryDirectory() as td:
    obj=pathlib.Path(td)/'swasf_c230.o'
    subprocess.check_call(['clang','--target=hexagon','-mcpu=hexagonv73','-O2','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(D/'scaffold/sp11-swasf-c230.c'),'-o',str(obj)])
    assert sha(obj)==R['swasf']['c230_hexagon_object_sha256']
    assert subprocess.check_output(['llvm-nm','-u',str(obj)],text=True).strip()==''

print('E004dh VERIFY: PASS (partial gate; SWASF pixel port pending)')
