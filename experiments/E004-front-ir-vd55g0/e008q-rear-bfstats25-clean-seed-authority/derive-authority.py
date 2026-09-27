#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json, struct, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
TUNING=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.surface.tuned.rfc_ov13858.bin")
TUNING_SHA="4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635"
DEC=REPO/"experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static/decode_imx681_chromatix.py"
RT_DEC=REPO/"experiments/E004-front-ir-vd55g0/e006a-windows-rear-rtcdm-targeted-corpus/decode_rear_rtcdm.py"
PRIVATE_A=REPO.parent/"private/e006a/E006A-PRIVATE-RECORDS-v2.json"
PRIVATE_B=REPO.parent/"private/e006b"
DMI_META=REPO/"experiments/E004-front-ir-vd55g0/e006b-windows-rear-dmi-source-payloads/PARTIAL-RESULT.json"

def sha(b:bytes)->str: return hashlib.sha256(b).hexdigest()
def mod(path,name):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s); sys.modules[name]=m
    assert s.loader; s.loader.exec_module(m); return m
def sx(v,bits):
    v &= (1<<bits)-1
    return v-(1<<bits) if v&(1<<(bits-1)) else v

b=TUNING.read_bytes(); assert sha(b)==TUNING_SHA
D=mod(DEC,"e008q_chromatix")
h=D.parse_header(b)
assert h["module_name"]=="com.surface.tuned.rfc_ov13858"
recs,_=D.parse_symbol_table(b,h["sections"][0],h["sections"][1])
assert recs[0xb2]["type"]=="BAF"

# Gamma preset: two valid+32-sample curves. The first is the accepted rear
# startup/steady BF gamma authority.
gamma_raw=D.data_bytes(b,h["sections"][1],recs[0x1bc1])
gamma_words=list(struct.unpack("<66I",gamma_raw))
assert gamma_words[0]==1 and gamma_words[33]==1
gamma0=gamma_words[1:33]
gamma1=gamma_words[34:66]
assert len(gamma0)==len(gamma1)==32

# Filter preset: four [enable, 10 float coefficients, mode, initState-ref]
# blocks. Block 1 reproduces every accepted rear BF register state except
# startup packet0 after Q14 conversion. Titan register A order is a fixed
# permutation of the same ten semantic coefficients.
filter_raw=D.data_bytes(b,h["sections"][1],recs[0x1bc4])
assert len(filter_raw)==4*52
blocks=[]
for i in range(4):
    raw=filter_raw[i*52:(i+1)*52]
    u=struct.unpack("<13I",raw); f=struct.unpack("<13f",raw)
    assert u[0]==1 and u[11]==2
    blocks.append({"coeff":list(f[1:11]),"init_ref":u[12]})
selected=blocks[1]
qb=[round(x*16384.0) for x in selected["coeff"]]
qa=[qb[i] for i in [0,1,2,7,3,4,5,6,8,9]]

# Coring preset: two 20-word records. For the accepted normal rear state the
# first record maps directly to [17 lane thresholds, scalar] after its valid
# word. The final word is retained only as tuning metadata and is not claimed
# by this checkpoint as a Titan register producer.
coring_raw=D.data_bytes(b,h["sections"][1],recs[0x1bc9])
coring_words=list(struct.unpack("<40I",coring_raw))
c0=coring_words[:20]
assert c0[0]==1
tail_lanes=c0[1:18]
tail_scalar=c0[18]
tail_extra=c0[19]

