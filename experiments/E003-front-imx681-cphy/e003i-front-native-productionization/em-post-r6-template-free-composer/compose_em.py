#!/usr/bin/env python3
from __future__ import annotations
import ctypes,hashlib,importlib.util,json,pathlib,struct,subprocess,sys,tempfile
HERE=pathlib.Path(__file__).resolve().parent
BASE=HERE.parent
REPO=HERE.parents[3]
EA_ROOT=pathlib.Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-ea/attempt1-pass-20260911T0348/runtime-output')
EB_ROOT=pathlib.Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-eb/windows-r4-r12-20260911/extracted')
DS_PATH=BASE/'ds-live-iq-producer-awb-hold/live-iq-producer.py'
E_PATH=BASE/'e-template-free-capsule/build-template-free-0076-capsules.py'
DV_PATH=BASE/'dv-live-residual-isp-demux/demux_bls.py'
EL_PATH=BASE/'el-calibrated-awb-scalar-join/awb_scalar.py'
DR_SRC=BASE/'dr-native-awb-zero-weight-hold/native-trigger-core.c'
ED_RESULT=BASE/'ed-windows-r4-r12-tintless-trigger-staging-oracle/RESULT.json'
EB_RESULT=BASE/'eb-windows-r4-r12-gtm-state-oracle/RESULT.json'
IQ_BYTES=41088
GTM_SHA='074564f99a45d29a5dbe800c18bc0436735f70740cb8f42cd9a5c7b636ffcdfa'
EA_ISP={4:0x3f801646,5:0x3f801646,6:0x3f801646}
EA_STATS_SHA=[
'bd525eb750b042371f0d20dae3cc64fba780c11540d5c08ae6417028fd6aee48','2c99b96d0cf042c42e369fc5ea659cd476e030674798763b5ed3e6f08f84f2ad','18bb82c72b4adba2cd1b98dcce06b260ad8b455cfc5cdd5b93e0decf04aa9f54','be7070f2ceca327b3b7cc9bb71bdb3a757f9978512ea2dbd1f6ada6d097b4e63','0793d94a35795cb78537db383e26da2cac6612d8e3acc72bc14e45c271fc8a15','be7b6bcb4170e7231dd2040f6dd96cfbe855241c348b87631fe31fe4cc37689a']
EA_TLBG_SHA=[
'a1225991c2c7b9182262badf19d681bacc1fce1e1f6c1f1662768efe762434a2','a24c88ac5d8c95bd1f59887899c1f0611100c599243653caa8e753dfa3ee87b0','1d199c9cceb7047fc5fd7d3e33383f40a5a9894aa23f72e77533fc9f9e8c77d8','5960a862c73ebb9ed59e77c44d1a65d730cf20b23895f42f0a474f5322db4b43','e52f0ba64f578ba6982e98b851507c1a67f952878014d5d192637cdf00fc3652','d59c9c36315197707990ed331244b8dc1cfee3fe195e7288845dde9f3e2e613e']
INVARIANT_DMI={0,3,5,7,8,9,10,11,12,13}

def load(p,n):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;assert s.loader;s.loader.exec_module(m);return m
DS=load(DS_PATH,'em_ds');E=load(E_PATH,'em_e');DV=load(DV_PATH,'em_dv');EL=load(EL_PATH,'em_el')
def sha(b):return hashlib.sha256(bytes(b)).hexdigest()
def need(v,m):
    if not v: raise RuntimeError(m)
def fbits(u): return struct.unpack('<f',struct.pack('<I',u))[0]
def read_evidence(p:pathlib.Path)->bytes:
    try:return p.read_bytes()
    except PermissionError:return subprocess.check_output(['sudo','-n','cat',str(p)])

def request_parity_values(req:int)->dict[int,int]:
    even=(req&1)==0; out={}
    for ro in (0x3d58,0x3d5c,0x4358,0x435c,0x4758,0x475c,0x4958,0x495c,0xa058,0xa05c,0xa258,0xa25c):out[ro]=1 if even else 0
    for ro in (0x5a58,0x5a5c,0x5f58,0x5f5c):out[ro]=0 if even else 1
    return out

