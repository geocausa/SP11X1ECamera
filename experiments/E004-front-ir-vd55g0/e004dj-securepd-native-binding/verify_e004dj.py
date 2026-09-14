#!/usr/bin/env python3
import hashlib,json,pathlib,subprocess,tempfile
D=pathlib.Path(__file__).resolve().parent
S=D/'scaffold'
DG=D.parent/'e004dg-offline-parity-worker'/'scaffold'
DH=D.parent/'e004dh-swab-exact-offline-port'/'scaffold'
O=D.parent/'e004dh-swab-exact-offline-port'/'oracle/windows-sync-oracle'
R=json.loads((D/'RESULT.json').read_text())
def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
expected=set(R['hexagon']['unresolved_symbols'])
assert R['status']=='PASS_OFFLINE_NATIVE_SECUREPD_BINDING_REUSES_SHIPPED_PROXY_WINDOWS_EXACT'
assert R['proxy']['packet_bytes']==96 and R['proxy']['response_bytes']==8
assert not R['proxy']['src_offset_consumed'] and not R['proxy']['dst_offset_consumed'] and not R['proxy']['heap_offset_consumed']
assert R['proxy']['mode_static']==0 and not R['proxy']['existing_proxy_modified']
assert R['control']['heap_prefix_bytes']==32 and R['control']['request_id_bits']==64
assert R['native']['data_type']==7 and R['native']['heap_type']==5
assert R['native']['cache_mode']==7 and R['native']['mapping_permission']==3
assert R['native']['thread_stack_bytes']==131072 and R['native']['thread_priority']==150
assert R['differential']['luma_diff_bytes']==0 and R['differential']['neutral_tail_diff_bytes']==0
assert not R['trust']['signed'] and not R['trust']['production_admitted'] and not R['trust']['runtime_authorized']
assert not any(R['runtime_actions'].values())
wire=(S/'sp11-securepd-camera-wire.c').read_text()
native=(S/'sp11-securepd-native-binding.c').read_text()
proxy=(S/'sp11-loadalgo-camera-proxy.c').read_text()
for token in ['sizeof(struct sp11_securepd_gaussian_packet) == 96','sizeof(struct sp11_securepd_camera_control) == 32','sp11_parity_worker_run']:
    assert token in wire
for token in ['SP11_QURT_MEM_CACHE_WRITEBACK','SP11_SECUREPD_MAP_PERMISSION_RW','"s2p_algo"','"p2s_algo"','secure_pd_thread_create','void algo_main']:
    assert token in native
for token in ['c->src_offset=0','c->dst_offset=0','c->heap_offset=0','c->mode_static=0']:
    assert token in proxy
core_sources=[S/'sp11-securepd-camera-wire.c',DG/'sp11-parity-worker.c',DH/'sp11-swabf-reference.c',DH/'sp11-swasf-reference.c',DH/'sp11-swasf-windows-tuning.c',DH/'sp11-swasf-helpers.c',DH/'sp11-swasf-c230.c',DH/'sp11-swasf-c3e8.c',DH/'sp11-swasf-cd90.c']
native_sources=[S/'sp11-securepd-native-binding.c']+core_sources
with tempfile.TemporaryDirectory() as td:
    td=pathlib.Path(td)
    common=['clang','-std=c11','-O2','-Wall','-Wextra','-Werror',f'-I{S}',f'-I{DG}',f'-I{DH}']+[str(x) for x in core_sources]
    vec=td/'wire-vectors'
    subprocess.check_call(common+[str(S/'test_camera_wire.c'),'-o',str(vec)])
    assert 'E004dj Gaussian-wire vectors: PASS' in subprocess.check_output([str(vec)],text=True)
    full=td/'wire-full'
    subprocess.check_call(common+[str(S/'test_camera_wire_fullframe.c'),'-o',str(full)])
    out=subprocess.check_output([str(full),str(O/'input-644x604-nv12.bin'),str(O/'windows-trustlet-sync-swasf-644x604-stable.bin')],text=True)
    assert 'GAUSSIAN_WIRE_FULL_LUMA_DIFF=0' in out and 'GAUSSIAN_WIRE_NEUTRAL_TAIL_DIFF=0' in out
    prox=td/'proxy-contract'
    subprocess.check_call(['clang','-std=c11','-O2','-Wall','-Wextra','-Werror',f'-I{S}',f'-I{DG}',f'-I{DH}',str(S/'sp11-loadalgo-camera-proxy.c')]+[str(x) for x in core_sources]+[str(S/'test_proxy_contract.c'),'-o',str(prox)])
    assert 'E004dj shipped-proxy call contract: PASS' in subprocess.check_output([str(prox)],text=True)
    objs=[]
    for sp in native_sources:
        obj=td/(sp.stem+'.o')
        subprocess.check_call(['clang','--target=hexagon','-mcpu=hexagonv73','-O2','-ffreestanding','-fno-builtin','-fno-pic','-fno-pie','-Wall','-Wextra','-Werror',f'-I{S}',f'-I{DG}',f'-I{DH}','-c',str(sp),'-o',str(obj)])
        objs.append(obj)
    combined=td/'e004dj-native.hexagon-v73.o'
    subprocess.check_call(['ld.lld','-m','hexagonelf','-r']+[str(x) for x in sorted(objs,key=lambda p:p.name)]+['-o',str(combined)])
    unresolved=set()
    for line in subprocess.check_output(['llvm-nm','-u',str(combined)],text=True).splitlines():
        if line.strip(): unresolved.add(line.split()[-1])
    assert unresolved==expected, (unresolved,expected)
    assert sha(combined)==R['hexagon']['combined_object_sha256']
    defs=subprocess.check_output(['llvm-nm','--defined-only',str(combined)],text=True)
    assert ' algo_main' in defs and ' sp11_securepd_camera_worker_thread' in defs
print('E004dj VERIFY: PASS (native SecurePD binding + unmodified shipped-proxy wire)')
