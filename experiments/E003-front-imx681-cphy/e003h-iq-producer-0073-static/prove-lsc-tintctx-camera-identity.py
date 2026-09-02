#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json, struct
from pathlib import Path
import pefile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PROJECT = REPO.parent.parent
DRIVERDUMP = PROJECT / '00-RE-archive' / 'sp11-driverdump'
DLL = DRIVERDUMP / 'surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342' / 'QcDeviceMFT8380.dll'
REAR = DRIVERDUMP / 'surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021' / 'com.surface.sensormodule.rfc_ov13858.bin'
FRONT = DRIVERDUMP / 'surfacecamfrontsensor_extension8380.inf_arm64_5a4c66ce4812274e' / 'com.surface.sensormodule.ffc_imx681.bin'
CARVE = HERE / 'oracle-carved-20260902'
X1 = CARVE / 'TINTCTX_REQ5' / 'REQ5_CB_X1_PRE_0400.bin'
FRONT_COMMON = HERE / 'windows-adaptive-live-20260902' / 'REQ5_LSC_COMMON.bin'
OUT = HERE / 'lsc-tintctx-camera-identity-oracle.json'

DEVICE_MFT_SHA = 'c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
REAR_SHA = 'f8f60e79b77bd3d5896cb04167ee428455e1a241f1ff9e50abee6b4dacfe6b14'
FRONT_SHA = 'f7dd81be64153fd3f0da8e6288ee1b9906b7bf51b773a98496934d76dc96a45c'
X1_SHA = 'b8bb8f82548baa20ea3ce5156d9da1837f65415a6cfc907813c858c7cfcaaffd'
FRONT_COMMON_SHA = '39c51103c2a92c566ff4493ede1a25a594d089b2e79a46857105f84f15ca2798'

CARVED = {
    'REQ5_X22_RAW_0DF0.bin': ('0xebb69c000', 3568, 'e35ad052a2d219bcded1283c72922fd0c5722431ad511c496ab1ab4ec03dc9de'),
    'REQ5_X23_RAW_0DF0.bin': ('0xebb6b0000', 3568, '94cbaac591fabf97ebff4a005b02fbcfa7a2bfff5783134794e1c52f0bcead71'),
    'REQ6_X22_RAW_0DF0.bin': ('0xebc263000', 3568, '3acd68d81103656463b65b448f3a6106c907a48f1f08acb4c3132d30c1b28ca8'),
    'REQ6_X23_RAW_0DF0.bin': ('0xebc7fb000', 3568, '62b39d4ee8f66dc4931c0a99bf4c51cc7069ea4829f78df6c80dbfa82b48ad15'),
    'TINTCTX_REQ5/REQ5_CB_IN_MESH_PRE_0DF0.bin': ('0xcf51ba000', 3568, 'd80d3bf1326d34fce4ee67ace514a1fc5470b9101b611432cf8b81683b39e74a'),
    'TINTCTX_REQ5/REQ5_CB_OUT_MESH_PRE_0DF0.bin': ('0xcf51bb000', 3568, '84957a7d73b8e9905fd60e30b89e18472bd62689468b6515ba8cea6d39f032f0'),
    'TINTCTX_REQ5/REQ5_CB_X1_PRE_0400.bin': ('0xcf53ac000', 1024, X1_SHA),
    'TINTCTX_REQ5/REQ5_CB_OUT_MESH_POST_0DF0.bin': ('0xcf6e02000', 3568, '1978d282a472117a2b28a3fb1c4b41295e1b8190c4737b448373e5571f381490'),
    'TINTCTX_NEAR_R6/REQ6_CB_STATE_POST_1100.bin': ('0x1741f8000', 4352, '3d4c1afa0e45f46887c4376044b853d8a10ae74e9346de8d798855066346a3c6'),
}

COPY_SIG_RVA = 0xC960F0
COPY_SIG = bytes.fromhex(
    '880640b9c81600b9880240b9c81200b9881e40b9c83200b9882240b9c83600b9'
    '882640b9c83a00b9882a40b9c83e00b9880a40b9c81a00b9880e40b9c81e00b9'
    '881240b9c82600b9881640b9c82200b9882e40b9c82e00b9'
)
VALIDATE_SIG_RVA = 0xC96380
VALIDATE_SIG = bytes.fromhex(
    'a90e40b9294d0034ad0a40b9ed4c0034c94c0037ad4c0037a81640b9684c0034'
    'ac1240b92c4c0034084c0037ec4b0037ab1a40b9087d0b1b294128cb68791f53'
    '3f4128eb2c4b0054aa1e40b9887d0a1ba94128cb48791f533f4128eb6c4a0054'
    'a82240b988000035080480527f610071050000141f050071a1000054080880527f'
    'c100714001487a01490054'
)
HANDOFF_SIG_RVA = 0x88E3A8
HANDOFF_SIG = bytes.fromhex(
    '88ae4079e00314aa690640f9a48744a928110079a80b40f9650640f903110091'
    '02510191083f43f9ef0308aa9137009031de43f920023fd6e0013fd61f040071'
)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def need(cond: bool, message: str) -> None:
    if not cond:
        raise RuntimeError(message)


