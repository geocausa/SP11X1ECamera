#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,importlib.util,json,math,struct
from pathlib import Path

PRE_EXPECTED={4:'25b80b20b5410ac0742a5fd26dbb32ac716cfa41a41965a5aaa98cbba39635e7',5:'beea73b4857fc1c39464f6d360a43c5ba4232e22a16fbb190206d5f2d704f7c7',6:'beea73b4857fc1c39464f6d360a43c5ba4232e22a16fbb190206d5f2d704f7c7'}
WIRE_EXPECTED={
 4:{'lsc0':'eb41b13a2049ecfe835266fefedd2d41c3e15564a8826ee06437f48a533234e5','lsc1':'c140edeb7b40eaefa5f904116cc4ce25478494bc9508160742cdc18881bfc676','gic':'f25ba0e9841133d7505cc3c34bef7c8a5b5c0e79f9f53b8163eb8a5d2ed63a94'},
 5:{'lsc0':'1033e0732a1f2edf2263351be7ad213a98864ba0b9feb0a1d2eb27fbcf31953c','lsc1':'eab65d435c04a768bc53009c0cfdf05055168213b50c83385459679dfc790590','gic':'25882eeae1fe0a61a9f4feb08c2387d32f83c17b1592155995a6d730875ac86c'},
 6:{'lsc0':'94dda0dd0c221da88a1087b13305c1cbe440cd314b3f0f6e324504494aab758e','lsc1':'5322633904bc97e2d647cf27c9f4f21a92b532272d063a4175028b3a8ad90076','gic':'fea286613a8dd7ad4445effa63479efef71fc52ce539220928e135a0894bdc44'},
}
ZERO_SHA='6ca83adefc47fc9ab71637c150b95b33083e61e507dff2ee5f2692aa27e1453e'
TUNING_SHA='2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d'
OTP_SHA='2ce64e72ae57bf19a4c60819a242a35bf5a09876862b21387e63b512d5026cdc'
GOLD_SHA='b0023db8b7254a9922c60506db58fd9bf2d717e09a8f088d31f33b2316538f6e'
LEAF_A_SHA='bdcf62f46070513ca0d343dda341336fe3953891a2643581e8ee455b77f37a3e'
LEAF_B_SHA='afc02261b98c3e2655039e29ace838f5780ac26202beda08db74dbd876822a11'

IFACE=0x260000000000;WRAP=0x260000001000;X1=0x260000003000
X2={4:0x260000010000,5:0x260000030000,6:0x260000050000}
D3={4:0x260000070000,5:0x260000072000,6:0x260000074000}
D4={4:0x260000071000,5:0x260000073000,6:0x260000075000}
CORE=0x260000100000;ADAPT=0x260000140000

class SparseMemory:
    PAGE=0x1000
    def __init__(self): self.pages={}
    def _page(self,base,create=False):
        p=self.pages.get(base)
        if p is None and create:
            p=bytearray(self.PAGE);self.pages[base]=p
        return p
    def mem_write(self,addr,data):
        data=bytes(data);pos=0
        while pos<len(data):
            a=addr+pos;base=a&~(self.PAGE-1);off=a-base;n=min(self.PAGE-off,len(data)-pos)
            p=self._page(base,True);p[off:off+n]=data[pos:pos+n];pos+=n
    def mem_read(self,addr,size):
        out=bytearray();pos=0
        while pos<size:
            a=addr+pos;base=a&~(self.PAGE-1);off=a-base;n=min(self.PAGE-off,size-pos)
            p=self._page(base,False)
            if p is None: raise RuntimeError(f'unmapped clean-room read addr=0x{a:x} size={n}')
            out+=p[off:off+n];pos+=n
        return bytes(out)
    def fill(self,addr,size,value): self.mem_write(addr,bytes((value&0xff,))*size)

def sha(b): return hashlib.sha256(b).hexdigest()
def shaf(p): return sha(p.read_bytes())
def need(v,msg):
    if not v: raise RuntimeError(msg)
