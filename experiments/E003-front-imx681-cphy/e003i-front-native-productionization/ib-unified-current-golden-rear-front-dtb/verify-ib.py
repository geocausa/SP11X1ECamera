#!/usr/bin/env python3
from __future__ import annotations
import hashlib,importlib.util,json,re,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent; BASE=HERE.parent; REPO=HERE.parents[3]
IA=BASE/'ia-unified-rear-front-shared-camss-authority'; HV=BASE/'hv-current-golden-camera-dtb-merge'
R3=REPO/'experiments/E002-rear-ov13858-dphy/e002k-rear-native-productionization/d-source-integration/r3-source-integrated-runtime'
G=Path('/boot/sp11-7.1.5-audio-fullio-v19c/x1e80100-microsoft-denali-sp11-fullio-v19c.dtb')
F=HV/'x1e80100-microsoft-denali-sp11-hv-current-golden-frontonly.dtb'
R=R3/'x1e80100-microsoft-denali-sp11-e002k-d-r3.dtb'
O=HERE/'x1e80100-microsoft-denali-sp11-ib-unified-rear-front.dtb'
BUILDER=HERE/'build-ib-dtb.py'; HVB=HV/'build-hv-dtb.py'
G_SHA='2fcfa738c229b32764ff2722847cf4056b3153c64a12f8490429309f29df6d00'; F_SHA='34880dc20d349bf966ebf62d6d8bb3f0130f436c88d9e4838585624a869e04c7'; R_SHA='8cb5783fed2711758763aa81dc2f28c9f348259830ad6f57ffa18a6c5fd0d553'; O_SHA='5e919d6bf778eb9eff5bf270447fa37f3c50ee16625c085c325e8d275d162321'
UNION=[(0x800,0x60),(0x860,0x60),(0x1800,0x60),(0x1860,0x60),(0x18e0,0),(0x1980,0x20),(0x1900,0),(0x19a0,0x20),(0x820,0x60),(0x840,0x60),(0x18a0,0)]
REAR='/soc@0/cci@ac15000/i2c-bus@1/camera@10'; FRONT='/soc@0/cci@ac16000/i2c-bus@1/camera@10'; CAMSS='/soc@0/isp@acb7000'; PORTS=CAMSS+'/ports'
def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('hv',HVB); hv=importlib.util.module_from_spec(spec); spec.loader.exec_module(hv)
def canon_ref(tree,n2p,prop,data):
    vals=hv.u32s(data)
    if hv.is_list_ref(prop):
        out=[]
        for x in vals: need(x in n2p,f'{prop}: unresolved phandle {x:#x}'); out.append(('REF',n2p[x]))
        return out
    cp=hv.seq_cellprop(prop); need(cp is not None,'not ref '+prop)
    out=[]; i=0
    while i<len(vals):
        ph=vals[i]; need(ph in n2p,f'{prop}: provider {ph:#x} missing'); p=n2p[ph]; raw=tree[p].get(cp); need(raw is not None,p+' missing '+cp); n=hv.u32s(raw)[0]; need(i+1+n<=len(vals),prop+' truncated'); out.append((p,tuple(vals[i+1:i+1+n]))); i+=1+n
    return out
def sem_equal(ta,ma,tb,mb,prop,a,b):
    if prop in ('phandle','linux,phandle'): return True
    if hv.is_list_ref(prop) or hv.seq_cellprop(prop): return canon_ref(ta,ma,prop,a)==canon_ref(tb,mb,prop,b)
    return a==b
def warnings(dt):
    with tempfile.TemporaryDirectory(prefix='ib-dtc-') as td:
        cp=subprocess.run(['dtc','-I','dtb','-O','dtb',str(dt),'-o',str(Path(td)/'x.dtb')],text=True,capture_output=True,check=True)
    out=[]
    for line in cp.stderr.splitlines():
        if ': Warning ' in line: out.append(line.split(': Warning ',1)[1])
    return sorted(out)
