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
assert R['swasf']['pixel_transform_port_complete']

# Windows-authoritative SWASF helper closure.
assert sha(D/'oracle/windows-helper-oracle/HELPERS.txt') == '9523aeafa7139bcf02f7c8251867d9f5094449de5b59edf57bffd1f0db60e573'
assert (D/'oracle/windows-c078-basis/C078-BASIS.txt').exists()
assert R['swasf']['helper_local_extrema_exact']
assert R['swasf']['helper_c078_activity_exact']
assert R['swasf']['pixel_transform_port_complete']
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
assert R['swasf']['c230_random_differential_exact']
assert R['swasf']['c230_random_differential_cases']==4096
rr=(D/'oracle/windows-c230-random-diff/RESULT.txt').read_text(errors='replace')
assert 'BYTE_EXACT=true' in rr
assert rr.count(R['swasf']['c230_random_differential_sha256'])==2
out=subprocess.check_output([str(D/'verify_c230_windows_basis.py')],text=True)
assert 'PASS (232 direct oracle cases)' in out
with tempfile.TemporaryDirectory() as td:
    obj=pathlib.Path(td)/'swasf_c230.o'
    subprocess.check_call(['clang','--target=hexagon','-mcpu=hexagonv73','-O2','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(D/'scaffold/sp11-swasf-c230.c'),'-o',str(obj)])
    assert sha(obj)==R['swasf']['c230_hexagon_object_sha256']
    assert subprocess.check_output(['llvm-nm','-u',str(obj)],text=True).strip()==''


# Windows-authoritative C3E8 cross-median/tile candidate.
assert R['swasf']['c3e8_cross5_exact']
assert R['swasf']['c3e8_random_differential_exact']
assert R['swasf']['c3e8_random_images']==512
assert R['swasf']['c3e8_random_tiles']==1024
rr=(D/'oracle/windows-c3e8-random-diff/RESULT.txt').read_text(errors='replace')
assert 'BYTE_EXACT=true' in rr
assert 'EXTRA_WRITES_HP=0 LP=0 MED=0' in rr
assert rr.count(R['swasf']['c3e8_random_differential_sha256'])==2
out=subprocess.check_output([str(D/'verify_c3e8_cross5.py')],text=True)
assert 'PASS (1792 tile pixels)' in out
with tempfile.TemporaryDirectory() as td:
    a=pathlib.Path(td)/'c230.o'; b=pathlib.Path(td)/'c3e8.o'; c=pathlib.Path(td)/'combined.o'
    common=['clang','--target=hexagon','-mcpu=hexagonv73','-O2','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
    subprocess.check_call(common+[str(D/'scaffold/sp11-swasf-c230.c'),'-o',str(a)])
    subprocess.check_call(common+[str(D/'scaffold/sp11-swasf-c3e8.c'),'-o',str(b)])
    subprocess.check_call(['ld.lld','-m','hexagonelf','-r',str(a),str(b),'-o',str(c)])
    assert sha(c)==R['swasf']['c3e8_combined_hexagon_object_sha256']
    assert subprocess.check_output(['llvm-nm','-u',str(c)],text=True).strip()==''


# Self-consistent shipping-Windows CD90 capture and scalar candidate.
assert R['swasf']['cd90_consistent_windows_capture']
assert R['swasf']['cd90_final_combine_exact']
out=subprocess.check_output([str(D/'verify_cd90_consistent.py')],text=True)
assert 'PASS' in out
assert sha(D/'oracle/windows-cd90-consistent/p13.bin') == R['windows_oracle']['swasf_payload_sha256']
with tempfile.TemporaryDirectory() as td:
    obj=pathlib.Path(td)/'cd90.o'
    subprocess.check_call(['clang','--target=hexagon','-mcpu=hexagonv73','-O2','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(D/'scaffold/sp11-swasf-cd90.c'),'-o',str(obj)])
    assert sha(obj)==R['swasf']['cd90_hexagon_object_sha256']
    assert subprocess.check_output(['llvm-nm','-u',str(obj)],text=True).strip()==''


# Shipping-Windows CD90 randomized closure.
assert R['swasf']['cd90_final_combine_exact']
assert R['swasf']['cd90_random_differential_exact']
assert R['swasf']['cd90_random_differential_cases']==4096
assert R['swasf']['cd90_random_differential_lanes']==32768
out=subprocess.check_output([str(D/'verify_cd90_random_vectors.py')],text=True)
assert 'PASS (4096 cases / 32768 lanes)' in out


# Full Windows-authoritative SWASF scalar and stable 644x604 differential.
import re, struct
assert R['swasf']['full_scalar_reference_complete']
assert R['swasf']['full_frame_windows_stable_exact']
assert R['swasf']['full_frame_luma_diff_bytes']==0
assert R['swasf']['full_frame_luma_bytes']==644*604
assert R['swasf']['full_scalar_hexagon_undefined_symbols']==0
# The generated C tuning array must be a byte-for-byte representation of the live 0x804 payload.
tuning_src=(D/'scaffold/sp11-swasf-windows-tuning.c').read_text()
words=[int(x,16) for x in re.findall(r'0x([0-9a-fA-F]{8})u',tuning_src)]
assert len(words)==513
assert struct.pack('<513I',*words)==(D/'oracle/windows-live/SWASF-derived-from-live-cache.bin').read_bytes()
full_sources=[
    D/'scaffold/sp11-swasf-reference.c',
    D/'scaffold/sp11-swasf-windows-tuning.c',
    D/'scaffold/sp11-swasf-helpers.c',
    D/'scaffold/sp11-swasf-c230.c',
    D/'scaffold/sp11-swasf-c3e8.c',
    D/'scaffold/sp11-swasf-cd90.c',
]
with tempfile.TemporaryDirectory() as td:
    td=pathlib.Path(td)
    exe=td/'swasf_full'
    subprocess.check_call(['clang','-std=c11','-O2','-Wall','-Wextra','-Werror',f'-I{D/"scaffold"}']+
                          [str(x) for x in full_sources]+[str(D/'scaffold/test_swasf_fullframe.c'),'-o',str(exe)])
    out=subprocess.check_output([str(exe),
        str(D/'oracle/windows-sync-oracle/windows-trustlet-sync-swabf-644x604.bin'),
        str(D/'oracle/windows-sync-oracle/windows-trustlet-sync-swasf-644x604-stable.bin')],text=True)
    assert 'SWASF_FULL_LUMA_DIFF=0' in out
    objs=[]
    for sp in full_sources:
        obj=td/(sp.stem+'.o')
        subprocess.check_call(['clang','--target=hexagon','-mcpu=hexagonv73','-O2','-ffreestanding',
            '-fno-builtin','-fno-pic','-fno-pie','-Wall','-Wextra','-Werror',f'-I{D/"scaffold"}',
            '-c',str(sp),'-o',str(obj)])
        objs.append(obj)
    combined=td/'swasf-full.hexagon-v73.o'
    subprocess.check_call(['ld.lld','-m','hexagonelf','-r']+[str(x) for x in sorted(objs,key=lambda q:q.name)]+['-o',str(combined)])
    assert subprocess.check_output(['llvm-nm','-u',str(combined)],text=True).strip()==''
    assert sha(combined)==R['swasf']['full_scalar_hexagon_object_sha256']

print('E004dh VERIFY: PASS (full SWABF/SWASF offline pixel parity closed)')
