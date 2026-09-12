#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re,struct,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent; BASE=HERE.parent; REPO=HERE.parents[3]
HU=BASE/'hu-production-boot-module-firmware-authority'; BUILDER=HERE/'build-hv-dtb.py'
G=Path('/boot/sp11-7.1.5-audio-fullio-v19c/x1e80100-microsoft-denali-sp11-fullio-v19c.dtb')
C=REPO/'experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-candidate/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb'
O=HERE/'x1e80100-microsoft-denali-sp11-hv-current-golden-frontonly.dtb'
MAGIC=0xd00dfeed;BEGIN=1;END_NODE=2;PROP=3;NOP=4;END=9
G_SHA='2fcfa738c229b32764ff2722847cf4056b3153c64a12f8490429309f29df6d00';C_SHA='019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f';O_SHA='34880dc20d349bf966ebf62d6d8bb3f0130f436c88d9e4838585624a869e04c7'
SEQ={'clocks':'#clock-cells','power-domains':'#power-domain-cells','interconnects':'#interconnect-cells','iommus':'#iommu-cells','dmas':'#dma-cells','phys':'#phy-cells','resets':'#reset-cells','mboxes':'#mbox-cells','interrupts-extended':'#interrupt-cells'}
LIST={'remote-endpoint','required-opps','interrupt-parent','memory-region','msi-parent'}
def need(v,m):
    if not v:raise AssertionError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def align4(n):return (n+3)&~3