def pe_bytes(pe: pefile.PE, raw: bytes, rva: int, size: int) -> bytes:
    off = pe.get_offset_from_rva(rva)
    return raw[off:off + size]


def load_summary_module():
    p = REPO / 'tools' / 'qti_sensor_summary.py'
    spec = importlib.util.spec_from_file_location('qti_sensor_summary', p)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    need(sha(DLL) == DEVICE_MFT_SHA, 'DeviceMFT authority SHA mismatch')
    need(sha(REAR) == REAR_SHA, 'rear OV13858 sensor authority SHA mismatch')
    need(sha(FRONT) == FRONT_SHA, 'front IMX681 sensor authority SHA mismatch')
    need(sha(X1) == X1_SHA and X1.stat().st_size == 0x400, 'carved TINTCTX req5 x1 mismatch')
    need(sha(FRONT_COMMON) == FRONT_COMMON_SHA, 'verified-front LSC common authority mismatch')

    carved = {}
    for rel, (offset, size, expected) in CARVED.items():
        p = CARVE / rel
        need(p.exists() and p.stat().st_size == size, f'carved file missing/size mismatch: {rel}')
        actual = sha(p)
        need(actual == expected, f'carved SHA mismatch: {rel}')
        carved[rel] = {'ntfs_partition_offset': offset, 'bytes': size, 'sha256': actual}

    # Machine-code pin: wrapper copies the x1 geometry tuple into its persistent
    # internal structure and then validates dimensions/cell counts/cell sizes.
    raw = DLL.read_bytes(); pe = pefile.PE(str(DLL), fast_load=False)
    need(pe_bytes(pe, raw, COPY_SIG_RVA, len(COPY_SIG)) == COPY_SIG, 'Tintless x1 copy signature mismatch')
    need(pe_bytes(pe, raw, VALIDATE_SIG_RVA, len(VALIDATE_SIG)) == VALIDATE_SIG, 'Tintless geometry validation signature mismatch')
    need(pe_bytes(pe, raw, HANDOFF_SIG_RVA, len(HANDOFF_SIG)) == HANDOFF_SIG, 'LSC interpolation->HW handoff signature mismatch')

    x1 = X1.read_bytes()
    vals = {off: struct.unpack_from('<I', x1, off)[0] for off in (0x1c,0x20,0x24,0x28,0x2c,0x30,0x34)}
    expected_vals = {0x1c:4064, 0x20:2286, 0x24:126, 0x28:94, 0x2c:32, 0x30:24, 0x34:0}
    need(vals == expected_vals, f'unexpected TINTCTX geometry tuple: {vals!r}')
    width,height,cells_x,cells_y,cell_w,cell_h = vals[0x1c],vals[0x20],vals[0x24],vals[0x28],vals[0x2c],vals[0x30]
    # Exact inequalities enforced by the wrapper at RVA 0xc963b0..0xc96408.
    need(width % 2 == 0 and height % 2 == 0, 'Tintless image dimensions not even')
    need(width - cells_x*cell_w <= 2*cell_w, 'Tintless horizontal grid residual fails wrapper bound')
    need(height - cells_y*cell_h <= 2*cell_h, 'Tintless vertical grid residual fails wrapper bound')
    need((cell_w,cell_h) == (32,24), 'Tintless packing-mode-0 expected 32x24 cells')

    qss = load_summary_module()
    rear = qss.summarize(REAR); front = qss.summarize(FRONT)
    target = (width,height)
    rear_hits = [m for m in rear['modes'] if (m['width'],m['height']) == target]
    front_hits = [m for m in front['modes'] if (m['width'],m['height']) == target]
    need(len(rear_hits) == 1 and rear_hits[0]['index'] == 1, 'target geometry not uniquely rear mode1 in rear authority')
    rm = rear_hits[0]
    need((rm['x_start'],rm['y_start'],rm['frame_rate'],rm['data_type'],rm['bit_width']) == (6,260,30.0,43,10), 'rear mode1 metadata mismatch')
    need(not front_hits, 'IMX681 unexpectedly exposes 4064x2286')

    all_surface_modes=[]; target_hits=[]
    for p in sorted(DRIVERDUMP.rglob('com.surface.sensormodule*.bin')):
        try:
            s=qss.summarize(p)
        except Exception:
            continue
        entry={'sensor_name':s['probe']['sensor_name'],'file':p.name,'sha256':sha(p),
               'modes':[{'index':m['index'],'width':m['width'],'height':m['height'],'x_start':m['x_start'],'y_start':m['y_start'],'fps':m['frame_rate']} for m in s['modes']]}
        all_surface_modes.append(entry)
        for m in s['modes']:
            if (m['width'],m['height']) == target:
                target_hits.append({'sensor_name':s['probe']['sensor_name'],'file':p.name,'sha256':sha(p),'mode':m})
    need(len(target_hits) == 1, f'4064x2286 not unique across Surface sensor modules: {target_hits!r}')
    need(target_hits[0]['sensor_name'] == 'ov13858' and target_hits[0]['mode']['index'] == 1, 'unique target is not OV13858 mode1')

    fc = FRONT_COMMON.read_bytes()
    fg = {name:struct.unpack_from('<I',fc,off)[0] for name,off in {
        'full_width':0x1c,'full_height':0x20,'output_width':0x24,'output_height':0x28,
        'offset_x':0x2c,'offset_y':0x30,'scale_x':0x34,'scale_y':0x38,'scale':0x3c}.items()}
    need(fg == {'full_width':4048,'full_height':3152,'output_width':3840,'output_height':2160,
                'offset_x':104,'offset_y':496,'scale_x':0,'scale_y':0,'scale':1},
         f'verified-front geometry mismatch: {fg!r}')

    out={
      'schema':'sp11-e003h-lsc-tintctx-camera-identity-v1','accepted':True,'offline_only':True,
      'classification':'CLOSED CORRECTION: E003H_20260902_TINTCTX is an OV13858 rear mode-1 Tintless session, not the verified IMX681 front stream.',
      'source_authority':{
        'device_mft_sha256':DEVICE_MFT_SHA,'rear_sensor_module_sha256':REAR_SHA,'front_sensor_module_sha256':FRONT_SHA,
        'tintctx_req5_x1_sha256':X1_SHA,'verified_front_req5_lsc_common_sha256':FRONT_COMMON_SHA,
        'raw_ntfs_carve':carved},
      'machine_code':{
        'tintless_wrapper_process_rva':'0xc95fd0','x1_geometry_copy_signature':{'rva':hex(COPY_SIG_RVA),'hex':COPY_SIG.hex()},
        'geometry_validation_signature':{'rva':hex(VALIDATE_SIG_RVA),'hex':VALIDATE_SIG.hex()},
        'lsc_interpolation_to_hw_handoff_signature':{'rva':hex(HANDOFF_SIG_RVA),'hex':HANDOFF_SIG.hex()},
        'handoff_fact':'IQInterface calls LSC411Interpolation then LSC411Setting::CalculateHWSetting with the same param1+0x1e8 pData buffer; no hidden copy/reorder stage lies between calibrated x23 and geometry.'},
      'tintctx_req5_geometry':{
        'x1_offsets':{'image_width':'0x1c','image_height':'0x20','cells_x':'0x24','cells_y':'0x28','cell_width':'0x2c','cell_height':'0x30','packing_mode':'0x34'},
        'values':{'image_width':width,'image_height':height,'cells_x':cells_x,'cells_y':cells_y,'cell_width':cell_w,'cell_height':cell_h,'packing_mode':vals[0x34]},
        'wrapper_validation':{'horizontal_residual':width-cells_x*cell_w,'horizontal_max':2*cell_w,
                              'vertical_residual':height-cells_y*cell_h,'vertical_max':2*cell_h,'passes':True}},
      'sensor_identity':{
        'unique_4064x2286_surface_sensor_hits':target_hits,
        'rear_mode1':rm,
        'front_imx681_has_4064x2286':False,
        'all_surface_sensor_modules':all_surface_modes},
      'verified_front_reference':{'capture':'E003H_ADAPTIVE_0073_LIVE_20260902','geometry':fg},
      'impact':{
        'sequential_tintless_replay':'REMAINS BYTE-EXACT and valuable as a shared Surface Tintless/OV13858 rear stateful oracle, but is withdrawn as evidence of front IMX681 sequential Tintless state.',
        'front_integrated_gate':'FAIL-CLOSED: do not splice TINTCTX request5/request6 into LSCTRIGSRC or the verified-front adaptive capsule. A true front same-stream Tintless capsule is still required for 1:1 front integrated proof.',
        'rear_stack':'The recovered TINTCTX session strengthens rear OV13858 parity by providing exact stateful Tintless request5->request6 behavior for rear mode1.'},
      'safety':{'linux_camera_runtime':False,'linux_request6_executed':False,'runtime_authorized':False}
    }
    OUT.write_text(json.dumps(out,indent=2)+'\n')
    print('PASS TINTCTX camera identity: OV13858 rear mode1; front use revoked')
    print('TINTCTX',width,height,'grid',cells_x,cells_y,'cell',cell_w,cell_h)
    print('rear mode1 crop',rm['x_start'],rm['y_start'],'front ref',fg['output_width'],fg['output_height'])
    print('oracle',OUT.name,sha(OUT))

if __name__=='__main__': main()
