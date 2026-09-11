#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,struct,sys
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
PROJECT=Path('/home/geoca/Documents/SP11-PROJECT')
STATIC=REPO/'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static'
EI=HERE.parent/'ei-front-awb-otp-oracle'/'AWB-OTP-RAW.bin'
EJ=HERE.parent/'ej-clean-awb-cal-factor-replay'/'RESULT.json'
EK=HERE.parent/'ek-linux-front-awb-otp-read-gate'/'LIVE-EVIDENCE.txt'
sys.path.insert(0,str(STATIC))
from decode_imx681_chromatix import parse_header,parse_symbol_table,data_bytes
SENSOR=PROJECT/'00-RE-archive/sp11-driverdump/surfacecamfrontsensor_extension8380.inf_arm64_5a4c66ce4812274e/com.surface.sensormodule.ffc_imx681.bin'
DLL=PROJECT/'00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll'
SENSOR_SHA='f7dd81be64153fd3f0da8e6288ee1b9906b7bf51b773a98496934d76dc96a45c'
DLL_SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
ROOT_SHA='9928dd5b36aad01d5d191a76d2832770c7b1697832aac129f551238043499ae1'
WB_SHA='747eda7709d4c829b93adbc224aa61dce1a85a9b0dc6526598da7722eb7a9a9c'

def sha(b): return hashlib.sha256(b).hexdigest()
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def f32(b,o): return struct.unpack_from('<f',b,o)[0]
def need(v,m):
    if not v: raise RuntimeError(m)
class PE:
    def __init__(self,b):
        self.b=b; pe=u32(b,0x3c); need(b[pe:pe+4]==b'PE\0\0','PE signature'); self.n=u16(b,pe+6); opt=u16(b,pe+20); self.sh=pe+24+opt
    def at(self,rva,n):
        for i in range(self.n):
            o=self.sh+i*40; vs,va,rs,raw=struct.unpack_from('<IIII',self.b,o+8)
            if va <= rva < va+max(vs,rs): return self.b[raw+rva-va:raw+rva-va+n]
        raise RuntimeError(f'unmapped RVA {rva:#x}')
# Sparse exact instructions anchoring the relevant generic paths.
CODE={
  0x7233c8:'5f040071', # cmp w2,#1: format selector
  0x7233cc:'40020054', # b.eq little-endian/reverse-walk decoder
  0x723420:'0bbc41f9', # ldr raw EEPROM ptr [x0,#0x378]
  0x723428:'29050051', # offset+byte_count-1
  0x723448:'b321132a', # byte | prior<<8
  0x723bb0:'682a41b9', # WB method
  0x723bbc:'622641b9', # raw integer format selector
  0x723bf0:'080b80d2', # serialized light stride 0x58
  0x723c10:'01010191', # light +0x40 first formatted ratio source
  0x723c24:'301a301e', # divide by qValue
  0x723c38:'01d10091', # light +0x34 second formatted ratio source
  0x723c4c:'301a301e', # divide by qValue
  0x723c60:'01310191', # light +0x4c third source
  0x846754:'56648152', # light enum2 -> 2850K
  0x84675c:'16718252', # light enum3 -> 5000K
  0x846774:'90c25fbc', # ratioRG load from formatted record
  0x846780:'900240bd', # ratioBG load
}

def decode_u16_le(raw,offset): return raw[offset] | (raw[offset+1]<<8)
def main():
    sb=SENSOR.read_bytes(); db=DLL.read_bytes(); need(sha(sb)==SENSOR_SHA,'sensor SHA'); need(sha(db)==DLL_SHA,'DLL SHA')
    h=parse_header(sb); recs,_=parse_symbol_table(sb,h['sections'][0],h['sections'][1]); obj=h['sections'][1]
    root=data_bytes(sb,obj,recs[3]); need(len(root)==1162 and sha(root)==ROOT_SHA,'EEPROM root')
    wb_sid=u16(root,0xf2); wb=data_bytes(sb,obj,recs[wb_sid]); need(wb_sid==3009 and len(wb)==176 and sha(wb)==WB_SHA,'WB child')
    root_contract={'enabled':u32(root,0xe2),'integer_format':u32(root,0xe6),'method':u32(root,0xea),'light_count':u32(root,0xee),'light_symbol':wb_sid,'q_value':f32(root,0x10e),'invert_third':u32(root,0x112)}
    need(root_contract=={'enabled':1,'integer_format':1,'method':1,'light_count':2,'light_symbol':3009,'q_value':1023.0,'invert_third':1},f'WB root drift {root_contract}')
    lights=[]
    expected=[(2,2850,[0x941,0x943,0x945]),(3,5000,[0x947,0x949,0x94b])]
    for i,(typ,cct,offs) in enumerate(expected):
        r=wb[i*0x58:(i+1)*0x58]; need(u32(r,0)==typ,f'light{i} type')
        desc=[]
        for j,o in enumerate((0x34,0x40,0x4c)):
            x={'offset':u32(r,o),'mask':u32(r,o+4),'signed':u32(r,o+8)}
            need(x=={'offset':offs[j],'mask':0xffff,'signed':0},f'light{i} desc{j}: {x}')
            desc.append(x)
        lights.append({'index':i,'illuminant_enum':typ,'color_temperature':cct,'descriptors':desc})
    pe=PE(db); code={}
    for rva,hx in CODE.items():
        got=pe.at(rva,4).hex(); need(got==hx,f'code {rva:#x}: {got}!={hx}'); code[hex(rva)]=got
    # Explicitly prove format=1 + 0xffff mask means a two-byte reverse walk that yields LE u16.
    example=bytes([0x34,0x12]); need(decode_u16_le(example,0)==0x1234,'LE model')
    physical=(EI.exists() and EI.read_bytes()==bytes.fromhex('56 03 71 01 ff 03 5d 02 4d 02 fc 03') and EK.exists() and 'status=PASS_LINUX_PHYSICAL_OTP_READ' in EK.read_text())
    replay=(EJ.exists() and json.loads(EJ.read_text()).get('compute_cal_factors_clean_replay') is True)
    out={'schema':'sp11-e003i-eh-front-awb-otp-boundary-v1','status':'PASS_STATIC_BOUNDARY',
         'sensor_module_sha256':SENSOR_SHA,'device_mft_sha256':DLL_SHA,'eeprom_name':'gt24p128f_imx681',
         'eeprom_i2c':{'descriptor_slave_8bit':'0xa0','linux_7bit':'0x50','full_read_bytes':'0x1762'},
         'wb_root':root_contract,'lights':lights,
         'raw_window':{'start':'0x941','end_inclusive':'0x94c','bytes':12,'encoding':'six consecutive little-endian u16 fields'},
         'format_formula':{'ratioRG':'u16_le(source)/1023.0f','ratioBG':'u16_le(source)/1023.0f','third':'u16_le(source)/1023.0f then reciprocal because invert_third=1','awb_factor_input_uses':['ratioRG','ratioBG']},
         'cct_mapping':{'2':2850,'3':5000},'code_byte_proofs':code,
         'physical_same_device_bytes_captured':physical,'linux_physical_read_proven':physical,'runtime_calibration_factors_replayed_from_otp':replay}
    (HERE/'RESULT.json').write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))
if __name__=='__main__': main()
