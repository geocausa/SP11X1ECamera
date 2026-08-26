#!/usr/bin/env python3
"""Extract a conservative hardware summary from QTI Parameter Parser v3 sensor-module bins.

Only fields whose layout has been mechanically cross-checked against the public CamX sensor
schema and repeated SP11 structures are emitted. Unknown fields remain unknown rather than guessed.
"""
from __future__ import annotations
import argparse, importlib.util, json, struct
from pathlib import Path

HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('qti_parameter_bin', HERE/'qti_parameter_bin.py')
qti=importlib.util.module_from_spec(sp); sp.loader.exec_module(qti)
I2C={0:'STANDARD',1:'FAST',2:'FAST_PLUS',3:'CUSTOM'}

def u32s(raw): return list(struct.unpack('<'+'I'*(len(raw)//4),raw))
def entry_map(o): return {e['id']:e for e in o['entries']}
def raw(e): return bytes.fromhex(e['raw_hex'])

def scalar(e):
    b=raw(e)
    if not b: return None
    if len(b)==1:return b[0]
    if len(b)==2:return int.from_bytes(b,'little')
    if len(b)==4:return int.from_bytes(b,'little')
    return None

def reg_list(e, ids):
    b=raw(e)
    if len(b)%40: raise ValueError(f'regSetting id {e["id"]}: size not multiple of 40')
    out=[]
    for off in range(0,len(b),40):
        w=struct.unpack('<10I',b[off:off+40])
        data=scalar(ids.get(w[4],{'raw_hex':''})) if w[4] in ids else None
        delay=scalar(ids.get(w[9],{'raw_hex':''})) if w[9] in ids else None
        out.append({'address':w[2], 'data':data, 'addr_type':w[5], 'data_type':w[6],
                    'operation':w[7], 'delay_us':delay, 'slave_override':w[0] or None})
    return out

def summarize(path):
    o=qti.parse(path); ids=entry_map(o); drv=raw(ids[1]); w=u32s(drv)
    # Layout cross-checked on all three SP11 files: fixed slave-info header then power arrays.
    probe={'sensor_name':next((e['text'] for e in o['entries'] if e['name']=='sensorName' and e['text']),None),
           'slave_address_8bit':w[11], 'slave_address_7bit':w[11]>>1,
           'reg_addr_type':w[12], 'reg_data_type':w[13], 'sensor_id_reg':w[14],
           'sensor_id':w[15], 'sensor_id_mask':w[16], 'i2c_frequency_mode':w[17],
           'i2c_frequency_name':I2C.get(w[17],f'UNKNOWN_{w[17]}'),
           'power_up_count':w[18], 'power_down_count':w[20]}
    # stream on/off/group hold arrays: repeated count/ref pairs at fixed layout in this v3.4 schema.
    lifecycle={}
    for label,ci,ri in [('stream_on',90,91),('stream_off',92,93),('group_hold_on',94,95),('group_hold_off',96,97)]:
        cnt=w[ci]; ref=w[ri]; e=ids.get(ref)
        if cnt and e and e['name']=='regSetting': lifecycle[label]=reg_list(e,ids)[:cnt]
        else: lifecycle[label]=[]
    # Module configuration: use named leaf fields only; absent override means sensor-driver value applies.
    def last_named(name):
        xs=[e for e in o['entries'] if e['name']==name]
        return xs[-1] if xs else None
    lane=last_named('laneAssign'); combo=last_named('isComboMode'); cdc=last_named('cphyDphyComboMode')
    module={'lane_assign':scalar(lane) if lane else None,
            'is_combo_mode':scalar(combo) if combo else None,
            'cphy_dphy_combo_mode':scalar(cdc) if cdc else None}
    # Resolution records are fixed 252-byte elements in these SP11 v3.4 files.
    rd=next(e for e in o['entries'] if e['name']=='resolutionData' and e['payload_size'])
    rdb=raw(rd); modes=[]
    if len(rdb)%252: raise ValueError('unexpected resolutionData element size')
    streams=[e for e in o['entries'] if e['name']=='streamConfiguration' and e['payload_size']]
    for i in range(len(rdb)//252):
        b=rdb[i*252:(i+1)*252]; rw=u32s(b)
        sc=raw(streams[i]); sw=u32s(sc)
        fps=struct.unpack_from('<d',b,0x40)[0]
        vc=scalar(ids.get(sw[1])) if sw[1] in ids else None
        modes.append({'index':i,'vc':vc, 'data_type':sw[2], 'x_start':sw[3], 'y_start':sw[4],
                      'width':sw[5], 'height':sw[6], 'bit_width':sw[7],
                      'line_length_pixel_clock':rw[9], 'frame_length_lines':rw[10],
                      'min_horizontal_blanking':rw[11], 'min_vertical_blanking':rw[12],
                      'output_pixel_clock_hz':rw[13], 'horizontal_binning':rw[14],
                      'vertical_binning':rw[15], 'frame_rate':fps})
    return {'file':Path(path).name,'file_size':o['size'],'probe':probe,'module':module,'lifecycle':lifecycle,'modes':modes}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('file'); a=ap.parse_args(); print(json.dumps(summarize(a.file),indent=2))
if __name__=='__main__': main()
