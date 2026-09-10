#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib,importlib.util,json,struct,tempfile

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
DS=BASE/'ds-live-iq-producer-awb-hold/live-iq-producer.py'
DW=HERE/'live-iq-producer.py'
DV=BASE/'dv-live-residual-isp-demux/demux_bls.py'
DEFAULT_DT=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-dt/attempt1-six-frame-pass-20260910T2052/runtime-output')
GAIN_BITS={1:0x3f80397b,2:0x3f80216a,3:0x3f801646}
OLD_DT_CAP={5:'6e6eaa1ab014a1c9c86b669452f7cd64c64040b74186ae357c8ef6daf357d802',
            6:'d6bea8a77e7d67a3e9e082b8a092e201e5c9f2419658b061326c63295966107e'}

def load(p,n):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def fb(u): return struct.unpack('<f',struct.pack('<I',u))[0]
def sha(b): return hashlib.sha256(bytes(b)).hexdigest()

def sections(cap):
    n=struct.unpack_from('<I',cap,20)[0]
    out=[]
    for i in range(n):
        typ,idx,off,size=struct.unpack_from('<IIII',cap,64+i*16)
        out.append((typ,idx,off,size,cap[off:off+size]))
    return out

def assert_only_demux_diff(old,new,expected70,expected74):
    so=sections(old); sn=sections(new)
    assert [(a,b,c,d) for a,b,c,d,_ in so]==[(a,b,c,d) for a,b,c,d,_ in sn]
    changed=[]
    for (typ,idx,off,size,bo),(_,_,_,_,bn) in zip(so,sn):
        if bo!=bn: changed.append((typ,idx,off,size,bo,bn))
    assert len(changed)==1
    typ,idx,off,size,bo,bn=changed[0]
    assert (typ,idx,size)==(4,0,0x120)
    diff=[i for i,(a,b) in enumerate(zip(bo,bn)) if a!=b]
    assert diff and all(4<=i<12 for i in diff),diff
    r70,r74=struct.unpack_from('<II',bn,4)
    assert (r70,r74)==(expected70,expected74)
    assert bo[:4]==bn[:4] and bo[12:]==bn[12:]
    return {'section_type':typ,'section_index':idx,'capsule_offset':off,
            'module_diff_byte_offsets':diff,
            'old_regs':[f'0x{x:08x}' for x in struct.unpack_from('<II',bo,4)],
            'new_regs':[f'0x{r70:08x}',f'0x{r74:08x}']}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--dt-archive',type=Path,default=DEFAULT_DT);ap.add_argument('--manifest',type=Path,default=HERE/'RESULT.json');a=ap.parse_args()
    DSmod=load(DS,'dw_ds'); DWmod=load(DW,'dw_new'); DVmod=load(DV,'dw_dv')
    with tempfile.TemporaryDirectory(prefix='e003i-dw-proof-') as td:
        td=Path(td); old=DSmod.Producer(td/'ds'); new=DWmod.Producer(td/'dw')
        rows=[]; caps_old={};caps_new={};diffs={}
        for gen in (1,2,3):
            s=(a.dt_archive/'producer'/f'STATS3A-G{gen}.bin').read_bytes()
            t=(a.dt_archive/'producer'/f'TLBG-G{gen}.bin').read_bytes()
            gain=fb(GAIN_BITS[gen])
            ro,co,_=old.process(s,t)
            rn,cn,_=new.process(s,t,gain)
            assert ro['generation']==rn['generation']==gen
            for k in ('measured_luma_bits','lux_bits','fresh_cct_bits','final_xy_bits','final_cct_bits','published_cct','p01','valid','awb_hold_previous'):
                assert ro[k]==rn[k],(gen,k,ro[k],rn[k])
            # Dynamic LSC/Tintless state must remain exactly unchanged; timing fields are observational.
            lso={k:v for k,v in ro['lsc'].items() if not k.endswith('_ms')}
            lsn={k:v for k,v in rn['lsc'].items() if not k.endswith('_ms')}
            assert lso==lsn,(gen,lso,lsn)
            assert rn['cq_isp_gain_bits']==f'0x{GAIN_BITS[gen]:08x}'
            if gen in (2,3):
                req=gen+3; caps_old[req]=co;caps_new[req]=cn
                assert sha(co)==OLD_DT_CAP[req]
                dm=DVmod.calculate(gain)
                assert rn['demux_bls']['reg_3b70']==f"0x{dm['reg_3b70']:08x}"
                assert rn['demux_bls']['reg_3b74']==f"0x{dm['reg_3b74']:08x}"
                diffs[req]=assert_only_demux_diff(co,cn,dm['reg_3b70'],dm['reg_3b74'])
            rows.append({'generation':gen,'gain_bits':f'0x{GAIN_BITS[gen]:08x}','old_capsule':None if co is None else sha(co),'new_capsule':None if cn is None else sha(cn),'demux':rn['demux_bls']})
        assert rows[1]['demux']['reg_3b70']=='0x04280428' and rows[1]['demux']['reg_3b74']=='0x04280427'
        assert rows[2]['demux']['reg_3b70']=='0x04270427' and rows[2]['demux']['reg_3b74']=='0x04280427'
        result={'schema':'sp11-e003i-dw-iq-producer-live-cq-demux-proof-v1','status':'PASS','runtime_performed':False,
                'source':'preserved DT attempt1 G1..G3 replay; CQ gain bits independently replayed from same stats',
                'gain_bits':{str(k):f'0x{v:08x}' for k,v in GAIN_BITS.items()},
                'rows':rows,'capsule_diff':{str(k):v for k,v in diffs.items()},
                'all_non_demux_state_unchanged':True,
                'live_mode_enabled':False,
                'next_gate':'DX generation-tagged parent AEC/CQ gain pipe to producer',
                'continuous_aec_claimed':False}
        a.manifest.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        print('DW_DT_G1_G3_AWB_LSC_UNCHANGED=PASS')
        print('DW_R5_DEMUX=0x04280428/0x04280427')
        print('DW_R6_DEMUX=0x04270427/0x04280427')
        print('DW_CAPSULE_DIFF_ONLY_DEMUX=PASS')
        print('DW_LIVE_MODE_ENABLED=0')
        print('DW_VERIFY=PASS')
if __name__=='__main__': main()
