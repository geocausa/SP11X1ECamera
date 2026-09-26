#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, math, struct

D=Path(__file__).resolve().parent
SAFE=json.loads((D/"TUNING-SAFE.json").read_text())
P=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.surface.tuned.rfc_ov13858.bin")
b=P.read_bytes()
assert hashlib.sha256(b).hexdigest()==SAFE["source"]["sha256"]
assert b.startswith(b"QTI Chromatix Header")
assert struct.unpack_from("<I",b,0x1c)[0]==len(b)-4
header_bytes=struct.unpack_from("<I",b,0xa0)[0]
nsec=struct.unpack_from("<I",b,0xa4)[0]
assert header_bytes==0xa8 and nsec==3
sec=[]
for i in range(3):
    tag,off,size=struct.unpack_from("<III",b,header_bytes+i*12)
    assert tag==i
    sec.append((off,size))
sym_off,sym_size=sec[0]
obj_off,obj_size=sec[1]
assert sym_size%56==0
found=[]
revision=None
for off in range(sym_off,sym_off+sym_size,56):
    sid=struct.unpack_from("<I",b,off)[0]
    typ=b[off+4:off+36].split(b"\0",1)[0].decode("ascii","replace")
    version,mode_id,mode_symbol_id,data_offset,data_bytes=struct.unpack_from("<5I",b,off+36)
    if typ=="cst12_ife":
        found.append((sid,version,mode_id,mode_symbol_id,data_offset,data_bytes))
    if sid==SAFE["source"]["revision_symbol_id"]:
        revision=(typ,data_bytes)
assert len(found)==1
sid,version,mode_id,mode_symbol_id,data_offset,data_bytes=found[0]
assert sid==SAFE["source"]["cst12_ife_symbol_id"]
assert version&0xffff==SAFE["source"]["version_major"]
assert version>>16==SAFE["source"]["version_minor"]
assert mode_id==SAFE["source"]["mode_id"]
assert mode_symbol_id==SAFE["source"]["mode_symbol_id"]
assert data_bytes==SAFE["source"]["cst12_ife_data_bytes"]
assert obj_off+data_offset==SAFE["source"]["cst12_ife_abs_offset"]
assert revision==("revision",2)
raw=b[obj_off+data_offset:obj_off+data_offset+data_bytes]
prefix=struct.unpack_from("<6I",raw,0)
assert prefix[:4]==(1,1,2,0)
assert prefix[4]==SAFE["source"]["revision_reference_kind"]
assert prefix[5]==SAFE["source"]["revision_symbol_id"]
assert SAFE["source"]["reserve_offset"]==24 and SAFE["source"]["reserve_bytes"]==84
assert list(struct.unpack_from("<3I",raw,24))==SAFE["reserve"]["c_x0"]
assert list(struct.unpack_from("<3I",raw,36))==SAFE["reserve"]["c_x1"]
m=list(struct.unpack_from("<9f",raw,48))
assert m==SAFE["reserve"]["m_float32"]
assert list(struct.unpack_from("<3I",raw,84))==SAFE["reserve"]["o"]
assert list(struct.unpack_from("<3i",raw,96))==SAFE["reserve"]["s"]

def roundf_away(x):
    return math.floor(x+0.5) if x>=0 else math.ceil(x-0.5)
q=[roundf_away(x*1024.0) for x in m]
assert q==SAFE["reserve"]["m_q10_roundf"]
print("E006R_TUNING_SOURCE_PASS")
print("rear_cst12_ife=symbol28 version1.2 reserve_bytes=84 q10_matrix_exact")