ia=json.load(open(IA/'RESULT.json')); need(ia['status']=='PASS_OFFLINE_UNIFIED_REAR_FRONT_SHARED_CAMSS_AUTHORITY','IA parent')
need(sha(G)==G_SHA and sha(F)==F_SHA and sha(R)==R_SHA and sha(O)==O_SHA,'DTB identity')
g=hv.parse_fdt(G); f=hv.parse_fdt(F); r=hv.parse_fdt(R); o=hv.parse_fdt(O)
gn,fn,rn,on=map(set,(g,f,r,o)); need((len(g),len(f),len(r),len(o))==(1402,1433,1422,1437),'node counts')
need(not (gn-on),'Golden node removed'); need(len(on-gn)==35,'camera additions vs Golden')
# Golden semantics stay byte-exact. Only camera symbol aliases may be extra on a pre-existing node.
for p in gn:
    for k,v in g[p].items(): need(o[p].get(k)==v,'Golden property drift '+p+':'+k)
    extra=set(o[p])-set(g[p])
    if p!='/__symbols__': need(not extra,'new property on Golden node '+p+':'+repr(extra))
# Relative to HV front authority only four rear route nodes are added; common-property changes are exactly rear status removal + CAMSS iommus replacement.
rear_only={REAR+'/port',REAR+'/port/endpoint',PORTS+'/port@1',PORTS+'/port@1/endpoint'}
need(on-fn==rear_only and not (fn-on),'front structural delta')
changes=[]
for p in sorted(fn&on):
    fk=set(f[p]); ok=set(o[p]);
    if fk!=ok: changes.append((p,'keys',tuple(sorted(fk-ok)),tuple(sorted(ok-fk))))
    for k in sorted(fk&ok):
        if f[p][k]!=o[p][k]: changes.append((p,k))
need(changes==[(REAR,'keys',('status',),()),(CAMSS,'iommus')],'unexpected front common delta '+repr(changes))
# Rear accepted sensor and new route nodes are semantically exact, allowing phandle renumbering.
rph,_=hv.phandle_map(r); oph,_=hv.phandle_map(o)
for p in [REAR,*sorted(rear_only)]:
    rk=set(r[p]); ok=set(o[p]); need(rk==ok,'rear property set '+p+' '+repr((rk-ok,ok-rk)))
    for k in rk: need(sem_equal(r,rph,o,oph,k,r[p][k],o[p][k]),'rear semantic drift '+p+':'+k)
# Front sensor subtree/route remains byte-exact because it is copied from HV unchanged.
for p in [FRONT,FRONT+'/port',FRONT+'/port/endpoint',PORTS+'/port@2',PORTS+'/port@2/endpoint']:
    need(o[p]==f[p],'front route raw drift '+p)
# Front CAMSS resource superset is preserved except intentional IOMMU union.
for k,v in f[CAMSS].items():
    if k=='iommus': continue
    need(o[CAMSS].get(k)==v,'front CAMSS resource drift '+k)
# Exact union fwspec on target apps_smmu.
seq=canon_ref(o,oph,'iommus',o[CAMSS]['iommus']); need(all(p=='/soc@0/iommu@15000000' for p,_ in seq),'IOMMU provider'); got=[args for _,args in seq]; need(got==UNION,'IOMMU union '+repr(got))
# Graph endpoints resolve pairwise for both cameras.
def endpoint_peer(path):
    vals=hv.u32s(o[path]['remote-endpoint']); need(len(vals)==1 and vals[0] in oph,'remote endpoint '+path); return oph[vals[0]]
