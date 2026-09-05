#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re, shutil, subprocess, tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
SRC=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/e003i-front-production-src')
MAN=json.loads((HERE/'BUILD-MANIFEST.json').read_text())
AUTH=json.loads((HERE/'RAW-AUTHORITY.json').read_text())
PATCH=HERE/MAN['patch']['file']
FILES=list(MAN['source'])

def need(v,m):
    if not v: raise RuntimeError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

need(AUTH['accepted'] and AUTH['bundle']['raw_bytes']==0x51000,'raw authority not accepted')
need(sha(PATCH)==MAN['patch']['sha256'],'patch SHA drift')
for f,h in MAN['source'].items(): need(sha(SRC/f)==h['post_sha256'],f'postimage drift {f}')

h=(SRC/'drivers/media/platform/qcom/camss/camss-video.h').read_text()
v=(SRC/'drivers/media/platform/qcom/camss/camss-video.c').read_text()
vfe=(SRC/'drivers/media/platform/qcom/camss/camss-vfe-680.c').read_text()
c=(SRC/'drivers/media/platform/qcom/camss/camss.c').read_text()
for x in (
 '#define CAMSS_X1E_3A_AEC_BE_RAW_BYTES\t\t0x00014000',
 '#define CAMSS_X1E_3A_BHIST_RAW_BYTES\t\t0x00001000',
 '#define CAMSS_X1E_3A_AWB_BG_RAW_BYTES\t\t0x0003c000',
 '#define CAMSS_X1E_3A_RAW_BYTES\t\t\t0x00051000',
 '#define CAMSS_X1E_3A_SNAPSHOT_HEADER_BYTES\t64'):
    need(x in h,f'missing ABI constant {x}')
need('static_assert(sizeof(struct camss_x1e_3a_snapshot_header) ==' in v,'missing 3A header assertion')
need('V4L2_CID_QCOM_CAMSS_X1E_3A_SNAPSHOT\t(V4L2_CID_USER_BASE + 0x1242)' in v,'3A control ID drift')
need('.dims = { CAMSS_X1E_3A_SNAPSHOT_BYTES }' in v,'3A control size drift')
need('V4L2_CTRL_FLAG_READ_ONLY | V4L2_CTRL_FLAG_VOLATILE' in v,'3A control not read-only volatile')
need('video_is_x1e_front_pix(video) ? 3 : 0' in v,'front control count drift')

# Existing hardware allocation ceilings remain byte-for-byte unchanged.
for x in (
 '#define VFE680_X1E_AUX_AEC_BE_SIZE\t0x000a0000',
 '#define VFE680_X1E_AUX_BHIST_SIZE\t0x00001800',
 '#define VFE680_X1E_AUX_TL_BG_SIZE\t0x00048000',
 '#define VFE680_X1E_AUX_AWB_BG_SIZE\t0x00151800'):
    need(x in vfe,f'VFE allocation drift {x}')
need('u8 required = VFE680_X1E_DONE_AEC_BE_BHIST | VFE680_X1E_DONE_AWB_BG;' in vfe,
     '3A ownership completion gate missing')
need('(slot->pending_mask & required) != required' in vfe,'3A pending ownership check missing')
for aux in ('VFE680_X1E_AUX_AEC_BE','VFE680_X1E_AUX_BHIST','VFE680_X1E_AUX_AWB_BG'):
    need(aux in vfe,f'missing {aux} access')

# Six source generations: all_done -> TLBG -> 3A -> retire_aux; same source_seq and slot.
need(c.count('camss_x1e_pix_publish_3a(req->live_video')==6,'3A publish count != 6')
need(c.count('camss_x1e_pix_publish_tlbg(req->live_video')==6,'TLBG publish count drift')
for n,slot in enumerate((0,1,0,1,0,1),1):
    poll=f'csid680_x1e_front_poll_all_done(csid, video_seq + {n},'
    tl=f'camss_x1e_pix_publish_tlbg(req->live_video, pix, {slot}, video_seq + {n});'
    a=f'camss_x1e_pix_publish_3a(req->live_video, pix, {slot}, video_seq + {n});'
    r=f'vfe680_x1e_pix_runtime_retire_aux(pix, {slot});'
    ip=c.find(poll); it=c.find(tl,ip); ia=c.find(a,it); ir=c.find(r,ia)
    need(min(ip,it,ia,ir)>=0 and ip<it<ia<ir and ir-ip<1000,f'generation {n} publication ordering drift')

# Patch is software-only: no newly added direct hardware access or allocation ceiling edit.
plus='\n'.join(x[1:] for x in PATCH.read_text().splitlines() if x.startswith('+') and not x.startswith('+++'))
need(not re.search(r'\b(?:readl|writel|readq|writeq|iowrite|regmap_write|cci_write)\s*\(',plus),
     'new direct hardware access in patch')
for macro in ('VFE680_X1E_AUX_AEC_BE_SIZE','VFE680_X1E_AUX_BHIST_SIZE','VFE680_X1E_AUX_TL_BG_SIZE','VFE680_X1E_AUX_AWB_BG_SIZE'):
    need(macro not in plus,'allocation ceiling modified by patch')

# Reconstruct the exact preimage by reversing the tracked patch, then reapply it.
with tempfile.TemporaryDirectory(prefix='e003i-y-roundtrip-') as td:
    t=Path(td)
    for f in FILES:
        (t/f).parent.mkdir(parents=True,exist_ok=True); shutil.copy2(SRC/f,t/f)
    subprocess.run(['patch','--batch','--silent','-R','-p1','-i',str(PATCH)],cwd=t,check=True)
    for f,hv in MAN['source'].items(): need(sha(t/f)==hv['pre_sha256'],f'reverse preimage mismatch {f}')
    subprocess.run(['patch','--batch','--silent','-p1','-i',str(PATCH)],cwd=t,check=True)
    for f,hv in MAN['source'].items(): need(sha(t/f)==hv['post_sha256'],f'forward postimage mismatch {f}')

ko=SRC/'drivers/media/platform/qcom/camss/qcom-camss.ko'
need(ko.exists() and sha(ko)==MAN['module']['sha256'],'built module hash drift')
ver=subprocess.check_output(['modinfo','-F','vermagic',ko],text=True).strip()
need(ver==MAN['module']['vermagic'],'module vermagic drift')

result={
 'schema':'sp11-e003i-y-generation-tagged-3a-inspection-v1','accepted':True,
 'raw_authority_accepted':True,'source_roundtrip':True,'six_publication_windows':True,
 'same_source_seq_as_tlbg':True,'all_groups_complete_before_copy':True,'slot_owned_until_after_copy':True,
 'new_direct_hardware_accesses':0,'allocation_ceiling_changes':0,
 'module_sha256':sha(ko),'module_vermagic':ver,
 'runtime_executed':False,
}
(HERE/'INSPECTION.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps(result,indent=2,sort_keys=True))