def load(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(m);return m

def q10(v):
    x=int(math.floor(v*1024.0+0.5));return max(0x400,min(0x3fff,x))
def wire_from_output(output):
    vals=struct.unpack('<884f',output[:0xdd0]);ch=[[q10(v) for v in vals[i*221:(i+1)*221]] for i in range(4)]
    need(ch[1]==ch[2],'green planes diverged')
    l0=b''.join(struct.pack('<I',(ch[0][i]&0x3fff)|((ch[1][i]&0x3fff)<<14)) for i in range(221))
    l1=b''.join(struct.pack('<I',(ch[3][i]&0x3fff)|((ch[2][i]&0x3fff)<<14)) for i in range(221))
    l2=b'\0'*0x374;gic=(l0+l1)[0x22e:0x42e]
    return l0,l1,l2,gic

def output_seed(mode):
    if mode=='zero': return b'\0'*0xdf0
    if mode=='a5': return b'\xa5'*0xdf0
    if mode=='ones': return struct.pack('<884f',*([1.0]*884))+b'\x5a'*0x20
    raise ValueError(mode)

def build_pretintless(repo):
    prod=repo/'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static'
    g=repo/'experiments/E003-front-imx681-cphy/e003i-front-native-productionization/g-cleanroom-lsc-upstream'
    project=Path('/home/geoca/Documents/SP11-PROJECT')
    tuning=project/'00-RE-archive/sp11-driverdump/surfacecamfrontsensor_extension8380.inf_arm64_5a4c66ce4812274e/com.surface.tuned.ffc_imx681.bin'
    otp_path=prod/'oracle-live-20260904-current-repair/live-front-potp-slot-20260904.bin'
    need(shaf(tuning)==TUNING_SHA,'front tuning SHA drift');need(shaf(otp_path)==OTP_SHA,'front OTP SHA drift')
    cl=load(g/'cleanroom-front-lsc.py','e003i_k_cleanroom_lsc');dec=load(prod/'decode_imx681_chromatix.py','e003i_k_decode');gp=load(prod/'prove-lsc-live-golden-authority.py','e003i_k_golden')
    blob=tuning.read_bytes();hdr=dec.parse_header(blob);rec,_=dec.parse_symbol_table(blob,hdr['sections'][0],hdr['sections'][1]);obj=hdr['sections'][1]
    A=dec.data_bytes(blob,obj,rec[0x4bd]);B=dec.data_bytes(blob,obj,rec[0x4bf]);need(sha(A)==LEAF_A_SHA,'leaf A drift');need(sha(B)==LEAF_B_SHA,'leaf B drift')
    gold=gp.parse_golden(tuning);need(gold and gold['golden_region_sha256']==GOLD_SHA,'front golden drift');otp=cl.parse_otp(otp_path.read_bytes())
    ratios={4:0.342,5:0.0,6:0.0};out={};detail={}
    for req in (4,5,6):
        x22=cl.interpolate_leaf(A,B,ratios[req]);x23=cl.calibrate(x22,gold['values'],otp);payload=cl.resample_x23(x23)
        need(len(payload)==0xdd0 and sha(payload)==PRE_EXPECTED[req],f'R{req} pre-Tintless drift')
        out[req]=payload;detail[str(req)]={'ratio_float32':struct.unpack('<f',struct.pack('<f',ratios[req]))[0],'x22_sha256':sha(x22),'x23_sha256':sha(x23),'payload_sha256':sha(payload)}
    return out,detail

def verify_fixtures(cap,manifest_path):
    manifest=json.loads(manifest_path.read_text(encoding='utf-8-sig'));hashes=manifest['hashes'];names=['req4_wrapper_pre.bin']
    for req in (4,5,6): names += [f'req{req}_x1_config.bin',f'req{req}_x2_stats.bin',f'req{req}_x3_desc.bin',f'req{req}_x4_desc.bin',f'req{req}_output_mesh_post.bin']
    for req in (5,6): names += [f'req{req}_wrapper_pre.bin',f'req{req}_core_pre.bin']
    for name in names:
        b=(cap/name).read_bytes();meta=hashes[name];need(len(b)==int(meta['bytes']) and sha(b)==meta['sha256'],f'fixture drift {name}')
    return names

def put(m,addr,b): m.mem_write(addr,b);return b

def run_sequence(repo,cap,C,pretintless,core_fill=0,out_mode='zero'):
    m=SparseMemory();m.mem_write(IFACE,b'\0'*0x1000);m.mem_write(IFACE+0x18,struct.pack('<Q',WRAP));m.fill(CORE,C.CORE_BYTES,core_fill);m.mem_write(ADAPT,b'\0'*0x1000)
    result={}
    for req in (4,5,6):
        if req==4:
            put(m,WRAP,(cap/'req4_wrapper_pre.bin').read_bytes())
        else:
            wantw=(cap/f'req{req}_wrapper_pre.bin').read_bytes();wantc=(cap/f'req{req}_core_pre.bin').read_bytes();gotw=m.mem_read(WRAP,len(wantw));gotc=m.mem_read(CORE,len(wantc));w=bytearray(wantw);w[0x128:0x130]=struct.pack('<Q',CORE)
            need(gotw==bytes(w),f'R{req} wrapper carry drift');need(gotc==wantc,f'R{req} core carry drift')
        cfg=put(m,X1,(cap/f'req{req}_x1_config.bin').read_bytes());stats=put(m,X2[req],(cap/f'req{req}_x2_stats.bin').read_bytes());d3=put(m,D3[req],(cap/f'req{req}_x3_desc.bin').read_bytes());d4=put(m,D4[req],(cap/f'req{req}_x4_desc.bin').read_bytes())
        in_addr=struct.unpack_from('<Q',d3,8)[0];out_addr=struct.unpack_from('<Q',d4,8)[0]
        m.mem_write(in_addr,pretintless[req]+b'\0'*0x20);seed=output_seed(out_mode);m.mem_write(out_addr,seed)
        rc=C.wrapper_front_mode2(m,WRAP,X1,X2[req],D3[req],D4[req],CORE if req==4 else 0,ADAPT)
        need(rc==0,f'R{req} clean Tintless error {rc}')
        got=m.mem_read(out_addr,0xdf0);want=(cap/f'req{req}_output_mesh_post.bin').read_bytes();need(got[:0xdd0]==want[:0xdd0],f'R{req} output ABI != Windows');need(got[0xdd0:]==seed[0xdd0:],f'R{req} output tail changed')
        l0,l1,l2,gic=wire_from_output(got);obs={'lsc0':sha(l0),'lsc1':sha(l1),'gic':sha(gic)};need(obs==WIRE_EXPECTED[req],f'R{req} wire drift {obs}');need(sha(l2)==ZERO_SHA,f'R{req} LSC2 drift')
        result[req]={'output_abi':got[:0xdd0],'lsc0':l0,'lsc1':l1,'lsc2':l2,'gic':gic}
    return result

def main():
    here=Path(__file__).resolve().parent;repo=here.parents[3];prod=repo/'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static';idir=here.parent/'i-cleanroom-tintless'
    ap=argparse.ArgumentParser();ap.add_argument('--capture-dir',type=Path,default=repo.parent/'.local-oracles/oracle-live-20260904-front-atomic');ap.add_argument('--output-dir',type=Path,default=Path('/tmp/e003i-cleanroom-lsc'));ap.add_argument('--manifest',type=Path);a=ap.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
    C=load(idir/'cleanroom-tintless-helpers.py','e003i_k_tintless');fixtures=verify_fixtures(a.capture_dir,prod/'FRONT-ATOMIC-TINTLESS-STAGING-20260904.json');pre,pre_detail=build_pretintless(repo)
    cases=[('zero',0x00),('a5',0x00),('ones',0x00),('zero',0xa5)];runs={(mode,fill):run_sequence(repo,a.capture_dir,C,pre,fill,mode) for mode,fill in cases};base=runs[('zero',0x00)]
    manifest={'schema':'sp11-e003i-cleanroom-front-lsc-backend-v1','accepted':True,'device_mft_required':False,'unicorn_required':False,'cleanroom_upstream':pre_detail,'remaining_raw_request_inputs':[x for x in fixtures if 'output_mesh_post' not in x and 'wrapper_pre' not in x and 'core_pre' not in x],'validation_only_fixtures':[x for x in fixtures if 'output_mesh_post' in x or 'wrapper_pre' in x or 'core_pre' in x],'captured_pretintless_mesh_input':False,'captured_output_mesh_pre_input':False,'captured_lsc_staging_input':False,'output_initializations_tested':['zero','0xa5','float1+tail0x5a'],'core_initial_fills_tested':['0x00','0xa5'],'requests':{},'remaining_production_boundary':'replace captured x1 config/x2 Tintless stats/x3/x4 request descriptor metadata with live Linux request-state acquisition','safety':{'offline_only':True,'linux_camera_runtime':False}}
    for req in (4,5,6):
        for run in runs.values():
            for k in ('output_abi','lsc0','lsc1','lsc2','gic'): need(run[req][k]==base[req][k],f'R{req} counterfactual drift {k}')
        for name in ('lsc0','lsc1','lsc2','gic'): (a.output_dir/f'R{req}_{name.upper()}.bin').write_bytes(base[req][name])
        manifest['requests'][str(req)]={'pretintless_sha256':sha(pre[req]),'output_abi_sha256':sha(base[req]['output_abi']),'lsc0_sha256':sha(base[req]['lsc0']),'lsc1_sha256':sha(base[req]['lsc1']),'lsc2_sha256':sha(base[req]['lsc2']),'gic_sha256':sha(base[req]['gic'])}
        print(f"R{req} CLEANROOM_LSC PASS pre={sha(pre[req])} output={sha(base[req]['output_abi'])} LSC0={sha(base[req]['lsc0'])}")
    mp=a.manifest or a.output_dir/'MANIFEST.json';mp.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n');print('CLEANROOM_FRONT_LSC_BACKEND=PASS');print('MANIFEST',mp)
if __name__=='__main__':main()
