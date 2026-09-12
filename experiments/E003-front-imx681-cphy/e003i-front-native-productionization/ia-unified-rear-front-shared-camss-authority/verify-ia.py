#!/usr/bin/env python3
from __future__ import annotations
import difflib,hashlib,json,re,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent; BASE=HERE.parent; REPO=HERE.parents[3]
HZ=BASE/'hz-production-handoff-decision'; B=BASE/'b-dual-source-foundation'
R3=REPO/'experiments/E002-rear-ov13858-dphy/e002k-rear-native-productionization/d-source-integration/r3-source-integrated-runtime'
GOLD_CAMSS=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-repro/src/drivers/media/platform/qcom/camss/camss.c')
FRONT_CAMSS=REPO/'src/front-imx681/kernel/camss/camss.c'
SMMU=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-repro/src/drivers/iommu/arm/arm-smmu/arm-smmu.c')
FRONT_MOD=BASE/'hy-production-one-stream-r27/build/qcom-camss.ko'
FRONT_IMX=BASE/'hy-production-one-stream-r27/build/imx681.ko'
REAR_MOD=R3/'ov13858-production.ko'
FRONT=[(0x800,0x60),(0x820,0x60),(0x840,0x60),(0x860,0x60),(0x18a0,0)]
REAR=[(0x800,0x60),(0x860,0x60),(0x1800,0x60),(0x1860,0x60),(0x18e0,0),(0x1980,0x20),(0x1900,0),(0x19a0,0x20)]
UNION=[]
for x in REAR+FRONT:
    if x not in UNION: UNION.append(x)
VM='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def modinfo(field,p): return subprocess.check_output(['modinfo','-F',field,str(p)],text=True).strip()
def extract_array(text,name):
    m=re.search(rf'static const struct [^\n]+\b{name}\[\]\s*=\s*\{{',text)
    if not m: raise AssertionError('array start '+name)
    i=m.start(); depth=0; seen=False; j=m.end()-1
    while j<len(text):
        if text[j]=='{': depth+=1; seen=True
        elif text[j]=='}':
            depth-=1
            if seen and depth==0:
                semi=text.find(';',j); return text[i:semi+1]
        j+=1
    raise AssertionError('array end '+name)
def extract_scalar(text,name):
    m=re.search(rf'static const struct [^\n]+\b{name}\s*=\s*\{{',text)
    if not m: raise AssertionError('scalar start '+name)
    i=m.start(); depth=0; seen=False; j=m.end()-1
    while j<len(text):
        if text[j]=='{': depth+=1;seen=True
        elif text[j]=='}':
            depth-=1
            if seen and depth==0:
                semi=text.find(';',j);return text[i:semi+1]
        j+=1
    raise AssertionError('scalar end '+name)
def alloc(seq):
    smrs=[]; idx=[]
    for sid,mask in seq:
        found=None
        for i,(esid,emask) in enumerate(smrs):
            if (mask & emask)==mask and not ((sid^esid)& ~emask):
                found=i; break
            if not ((sid^esid)& ~(emask|mask)):
                return False,smrs,idx,(sid,mask,esid,emask)
        if found is None:
            found=len(smrs); smrs.append((sid,mask))
        idx.append(found)
    return True,smrs,idx,None
hz=json.load(open(HZ/'RESULT.json')); need(hz['status']=='PASS_OFFLINE_PRODUCTION_HANDOFF_DECISION','HZ parent')
b=json.load(open(B/'BUILD-MANIFEST.json')); need(b['accepted'] is True and b['dual_dtb']['rear_enabled'] is True and b['dual_dtb']['front_enabled'] is True,'B dual foundation')
need(b['dual_dtb']['iommu_set']==['0x800/0x60','0x820/0x60','0x840/0x60','0x860/0x60','0x18a0/0'],'B five-entry set')
need(sha(SMMU)=='580bcc9326837da0607e45843f4906694c28a0a5b68ca9297bc516747704d55f','SMMU source')
need(sha(GOLD_CAMSS)=='873122ba4e82e7a56007ef7409c53e70870d44be9e3d168e65be3696f915daae','Golden CAMSS source')
need(sha(FRONT_CAMSS)=='117136b2c624de5ef3f4c081cdcf9c363cda9f6db5c752b7ade5f5e11b1b3e95','front CAMSS source')
need(sha(REAR_MOD)=='13a8ad956075c518687149f8473764d85979f38a7666244b132ad992a9bc1309','rear module')
need(sha(FRONT_MOD)=='7afe6ed0bd0b945092256c53d111601c44cf33c174c1988945c05d8ef2697e95','front CAMSS module')
need(sha(FRONT_IMX)=='ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6','front IMX module')
for p in (REAR_MOD,FRONT_MOD,FRONT_IMX): need(modinfo('vermagic',p)==VM,'vermagic '+p.name)
# Exact arm-smmu overlap/reuse rules that make a conservative union mechanically admissible.
sm=SMMU.read_text()
for marker in ('if ((mask & smrs[i].mask) == mask &&','if (!((id ^ smrs[i].id) & ~(smrs[i].mask | mask)))','return -EINVAL;','arm_smmu_master_install_s2crs(cfg, S2CR_TYPE_TRANS,'):
    need(marker in sm,'SMMU rule '+marker)
