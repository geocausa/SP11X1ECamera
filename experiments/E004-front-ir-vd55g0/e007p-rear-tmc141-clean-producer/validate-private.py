#!/usr/bin/env python3
from __future__ import annotations
import argparse, ctypes, json, struct, subprocess, tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent

class Input(ctypes.Structure):
    _fields_=[
        ('runtime_0c',ctypes.c_float),('runtime_18',ctypes.c_float),
        ('runtime_480',ctypes.c_float),('runtime_488',ctypes.c_float),
        ('runtime_48c',ctypes.c_float),('common_64',ctypes.c_float),
        ('mode',ctypes.c_uint32),('curve_order',ctypes.c_uint32),
        ('ctrl_8234',ctypes.c_uint32),('ctrl_8238',ctypes.c_uint32),
        ('ctrl_8244',ctypes.c_uint32),('ctrl_8254',ctypes.c_uint32),
        ('face_count',ctypes.c_uint32),
    ]

def f32(b,o): return struct.unpack_from('<f',b,o)[0]
def u32(b,o): return struct.unpack_from('<I',b,o)[0]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('capture_dir',type=Path)
    ap.add_argument('--out',type=Path,default=HERE/'PRIVATE-VALIDATION-SAFE.json')
    a=ap.parse_args()

    with tempfile.TemporaryDirectory(prefix='e007p-') as td:
        so=Path(td)/'libe007p.so'
        subprocess.run([
            'gcc','-O2','-shared','-fPIC','-Wall','-Wextra','-Werror',
            '-fno-fast-math','-ffp-contract=off',
            str(HERE/'tmc141-clean.c'),'-lm','-o',str(so)
        ],check=True)
        lib=ctypes.CDLL(str(so))
        solve=lib.e007p_tmc141_solve
        solve.argtypes=[
            ctypes.POINTER(ctypes.c_float),ctypes.c_size_t,
            ctypes.POINTER(Input),ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float),ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_uint)
        ]
        solve.restype=ctypes.c_int

        exact=0; indices=[]; branch_on=0
        for hit in range(1,21):
            q=f'H{hit:02d}'
            names=['TUNE','RUNTIME','COMMON','CTRL','FACE',
                   'POST_SRC','POST_DST','POST_COEF']
            p={n:a.capture_dir/f'{q}_{n}.bin' for n in names}
            if not all(x.is_file() for x in p.values()):
                raise RuntimeError(f'{q}: incomplete private oracle')
            tune=p['TUNE'].read_bytes(); runtime=p['RUNTIME'].read_bytes()
            common=p['COMMON'].read_bytes(); ctrl=p['CTRL'].read_bytes()
            face=p['FACE'].read_bytes()
            if len(tune)!=0x170 or len(runtime)!=0x498 or len(common)!=0x80:
                raise RuntimeError(f'{q}: input size drift')
            if len(ctrl)!=0x40 or len(face)<4:
                raise RuntimeError(f'{q}: control size drift')

            tin=(ctypes.c_float*(len(tune)//4)).from_buffer_copy(tune)
            inp=Input(
                f32(runtime,0x0c),f32(runtime,0x18),
                f32(runtime,0x480),f32(runtime,0x488),
                f32(runtime,0x48c),f32(common,0x64),
                0x60800,u32(common,0x60),
                u32(ctrl,0x0c),u32(ctrl,0x10),
                ctrl[0x1c],u32(ctrl,0x2c),u32(face,0)
            )
            src=(ctypes.c_float*7)(); dst=(ctypes.c_float*7)()
            coef=(ctypes.c_float*15)(); idx=ctypes.c_uint()
            rc=solve(tin,len(tune)//4,ctypes.byref(inp),
                     src,dst,coef,ctypes.byref(idx))
            if rc!=0:
                raise RuntimeError(f'{q}: solver rc={rc}')
            indices.append(int(idx.value))
            branch_on += int(inp.ctrl_8244==1)

            got=(bytes(src),bytes(dst),bytes(coef))
            want=(p['POST_SRC'].read_bytes(),p['POST_DST'].read_bytes(),
                  p['POST_COEF'].read_bytes())
            if got!=want:
                which=[n for n,g,w in zip(('SRC','DST','COEF'),got,want) if g!=w]
                raise RuntimeError(f'{q}: mismatch {which}')
            exact+=1

    safe={
        'schema':'E007p-private-validation-safe-v1',
        'status':'PASS',
        'capture_hits_checked':20,
        'exact_src_hits':exact,
        'exact_dst_hits':exact,
        'exact_coeff_hits':exact,
        'exact_complete_triplets':exact,
        'scale_index_sequence':indices,
        'rear_mode_branch_enabled_hits':branch_on,
        'mode':'0x60800',
        'raw_windows_values_emitted':False,
        'captured_knots_used_as_producer_inputs':False,
        'producer_inputs':[
            'TUNE semantic state','RUNTIME semantic scalars',
            'COMMON cap/curve-order','CTRL branch/control state','FACE count'
        ],
    }
    a.out.write_text(json.dumps(safe,indent=2,sort_keys=True)+'\n')
    print('E007P_PRIVATE_VALIDATION_PASS triplets=20/20 src=20/20 dst=20/20 coeff=20/20')
    print('scale_indices='+','.join(map(str,indices)))
    print('raw_windows_values_emitted=false captured_knots_used_as_inputs=false')

if __name__=='__main__':
    main()