need(endpoint_peer(REAR+'/port/endpoint')==PORTS+'/port@1/endpoint','rear sensor remote')
need(endpoint_peer(PORTS+'/port@1/endpoint')==REAR+'/port/endpoint','rear CAMSS remote')
need(endpoint_peer(FRONT+'/port/endpoint')==PORTS+'/port@2/endpoint','front sensor remote')
need(endpoint_peer(PORTS+'/port@2/endpoint')==FRONT+'/port/endpoint','front CAMSS remote')
need(set(subprocess.check_output(['fdtget','-l',str(O),PORTS],text=True).split())=={'port@1','port@2'},'CAMSS ports')
need('status' not in o[REAR],'rear still disabled'); need(o[REAR]['compatible'].rstrip(b'\0')==b'ovti,ov13858','rear sensor'); need(o[FRONT]['compatible'].rstrip(b'\0')==b'sony,imx681','front sensor')
# Camera symbols already existed in HV and now resolve to real rear+front paths.
for sym,path in [('ov13858_ep',REAR+'/port/endpoint'),('camss_csiphy1_ep',PORTS+'/port@1/endpoint'),('imx681_ep',FRONT+'/port/endpoint'),('camss_csiphy2_ep',PORTS+'/port@2/endpoint')]:
    got=subprocess.check_output(['fdtget','-t','s',str(O),'/__symbols__',sym],text=True).strip(); need(got==path and path in o,'symbol '+sym)
# No new DTC warning class/text relative to HV; graph remains clean.
need(warnings(O)==warnings(F),'DTC warning regression')
# Deterministic rebuild.
with tempfile.TemporaryDirectory(prefix='ib-rebuild-') as td:
    q=Path(td)/'out.dtb'; subprocess.run([str(BUILDER),'--front',str(F),'--rear',str(R),'--hv-builder',str(HVB),'--out',str(q)],text=True,capture_output=True,check=True); need(sha(q)==O_SHA,'rebuild nondeterminism')
result={
 'schema':'sp11-camera-ib-unified-current-golden-rear-front-dtb-v1','status':'PASS_OFFLINE_UNIFIED_CURRENT_GOLDEN_REAR_FRONT_DTB','camera_runtime_performed':False,'golden_system_modified':False,
 'parents':['IA unified shared-CAMSS authority','HV current-Golden front DTB','E002k-D-R3 rear DTB'],
 'golden_dtb_sha256':G_SHA,'front_hv_dtb_sha256':F_SHA,'rear_r3_dtb_sha256':R_SHA,'unified_dtb_sha256':O_SHA,'unified_dtb_bytes':O.stat().st_size,
 'node_semantics':{'golden_nodes':len(g),'front_nodes':len(f),'rear_nodes':len(r),'unified_nodes':len(o),'camera_nodes_vs_golden':len(on-gn),'golden_nodes_removed':0,'all_preexisting_golden_properties_byte_exact':True,'rear_only_nodes_added_to_front':4},
 'intentional_front_common_changes':['remove rear sensor status=disabled','replace CAMSS five-entry iommus with IA conservative union'],
 'front_authority_preserved':{'front_sensor_and_port_raw_exact':True,'camss_resources_except_iommus_raw_exact':True,'rt_cdm1_preserved':True,'port2_preserved':True},
 'rear_authority_preserved':{'rear_sensor_semantics_exact':True,'rear_port1_semantics_exact':True,'rear_enabled':True},
 'iommu_union':[list(x) for x in UNION],
 'graph':{'ports':[1,2],'rear_remote_pair':True,'front_remote_pair':True,'camera_symbols_resolve':True},
 'validation':{'deterministic_rebuild':True,'dtc_warning_regression':False,'graph_warnings_added':0},
 'runtime_authorized':False,'production_default_authorized':False,
 'next_gate':'IC prepare rear-first unified-DTB live regression candidate offline; checkpoint before install/arm'
}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('IB_UNIFIED_DTB=PASS SHA='+O_SHA)
print('IB_GOLDEN_SEMANTICS=BYTE_EXACT NODES=1402')
print('IB_GRAPH=REAR_PORT1+FRONT_PORT2 REAR_ENABLED=YES FRONT_PRESERVED=YES')
print('IB_IOMMU_UNION=11_SPECIFIERS')
print('IB_DTC_REGRESSION=PASS DETERMINISTIC=YES')
print('IB_RUNTIME_AUTHORIZED=NO')
print('IB_VERIFY=PASS')
