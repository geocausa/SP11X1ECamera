#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent; BASE=HERE.parent; REPO=HERE.parents[3]
HY=BASE/'hy-production-one-stream-r27'; HV=BASE/'hv-current-golden-camera-dtb-merge'
R3=REPO/'experiments/E002-rear-ov13858-dphy/e002k-rear-native-productionization/d-source-integration/r3-source-integrated-runtime'
G=Path('/boot/sp11-7.1.5-audio-fullio-v19c/x1e80100-microsoft-denali-sp11-fullio-v19c.dtb')
F=HV/'x1e80100-microsoft-denali-sp11-hv-current-golden-frontonly.dtb'
R=R3/'x1e80100-microsoft-denali-sp11-e002k-d-r3.dtb'
G_SHA='2fcfa738c229b32764ff2722847cf4056b3153c64a12f8490429309f29df6d00'
F_SHA='34880dc20d349bf966ebf62d6d8bb3f0130f436c88d9e4838585624a869e04c7'
R_SHA='8cb5783fed2711758763aa81dc2f28c9f348259830ad6f57ffa18a6c5fd0d553'
OV_SHA='13a8ad956075c518687149f8473764d85979f38a7666244b132ad992a9bc1309'
def need(v,m):
    if not v: raise AssertionError(m)
def sha(p):
    import hashlib
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def s(raw): return raw.rstrip(b'\0').decode() if raw is not None else None
def u(raw): return hv.u32s(raw)
def seqref(tree,phmap,prop,data):
    vals=u(data); cp=hv.seq_cellprop(prop); need(cp is not None,'not seq ref '+prop); out=[]; i=0
    while i<len(vals):
        ph=vals[i]; path=phmap.get(ph); need(path is not None,f'{prop} provider {ph:#x} missing')
        raw=tree[path].get(cp); need(raw is not None,path+' missing '+cp); n=u(raw)[0]
        out.append((path,tuple(vals[i+1:i+1+n]))); i+=1+n
    return out