ok,groups,idx,err=alloc(UNION); need(ok,'rear-first union conflict '+repr(err)); need(len(groups)==6,'rear-first union mapping groups')
front_first=[]
for x in FRONT+REAR:
    if x not in front_first:front_first.append(x)
ok2,groups2,idx2,err2=alloc(front_first); need(ok2,'front-first union conflict '+repr(err2)); need(set(groups2)==set(groups),'order changes mapping coverage')
# Static X1E route resources: private front CAMSS keeps rear CSIPHY/CSID/ICC/wrapper tables byte-exact.
g=GOLD_CAMSS.read_text(); f=FRONT_CAMSS.read_text()
for name in ('csiphy_res_x1e80100','csid_res_x1e80100','icc_res_x1e80100'):
    need(extract_array(g,name)==extract_array(f,name),name+' drift')
need(extract_scalar(g,'csid_wrapper_res_x1e80100')==extract_scalar(f,'csid_wrapper_res_x1e80100'),'wrapper drift')
# VFE static table changes only the X1E VFE1 PIX format pointer; VFE0/RDI static authority is byte-identical.
gv=extract_array(g,'vfe_res_x1e80100'); fv=extract_array(f,'vfe_res_x1e80100')
d=list(difflib.unified_diff(gv.splitlines(),fv.splitlines(),lineterm=''))
meaning=[x for x in d if (x.startswith('+') or x.startswith('-')) and not x.startswith(('+++','---'))]
need(meaning==['-\t\t\t.formats_pix = &vfe_formats_pix_845','+\t\t\t.formats_pix = &vfe_formats_pix_x1e80100'],'VFE static delta '+repr(meaning))
need('.formats_rdi = &vfe_formats_rdi_845' in gv and gv.count('.formats_rdi = &vfe_formats_rdi_845')==4,'Golden RDI table')
need(fv.count('.formats_rdi = &vfe_formats_rdi_845')==4,'front RDI table')
result={
 'schema':'sp11-camera-ia-unified-rear-front-shared-camss-authority-v1',
 'status':'PASS_OFFLINE_UNIFIED_REAR_FRONT_SHARED_CAMSS_AUTHORITY',
 'camera_runtime_performed':False,'golden_system_modified':False,
 'parents':['HZ production handoff decision','E003i-B dual-source foundation','E002k-D-R3 rear production pass','HY front production pass'],
 'module_set':{
   'qcom_camss_sha256':'7afe6ed0bd0b945092256c53d111601c44cf33c174c1988945c05d8ef2697e95',
   'imx681_sha256':'ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6',
   'ov13858_sha256':'13a8ad956075c518687149f8473764d85979f38a7666244b132ad992a9bc1309',
   'vermagic':VM,
 },
 'camss_static_regression':{
   'csiphy_x1e_table_byte_exact':True,'csid_x1e_table_byte_exact':True,'icc_x1e_table_byte_exact':True,'csid_wrapper_x1e_byte_exact':True,
   'vfe_static_delta_only':'VFE1 PIX format pointer 845 -> x1e80100','vfe0_rdi_static_authority_preserved':True,
   'rear_live_regression_still_required':True,
 },
 'iommu':{
   'front_set':[list(x) for x in FRONT],'rear_set':[list(x) for x in REAR],'conservative_union':[list(x) for x in UNION],
   'union_specifier_count':len(UNION),'arm_smmu_mapping_group_count':len(groups),'rear_first_allocation_indices':idx,
   'front_first_allocation_indices':idx2,'partial_overlap_conflict':False,'all_entries_same_camss_domain':True,
   'candidate_kind':'conservative accepted-set union; no accepted specifier removed or weakened',
 },
 'unified_camss_candidate':{
   'base':'exact current Golden + HV front resource superset',
   'ports':[1,2],'rear_sensor_enabled':True,'front_sensor_enabled':True,
   'rt_cdm1_resource':True,'iommu_policy':'conservative_union','front_post_g3_policy':'shadow',
 },
 'runtime_authorized':False,
 'production_default_authorized':False,
 'reason_runtime_still_blocked':'generic front CAMSS runtime code differs from Golden; rear VFE0 RDI must be live-regressed under the private front CAMSS module and unified fwspec before front regression',
 'next_gate':'IB construct deterministic exact-Golden unified rear+front DTB with conservative IOMMU union; offline semantic regression only'
}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('IA_SHARED_CAMSS_AUTHORITY=PASS')
print('IA_MODULES=CAMSS_FRONT+IMX681_FRONT+OV13858_REAR VERMAGIC=PASS')
print('IA_X1E_STATIC_REAR_ROUTE=CSIPHY/CSID/ICC/WRAPPER_EXACT VFE0_RDI_PRESERVED')
print('IA_IOMMU_UNION=11_SPECIFIERS 6_SMR_GROUPS CONFLICTS=0')
print('IA_RUNTIME_AUTHORIZED=NO REAR_LIVE_REGRESSION_REQUIRED=YES')
print('IA_NEXT=IB_UNIFIED_DTB_OFFLINE')
print('IA_VERIFY=PASS')
