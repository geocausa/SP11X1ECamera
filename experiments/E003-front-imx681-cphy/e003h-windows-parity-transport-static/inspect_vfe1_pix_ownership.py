#!/usr/bin/env python3
import argparse, hashlib, json, re, subprocess
from pathlib import Path

def die(s): raise SystemExit('FAIL: '+s)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(*a): return subprocess.check_output(a,text=True,stderr=subprocess.STDOUT)
def need(s,x,label):
    if x not in s: die(label+': '+x)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--vfe-source',type=Path,required=True)
    ap.add_argument('--camss-header',type=Path,required=True)
    ap.add_argument('--object',type=Path,required=True)
    ap.add_argument('--module',type=Path,required=True)
    ap.add_argument('--patch',type=Path,required=True)
    ap.add_argument('--completion-oracle',type=Path,required=True)
    ap.add_argument('--dynamic-oracle',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path)
    a=ap.parse_args()
    src=a.source.read_text(); vfe=a.vfe_source.read_text(); hdr=a.camss_header.read_text(); patch=a.patch.read_text()
    comp=json.loads(a.completion_oracle.read_text()); dyn=json.loads(a.dynamic_oracle.read_text())
    if not comp.get('accepted') or not dyn.get('accepted'): die('oracle not accepted')
    groups=[(g['event_id'],g['group'],g['clients']) for g in comp['groups']]
    expected=[(3,'VIDEO',[0,1,2,3]),(0xd,'AEC_BE_BHIST',[11,12]),(0xe,'TINTLESS_BG',[13]),(0x10,'AWB_BG',[14]),(0x12,'RS',[18])]
    if groups!=expected: die('completion group contract drift')
    if comp['linux_logical_completion_mask'].get('ALL')!='0x1f': die('completion mask drift')
    q=comp.get('group_queue_model',{})
    if q.get('helper_rva')!='0x26460' or q.get('cross_group_order_enforced') is not False:
        die('Windows independent-group FIFO proof missing')
    if not re.search(r'#define CAMSS_INIT_BUF_COUNT\s+2\b',hdr): die('CAMSS_INIT_BUF_COUNT is not two')

    required=[
      '#define VFE680_X1E_PIX_SLOT_COUNT\tCAMSS_INIT_BUF_COUNT',
      '#define VFE680_X1E_PIX_GROUP_COUNT\t5',
      '#define VFE680_X1E_AUX_DS4_SIZE\t\t0x00084000',
      '#define VFE680_X1E_AUX_DS16_SIZE\t0x0000c000',
      '#define VFE680_X1E_AUX_AEC_BE_SIZE\t0x000a0000',
      '#define VFE680_X1E_AUX_BHIST_SIZE\t0x00001800',
      '#define VFE680_X1E_AUX_TL_BG_SIZE\t0x00048000',
      '#define VFE680_X1E_AUX_AWB_BG_SIZE\t0x00151800',
      '#define VFE680_X1E_AUX_RS_SIZE\t\t0x00010000',
      '#define VFE680_X1E_DONE_ALL\t\tGENMASK(4, 0)',
      'struct vfe680_x1e_group_fifo {',
      'struct vfe680_x1e_group_fifo group[VFE680_X1E_PIX_GROUP_COUNT];',
      'static int vfe680_x1e_group_from_event(u32 event_id)',
      'case 0x03:', 'return VFE680_X1E_GROUP_VIDEO;',
      'case 0x0d:', 'return VFE680_X1E_GROUP_AEC_BE_BHIST;',
      'case 0x0e:', 'return VFE680_X1E_GROUP_TINTLESS_BG;',
      'case 0x10:', 'return VFE680_X1E_GROUP_AWB_BG;',
      'case 0x12:', 'return VFE680_X1E_GROUP_RS;',
      'fifo->slot[fifo->tail] = index;',
      'fifo->tail = (fifo->tail + 1) % VFE680_X1E_PIX_SLOT_COUNT;',
      'return fifo->slot[fifo->head];',
      'fifo->head = (fifo->head + 1) % VFE680_X1E_PIX_SLOT_COUNT;',
      'dma_alloc_coherent(dev, size, &buf->dma, GFP_KERNEL)',
      'memset(buf->cpu, 0, size);',
      'memset(buf->cpu, 0, buf->size);',
      'vb2_plane_size(&video->vb.vb2_buf, 0) < VFE680_X1E_QC10C_SIZE',
      'slot->pending_mask = VFE680_X1E_DONE_ALL;',
      'for (group = 0; group < VFE680_X1E_PIX_GROUP_COUNT; group++)',
      'vfe680_x1e_group_fifo_push(&own->group[group], index);',
      'group = vfe680_x1e_group_from_event(event_id);',
      'queued_index = vfe680_x1e_group_fifo_peek(fifo);',
      'bit = BIT(group);',
      'vfe680_x1e_group_fifo_pop(fifo);',
      'iovas->qc10c = video->addr[0];',
      'iovas->ds4 = slot->aux[VFE680_X1E_AUX_DS4].dma;',
      'iovas->ds16 = slot->aux[VFE680_X1E_AUX_DS16].dma;',
      'iovas->aec_be = slot->aux[VFE680_X1E_AUX_AEC_BE].dma;',
      'iovas->bhist = slot->aux[VFE680_X1E_AUX_BHIST].dma;',
      'iovas->tl_bg = slot->aux[VFE680_X1E_AUX_TL_BG].dma;',
      'iovas->awb_bg = slot->aux[VFE680_X1E_AUX_AWB_BG].dma;',
      'iovas->rs = slot->aux[VFE680_X1E_AUX_RS].dma;',
      'if (group == VFE680_X1E_GROUP_VIDEO) {',
      'if (!slot->pending_mask) {',
      'vfe680_x1e_pix_ownership_recipe __used = {'
    ]
    for x in required: need(src,x,'source contract drift')

    # Windows has independent per-group FIFOs. Never turn the five observed
    # live-event order into a cross-group protocol requirement.
    for forbidden_order in ('next_group', 'vfe680_x1e_completion_events',
                            'event_id != vfe680_x1e_completion_events'):
        if forbidden_order in src: die('cross-group sequencing reintroduced: '+forbidden_order)

    # Exact payload sizes must come from Windows FRAME_INCR, not observed Windows ring spacing.
    slots=dyn['auxiliary_slots']
    expected_sizes={'0x3001':0x84000,'0x3002':0xc000,'0x301c':0xa0000,'0x3010':0x10000,'0x300f':0x1800,'0x300e':0x151800,'0x300c':0x48000}
    for port,size in expected_sizes.items():
        if slots[port]['frame_incr']!=size: die('dynamic oracle size drift '+port)
    for frozen in (r'0x0*76c000\b',r'0x0*154000\b',r'0x0*4000\b'):
        if re.search(frozen,patch,re.I): die('Windows ring stride frozen in 0018: '+frozen)
    # Captured Windows addresses are evidence only; reject any exact observed address literal in 0018.
    vals=set()
    for key in ('initial_pre_start_set','first_post_start_set'):
        for rec in dyn.get(key,[]):
            vals.add(rec['image'].lower()); vals.add(rec['meta'].lower())
    lowpatch=patch.lower()
    for val in vals:
        if val in lowpatch: die('Windows IOVA frozen in 0018: '+val)

    # 0018 may create iovas but must not invoke the unreachable 0017 hardware-writing helpers.
    for f in ('vfe680_x1e_bus_prepare(', 'vfe680_x1e_bus_update(', 'vfe680_x1e_bus_stop('):
        if f in patch: die('0018 connects BUS recipe: '+f)
    for f in ('vfe_buf_done(', '.vfe_buf_done =', '.isr ='):
        if f in patch: die('0018 modifies live completion/ISR path: '+f)
    if patch.count('--- a/drivers/media/platform/qcom/camss/camss-vfe-680.c')!=1 or patch.count('--- a/')!=1:
        die('0018 path set drift')

    # The existing stream gate must remain ahead of mutex/IRQ/output setup.
    m=re.search(r'int vfe_enable_v2\(struct vfe_line \*line\)\n\{(.*?)\n\}',vfe,re.S)
    if not m: die('vfe_enable_v2 missing')
    b=m.group(1); gate=b.find('return -EOPNOTSUPP;'); lock=b.find('mutex_lock(&vfe->stream_lock)')
    if gate<0 or lock<0 or gate>=lock: die('VFE1 PIX stream gate no longer fail-closed')

    rel=run('aarch64-linux-gnu-objdump','-r',str(a.object))
    helpers=['vfe680_x1e_pix_ownership_alloc','vfe680_x1e_pix_ownership_free','vfe680_x1e_pix_ownership_begin','vfe680_x1e_pix_ownership_complete']
    hrel=[ln.strip() for ln in rel.splitlines() if any(h in ln for h in helpers)]
    if len(hrel)!=4 or any('R_AARCH64_ABS64' not in x for x in hrel): die('ownership helper relocation set drift: '+repr(hrel))
    if 'vfe680_x1e_pix_ownership_recipe' in rel: die('runtime/data relocation references ownership recipe')
    if src.count('vfe680_x1e_pix_ownership_recipe')!=1: die('ownership recipe source reference count drift')
    nm=run('aarch64-linux-gnu-nm','-an',str(a.module))
    for h in helpers+['vfe680_x1e_pix_ownership_recipe']:
        if h not in nm: die('retained module symbol missing '+h)

    out={
      'schema':'sp11-e003h-linux-vfe1-pix-ownership-static-inspection-v1','accepted':True,
      'source_sha256':sha(a.source),'object_sha256':sha(a.object),'module_sha256':sha(a.module),
      'patch_sha256':sha(a.patch),'completion_oracle_sha256':sha(a.completion_oracle),'dynamic_oracle_sha256':sha(a.dynamic_oracle),
      'slots':2,
      'observed_completion_order':['VIDEO','AEC_BE_BHIST','TINTLESS_BG','AWB_BG','RS'],
      'cross_group_order_required':False,
      'group_fifo_model':'five independent two-slot FIFO queues; each begin enqueues the slot into every group and each event pops only its own group',
      'linux_logical_completion_mask':'0x1f',
      'video_group':{'user_qc10c':True,'internal':['DS4','DS16']},
      'auxiliary_payload_sizes':{'DS4':0x84000,'DS16':0xc000,'AEC_BE':0xa0000,'BHIST':0x1800,'TL_BG':0x48000,'AWB_BG':0x151800,'RS':0x10000},
      'allocation_model':'each of two slots owns seven separate coherent Linux auxiliary allocations; user QC10C is caller/vb2-owned',
      'lifetime':'VIDEO may return user buffer; slot reusable only after all five independent groups retire, in any cross-group order',
      'windows_iovas_frozen':False,'windows_ring_strides_frozen':False,
      'runtime_isolation':{'recipe_source_reference_count':1,'recipe_compiled_relocation_present':False,'helper_relocations':hrel,'bus_recipe_called':False,'live_isr_or_vfe_buf_done_modified':False,'pix_stream_gate':'-EOPNOTSUPP before stream lock/IRQ/output'},
      'policy':'static-only; no module load, BUS write, RT-CDM submission, PIX enable, sensor transmission or frame authorized'}
    txt=json.dumps(out,indent=2,sort_keys=True)+'\n'
    if a.output: a.output.write_text(txt)
    else: print(txt,end='')
    print('PASS: two-slot PIX ownership uses independent Windows-style group FIFOs, Linux-only allocations, retained-only code and a blocked runtime path')
if __name__=='__main__': main()