# Load exact HV FDT parser/authority implementation.
spec=importlib.util.spec_from_file_location('hvbuild',HV/'build-hv-dtb.py'); hv=importlib.util.module_from_spec(spec); spec.loader.exec_module(hv)
need(sha(G)==G_SHA,'Golden DTB identity'); need(sha(F)==F_SHA,'front DTB identity'); need(sha(R)==R_SHA,'rear DTB identity'); need(sha(R3/'ov13858-production.ko')==OV_SHA,'rear module identity')
hy=json.load(open(HY/'RESULT.json')); need(hy['status']=='PASS_CAPTURE_HY_PRODUCTION_ONE_STREAM_R27_GOLDEN_RESTORED_RETIRED','HY pass')
need(hy['production_stream_on_current_golden_merge_proven'] is True and hy['post_g3_native_writes']==0,'HY proof scope')
r3=(R3/'RESULT.md').read_text(); need('**PASS.**' in r3,'rear R3 PASS marker')
need('16/16 normal frames' in r3 and '29.9504 fps' in r3 and 'source-integration gate is closed' in r3,'rear R3 acceptance')
g=hv.parse_fdt(G); f=hv.parse_fdt(F); r=hv.parse_fdt(R); gn=set(g); fn=set(f); rn=set(r); fa=fn-gn; ra=rn-gn
need(len(gn)==1402 and len(fn)==1433 and len(rn)==1422,'node counts')
need(len(fa)==31 and len(ra)==20 and len(fa&ra)==16 and len(fa-ra)==15 and len(ra-fa)==4,'camera node-set decomposition')
rear='/soc@0/cci@ac15000/i2c-bus@1/camera@10'; cam='/soc@0/isp@acb7000'; ports=cam+'/ports'
need(s(f[rear].get('status'))=='disabled','front authority must disable rear sensor')
need('status' not in r[rear] or s(r[rear].get('status'))!='disabled','rear authority unexpectedly disabled')
need(ports+'/port@2' in f and ports+'/port@1' not in f,'front route ports')
need(ports+'/port@1' in r and ports+'/port@2' not in r,'rear route ports')
fph,_=hv.phandle_map(f); rph,_=hv.phandle_map(r)
fi=seqref(f,fph,'iommus',f[cam]['iommus']); ri=seqref(r,rph,'iommus',r[cam]['iommus'])
fi_args=[x[1] for x in fi]; ri_args=[x[1] for x in ri]
need(fi_args==[(0x800,0x60),(0x820,0x60),(0x840,0x60),(0x860,0x60),(0x18a0,0)],'front IOMMU authority')
need(ri_args==[(0x800,0x60),(0x860,0x60),(0x1800,0x60),(0x1860,0x60),(0x18e0,0),(0x1980,0x20),(0x1900,0),(0x19a0,0x20)],'rear IOMMU authority')
frn=s(f[cam]['reg-names']).split('\x00') if False else f[cam]['reg-names'].rstrip(b'\0').decode().split('\x00')
rrn=r[cam]['reg-names'].rstrip(b'\0').decode().split('\x00')
fin=f[cam]['interrupt-names'].rstrip(b'\0').decode().split('\x00'); rin=r[cam]['interrupt-names'].rstrip(b'\0').decode().split('\x00')
need('rt_cdm1' in frn and 'rt_cdm1' not in rrn,'RT-CDM reg authority conflict')
need('rt_cdm1' in fin and 'rt_cdm1' not in rin,'RT-CDM irq authority conflict')
# Golden remains default and there is no residual one-shot state.
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True)
need('saved_entry=sp11-audio-fullio-v19c' in env,'Golden saved entry'); need(not any(x.startswith('next_entry=') and x!='next_entry=' for x in env.splitlines()),'pending next_entry')
result={
 'schema':'sp11-e003i-hz-production-handoff-decision-v1',
 'status':'PASS_OFFLINE_PRODUCTION_HANDOFF_DECISION',
 'camera_runtime_performed':False,
 'golden_system_modified':False,
 'front_authority':{'stage':'HY','dtb_sha256':F_SHA,'stream_proven':True,'post_g3_policy':'shadow','rear_sensor_status':'disabled','camss_ports':['port@2'],'camss_iommus':[list(x) for x in fi_args],'rt_cdm1_resource':True},
 'rear_authority':{'stage':'E002k-D-R3','dtb_sha256':R_SHA,'ov13858_module_sha256':OV_SHA,'stream_proven':True,'frames':16,'mode':'4076x2806 RAW10','fps':29.9504,'camss_ports':['port@1'],'camss_iommus':[list(x) for x in ri_args],'rt_cdm1_resource':False},
 'structural_decomposition':{'golden_nodes':len(gn),'front_nodes':len(fn),'rear_nodes':len(rn),'front_added_nodes':len(fa),'rear_added_nodes':len(ra),'shared_camera_added_nodes':len(fa&ra),'front_only_camera_nodes':len(fa-ra),'rear_only_camera_nodes':len(ra-fa)},
 'naive_front_dtb_as_full_camera_stack_authorized':False,
 'naive_rear_plus_front_node_concatenation_authorized':False,
 'persistent_replacement_of_golden_default_authorized':False,
 'reason':'front authority disables rear and shared CAMSS authority conflicts in route children, IOMMU fwspec and RT-CDM1 resources',
 'handoff_decision':'retain Golden as protected default and retain front/rear proofs separately until a unified current-Golden rear+front CAMSS authority is derived and regression-proven',
 'post_g3_write_policy_must_remain':'shadow',
 'next_gate':'IA unified rear+front shared-CAMSS authority analysis on exact current Golden, offline only'
}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('HZ_HANDOFF_DECISION=PASS')
print('HZ_FRONT_PROVEN=YES REAR_PROVEN=YES FULL_STACK_DTB=NO')
print('HZ_NODESETS GOLDEN=1402 FRONT=1433 REAR=1422 SHARED_CAMERA_ADDED=16 FRONT_ONLY=15 REAR_ONLY=4')
print('HZ_CONFLICTS=rear-disabled-in-front,ports1-vs2,iommu-fwspec,rt_cdm1-resource')
print('HZ_GOLDEN_DEFAULT_REPLACEMENT=BLOCKED')
print('HZ_NEXT=IA_UNIFIED_REAR_FRONT_CAMSS_AUTHORITY_OFFLINE')
print('HZ_VERIFY=PASS')