# Private Windows validation: register values never leave this process.
RT=mod(RT_DEC,"e008q_rt")
priv=json.load(open(PRIVATE_A,encoding="utf-8-sig"))["records"]
reg_seen=reg_filter_match=reg_tail_match=0
for rec in priv:
    if rec.get("idx")!=1 or not rec.get("complete"): continue
    vals={r:v for r,v,*_ in RT.decode(bytes.fromhex(rec["hex"]))["writes"]}
    if 0xbcd0 not in vals: continue
    reg_seen += 1
    qa_obs=[]
    for reg in [0xbc7c,0xbc80,0xbc84,0xbc88,0xbc8c]:
        qa_obs += [sx(vals[reg],16),sx(vals[reg]>>16,16)]
    qb_obs=[sx(vals[0xbc90],16),sx(vals[0xbc90]>>16,16),sx(vals[0xbc94],16),
            sx(vals[0xbc98],16),sx(vals[0xbc98]>>16,16),sx(vals[0xbc9c],16),
            sx(vals[0xbc9c]>>16,16),sx(vals[0xbca0],16),sx(vals[0xbca4],16),
            sx(vals[0xbca4]>>16,16)]
    if qa_obs==qa and qb_obs==qb:
        reg_filter_match += 1
    def tail(scalar, regs):
        lanes=[]
        for reg,count in zip(regs,(5,5,5,2)):
            lanes += [(vals[reg]>>(6*i))&0x1f for i in range(count)]
        return vals[scalar]&0x1ffff,lanes
    t0=tail(0xbcac,[0xbcb0,0xbcb4,0xbcb8,0xbcbc])
    t1=tail(0xbcc0,[0xbcc4,0xbcc8,0xbccc,0xbcd0])
    if t0==(tail_scalar,tail_lanes) and t1==(tail_scalar,tail_lanes):
        reg_tail_match += 1

assert reg_seen==35
assert reg_filter_match==34 and reg_tail_match==34

# Private DMI validation for gamma. Exact payload bytes are read only to
# compare semantic samples; no raw payload is written to the safe result.
meta=json.load(open(DMI_META))
files={"startup1":"E006B-START1-SOURCE.bin",
       "startup2":"E006B-START2-SOURCE.bin",
       "startup3":"E006B-START3-SOURCE.bin",
       "steady_ac8":"E006B-STEADY-AC8-SOURCE.bin"}
gamma_seen=gamma_match=0
for cap in meta["captured"]["captures"]:
    lab=cap["label"]
    if lab not in files: continue
    item=next((x for x in cap["payloads"]
               if x["dmi_register_offset"]=="0xbc08" and x["selector"]==2),None)
    if item is None: continue
    blob=(PRIVATE_B/files[lab]).read_bytes()
    base=int(cap["captured_source_window_base"],16)
    rel=int(item["source_offset"],16)-base
    payload=blob[rel:rel+item["payload_bytes"]]
    words=struct.unpack("<32I",payload)
    samples=[w&0x3fff for w in words]
    gamma_seen += 1
    gamma_match += samples==gamma0
assert gamma_seen==4 and gamma_match==4

safe={
 "schema":"E008q-rear-bfstats25-clean-seed-authority-v1",
 "status":"PASS_PARTIAL_CLEAN_BF_AUTHORITY",
 "source":{
   "module":"com.surface.tuned.rfc_ov13858",
   "tuning_sha256":TUNING_SHA,
   "baf_root_symbol":"0xb2",
   "gamma_preset_symbol":"0x1bc1",
   "filter_preset_symbol":"0x1bc4",
   "coring_preset_symbol":"0x1bc9"
 },
 "gamma":{
   "selected_curve_index":0,
   "samples":32,
   "private_payloads_checked":gamma_seen,
   "private_exact_matches":gamma_match,
   "second_curve_distinct":gamma1!=gamma0
 },
 "filter":{
   "selected_block_index":1,
   "coefficient_count":10,
   "quantization":"round(float * 16384)",
   "register_a_reorder":[0,1,2,7,3,4,5,6,8,9],
   "register_b_order":[0,1,2,3,4,5,6,7,8,9],
   "private_register_records_checked":reg_seen,
   "private_exact_matches":reg_filter_match,
   "startup_packet0_is_distinct":True
 },
 "coring":{
   "selected_record_index":0,
   "lane_count":17,
   "tuning_scalar":tail_scalar,
   "tuning_extra_field":tail_extra,
   "private_register_records_checked":reg_seen,
   "private_exact_matches":reg_tail_match,
   "startup_packet0_is_distinct":True
 },
 "scope":{
   "closes_standard_packet1_plus_filter_coefficients":True,
   "closes_standard_packet1_plus_gamma":True,
   "closes_standard_packet1_plus_coring":True,
   "does_not_close_packet0_filter_seed":True,
   "does_not_close_feature_enable_or_bank_policy":True,
   "does_not_close_signed4_shift_producer":True,
   "does_not_close_25_roi_generator":True
 },
 "private_windows_register_values_emitted":False,
 "private_windows_dmi_bytes_emitted":False,
 "runtime_actions_performed":False
}
(HERE/"AUTHORITY-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
print("E008Q_AUTHORITY_PASS gamma=4/4 filter=34/35 tail=34/35 packet0_distinct=true")