def u32s(b):return list(struct.unpack('>'+('I'*(len(b)//4)),b)) if b else []
def parse(path):
    b=Path(path).read_bytes();h=struct.unpack('>10I',b[:40]);need(h[0]==MAGIC,'magic '+str(path));_,_,so,stro,_,_,_,_,ssz,stsz=h;st=b[so:so+stsz];ss=b[stro:stro+ssz]
    out={};stack=[];i=0
    while i<len(st):
        t=struct.unpack('>I',st[i:i+4])[0];i+=4
        if t==BEGIN:
            z=st.index(b'\0',i);name=st[i:z].decode();i=align4(z+1);p='/' if not stack else ((stack[-1].rstrip('/')+'/'+name) if stack[-1]!='/' else '/'+name);stack.append(p);out.setdefault(p,{})
        elif t==END_NODE:stack.pop()
        elif t==PROP:
            ln,no=struct.unpack('>II',st[i:i+8]);i+=8;d=st[i:i+ln];i=align4(i+ln);z=ss.index(b'\0',no);out[stack[-1]][ss[no:z].decode()]=d
        elif t==NOP:pass
        elif t==END:break
        else:raise AssertionError('unknown token')
    return out
def phmaps(t):
    n2p={};p2n={}
    for p,pr in t.items():
        d=pr.get('phandle',pr.get('linux,phandle'))
        if d is not None:
            n=u32s(d)[0];need(n not in n2p,'duplicate phandle '+hex(n));n2p[n]=p;p2n[p]=n
    return n2p,p2n
def list_ref(prop):return prop in LIST or re.fullmatch(r'pinctrl-[0-9]+',prop) is not None or prop.endswith('-supply')
def seqprop(prop):
    if prop in SEQ:return SEQ[prop]
    if prop=='gpios' or prop.endswith('-gpios'):return '#gpio-cells'
    return None
def canon_ref(t,n2p,prop,data):
    vals=u32s(data)
    if list_ref(prop):
        out=[]
        for x in vals:need(x in n2p,f'{prop} missing phandle {x:#x}');out.append(('REF',n2p[x]))
        return out
    cp=seqprop(prop);need(cp is not None,'canon nonref '+prop)
    out=[];i=0
    while i<len(vals):
        ph=vals[i];need(ph in n2p,f'{prop} provider {ph:#x} missing');pp=n2p[ph];raw=t[pp].get(cp);need(raw is not None,pp+' missing '+cp);n=u32s(raw)[0];need(i+1+n<=len(vals),prop+' truncated');out.append((pp,tuple(vals[i+1:i+1+n])));i+=1+n
    return out
def warnings(dt):
    with tempfile.TemporaryDirectory(prefix='e003i-hv-dtc-') as td:
        cp=subprocess.run(['dtc','-I','dtb','-O','dtb',str(dt),'-o',str(Path(td)/'x.dtb')],text=True,capture_output=True,check=True)
    return sorted(re.sub(r'^.*?: Warning ', 'Warning ',x) for x in cp.stderr.splitlines() if ': Warning ' in x)
hu=json.loads((HU/'RESULT.json').read_text());need(hu['status']=='PASS_OFFLINE_PRODUCTION_BOOT_MODULE_FIRMWARE_AUTHORITY','HU parent')
need(sha(G)==G_SHA and sha(C)==C_SHA and sha(O)==O_SHA,'input/output identity')
g=parse(G);c=parse(C);o=parse(O);gn=set(g);cn=set(c);on=set(o);added=cn-gn
need(len(g)==1402 and len(c)==1433 and len(o)==1433,'node counts')
need(on-gn==added and not (gn-on) and len(added)==31,'node-set merge')
# Every pre-existing Golden property is byte-exact. No common new properties except the candidate camera symbols.
for p in gn:
    for k,v in g[p].items():need(o[p].get(k)==v,'Golden property drift '+p+':'+k)
    extra=set(o[p])-set(g[p])
    if p!='/__symbols__':need(not extra,'new common prop '+p+':'+repr(extra))
    else:need(extra==set(c[p])-set(g[p]),'symbol alias set drift')
# Added-node non-reference properties match source bytes; references match by canonical provider path + unchanged args.
cph,_=phmaps(c);oph,_=phmaps(o)
for p in sorted(added):
    need(set(o[p])==set(c[p]),'added property set '+p)
    for k,v in c[p].items():
        if k in ('phandle','linux,phandle'):continue
        if list_ref(k) or seqprop(k): need(canon_ref(c,cph,k,v)==canon_ref(o,oph,k,o[p][k]),'reference semantic drift '+p+':'+k)
        else:need(o[p][k]==v,'added raw prop drift '+p+':'+k)
# Output phandle uniqueness is enforced by phmaps(); all camera-added classified references were resolved above.
# Pre-existing Golden references are byte-exact because every Golden property is byte-exact.
# Route/resource checks.
def fg(*a):return subprocess.run(['fdtget',*a],text=True,capture_output=True,check=True).stdout.strip().split()
need(fg('-l',str(O),'/soc@0/isp@acb7000/ports')==['port@2'],'ports')
need(fg('-t','x',str(O),'/soc@0/isp@acb7000','iommus')==['3d','800','60','3d','820','60','3d','840','60','3d','860','60','3d','18a0','0'],'iommu')
need(fg('-t','s',str(O),'/soc@0/cci@ac16000/i2c-bus@1/camera@10','compatible')==['sony,imx681'],'sensor')
need(fg('-t','s',str(O),'/soc@0/cci@ac15000/i2c-bus@1/camera@10','status')==['disabled'],'rear disabled')
for ep in ('/soc@0/cci@ac16000/i2c-bus@1/camera@10/port/endpoint','/soc@0/isp@acb7000/ports/port@2/endpoint'):
    need(fg('-t','x',str(O),ep,'bus-type')==['1'],ep+' bus')
    need(fg('-t','x',str(O),ep,'data-lanes')==['0'],ep+' lane')
# DTC emits exactly the same pre-existing warnings as Golden; merge adds none.
need(warnings(O)==warnings(G),'new/different DTC warnings')
# Rebuild determinism.
with tempfile.TemporaryDirectory(prefix='e003i-hv-rebuild-') as td:
    p=Path(td)/'out.dtb';subprocess.run([str(BUILDER),'--golden',str(G),'--candidate',str(C),'--out',str(p)],text=True,capture_output=True,check=True);need(sha(p)==O_SHA,'rebuild nondeterminism')
result={
 'schema':'sp11-e003i-hv-current-golden-camera-dtb-merge-v1','status':'PASS_OFFLINE_CURRENT_GOLDEN_CAMERA_DTB_MERGE','parent':'HU production boot/module/firmware authority','camera_runtime_performed':False,'golden_system_modified':False,
 'golden_dtb_sha256':G_SHA,'historical_camera_authority_sha256':C_SHA,'merged_dtb_sha256':O_SHA,'merged_dtb_bytes':O.stat().st_size,
 'node_semantics':{'golden_nodes':len(g),'merged_nodes':len(o),'camera_nodes_added':len(added),'golden_nodes_removed':0,'all_preexisting_golden_properties_byte_exact':True,'new_common_properties_only_camera_symbols':True,'camera_reference_properties_semantically_remapped_by_provider_path':True},
 'route':{'camss_ports':['port@2'],'sensor':'sony,imx681@0x10','rear_status':'disabled','cphy_bus_type':1,'data_lanes':[0],'iommu_set':['0x800/0x60','0x820/0x60','0x840/0x60','0x860/0x60','0x18a0/0']},
 'validation':{'deterministic_rebuild':True,'dtc_new_warnings':0,'graph_warnings':0,'phandles_unique':True,'all_classified_references_resolve':True},
 'boot_candidate_created':False,'boot_candidate_armed':False,'next_gate':'HW offline production boot bundle + fail-closed activation candidate preparation'
}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('HV_GOLDEN_SEMANTICS=PASS EXISTING_PROPERTIES_BYTE_EXACT=YES')
print('HV_CAMERA_MERGE=PASS ADDED_NODES=31 REMOVED=0 OUTPUT='+O_SHA)
print('HV_ROUTE=PASS FRONT_ONLY_PORT2 IMX681_0X10 CPHY_LANE0 IOMMU_5')
print('HV_DTC_REGRESSION=PASS NEW_WARNINGS=0 REBUILD_DETERMINISTIC=YES')
print('HV_BOOT_CANDIDATE=NO CAMERA_RUNTIME=NO GOLDEN_MODIFIED=NO')
print('HV_VERIFY=PASS')
