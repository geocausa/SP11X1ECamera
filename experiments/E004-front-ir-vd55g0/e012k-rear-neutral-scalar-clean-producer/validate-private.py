#!/usr/bin/env python3
import ctypes, importlib.util, json, math, pathlib, subprocess, tempfile
ROOT=pathlib.Path(__file__).resolve().parents[3]
PRIVATE=ROOT.parent/'private'/'E011X-source-recovered'
DECODER=ROOT/'experiments/E004-front-ir-vd55g0/e006a-windows-rear-rtcdm-targeted-corpus/decode_rear_rtcdm.py'

class In(ctypes.Structure):
    _fields_=[('demux_gain',ctypes.c_float),('bls',ctypes.c_float*4),('channel',ctypes.c_float*4),
              ('awb_g',ctypes.c_float),('awb_b',ctypes.c_float),('awb_r',ctypes.c_float),
              ('predictive_gain',ctypes.c_float),('bayer',ctypes.c_uint8)]
class Out(ctypes.Structure):
    _fields_=[('demux_q10',ctypes.c_uint16*4),('pdpc_q12',ctypes.c_uint32*4),
              ('wb_b_q10',ctypes.c_uint16),('wb_r_q10',ctypes.c_uint16)]

def pack(o):
    return {0x3b70:(o.demux_q10[0]<<16)|o.demux_q10[1],
            0x3b74:(o.demux_q10[3]<<16)|o.demux_q10[2],
            0x3d78:o.pdpc_q12[0],0x3d7c:o.pdpc_q12[1],0x3d80:o.pdpc_q12[2],0x3d84:o.pdpc_q12[3],
            0x456c:o.wb_b_q10<<17,0x4570:o.wb_r_q10<<17}

def main():
    samples=json.load(open(PRIVATE/'samples.json'))['samples']
    corpus=json.load(open(PRIVATE/'E006A-PRIVATE-RECORDS-v2.json',encoding='utf-8-sig'))['records']
    spec=importlib.util.spec_from_file_location('dec',DECODER); dec=importlib.util.module_from_spec(spec); spec.loader.exec_module(dec)
    with tempfile.TemporaryDirectory() as td:
        so=pathlib.Path(td)/'libe012k.so'
        subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-fPIC','-shared',str(pathlib.Path(__file__).with_name('rear-neutral-scalar.c')),'-lm','-o',str(so)],check=True)
        lib=ctypes.CDLL(str(so)); fn=lib.e012k_rear_scalar_calculate; fn.argtypes=[ctypes.POINTER(In),ctypes.POINTER(Out)]; fn.restype=ctypes.c_int
        phase_map=[0,1,2,2]
        totals=[]
        for phase,sidx in enumerate(phase_map):
            s=samples[sidx]
            x=In(); x.demux_gain=s['demux_gain']; x.bls[:]=s['bls']; x.channel[:]=s['channel']; x.awb_g,x.awb_b,x.awb_r=s['pdpc_floats'][2:5]; x.predictive_gain=s['wb'][3]; x.bayer=s['bayer']
            o=Out(); assert fn(ctypes.byref(x),ctypes.byref(o))==0
            expected=pack(o)
            mainrec=next(r for r in corpus if r['n']==phase and r['idx']==1)
            d=dec.decode(bytes.fromhex(mainrec['hex']))
            actual={reg:val for reg,val,_,_ in d['writes'] if reg in expected}
            common=sorted(set(actual)&set(expected)); exact=sum(actual[r]==expected[r] for r in common)
            totals.append({'phase':phase,'semantic_sample_index':sidx,'registers_present':len(common),'registers_exact':exact})
            if exact != len(common): raise SystemExit(f'phase {phase} mismatch')
        safe={'schema':'E012K-private-validation-safe-v1','classification':'PASS','phase_results':totals,
              'register_instances_present':sum(x['registers_present'] for x in totals),
              'register_instances_exact':sum(x['registers_exact'] for x in totals),
              'captured_register_values_emitted':False,'captured_packet_bytes_emitted':False,
              'semantic_inputs_embedded_in_git':False}
        pathlib.Path(__file__).with_name('VALIDATION-SAFE.json').write_text(json.dumps(safe,indent=2)+'\n')
        print(f"E012K_PRIVATE_VALIDATION=PASS exact={safe['register_instances_exact']}/{safe['register_instances_present']}")
if __name__=='__main__': main()
