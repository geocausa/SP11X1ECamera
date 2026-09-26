#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,struct

D=Path(__file__).resolve().parent
T=json.loads((D/"TUNING-SAFE.json").read_text())
V=json.loads((D/"VALIDATION-SAFE.json").read_text())
S=(D/"camss-e006t-small-iq.inc").read_text()

assert T["schema"]=="E006t-rear-small-iq-tuning-safe-v1"
assert T["source"]["sha256"]=="4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635"
expected={
 "BAYER_GTM101":("bgtm10_ife_v2",22,"1.0",52),
 "BAYER_LTM101":("bltm10_ife_v2",25,"1.0",740),
 "LCAC111":("lcac11_ife_v2",40,"1.1",52),
 "UV_GAMMA101":("uvg10_ife_v2",44,"1.0",48),
}
for x in T["records"]:
    typ,sid,ver,n=expected[x["owner"]]
    assert (x["type"],x["symbol_id"],x["version"],x["data_bytes"])==(typ,sid,ver,n)
    assert x["mode_id"]==1 and x["mode_symbol_id"]==2
    assert x["serialized_enable_word_offset"]==0 and x["serialized_enable"]==0
assert {x["owner"] for x in T["records"]}==set(expected)
assert T["raw_windows_command_values_committed"] is False

P=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.surface.tuned.rfc_ov13858.bin")
b=P.read_bytes()
assert hashlib.sha256(b).hexdigest()==T["source"]["sha256"]
hb,nsec=struct.unpack_from("<II",b,0xa0)
secs=[struct.unpack_from("<III",b,hb+i*12) for i in range(nsec)]
sym_off,sym_size=secs[0][1],secs[0][2]
obj_off=secs[1][1]
seen={}
for off in range(sym_off,sym_off+sym_size,56):
    sid=struct.unpack_from("<I",b,off)[0]
    typ=b[off+4:off+36].split(b"\0",1)[0].decode("ascii","replace")
    ver,mode,mode_sym,data_off,data_bytes=struct.unpack_from("<5I",b,off+36)
    if typ in {v[0] for v in expected.values()}:
        enable=struct.unpack_from("<I",b,obj_off+data_off)[0]
        seen[typ]=(sid,ver&0xffff,ver>>16,mode,mode_sym,data_bytes,enable)
for owner,(typ,sid,ver,data_bytes) in expected.items():
    maj,minr=map(int,ver.split("."))
    assert seen[typ]==(sid,maj,minr,1,2,data_bytes,0)

assert V["schema"]=="E006t-rear-small-iq-private-semantic-validation-v1"
assert V["startup_phase"]==0
assert all(x["final_active_enabled"] is False for x in V["families"])
assert V["other_startup_phases_emit_these_registers"] is False
assert V["raw_register_values_committed"] is False
assert V["raw_packet_bytes_committed"] is False
ltm=next(x for x in V["families"] if x["owner"]=="BAYER_LTM101")
assert ltm["enabled_path_has_additional_config_bits"] is True

owners=json.loads((D.parent/"e006l-rear-startup-register-ownership"/"STARTUP-REGISTER-OWNER-MAP.json").read_text())
want={"BAYER_GTM101":0x4d60,"BAYER_LTM101":0x5260,"LCAC111":0x5460,"UV_GAMMA101":0x6360}
for owner,reg in want.items():
    got={int(x["register"],16) for x in owners["startup_only"] if x["owner"]==owner}
    assert got=={reg}

for token in [
 "e006t_disabled_word","e006t_bayer_gtm101_lookup","e006t_bayer_ltm101_lookup",
 "e006t_lcac111_lookup","e006t_uv_gamma101_lookup",
 "e006t_bayer_gtm101_recipe","e006t_bayer_ltm101_recipe",
 "e006t_lcac111_recipe","e006t_uv_gamma101_recipe","-EOPNOTSUPP"
]:
    assert token in S

print("E006T_VERIFY_PASS")
print("small_iq_regs=4 startup0_active_disabled=4/4")
print("rear_tuning=bgtm/bltm/lcac/uvg IFE-v2 enable0")
print("enabled_paths=explicitly_unsupported_not_guessed")
print("raw_windows_command_values=false")
