#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,struct
HERE=Path(__file__).resolve().parent
EK=HERE.parent/'ek-linux-front-awb-otp-read-gate'/'LIVE-EVIDENCE.txt'
RAW=HERE/'AWB-OTP-RAW.bin'
DLL_SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
RAW_SHA=''
FORMATTED=[
    {'available':1,'cct':2850,'rg_bits':0x3f55b56d,'bg_bits':0x3eb8ae2c},
    {'available':1,'cct':5000,'rg_bits':0x3f1765d9,'bg_bits':0x3f1364d9},
]
FACTORS=[
 (0x3f7ebcac,0x3f79a47c),(0x3f7ebcac,0x3f79a47c),(0x3f7ebcac,0x3f79a47c),(0x3f7ebcac,0x3f79a47c),
 (0x3f7f2038,0x3f7a40d6),(0x3f7f2038,0x3f7a40d6),(0x3f7f2038,0x3f7a40d6),
 (0x3f7f66ed,0x3f7b3bff),(0x3f7f66ed,0x3f7b3bff),(0x3f7f66ed,0x3f7b3bff),
]
def f32(x): return struct.unpack('<f',struct.pack('<f',float(x)))[0]
def bits(x): return struct.unpack('<I',struct.pack('<f',f32(x)))[0]
def frombits(x): return struct.unpack('<f',struct.pack('<I',x))[0]
def need(x,m):
    if not x: raise AssertionError(m)
def main():
    raw=RAW.read_bytes(); need(len(raw)==12,'raw length')
    vals=list(struct.unpack('<6H',raw)); need(vals==[854,369,1023,605,589,1020],f'raw u16 drift {vals}')
    decoded=[]
    for i,cct in enumerate((2850,5000)):
        rg=f32(vals[i*3]/1023.0); bg=f32(vals[i*3+1]/1023.0); third=f32(vals[i*3+2]/1023.0)
        exp=FORMATTED[i]
        need(bits(rg)==exp['rg_bits'],f'{cct} RG')
        need(bits(bg)==exp['bg_bits'],f'{cct} BG')
        decoded.append({'cct':cct,'available':1,'raw_u16':vals[i*3:i*3+3],
                        'ratio_bits':{'rg':f'0x{bits(rg):08x}','bg':f'0x{bits(bg):08x}','third':f'0x{bits(third):08x}'}})
    reciprocals=[]
    for rg,bg in FACTORS:
        rr=f32(1.0/frombits(rg)); rb=f32(1.0/frombits(bg))
        reciprocals.append((bits(rr),bits(rb)))
    need(reciprocals[:4]==[(0x3f80a277,0x3f83427b)]*4,'high slots reciprocal')
    need(reciprocals[4:7]==[(0x3f807046,0x3f82f079)]*3,'mid slots reciprocal')
    need(reciprocals[7:]==[(0x3f804cb7,0x3f826d93)]*3,'low slots reciprocal')
    linux_bound=False
    if EK.exists():
        et=EK.read_text(); linux_bound=('status=PASS_LINUX_PHYSICAL_OTP_READ' in et and 'windows_ei_match=byte_exact_12_of_12' in et and 'stream_requested=false' in et)
    out={'schema':'sp11-e003i-ei-front-awb-otp-oracle-v1','status':'PASS_SAME_DEVICE_OTP_AND_FACTOR_TABLE',
         'device_mft_sha256':DLL_SHA,'raw_eeprom_sha256':hashlib.sha256(raw).hexdigest(),
         'raw_window':{'start':'0x941','end_inclusive':'0x94c','bytes':12,'u16_le':vals},
         'formatted_otp':decoded,
         'windows_factor_bits':[{'slot':i,'rg':f'0x{p[0]:08x}','bg':f'0x{p[1]:08x}'} for i,p in enumerate(FACTORS)],
         'reciprocal_scale_bits':[{'slot':i,'rg':f'0x{p[0]:08x}','bg':f'0x{p[1]:08x}'} for i,p in enumerate(reciprocals)],
         'eg_active_scale_bits':{'rg':'0x3f80a277','bg':'0x3f83427b'},
         'raw_read_pre_stream':True,'factor_capture_bounded_stream':True,'golden_returned':True,
         'compute_cal_factors_clean_replay':False,'linux_runtime_eeprom_read_bound':linux_bound}
    (HERE/'RESULT.json').write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))
if __name__=='__main__': main()
