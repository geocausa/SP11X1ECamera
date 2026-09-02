#!/usr/bin/env python3
"""Fail-closed offline replay of the exact Surface Tintless request5->request6 state machine.

Raw Windows captures stay local/untracked.  The proof SHA-pins the exact Surface
DeviceMFT and every bounded input/output capture it consumes, executes the native
ARM64 Tintless callback under Unicorn, and requires byte-for-byte Windows parity
for request5, the persistent carry into request6, and request6 itself.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, struct
from pathlib import Path
from unicorn import UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn.arm64_const import UC_ARM64_REG_X0, UC_ARM64_REG_X18

DEVICE_MFT_SHA256 = "c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
CALLBACK_RVA = 0xC95FD0
DEEP_RVA = 0xCA01B0
CONTEXT_CAPTURE_BYTES = 0x4000
CONTEXT_MAP_BYTES = 0x20000
EXPECTED_CONTEXT_READ_HI = 0x12694
EXPECTED_CONTEXT_WRITE_HI = 0x126E8
# Raw NTFS recovery later established that this capture is OV13858 rear mode 1,
# not the verified IMX681 front stream.  Preserve this identity on every rerun.
CAPTURE_CAMERA_IDENTITY = {
    "sensor": "ov13858", "mode_index": 1, "width": 4064, "height": 2286,
    "cells_x": 126, "cells_y": 94, "cell_width": 32, "cell_height": 24,
    "correction_proof": "LSC-TINTCTX-CAMERA-IDENTITY-CORRECTION.md",
}

EXPECTED = {
    "REQ5_CB_OBJ_PRE_0100.bin": "5f15af83e81c6147104aff1fbad702851d8fbebb3bc0904ac4d26f4f849d0d2a",
    "REQ5_CB_STATE_PRE_1100.bin": "81b54ba5ad7d4a6b400070a1f85086f9eb7ceb45db383fb1f402543320748c05",
    "REQ5_CB_CTX_PRE_4000.bin": "6f56925e016351f9d0fdac61dcef53bfce8d1bc6915e9d95d73af40925f05fc3",
    "REQ5_CB_X1_PRE_0400.bin": "b8bb8f82548baa20ea3ce5156d9da1837f65415a6cfc907813c858c7cfcaaffd",
    "REQ5_CB_X2_PRE_14000.bin": "0d1df41f674a12531d777a7e3bbd6d66e22c2d5f65cf261825c45a04783619a9",
    "REQ5_CB_IN_DESC_PRE_0030.bin": "34591c14f58a42839adfa43bcc1c8cf1c33eed307d8fc523566d265714ddff56",
    "REQ5_CB_OUT_DESC_PRE_0030.bin": "5c567e435e043b9eeaddf8e9c2f6ac0caa03518a8604093142dde0cd7895d11a",
    "REQ5_CB_IN_MESH_PRE_0DF0.bin": "d80d3bf1326d34fce4ee67ace514a1fc5470b9101b611432cf8b81683b39e74a",
    "REQ5_CB_OUT_MESH_PRE_0DF0.bin": "84957a7d73b8e9905fd60e30b89e18472bd62689468b6515ba8cea6d39f032f0",
    "REQ5_CB_STATE_POST_1100.bin": "80149f9dc3df9c7f7b3856b5226c1994c77f3619ac00ad9335073690c066a6d4",
    "REQ5_CB_CTX_POST_4000.bin": "f30e829d54e1da8664f1c1722d34b71f151cd308d208b9400daf87188359b570",
    "REQ5_CB_OUT_MESH_POST_0DF0.bin": "1978d282a472117a2b28a3fb1c4b41295e1b8190c4737b448373e5571f381490",
    "REQ6_CB_OBJ_PRE_0100.bin": "5f15af83e81c6147104aff1fbad702851d8fbebb3bc0904ac4d26f4f849d0d2a",
    "REQ6_CB_STATE_PRE_1100.bin": "80149f9dc3df9c7f7b3856b5226c1994c77f3619ac00ad9335073690c066a6d4",
    "REQ6_CB_CTX_PRE_4000.bin": "f30e829d54e1da8664f1c1722d34b71f151cd308d208b9400daf87188359b570",
    "REQ6_CB_X1_PRE_0400.bin": "d18ac05d4a9e0a4caf17f8c649d4fc2a93fc323f1204912aeb80b4a9a181d5ec",
    "REQ6_CB_X2_PRE_14000.bin": "9311d082d6a6f6f59afeded7202b1e46c8f63137d6ce5c4f0188fcb8cf7523c2",
    "REQ6_CB_IN_DESC_PRE_0030.bin": "ae19e17d69d5f4f2132a17bbf2403f41f89d9d98eb0611cf6ebb9a1a292eecb0",
    "REQ6_CB_OUT_DESC_PRE_0030.bin": "22854b974f9f6d494599a08bb678f4a325459f69da072107f03c6a682d01d85f",
    "REQ6_CB_IN_MESH_PRE_0DF0.bin": "c7597c16f3d496555a6e7a3c2364e71cdf21b1476700f6043c0e43bb0fa71ed1",
    "REQ6_CB_OUT_MESH_PRE_0DF0.bin": "d3860266fcdfa3a641eef7a0cb04e7578e225323d6b190c9b552fc1a1430d125",
    "REQ6_CB_STATE_POST_1100.bin": "3d4c1afa0e45f46887c4376044b853d8a10ae74e9346de8d798855066346a3c6",
    "REQ6_CB_CTX_POST_4000.bin": "b0086c1090959f6fa210a8d88a1b1ec442429cf3d646654270c51e2f731d721c",
    "REQ6_CB_X1_POST_0400.bin": "d18ac05d4a9e0a4caf17f8c649d4fc2a93fc323f1204912aeb80b4a9a181d5ec",
    "REQ6_CB_X2_POST_14000.bin": "9311d082d6a6f6f59afeded7202b1e46c8f63137d6ce5c4f0188fcb8cf7523c2",
    "REQ6_CB_IN_MESH_POST_0DF0.bin": "c7597c16f3d496555a6e7a3c2364e71cdf21b1476700f6043c0e43bb0fa71ed1",
    "REQ6_CB_OUT_MESH_POST_0DF0.bin": "547d96e50a6775eff44c1af3085905c6c45705d1c59121a2b0eac7be58566824",
}

ADDR = {
    "obj": 0x1DEF66F5E00, "state": 0x1DEFFBD9060, "ctx": 0x1DEF6D63040,
    "x1": 0x1DEFC1039A8, "inmesh": 0x1DEFC1A5000,
    "x2_5": 0x1DF071C0000, "id5": 0x42FF5627F0, "od5": 0x42FF5627C8, "om5": 0x42FF563480,
    "x2_6": 0x1DF07670000, "id6": 0x42FF7E2330, "od6": 0x42FF7E2308, "om6": 0x42FF7E2FC0,
}

def sha_bytes(b: bytes) -> str: return hashlib.sha256(b).hexdigest()
def sha_file(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda:f.read(1<<20),b''): h.update(c)
    return h.hexdigest()

def verify_captures(cap: Path) -> None:
    for name,want in EXPECTED.items():
        p=cap/name
        if not p.is_file(): raise RuntimeError(f"missing capture {p}")
        got=sha_file(p)
        if got!=want: raise RuntimeError(f"capture SHA mismatch {name}: {got} != {want}")
    x1=(cap/'REQ5_CB_X1_PRE_0400.bin').read_bytes()
    geom=struct.unpack_from('<7I',x1,0x1c)
    expected=(4064,2286,126,94,32,24,0)
    if geom != expected:
        raise RuntimeError(f"TINTCTX camera-identity geometry drift: {geom!r} != {expected!r}")

def load_surface_emu(here: Path):
    p=here/'prove-gtm-live-exact-replay.py'
    spec=importlib.util.spec_from_file_location('surface_emu_source',p)
    mod=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(mod)
    return mod

def replay_once(mod, dll: Path, cap: Path, extension_fill: int) -> dict:
    e=mod.SurfaceEmu(dll); u=e.uc
    teb=0x70000000; u.mem_map(teb,0x1000); u.mem_write(teb+0x10,e.stack.to_bytes(8,'little')); u.reg_write(UC_ARM64_REG_X18,teb)
    def amap(a,n):
        b=a&~0xfff; z=(a+n+0xfff)&~0xfff
        try: u.mem_map(b,z-b)
        except Exception as ex:
            if 'UC_ERR_MAP' not in str(ex): raise
    def put(a,name):
        b=(cap/name).read_bytes(); amap(a,len(b)); u.mem_write(a,b)
    def exact(a,n,name): return bytes(u.mem_read(a,n)) == (cap/name).read_bytes()
    put(ADDR['obj'],'REQ5_CB_OBJ_PRE_0100.bin'); put(ADDR['state'],'REQ5_CB_STATE_PRE_1100.bin')
    amap(ADDR['ctx'],CONTEXT_MAP_BYTES); u.mem_write(ADDR['ctx']+CONTEXT_CAPTURE_BYTES,bytes([extension_fill])*(CONTEXT_MAP_BYTES-CONTEXT_CAPTURE_BYTES)); u.mem_write(ADDR['ctx'],(cap/'REQ5_CB_CTX_PRE_4000.bin').read_bytes())
    put(ADDR['x1'],'REQ5_CB_X1_PRE_0400.bin'); put(ADDR['inmesh'],'REQ5_CB_IN_MESH_PRE_0DF0.bin'); put(ADDR['x2_5'],'REQ5_CB_X2_PRE_14000.bin')
    amap(ADDR['od5'],0x20000); u.mem_write(ADDR['id5'],(cap/'REQ5_CB_IN_DESC_PRE_0030.bin').read_bytes()); u.mem_write(ADDR['od5'],(cap/'REQ5_CB_OUT_DESC_PRE_0030.bin').read_bytes()); u.mem_write(ADDR['om5'],(cap/'REQ5_CB_OUT_MESH_PRE_0DF0.bin').read_bytes())
    seen5={'r':0,'w':0}
    def h5(uc,access,address,size,value,ud):
        if ADDR['ctx']<=address<ADDR['ctx']+CONTEXT_MAP_BYTES:
            k='r' if access==16 else 'w'; seen5[k]=max(seen5[k],address+size-ADDR['ctx'])
    h=u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,h5); e.run(CALLBACK_RVA,xargs=(ADDR['obj'],ADDR['x1'],ADDR['x2_5'],ADDR['id5'],ADDR['od5']),instruction_limit=200_000_000); u.hook_del(h)
    if (u.reg_read(UC_ARM64_REG_X0)&0xffffffff)!=0: raise RuntimeError('request5 callback return != 0')
    checks5={
        'state_post': exact(ADDR['state'],0x1100,'REQ5_CB_STATE_POST_1100.bin'),
        'context_post_captured': exact(ADDR['ctx'],0x4000,'REQ5_CB_CTX_POST_4000.bin'),
        'output_mesh': exact(ADDR['om5'],0xdf0,'REQ5_CB_OUT_MESH_POST_0DF0.bin'),
        'state_carry_to_request6': exact(ADDR['state'],0x1100,'REQ6_CB_STATE_PRE_1100.bin'),
        'context_carry_to_request6': exact(ADDR['ctx'],0x4000,'REQ6_CB_CTX_PRE_4000.bin'),
    }
    if not all(checks5.values()): raise RuntimeError(f'request5 replay mismatch {checks5}')
    if seen5 != {'r':EXPECTED_CONTEXT_READ_HI,'w':EXPECTED_CONTEXT_WRITE_HI}: raise RuntimeError(f'request5 context footprint drift {seen5}')

    u.mem_write(ADDR['x1'],(cap/'REQ6_CB_X1_PRE_0400.bin').read_bytes()); u.mem_write(ADDR['inmesh'],(cap/'REQ6_CB_IN_MESH_PRE_0DF0.bin').read_bytes()); put(ADDR['x2_6'],'REQ6_CB_X2_PRE_14000.bin')
    amap(ADDR['od6'],0x20000); u.mem_write(ADDR['id6'],(cap/'REQ6_CB_IN_DESC_PRE_0030.bin').read_bytes()); u.mem_write(ADDR['od6'],(cap/'REQ6_CB_OUT_DESC_PRE_0030.bin').read_bytes()); u.mem_write(ADDR['om6'],(cap/'REQ6_CB_OUT_MESH_PRE_0DF0.bin').read_bytes())
    seen6={'r':0,'w':0}
    def h6(uc,access,address,size,value,ud):
        if ADDR['ctx']<=address<ADDR['ctx']+CONTEXT_MAP_BYTES:
            k='r' if access==16 else 'w'; seen6[k]=max(seen6[k],address+size-ADDR['ctx'])
    h=u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,h6); e.run(CALLBACK_RVA,xargs=(ADDR['obj'],ADDR['x1'],ADDR['x2_6'],ADDR['id6'],ADDR['od6']),instruction_limit=200_000_000); u.hook_del(h)
    if (u.reg_read(UC_ARM64_REG_X0)&0xffffffff)!=0: raise RuntimeError('request6 callback return != 0')
    checks6={
        'state_post': exact(ADDR['state'],0x1100,'REQ6_CB_STATE_POST_1100.bin'),
        'context_post_captured': exact(ADDR['ctx'],0x4000,'REQ6_CB_CTX_POST_4000.bin'),
        'x1_read_only': exact(ADDR['x1'],0x400,'REQ6_CB_X1_POST_0400.bin'),
        'x2_read_only': exact(ADDR['x2_6'],0x14000,'REQ6_CB_X2_POST_14000.bin'),
        'input_mesh_read_only': exact(ADDR['inmesh'],0xdf0,'REQ6_CB_IN_MESH_POST_0DF0.bin'),
        'output_mesh': exact(ADDR['om6'],0xdf0,'REQ6_CB_OUT_MESH_POST_0DF0.bin'),
    }
    if not all(checks6.values()): raise RuntimeError(f'request6 replay mismatch {checks6}')
    if seen6 != {'r':EXPECTED_CONTEXT_READ_HI,'w':EXPECTED_CONTEXT_WRITE_HI}: raise RuntimeError(f'request6 context footprint drift {seen6}')
    return {'extension_fill':f'0x{extension_fill:02x}','request5':{'context_access_hi':seen5,'checks':checks5},'request6':{'context_access_hi':seen6,'checks':checks6}}

def main() -> int:
    here=Path(__file__).resolve().parent
    ap=argparse.ArgumentParser(); ap.add_argument('--device-mft',type=Path,default=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll')); ap.add_argument('--capture-dir',type=Path,default=Path('/mnt/windows/Users/Geoca/Documents/SP11CameraOracle/E003H_20260902_TINTCTX')); ap.add_argument('--out',type=Path,default=here/'lsc-tintless-sequential-replay-oracle.json'); args=ap.parse_args()
    if sha_file(args.device_mft)!=DEVICE_MFT_SHA256: raise RuntimeError('DeviceMFT SHA mismatch')
    verify_captures(args.capture_dir); mod=load_surface_emu(here)
    runs=[replay_once(mod,args.device_mft,args.capture_dir,0x00),replay_once(mod,args.device_mft,args.capture_dir,0xA5)]
    oracle={
      'schema':'sp11-e003h-lsc-tintless-sequential-replay-v1','accepted':True,
      'source_authority':{'device_mft_sha256':DEVICE_MFT_SHA256,'windows_capture_session':'E003H_20260902_TINTCTX','camera_identity':CAPTURE_CAMERA_IDENTITY,'raw_capture_sha256':EXPECTED},
      'exact_functions':{'tintless_algorithm_wrapper_process_rva':hex(CALLBACK_RVA),'deeper_stateful_core_rva':hex(DEEP_RVA)},
      'bounded_state':{'captured_persistent_context_bytes':hex(CONTEXT_CAPTURE_BYTES),'dynamic_context_read_hi_exclusive':hex(EXPECTED_CONTEXT_READ_HI),'dynamic_context_write_hi_exclusive':hex(EXPECTED_CONTEXT_WRITE_HI),'extension_scratch_independence':'PASS for both 0x00 and hostile 0xa5 initial fill'},
      'sequential_replays':runs,
      'request5_output_mesh_sha256':EXPECTED['REQ5_CB_OUT_MESH_POST_0DF0.bin'],'request6_output_mesh_sha256':EXPECTED['REQ6_CB_OUT_MESH_POST_0DF0.bin'],
      'classification':'CLOSED BYTE-EXACT OV13858 REAR MODE-1 STATEFUL TINTLESS PRODUCER: exact Surface ARM64 request5 then request6 replay reproduces Windows persistent state and 0xdf0 output meshes with zero differing bytes. The algorithm/state proof remains valid; camera identity correction withdraws it as front IMX681 sequential-state evidence.',
      'next_gate':'Use this replay for rear/shared Tintless parity only. The verified IMX681 front path still requires a same-front-stream sequential Tintless capsule before integrated front producer parity can close. Linux request6 remains forbidden.',
      'safety':{'linux_camera_runtime':False,'linux_request6_executed':False,'raw_windows_captures_committed':False}}
    args.out.write_text(json.dumps(oracle,indent=2)+'\n')
    print('PASS exact sequential Tintless request5 -> request6 replay'); print('  request5 output',oracle['request5_output_mesh_sha256']); print('  request6 output',oracle['request6_output_mesh_sha256']); print('  context read/write hi',hex(EXPECTED_CONTEXT_READ_HI),hex(EXPECTED_CONTEXT_WRITE_HI)); print('  scratch fills tested: 0x00, 0xa5'); print('  oracle',args.out)
    return 0
if __name__=='__main__': raise SystemExit(main())
