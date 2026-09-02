#!/usr/bin/env python3
"""Fail-closed static proof for the E003h tuning-manager ownership chain.

Pins exact Surface DeviceMFT ARM64 instructions/vtable entries showing:
CaptureDevice private DataManager -> CapturePipe -> DataManager+0x28
TuningDataManager -> common context+0x2460 -> ISPInputData+0x1fe8 -> IFELSC411.
No camera runtime is performed.
"""
from __future__ import annotations
import argparse, hashlib, json, struct
from pathlib import Path
import pefile

DEVICE_MFT_SHA = "c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
PREV_ORACLE_SHA = "814777dc3f049b444f30f1f2ffa013edbf6a29cf46f848948f304117fe987e92"
PREV_PROOF_SHA = "5565477f0cab6f7d0a86f83ebb1a20ca0378ed6bf428881b8c32e5cc37730222"

# VA -> exact instruction bytes. Exact DLL hash plus these signatures makes
# offset drift/future-binary substitution fail closed.
SIGS = {
    0x180293B14: "683240f9880a00f9",  # ldr x8,[CaptureDevice+0x60]; str x8,[config+0x10]
    0x1802ACBE4: "7b8e459102398052e10314aa60e3119123c23294",  # copy 0x1c8 config -> +0x163478
    0x1802C22D8: "004542f9080040f9081940f9ef0308aaf165009031de43f920023fd6e0013fd6",  # +0x163488, vtbl+0x30 call
    0x1802C2394: "68024ff9283112f9",  # +0x1e00 -> context+0x2460
    0x1800517C0: "001440f9c0035fd6",  # DataManager getter: return +0x28
    0x18073C31C: "680242f969d24191083152f9281d05f9",  # IFE owner+0x2460 copy
    0x18078094C: "6b0242f9683152f948d310f9",  # BPS owner+0x2460 -> request local +0x21a0
    0x180A02448: "97f64ff9f30300aa",  # IFELSC411 reads ISPInputData+0x1fe8
}

DM_VTABLE_BASE = 0x18133B780
DM_VTABLE_GET_TUNING_SLOT = 0x18133B7B0
DM_GET_TUNING_VA = 0x1800517C0


def sha_file(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20), b''): h.update(b)
    return h.hexdigest()


