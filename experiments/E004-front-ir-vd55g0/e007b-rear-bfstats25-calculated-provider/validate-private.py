#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import json

D=Path(__file__).resolve().parent
REPO=D.parents[2]
PRIVATE=REPO.parent/"private"/"e006a"/"E006A-PRIVATE-RECORDS-v2.json"
DECODER=D.parent/"e006a-windows-rear-rtcdm-targeted-corpus"/"decode_rear_rtcdm.py"

spec=importlib.util.spec_from_file_location("e006a_decode", DECODER)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
records=json.load(open(PRIVATE,encoding="utf-8-sig"))

REGS=[
0xbc58,0xbc5c,0xbc60,0xbc6c,0xbc70,0xbc74,0xbc78,0xbc7c,0xbc80,
0xbc84,0xbc88,0xbc8c,0xbc90,0xbc94,0xbc98,0xbc9c,0xbca0,0xbca4,
0xbca8,0xbcac,0xbcb0,0xbcb4,0xbcb8,0xbcbc,0xbcc0,0xbcc4,0xbcc8,
0xbccc,0xbcd0]
CFG_BITS=(1<<0)|(1<<8)|(1<<9)|(1<<12)|(1<<13)|(1<<16)|(1<<17)|(1<<21)

def sx(v,bits):
    m=1<<(bits-1)
    v &= (1<<bits)-1
    return v-(1<<bits) if v&m else v

def pack_s6(v):
    return sum((x & 0x3f) << (8*i) for i,x in enumerate(v))

def pack_s16(a,b):
    return (a & 0xffff)|((b & 0xffff)<<16)

def unpack_tail_word(v,count):
    return [(v>>(6*i))&0x1f for i in range(count)]

def pack_tail(v):
    return sum(x<<(6*i) for i,x in enumerate(v))

def repack(vals):
    out={}
    out[0xbc58]=vals[0xbc58]&1
    out[0xbc5c]=vals[0xbc5c]&1
    cfg=vals[0xbc60]
    out[0xbc60]=(1 |
        (((cfg>>8)&1)<<8) | (((cfg>>9)&1)<<9) |
        (((cfg>>12)&1)<<12) | (((cfg>>13)&1)<<13) |
        (((cfg>>16)&1)<<16) | (((cfg>>17)&1)<<17) |
        (((cfg>>21)&1)<<21))

    s6=[]
    for reg,count in ((0xbc6c,4),(0xbc70,4),(0xbc74,4),(0xbc78,1)):
        s6.extend(sx(vals[reg]>>(8*i),6) for i in range(count))
    out[0xbc6c]=pack_s6(s6[0:4])
    out[0xbc70]=pack_s6(s6[4:8])
    out[0xbc74]=pack_s6(s6[8:12])
    out[0xbc78]=pack_s6(s6[12:13])

    qa=[]
    for reg in (0xbc7c,0xbc80,0xbc84,0xbc88,0xbc8c):
        v=vals[reg]
        qa += [sx(v,16),sx(v>>16,16)]
    for i,reg in enumerate((0xbc7c,0xbc80,0xbc84,0xbc88,0xbc8c)):
        out[reg]=pack_s16(qa[i*2],qa[i*2+1])

    qb=[
        sx(vals[0xbc90],16),sx(vals[0xbc90]>>16,16),
        sx(vals[0xbc94],16),
        sx(vals[0xbc98],16),sx(vals[0xbc98]>>16,16),
        sx(vals[0xbc9c],16),sx(vals[0xbc9c]>>16,16),
        sx(vals[0xbca0],16),
        sx(vals[0xbca4],16),sx(vals[0xbca4]>>16,16)]
    out[0xbc90]=pack_s16(qb[0],qb[1])
    out[0xbc94]=qb[2]&0xffff
    out[0xbc98]=pack_s16(qb[3],qb[4])
    out[0xbc9c]=pack_s16(qb[5],qb[6])
    out[0xbca0]=qb[7]&0xffff
    out[0xbca4]=pack_s16(qb[8],qb[9])

    s4=[sx(vals[0xbca8],4),sx(vals[0xbca8]>>4,4)]
    out[0xbca8]=(s4[0]&0xf)|((s4[1]&0xf)<<4)

    for scalar,words in (
        (0xbcac,(0xbcb0,0xbcb4,0xbcb8,0xbcbc)),
        (0xbcc0,(0xbcc4,0xbcc8,0xbccc,0xbcd0))):
        out[scalar]=vals[scalar]&0x1ffff
        for reg,count in zip(words,(5,5,5,2)):
            out[reg]=pack_tail(unpack_tail_word(vals[reg],count))
    return out

records_checked=0
startup_records=0
steady_records=0
register_checks=0
for rec in records["records"]:
    if rec.get("idx")!=1 or not rec.get("complete"):
        continue
    parsed=mod.decode(bytes.fromhex(rec["hex"]))
    vals={r:v for r,v,_off,_kind in parsed["writes"] if r in REGS}
    if not all(r in vals for r in REGS):
        continue
    out=repack(vals)
    assert all(out[r]==vals[r] for r in REGS)
    assert vals[0xbc60] & ~CFG_BITS == 0
    records_checked += 1
    register_checks += len(REGS)
    if rec["n"] < 4:
        startup_records += 1
    else:
        steady_records += 1

assert records_checked >= 20
assert register_checks == records_checked*len(REGS)
safe={
 "schema":"E007b-private-validation-safe-v1",
 "records_checked":records_checked,
 "startup_records_checked":startup_records,
 "steady_records_checked":steady_records,
 "register_roundtrip_checks":register_checks,
 "all_29_words_exact":True,
 "config_unknown_bits_zero":True,
 "raw_register_values_emitted":False,
 "raw_packet_bytes_emitted":False,
}
(D/"PRIVATE-VALIDATION-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
print("E007B_PRIVATE_VALIDATION_PASS")
print(f"records={records_checked} startup={startup_records} steady={steady_records} register_checks={register_checks}")
print("raw_values_emitted=false")
