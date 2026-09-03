#!/usr/bin/env python3
"""Fail-closed proof that verified front LSCTRIGSRC uses the rear/default LSC calibration slot."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, struct
from pathlib import Path
try:
    import pefile
except Exception as exc:
    raise SystemExit(f"missing proof dependency pefile: {exc}")

HERE = Path(__file__).resolve().parent
DEVICE_MFT_SHA = "c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
REAR_TUNING_SHA = "4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635"
REAR_GOLDEN_SHA = "f771e54d183281251bf0ef6d94e94a0d439c641f8b8ed9a3ad60ead4094487d6"
REAR_SLOT_SHA = "fb14d234d55317c9665de39fe93ddeb76ee06b9cffc64bee8d250152ae9dfa18"
REAR_COMMON_SHA = "4549e3577ba946817c49d93209e3a7e92a27825a1f4551acd4a587fd9f1e6c68"
CAPTURE = {
    5: {
        "x22": ("REQ5_X22_RAW_0DF0.bin", "e35ad052a2d219bcded1283c72922fd0c5722431ad511c496ab1ab4ec03dc9de"),
        "x23": ("REQ5_X23_RAW_0DF0.bin", "94cbaac591fabf97ebff4a005b02fbcfa7a2bfff5783134794e1c52f0bcead71"),
    },
    6: {
        "x22": ("REQ6_X22_RAW_0DF0.bin", "3acd68d81103656463b65b448f3a6106c907a48f1f08acb4c3132d30c1b28ca8"),
        "x23": ("REQ6_X23_RAW_0DF0.bin", "62b39d4ee8f66dc4931c0a99bf4c51cc7069ea4829f78df6c80dbfa82b48ad15"),
    },
}
GENERIC_TRIGGER_CODE = {
    0x897B9C: "70ba60bd", # ldr s16,[x19,#0x20b8]
    0x897BA8: "300100bd", # str s16,[x9] -> generic trigger vector[0]
    0x897BD4: "70ca60bd", # ldr s16,[x19,#0x20c8]
    0x897BD8: "301900bd", # str s16,[x9,#0x18] -> generic trigger vector[6]
}


def sha_bytes(b: bytes) -> str: return hashlib.sha256(b).hexdigest()
def sha_file(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda:f.read(1<<20),b''): h.update(c)
    return h.hexdigest()
def need(v, msg):
    if not v: raise RuntimeError(msg)
def f32(v: float) -> float: return struct.unpack('<f',struct.pack('<f',float(v)))[0]
def fbits(v: float) -> int: return struct.unpack('<I',struct.pack('<f',float(v)))[0]
def add(a,b): return f32(f32(a)+f32(b))
def mul(a,b): return f32(f32(a)*f32(b))
def div(a,b): return f32(f32(a)/f32(b))


def load_golden_parser():
    spec=importlib.util.spec_from_file_location('golden',HERE/'prove-lsc-live-golden-authority.py')
    mod=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(mod); return mod


def verify_code(dll: Path):
    need(sha_file(dll)==DEVICE_MFT_SHA,'DeviceMFT SHA mismatch')
    pe=pefile.PE(str(dll),fast_load=True); raw=dll.read_bytes(); out={}
    for rva,hx in GENERIC_TRIGGER_CODE.items():
        got=raw[pe.get_offset_from_rva(rva):pe.get_offset_from_rva(rva)+4].hex()
        need(got==hx,f'generic-trigger code mismatch RVA 0x{rva:x}: {got} != {hx}')
        out[f'0x{rva:x}']=got
    return out


def parse_slot(slot: bytes):
    need(len(slot)==0xDF0,'rear runtime slot size drift')
    availability,light_type,mesh_size=struct.unpack_from('<3I',slot,0)
    need((availability,light_type,mesh_size)==(1,3,221),'rear runtime slot header drift')
    vals=[]; channels=[]
    for off in (0x0C,0x380,0x6F4,0xA68):
        ch=struct.unpack_from('<221f',slot,off)
        need(all(v==float(int(v)) and 0 < v <= 65535 for v in ch),'runtime slot is not u16-as-float32')
        channels.append(tuple(int(v) for v in ch)); vals.extend(ch)
    need(slot[0xDDC:]==bytes(0x14),'runtime slot tail drift')
    return channels, vals


def calibrate_full(x22b: bytes, golden, eeprom):
    need(len(x22b)==0xDF0,'x22 size drift')
    x=struct.unpack('<884f',x22b[:0xDD0]); out=[0.0]*884
    for i in range(221):
        out[i]=mul(div(golden[i],eeprom[i]),x[i])
        g1=mul(div(golden[221+i],eeprom[221+i]),x[221+i])
        g2=mul(div(golden[442+i],eeprom[442+i]),x[442+i])
        gg=mul(add(g1,g2),f32(0.5))
        out[221+i]=gg; out[442+i]=gg
        out[663+i]=mul(div(golden[663+i],eeprom[663+i]),x[663+i])
    return struct.pack('<884f',*out)+x22b[0xDD0:]


def green_out(golden,x,req_i,e1,e2):
    g1=mul(div(golden[221+req_i],f32(float(e1))),x[221+req_i])
    g2=mul(div(golden[442+req_i],f32(float(e2))),x[442+req_i])
    return mul(add(g1,g2),f32(0.5))


def green_pair_candidates(golden,x22,x23,i):
    # Exact req5+req6 inverse, bounded by u16 formatter domain. Search e1 and
    # monotonic-bisect e2; this is used only to expose the three true plateaus.
    pairs=set()
    for e1 in range(1,2049): # observed slot max is 1023; keep a hostile margin
        target=x23[5][221+i]
        lo,hi=1,2048
        while lo<hi:
            mid=(lo+hi)//2
            y=green_out(golden,x22[5],i,e1,mid)
            if y <= target: hi=mid
            else: lo=mid+1
        for e2 in range(max(1,lo-4),min(2048,lo+4)+1):
            if (fbits(green_out(golden,x22[5],i,e1,e2))==fbits(x23[5][221+i]) and
                fbits(green_out(golden,x22[6],i,e1,e2))==fbits(x23[6][221+i])):
                pairs.add((e1,e2))
    return sorted(pairs)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--device-mft',type=Path,default=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll'))
    ap.add_argument('--rear-tuning',type=Path,default=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.surface.tuned.rfc_ov13858.bin'))
    ap.add_argument('--out',type=Path,default=HERE/'lsc-front-rear-calibration-authority-oracle.json')
    args=ap.parse_args()
    code=verify_code(args.device_mft)
    need(sha_file(args.rear_tuning)==REAR_TUNING_SHA,'rear tuning SHA mismatch')
    gp=load_golden_parser(); g=gp.parse_golden(args.rear_tuning)
    need(g and g['golden_region_sha256']==REAR_GOLDEN_SHA,'rear golden authority drift')

    vss=HERE/'oracle-vss-20260902-local'
    slot_path=vss/'REQ1_LSC_CAL_SLOT_0DF0.bin'; common_path=vss/'REQ1_LSC_COMMON_01E8.bin'
    need(sha_file(slot_path)==REAR_SLOT_SHA,'rear VSS slot SHA mismatch')
    need(sha_file(common_path)==REAR_COMMON_SHA,'rear VSS common SHA mismatch')
    common=common_path.read_bytes(); rear_geom=struct.unpack_from('<9I',common,0x1C)
    need(rear_geom==(4076,2806,4064,2286,6,260,0,0,1),f'rear VSS geometry drift {rear_geom!r}')
    channels,eeprom=parse_slot(slot_path.read_bytes())

    carve=HERE/'oracle-carved-20260902'; x22={}; x23={}; replays={}
    for req in (5,6):
        n22,h22=CAPTURE[req]['x22']; n23,h23=CAPTURE[req]['x23']
        p22=carve/n22; p23=carve/n23
        need(sha_file(p22)==h22 and sha_file(p23)==h23,f'request{req} capture SHA mismatch')
        b22=p22.read_bytes(); b23=p23.read_bytes(); need(len(b22)==len(b23)==0xDF0,'capture size drift')
        x22[req]=struct.unpack('<884f',b22[:0xDD0]); x23[req]=struct.unpack('<884f',b23[:0xDD0])
        generated=calibrate_full(b22,g['values'],[float(v) for ch in channels for v in ch])
        need(generated==b23,f'request{req}: rear slot does not reproduce verified front x23')
        replays[f'request{req}']={'x22_sha256':h22,'generated_x23_sha256':sha_bytes(generated),'windows_x23_sha256':h23,'full_0xdf0_equal':True}

    # Re-invert the direct planes and require the rear slot to be the unique integer solution.
    direct_unique=0
    flat=[v for ch in channels for v in ch]
    for idx in list(range(221))+list(range(663,884)):
        c5=set(gp.candidates(g['values'][idx],x22[5][idx],x23[5][idx])); c6=set(gp.candidates(g['values'][idx],x22[6][idx],x23[6][idx]))
        both=sorted(c5&c6); need(both==[flat[idx]],f'direct EEPROM inverse mismatch idx {idx}: {both} != {flat[idx]}')
        direct_unique += 1

    ambiguous_expected={19:[(335,335),(336,334)],57:[(751,753),(752,752)],94:[(967,968),(970,965)]}
    ambiguity={}
    for i,want in ambiguous_expected.items():
        got=green_pair_candidates(g['values'],x22,x23,i); need(got==want,f'green inverse drift at {i}: {got} != {want}')
        actual=(channels[1][i],channels[2][i]); need(actual in got,f'rear slot green pair not admissible at {i}')
        ambiguity[str(i)]={'equation_candidates':[list(x) for x in got],'rear_slot_pair':list(actual),'selected_index':got.index(actual)}

    oracle={
      'schema':'sp11-e003h-lsc-front-rear-calibration-authority-v1',
      'status':'PASS',
      'classification':'CLOSED BYTE-EXACT FRONT CALIBRATION PAYLOAD AUTHORITY: the exact older OV13858 rear runtime EEPROM slot is byte-equivalent to the calibration payload required by the verified front IMX681 LSCTRIGSRC equations; with the proven rear/default lscgolden41 region it reproduces Windows x23 byte-for-byte. Live front slot pointer/loader provenance is not asserted.',
      'source_authority':{
        'device_mft_sha256':DEVICE_MFT_SHA,'rear_tuning_sha256':REAR_TUNING_SHA,'rear_golden_region_sha256':REAR_GOLDEN_SHA,
        'rear_vss_runtime_slot':{'file':'oracle-vss-20260902-local/REQ1_LSC_CAL_SLOT_0DF0.bin','sha256':REAR_SLOT_SHA,'header':[1,3,221],'channel_offsets':['0x0c','0x380','0x6f4','0xa68'],'rear_geometry':list(rear_geom)},
        'rear_vss_common_sha256':REAR_COMMON_SHA,
      },
      'generic_trigger_mapping':{
        'function':'CamX::IQInterface::SetupGenericTrigger','rva':'0x897b78','code_byte_proofs':code,
        'vector0':'ISPInputData+0x20b8 = raw ISPIQTriggerData +0x38 = AECLuxIndex',
        'vector6':'ISPInputData+0x20c8 = raw ISPIQTriggerData +0x48 = AWBColorTemperature',
      },
      'front_replays':replays,
      'inverse_crosscheck':{'direct_unique_points':direct_unique,'green_points_total':221,'three_two-solution_green_points':ambiguity,'rear_slot_matches_all_884_inferred_values':True},
      'gate':'Front pre-Tintless reconstruction may use this exact rear runtime slot. The remaining front-only parity gap is sequential Tintless state/stats; do not use pre-request correction-table snapshots as post-request ratios. Linux request6 remains forbidden.'
    }
    args.out.write_text(json.dumps(oracle,indent=2,sort_keys=True)+'\n')
    print('PASS front rear-calibration authority')
    print('  req5 x23',replays['request5']['generated_x23_sha256'])
    print('  req6 x23',replays['request6']['generated_x23_sha256'])
    print('  direct unique',direct_unique,'green ambiguity resolved by rear slot', {k:v['rear_slot_pair'] for k,v in ambiguity.items()})
    print('  oracle',args.out)
    return 0
if __name__=='__main__': raise SystemExit(main())