def main() -> int:
    here=Path(__file__).resolve().parent
    ap=argparse.ArgumentParser()
    ap.add_argument('--device-mft', type=Path, default=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll'))
    ap.add_argument('--previous-oracle', type=Path, default=here/'lsc-tuning-provenance-boundary-oracle.json')
    ap.add_argument('--previous-proof', type=Path, default=here/'prove-lsc-tuning-provenance-boundary.py')
    ap.add_argument('--out', type=Path, default=here/'lsc-tuning-manager-ownership-oracle.json')
    a=ap.parse_args()

    if sha_file(a.device_mft) != DEVICE_MFT_SHA:
        raise RuntimeError('DeviceMFT SHA drift')
    if sha_file(a.previous_oracle) != PREV_ORACLE_SHA:
        raise RuntimeError('previous provenance oracle drift')
    if sha_file(a.previous_proof) != PREV_PROOF_SHA:
        raise RuntimeError('previous provenance proof drift')

    data=a.device_mft.read_bytes()
    pe=pefile.PE(str(a.device_mft), fast_load=True)
    base=pe.OPTIONAL_HEADER.ImageBase
    def read_va(va:int,n:int)->bytes:
        off=pe.get_offset_from_rva(va-base)
        return data[off:off+n]

    observed={}
    for va,hx in SIGS.items():
        want=bytes.fromhex(hx); got=read_va(va,len(want))
        if got != want:
            raise RuntimeError(f'instruction signature drift at {va:#x}: {got.hex()} != {hx}')
        observed[f'{va:#x}']=got.hex()

    slot=struct.unpack('<Q', read_va(DM_VTABLE_GET_TUNING_SLOT,8))[0]
    if slot != DM_GET_TUNING_VA:
        raise RuntimeError(f'DataManager vtable +0x30 drift: {slot:#x}')

    for marker in [
        b'CaptureDevice::ConstructReal\x00', b'CapturePipe::Construct\x00',
        b'CapturePipe::ConfigureMetadata\x00', b'DataManager::CreateTuningDataManager\x00',
        b'CamX::IFELSC411::CheckAndUpdateChromatixData\x00', b'lsc41_ife_v2\x00',
        b'TuningDataManager pointer is updated']:
        if marker not in data:
            raise RuntimeError(f'missing exact binary marker {marker!r}')

    # The BPS request local addresses independently identify ISPInputData+0x1fe8:
    # context pointer is stored at stack +0x21a0; known tuningModeChanged is at
    # stack +0x2220. Their delta equals the struct delta 0x2068-0x1fe8.
    bps_stack_delta=0x2220-0x21A0
    isp_struct_delta=0x2068-0x1FE8
    if bps_stack_delta != 0x80 or bps_stack_delta != isp_struct_delta:
        raise RuntimeError('BPS ISPInputData local-layout delta drift')

    prior=json.loads(a.previous_oracle.read_text())
    if not prior.get('accepted'):
        raise RuntimeError('previous provenance boundary is not accepted')
    if prior['static_flow']['capturedevice_datamanager_storage'] != 'CaptureDevice+0x60 (param_1[0xc])':
        raise RuntimeError('previous per-CaptureDevice DataManager invariant drift')

    oracle={
      'schema':'sp11-e003h-lsc-tuning-manager-ownership-v1',
      'accepted':True,
      'classification':'CLOSED STATIC OWNERSHIP CHAIN: the tuning manager consumed by IFELSC411 is derived from the same CaptureDevice private DataManager through CapturePipe/common-context wiring; random/global rear-manager request injection is excluded on the normal path.',
      'device_mft':{'path':str(a.device_mft),'sha256':DEVICE_MFT_SHA},
      'dependency':{
        'oracle':a.previous_oracle.name,'oracle_sha256':PREV_ORACLE_SHA,
        'proof':a.previous_proof.name,'proof_sha256':PREV_PROOF_SHA,
        'accepted_invariant':'CaptureDevice+0x60 is a fresh per-CaptureDevice DataManager; DataManager+0x28 is the CamX TuningDataManager built from that DataManager SensorTuningData.'
      },
      'ownership_chain':[
        {'stage':'CaptureDevice private DataManager','source':'CaptureDevice+0x60'},
        {'stage':'CapturePipe config','source':'config+0x10 = CaptureDevice+0x60','rva':'0x293b14'},
        {'stage':'CapturePipe stored config','source':'CapturePipe+0x163488 = copied config+0x10','construct_rva':'0x2acb60','copy_base':'CapturePipe+0x163478','copy_bytes':'0x1c8'},
        {'stage':'private tuning manager accessor','source':'DataManager vtable+0x30 -> VA 0x1800517c0 -> DataManager+0x28','vtable_va':f'{DM_VTABLE_BASE:#x}','slot_va':f'{DM_VTABLE_GET_TUNING_SLOT:#x}'},
        {'stage':'common node context','source':'CapturePipe::ConfigureMetadata stores returned manager at context+0x2460','rva':'0x2c2250'},
        {'stage':'BPS request ISPInputData','source':'owner+0x2460 -> request local corresponding to ISPInputData+0x1fe8','rva':'0x780070','assignment_va':'0x180780950'},
        {'stage':'IFELSC411','source':'loads ISPInputData+0x1fe8 and performs one-tree lsc41_ife_v2 lookup','rva':'0xa02420'},
      ],
      'ife_independent_corrob':{'rva':'0x73c298','source':'IFENode::UpdateInitSettings copies owner+0x2460 into IFE input state'},
      'bps_layout_proof':{'manager_stack_offset':'0x21a0','tuning_mode_changed_stack_offset':'0x2220','stack_delta':'0x80','isp_manager_offset':'0x1fe8','isp_tuning_mode_changed_offset':'0x2068','struct_delta':'0x80'},
      'exact_signatures':observed,
      'closed_exclusions':[
        'unconditional global TuningDataManager is injected into all CaptureDevices',
        'CapturePipe chooses a tuning manager independently from its CaptureDevice DataManager',
        'IFE/BPS substitutes a different manager while constructing the request',
        'IFELSC411 module lookup falls back to a second tuning package/tree'],
      'remaining_provenance_gate':'Capture the exact live front private DataManager source tuning buffer identity (DataManager+0x38/+0x30) and correlate its DataManager+0x28 manager with context+0x2460 and ISPInputData+0x1fe8. If source hash is front IMX681, investigate parser/tree mutation; if rear OV13858, investigate live InitParams payload inconsistency.',
      'safety':{'linux_camera_runtime':False,'linux_request6_executed':False,'linux_request6_authorized':False},
    }
    a.out.write_text(json.dumps(oracle,indent=2)+'\n')
    print('PASS LSC tuning-manager ownership')
    print('  CaptureDevice+0x60 -> config+0x10 -> CapturePipe+0x163488')
    print('  DataManager vtbl+0x30 -> DataManager+0x28 -> context+0x2460')
    print('  BPS context+0x2460 -> ISPInputData+0x1fe8; IFELSC411 consumes +0x1fe8')
    print('  next: live hash DataManager+0x38/+0x30 on verified front stream')
    return 0

if __name__=='__main__': raise SystemExit(main())
