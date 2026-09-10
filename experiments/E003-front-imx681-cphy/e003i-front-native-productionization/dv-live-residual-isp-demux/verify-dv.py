#!/usr/bin/env python3
from pathlib import Path
import hashlib, importlib.util, json, pefile, struct

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
STATIC=BASE.parent/'e003h-iq-producer-0073-static'
DLL=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll')
TUNING=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamfrontsensor_extension8380.inf_arm64_5a4c66ce4812274e/com.surface.tuned.ffc_imx681.bin')
DLL_SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
TUNING_SHA='2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d'

spec=importlib.util.spec_from_file_location('dv_demux',HERE/'demux_bls.py')
M=importlib.util.module_from_spec(spec); spec.loader.exec_module(M)

def sha(b): return hashlib.sha256(bytes(b)).hexdigest()
def fbits(x): return struct.unpack('<I',struct.pack('<f',float(x)))[0]

assert sha(DLL.read_bytes())==DLL_SHA
assert sha(TUNING.read_bytes())==TUNING_SHA

# Pin active selector proof already emitted by the project decoder.
container=json.loads((STATIC/'imx681-chromatix-container.json').read_text())
fb=container['front_branch']
assert fb['proven_sensor_mode']==2
assert fb['required_ife_modules_usecase_invariant'] is True
demux=fb['effective_required_ife_modules']['demuxblklevel14_ife_v2']
assert demux['symbol_id']==31
assert demux['selector']['mode_name']=='Default'
pg=container['pointer_graph']['demuxblklevel14_ife_v2']
# Walk the only nonempty trigger chain to its 16-byte region.
node=pg
regions=[]
def walk(x):
    if x.get('type')=='region' and x.get('data_bytes')==16: regions.append(x)
    for c in x.get('children',[]): walk(c)
walk(node)
assert len(regions)==1
assert regions[0]['region_summary']['first_floats']==[602.0,593.0,592.0,596.0]

# Pin exact Windows critical bytes/constants.
b=DLL.read_bytes(); pe=pefile.PE(data=b,fast_load=True); base=pe.OPTIONAL_HEADER.ImageBase
def chunk(va,n):
    off=pe.get_offset_from_rva(va-base); return b[off:off+n]
assert sha(chunk(0x180998ef0,0x29c))=='57255c88e4f526cd2c888f5dfd3af7a5444736eec080c5571e1df337697f8627'
assert sha(chunk(0x1800014d0,8))=='5a7c0d8e787755f52c8149240c202b219109509583c7e89c2d800afd856425d4'
assert chunk(0x180999478,8)==bytes.fromhex('f4fdff4100008044')

oracle=json.loads((STATIC/'demux-dgain-oracle.json').read_text())
req6=oracle['windows_frames']['6']
assert req6['dgain_raw']=='0x3f8024b7'
r=M.calculate(req6['dgain_float'])
assert r['isp_gain_bits']==0x3f8024b7
assert r['q10']==[1064,1064,1064,1064]
assert r['reg_3b70']==0x04280428
assert r['reg_3b74']==0x04280428
assert oracle['request6_reproduction']['observed_registers']=={'0x3b70':'0x04280428','0x3b74':'0x04280428'}

# Exercise scaling/clamp domain and determinism without claiming extra Windows samples.
for raw in (0x3f800000,0x3f8024b7,0x40000000,0x41800000,0x42000000):
    g=struct.unpack('<f',struct.pack('<I',raw))[0]
    a=M.calculate(g); c=M.calculate(g)
    assert a==c
    assert all(0<=q<=0x7fff for q in a['q10'])

out={
 'schema':'sp11-e003i-dv-live-residual-isp-demux-v1',
 'status':'PASS',
 'runtime_performed':False,
 'selector':{'sensor_mode':2,'required_ife_usecase_invariant':True,'effective_demux_symbol':31,
             'black_level':[602,593,592,596],'channel_terms':[1.0,1.0,1.0,1.0]},
 'windows':{'dll_sha256':DLL_SHA,'common_setting_rva':'0x998e70','frinta_va':'0x1800014d0',
            'normalization_limit_bits':'0x41fffdf4','q_gain_bits':'0x44800000'},
 'request6':{'isp_gain_bits':'0x3f8024b7','q10':[1064,1064,1064,1064],
             'reg_3b70':'0x04280428','reg_3b74':'0x04280428','byte_exact_register_match':True},
 'next_gate':'feed parent CQ per-generation isp_gain to IQ producer and replace only Demux/BLS 0x3b70/0x3b74 in generated R5/R6 module state',
 'continuous_aec_claimed':False
}
(HERE/'RESULT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print('DV_SELECTOR_SENSOR2_USECASE_INVARIANT=PASS')
print('DV_WINDOWS_REQ6_DEMUX=0x04280428/0x04280428')
print('DV_FRINTA_FLOAT32_PATH=PASS')
print('DV_RUNTIME=0')
print('DV_VERIFY=PASS')