class Composer:
    def __init__(self):
        _e,self.variant,self.main,self.raw4,self.slot4,self.startup,self.payloads,self.sp,self.pp=E.static_recipe(REPO)
        self.raw6,self.slot6,_=E.raw_request(REPO,6,self.raw4,self.slot4)
        # R6 is used only for DMI sections proven invariant over R4/R5/R6.
        self.paybase=[self.slot6[o:o+n] for _,o,n in E.DMI_SOURCE]
        for idx in INVARIANT_DMI:
            hs=set()
            for req in (4,5,6):
                _,slot,_=E.raw_request(REPO,req,self.raw4,self.slot4);_,o,n=E.DMI_SOURCE[idx];hs.add(sha(slot[o:o+n]))
            need(len(hs)==1,f'DMI {idx} not invariant R4-R6')
        # WB G channel word is outside the dynamic holes and must remain exact unity for this profile.
        for req in (4,5,6):
            raw,_,_=E.raw_request(REPO,req,self.raw4,self.slot4);need(struct.unpack_from('<I',raw,0x164)[0]==0x08000000,'WB 0x4568 static word drift')
        self.gtm=read_evidence(EB_ROOT/'R06_GTM_OUT.bin');need(len(self.gtm)==0x800 and sha(self.gtm)==GTM_SHA,'EB stable GTM authority drift')
        for req in (6,7,8,9):need(read_evidence(EB_ROOT/f'R{req:02d}_GTM_OUT.bin')==self.gtm,f'EB GTM R{req} not stable')
        eb=json.loads(EB_RESULT.read_text());need(eb.get('clean_gtm_replay')=='9/9 PASS' and eb.get('post_r6_common_law')=='bank_parity_only' and eb.get('post_r6_distinct_gtm_outputs')==1,'EB post-R6 GTM not closed')
        ed=json.loads(ED_RESULT.read_text());need(ed.get('clean_lsc_replay')=='9/9 byte-exact LSC0/LSC1/LSC2/GIC','ED LSC authority drift')
    def module(self,req:int,isp_gain:float,awb_regs:dict[int,int]):
        values=[[0]*6 for _ in E.MODULES];vm=[0]*len(E.MODULES)
        for r in self.variant['dynamic_register_fields']:
            ro=int(r['register_offset'],16);mi,si=E.REG_SLOT[ro];vm[mi]|=1<<si
        for ro,val in request_parity_values(req).items():mi,si=E.REG_SLOT[ro];values[mi][si]=val
        dm=DV.calculate(isp_gain)
        for ro,val in ((0x3b70,dm['reg_3b70']),(0x3b74,dm['reg_3b74'])):mi,si=E.REG_SLOT[ro];values[mi][si]=val
        for ro,val in awb_regs.items():
            if ro in E.REG_SLOT:mi,si=E.REG_SLOT[ro];values[mi][si]=val
        pm=[0]*len(E.MODULES)
        for mi,indices in {1:[0],2:[1,2,3],4:[4],5:[5],6:[6],7:[7,8,9],8:[10,11,12,13]}.items():
            for j,_ in enumerate(indices):pm[mi]|=1<<j
        module=b''.join(struct.pack('<BBH6I4x',vm[i],pm[i],0,*values[i]) for i in range(len(E.MODULES)))
        need(len(module)==0x120,'module bytes')
        return module,dm
    def compose(self,req:int,wire,isp_gain:float,awb_regs:dict[int,int]):
        need(req>=7,'EM is post-R6 only')
        module,dm=self.module(req,isp_gain,awb_regs);pay=list(self.paybase);pay[1],pay[2],pay[3],pay[4]=wire;pay[6]=self.gtm
        cap,desc=E.compose(req,self.main,self.startup,self.payloads,self.sp,self.pp,{'module':module,'payload':pay})
        need(len(cap)==IQ_BYTES,'capsule bytes')
        return cap,desc,module,pay,dm

def replay_ea():
    with tempfile.TemporaryDirectory(prefix='e003i-em-') as td:
        td=pathlib.Path(td);trig=td/'trigger.so';tint=td/'tintless.so';DS.compile_so(DR_SRC,trig,('-lm',));X=load(DS.XFILE,'em_x');X.compile_native(tint)
        trigger=DS.NativeTrigger(trig);lsc=DS.DynamicLsc(tint);awb=EL.CalibratedAWB();composer=Composer();rows=[]
        for gen in range(1,7):
            sb=read_evidence(EA_ROOT/f'STATS3A-{gen-1}.bin');tb=read_evidence(EA_ROOT/f'TLBG-{gen-1}.bin')
            need(sha(sb)==EA_STATS_SHA[gen-1],f'EA G{gen} STATS3A drift');need(sha(tb)==EA_TLBG_SHA[gen-1],f'EA G{gen} TLBG drift')
            id3,aec,aw=DS.parse_3a(sb);idt,tl=DS.parse_tlbg(tb);need(id3==idt and id3[0]==gen,f'EA G{gen} identity')
            tr,fx,fy,fc,_,hold=trigger.run(aec,aw);wire,ls=lsc.run(tl,tr.lux,fc)
            if gen<4:continue
            req=gen+3;need(hold,f'EA G{gen} unexpectedly fresh AWB');ao=awb.run(fx,fy,tr.lux,fc,1.0);isp=fbits(EA_ISP[gen]);cap,desc,module,pay,dm=composer.compose(req,wire,isp,ao['registers'])
            rows.append({'generation':gen,'request':req,'stats3a_sha256':sha(sb),'tlbg_sha256':sha(tb),'awb_hold_previous':hold,
              'decision_bits':[f'0x{DS.bits(fx):08x}',f'0x{DS.bits(fy):08x}'],'lux_bits':f'0x{DS.bits(tr.lux):08x}','cct_bits':f'0x{DS.bits(fc):08x}',
              'isp_gain_bits':f'0x{EA_ISP[gen]:08x}','demux_regs':[f"0x{dm['reg_3b70']:08x}",f"0x{dm['reg_3b74']:08x}"],
              'awb_dynamic_regs':{f'0x{k:04x}':f'0x{v:08x}' for k,v in sorted(ao['registers'].items()) if k in E.REG_SLOT},
              'bank_regs':{f'0x{k:04x}':v for k,v in sorted(request_parity_values(req).items())},'module_sha256':sha(module),'capsule_sha256':sha(cap),
              'lsc':ls,'gtm_sha256':sha(pay[6]),'section_sha256':[{'name':E.DMI_SOURCE[i][0],'sha256':sha(pay[i]),'bytes':len(pay[i])} for i in range(14)],
              'section_count':len(desc),'capsule_bytes':len(cap)})
        return rows
