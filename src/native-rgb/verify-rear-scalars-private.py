#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Verify libipa -> integer envelope -> real scalar binding/packer privately.
No camera access. Originals and calculated words stay on this same SP11.
The hosted fixture omits unused packet members; the full kernel types are checked
by the separate ARM64 module build. This is retained-trace, not fresh live proof.
"""
import argparse, ctypes, importlib.util, json, subprocess, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PRIVATE=ROOT.parent/'private/E011X-source-recovered'
DECODER=ROOT/'experiments/E004-front-ir-vd55g0/e006a-windows-rear-rtcdm-targeted-corpus/decode_rear_rtcdm.py'

class In(ctypes.Structure):
    _fields_=[('demux_gain',ctypes.c_float),('bls',ctypes.c_float*4),
              ('channel',ctypes.c_float*4),('awb_g',ctypes.c_float),
              ('awb_b',ctypes.c_float),('awb_r',ctypes.c_float),
              ('predictive_gain',ctypes.c_float),('bayer',ctypes.c_uint8)]
class Capsule(ctypes.Structure):
    _fields_=[('data',ctypes.c_uint8*208)]

BRIDGE="#include \"camss_x1e_helpers.h\"\n#include <cstdint>\nextern \"C\" int sp11_generate_rear_scalar_envelope(\n const e012k_rear_scalar_input *in,const uint64_t *ids,\n native_rear_startup_scalars *out)\n{\n return libcamera::ipa::camssX1ERearStartupScalars({in,4},{ids,4},out);\n}\n"
CBRIDGE="#include \"native-rear-startup-scalars.h\"\n#include <stdint.h>\n#include <stdbool.h>\n#include <errno.h>\ntypedef uint8_t u8;typedef uint16_t u16;typedef uint32_t u32;typedef uint64_t u64;\n#define __used __attribute__((used))\n#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))\n#define static_assert(x) _Static_assert(x,#x)\n#define E007Y_STARTUP_PACKETS NATIVE_REAR_SCALARS_PACKETS\n#include \"camss-e006z-clean-scalar-bank.inc\"\n/* Unused register/DMI members omitted ONLY in this hosted fixture. */\nstruct e008o_rear_packet_semantics {\n struct { struct e006z_rear_scalar_state scalar; } regs;\n u64 request_id;\n bool ready;\n};\n#include <string.h>\n#include \"native-rear-scalar-binding.inc\"\nint sp11_bind_and_pack_rear_scalars(\n const struct native_rear_startup_scalars *capsule,const uint64_t *ids,uint32_t *out)\n{\n struct e008o_rear_packet_semantics base[4]={0};\n const uint16_t registers[8]={0x3b70,0x3b74,0x3d78,0x3d7c,0x3d80,0x3d84,0x456c,0x4570};\n unsigned p,r;\n int ret;\n for(p=0;p<4;p++)base[p].request_id=ids[p];\n ret=native_rear_bind_startup_scalars(base,capsule);\n if(ret)return ret;\n for(p=0;p<4;p++)for(r=0;r<8;r++){\n  ret=e006z_rear_clean_scalar_bank_lookup(&base[p].regs.scalar,registers[r],&out[p*8+r]);\n  if(ret)return ret;\n }\n return 0;\n}\n"

def main():
    a=argparse.ArgumentParser()
    a.add_argument('--libcamera-source',type=Path,required=True)
    a.add_argument('--libcamera-build',type=Path,required=True)
    a.add_argument('--kernel-staged',type=Path,required=True)
    a.add_argument('--report',type=Path,required=True)
    args=a.parse_args()
    if args.report.exists():
        raise SystemExit('verification report identity already exists')
    if not str(ROOT).startswith('/home/geoca/Documents/SP11-PROJECT/'):
        raise SystemExit('private oracle only on authorized SP11 workspace')
    samples=json.loads((PRIVATE/'samples.json').read_text())['samples']
    corpus=json.loads((PRIVATE/'E006A-PRIVATE-RECORDS-v2.json').read_text(encoding='utf-8-sig'))['records']
    spec=importlib.util.spec_from_file_location('rear_decode',DECODER)
    dec=importlib.util.module_from_spec(spec);spec.loader.exec_module(dec)
    src=args.libcamera_source.resolve();build=args.libcamera_build.resolve()
    with tempfile.TemporaryDirectory(prefix='sp11-rear-scalar-private-') as td:
        td=Path(td);code=td/'bridge.cpp';code.write_text(BRIDGE);library=td/'bridge.so'
        ccode=td/'bind.c';ccode.write_text(CBRIDGE);obj=td/'bind.o'
        ccommand=['gcc','-std=c11','-Wall','-Wextra','-Werror','-fPIC',
                  '-I'+str(args.kernel_staged.resolve()),'-c',str(ccode),'-o',str(obj)]
        crun=subprocess.run(ccommand,capture_output=True,text=True)
        if crun.returncode:raise RuntimeError(crun.stdout+crun.stderr)
        command=['g++','-std=c++17','-Wall','-Wextra','-Werror','-shared','-fPIC',
                 '-I'+str(src/'include'),'-I'+str(build/'include'),
                 '-I'+str(src/'src/ipa/libipa'),'-I'+str(args.kernel_staged.resolve()),
                 str(code),str(obj),str(build/'src/ipa/libipa/libipa.a'),
                 '-L'+str(build/'src/libcamera'),'-L'+str(build/'src/libcamera/base'),
                 '-Wl,-rpath,'+str(build/'src/libcamera'),
                 '-Wl,-rpath,'+str(build/'src/libcamera/base'),
                 '-lcamera','-lcamera-base','-lm','-o',str(library)]
        compiled=subprocess.run(command,capture_output=True,text=True)
        if compiled.returncode:raise RuntimeError(compiled.stdout+compiled.stderr)
        lib=ctypes.CDLL(str(library))
        gen=lib.sp11_generate_rear_scalar_envelope
        gen.argtypes=[ctypes.POINTER(In),ctypes.POINTER(ctypes.c_uint64),ctypes.POINTER(Capsule)]
        gen.restype=ctypes.c_int
        bind=lib.sp11_bind_and_pack_rear_scalars
        bind.argtypes=[ctypes.POINTER(Capsule),ctypes.POINTER(ctypes.c_uint64),ctypes.POINTER(ctypes.c_uint32)]
        bind.restype=ctypes.c_int
        inputs=(In*4)();ids=(ctypes.c_uint64*4)(4,5,6,6);phase_map=[0,1,2,2]
        for p,index in enumerate(phase_map):
            s=samples[index];x=inputs[p]
            x.demux_gain=s['demux_gain'];x.bls[:]=s['bls'];x.channel[:]=s['channel']
            x.awb_g,x.awb_b,x.awb_r=s['pdpc_floats'][2:5]
            x.predictive_gain=s['wb'][3];x.bayer=s['bayer']
        capsule=Capsule()
        if gen(inputs,ids,ctypes.byref(capsule)):raise RuntimeError('libipa generation failed')
        packed=(ctypes.c_uint32*32)()
        if bind(ctypes.byref(capsule),ids,packed):raise RuntimeError('kernel scalar binding/packer failed')
        # Negative identity must fail before publishing any packed output.
        badids=(ctypes.c_uint64*4)(4,5,6,7)
        sentinel=(ctypes.c_uint32*32)(*([0x12345678]*32))
        if bind(ctypes.byref(capsule),badids,sentinel)!=-116:
            raise RuntimeError('stale request identity accepted')
        if any(x!=0x12345678 for x in sentinel):
            raise RuntimeError('stale identity partially published')
        registers=[0x3b70,0x3b74,0x3d78,0x3d7c,0x3d80,0x3d84,0x456c,0x4570]
        totals=[]
        for phase,index in enumerate(phase_map):
            expected={reg:packed[phase*8+r] for r,reg in enumerate(registers)}
            mainrec=next(r for r in corpus if r['n']==phase and r['idx']==1)
            actual={reg:val for reg,val,_,_ in dec.decode(bytes.fromhex(mainrec['hex']))['writes'] if reg in expected}
            common=set(actual)&set(expected)
            count=sum(actual[reg]==expected[reg] for reg in common)
            totals.append({'phase':phase,'semantic_sample_index':index,
                           'register_instances_present':len(common),
                           'register_instances_exact':count})
            if count!=len(common):raise RuntimeError('retained scalar comparison failed phase '+str(phase))
        present=sum(x['register_instances_present'] for x in totals)
        exact=sum(x['register_instances_exact'] for x in totals)
        if present!=26 or exact!=26:raise RuntimeError('expected retained 26-instance coverage missing')
    safe={'status':'PASS_LIBIPA_TO_REAR_PACKET_SCALAR_BINDING_RETAINED_ORACLE',
          'phase_results':totals,'register_instances_present':present,
          'register_instances_exact':exact,'libipa_helper_called':True,
          'actual_kernel_scalar_binder_and_register_packer_called_hosted':True,
          'unused_kernel_packet_fields_omitted_in_host_fixture':True,
          'synthetic_Linux_request_IDs':[4,5,6,6],
          'stale_identity_rejected_atomically':True,
          'captured_register_words_or_packet_bytes_exported':False,
          'private_semantic_inputs_exported_or_embedded':False,
          'new_hardware_capture':False,'new_camera_start':False,
          'rear_full_bootstrap_or_optical_quality_proven':False}
    args.report.write_text(json.dumps(safe,indent=2)+'\n')
    print(json.dumps(safe))
if __name__=='__main__':
    main()
