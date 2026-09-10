#!/usr/bin/env python3
"""Verify the omitted Windows pre-publication cap stage against a pinned PE."""
from pathlib import Path
import hashlib, json, struct, subprocess
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
DLL=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll')
EXPECTED='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
b=DLL.read_bytes()
assert hashlib.sha256(b).hexdigest()==EXPECTED
pe=struct.unpack_from('<I',b,60)[0]
count=struct.unpack_from('<H',b,pe+6)[0]
opt=struct.unpack_from('<H',b,pe+20)[0]
sections=[]
for i in range(count):
    p=pe+24+opt+40*i
    vs,va,sz,raw=struct.unpack_from('<IIII',b,p+8)
    sections.append((va,sz,raw))
def word(rva):
    for va,size,raw in sections:
        if va<=rva and rva+4<=va+size:
            return struct.unpack_from('<I',b,raw+rva-va)[0]
    raise AssertionError(hex(rva))
def op(rva,expected):
    assert word(rva)==expected,hex(rva)
def bl(rva,target):
    w=word(rva)
    assert w>>26==0b100101
    imm=w&0x3ffffff
    if imm&0x2000000: imm-=0x4000000
    assert rva+imm*4==target,(hex(rva),hex(target))
bl(0x3ce03c,0x3d33e0)
bl(0x3b63f0,0x3cdf50)
op(0x3b44d0,0xf94006e8) # input+8 -> x8
op(0x3b44d8,0xf9004ec8) # x8 -> convergence+0x98
op(0x374f04,0xf9065500) # pre-conv bridge return -> controller+0x14ca8
op(0x389efc,0x911a2260) # bridge returns child+0x688
op(0x3ce040,0xbd40da70) # cap-adjusted PredGain is published only after call
op(0x3ce044,0xbd007290)
# Exact per-lane lower/upper bound loads in the unconditional cap tail.
loads=[
 (0x3d3764,0xf9400d09,0x18),(0x3d377c,0xf9402108,0x40),
 (0x3d3790,0xf9403508,0x68),(0x3d37a4,0xf9404908,0x90),
 (0x3d37b8,0xf9405d09,0xb8),(0x3d37d0,0xf9407108,0xe0),
 (0x3d37e4,0xf9408508,0x108),(0x3d37f8,0xf9409908,0x130),
 (0x3d380c,0xf940ad09,0x158),(0x3d3824,0xf940c108,0x180),
 (0x3d3838,0xf940d508,0x1a8),(0x3d384c,0xf940e908,0x1d0),
 (0x3d3864,0xf940fd08,0x1f8),(0x3d3878,0xf9411108,0x220)]
for addr,instruction,_ in loads: op(addr,instruction)
op(0x3d3770,0x9a889129) # max(short, short_min)
op(0x3d3784,0x9a883128) # min(short, short_max)
op(0x3d38a0,0xf900026a) # ordered Short publication
op(0x3d38c0,0xf9000e6a) # S1 = ordered Short
op(0x3d38e8,0x1e301a31) # float32 Safe / Short
op(0x3d3900,0x1e313e10) # PredGain limited to ratio
# A pre-tail path additionally scales Short/S1..S4 under specific conditions:
# it must be recovered with its trigger/history inputs, not replaced by clamp().
op(0x3d35f4,0x54000b69)
op(0x3d360c,0x54000aa1)
op(0x3d3620,0x1e281a10)
op(0x3d3624,0x1e301a30)
op(0x3d3628,0x9e390208)
native=(BASE/'dj-native-aec-request4-warmup-rebase/native-aec-request-loop.c').read_text()
middle=native.split('rc = e003i_converge_front_preview_unlocked_qword_history',1)[1].split('rc = e003i_t681_preview_arbitrate',1)[0]
assert middle.strip()=='(&ci,\n                                                             &out->convergence);\n    if (rc != 0)\n        return -20 + rc;'
result={
 'schema':'sp11-e003i-dl-missing-cap-stage-v1','status':'PASS_STATIC_OMISSION_PROOF',
 'dll_sha256':EXPECTED,
 'call_chain':['RunConvProcesss 0x3b63f0 -> PopulateOutput 0x3cdf50','PopulateOutput 0x3ce03c -> CapExposure 0x3d33e0'],
 'bounds_provenance':['runConvergence bridge return stored controller+0x14ca8 (input+8)','RunConvProcesss input+8 stored convergence+0x98','bridge returns child+0x688 with seven 0x50-byte min/max records'],
 'bounds_offsets':[{'lane':i,'min':hex(0x18+0x50*i),'max':hex(0x40+0x50*i)} for i in range(7)],
 'additional_semantics':['conditional Safe-over-maximum Short rescaling and history snapping','per-lane integer min/max','Short/Long/Safe and S1..S4 ordering','PredGain <= float32(Safe)/float32(Short)'],
 'native_stage_present':False,'production_fix_implemented':False,
 'dc_controller_cap_flag_does_not_disable_this_internal_cap':True,
 'dg_postconvergence_injection_occurs_after_this_stage':True,
 'unresolved':['exact ordinary request-local seven min/max values and common +0x230 limit','ordinary branch inputs for internal cap and bound preparation','differential full-stage replay against matching Windows pre/post values'],
}
(HERE/'CAP-STAGE-RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print('PINNED_WINDOWS_CAP_CALL=PASS\nSEVEN_LANE_CAP_BOUNDS=PASS\nNATIVE_CAP_STAGE=OMITTED\nCAP_STAGE_VERIFY=PASS')
