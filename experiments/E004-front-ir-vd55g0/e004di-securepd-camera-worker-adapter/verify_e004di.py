#!/usr/bin/env python3
import hashlib,json,pathlib,subprocess,tempfile
D=pathlib.Path(__file__).resolve().parent
S=D/'scaffold'
ROOT=D.parent.parent.parent
DG=D.parent/'e004dg-offline-parity-worker'/'scaffold'
DH=D.parent/'e004dh-swab-exact-offline-port'/'scaffold'
O=D.parent/'e004dh-swab-exact-offline-port'/'oracle/windows-sync-oracle'
R=json.loads((D/'RESULT.json').read_text())
def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
assert R['status']=='PASS_OFFLINE_SECUREPD_CAMERA_WORKER_ADAPTER_FULL_FRAME_WINDOWS_EXACT'
assert R['packet']['bytes']==80 and R['packet']['result_bytes']==16
assert R['differential']['luma_diff_bytes']==0 and R['differential']['neutral_tail_diff_bytes']==0
assert not R['trust']['signed'] and not R['trust']['production_admitted'] and not R['trust']['runtime_authorized']
assert not any(R['runtime_actions'].values())
source=(S/'sp11-securepd-camera-worker.c').read_text()
for token in ['sizeof(struct sp11_securepd_camera_packet) == 80','ops->verify','ops->map','ops->unmap','sp11_parity_worker_run']:
    assert token in source
sources=[S/'sp11-securepd-camera-worker.c',DG/'sp11-parity-worker.c',DH/'sp11-swabf-reference.c',DH/'sp11-swasf-reference.c',DH/'sp11-swasf-windows-tuning.c',DH/'sp11-swasf-helpers.c',DH/'sp11-swasf-c230.c',DH/'sp11-swasf-c3e8.c',DH/'sp11-swasf-cd90.c']
with tempfile.TemporaryDirectory() as td:
    td=pathlib.Path(td)
    common=['clang','-std=c11','-O2','-Wall','-Wextra','-Werror',f'-I{S}',f'-I{DG}',f'-I{DH}']+[str(x) for x in sources]
    vectors=td/'vectors'
    subprocess.check_call(common+[str(S/'test_securepd_camera_worker.c'),'-o',str(vectors)])
    out=subprocess.check_output([str(vectors)],text=True)
    assert 'E004di SecurePD adapter vectors: PASS' in out
    full=td/'full'
    subprocess.check_call(common+[str(S/'test_securepd_fullframe.c'),'-o',str(full)])
    out=subprocess.check_output([str(full),str(O/'input-644x604-nv12.bin'),str(O/'windows-trustlet-sync-swasf-644x604-stable.bin')],text=True)
    assert 'SECUREPD_ADAPTER_FULL_LUMA_DIFF=0' in out and 'SECUREPD_ADAPTER_NEUTRAL_TAIL_DIFF=0' in out
    objs=[]
    for sp in sources:
        obj=td/(sp.stem+'.o')
        subprocess.check_call(['clang','--target=hexagon','-mcpu=hexagonv73','-O2','-ffreestanding','-fno-builtin','-fno-pic','-fno-pie','-Wall','-Wextra','-Werror',f'-I{S}',f'-I{DG}',f'-I{DH}','-c',str(sp),'-o',str(obj)])
        objs.append(obj)
    combined=td/'e004di.hexagon-v73.o'
    subprocess.check_call(['ld.lld','-m','hexagonelf','-r']+[str(x) for x in sorted(objs,key=lambda p:p.name)]+['-o',str(combined)])
    assert subprocess.check_output(['llvm-nm','-u',str(combined)],text=True).strip()==''
    assert sha(combined)==R['hexagon']['combined_object_sha256']
print('E004di VERIFY: PASS (SecurePD-shaped exact parity worker image core)')
