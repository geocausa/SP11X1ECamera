#!/usr/bin/env python3
import argparse, hashlib, json, re, subprocess
from pathlib import Path

def die(s): raise SystemExit('FAIL: '+s)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(*a): return subprocess.check_output(a,text=True,stderr=subprocess.STDOUT)
def need(s,x,label):
    if x not in s: die(label+': '+x)

def block(src, name):
    m=re.search(rf'{re.escape(name)}\s*\[[^]]+\]\s*=\s*\{{(.*?)\n\}};',src,re.S)
    if not m: die('table missing '+name)
    return m.group(1)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--vfe-source',type=Path,required=True)
    ap.add_argument('--object',type=Path,required=True)
    ap.add_argument('--module',type=Path,required=True)
    ap.add_argument('--patch',type=Path,required=True)
    ap.add_argument('--oracle',type=Path,required=True)
    ap.add_argument('--static-proof',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path)
    a=ap.parse_args()
    src=a.source.read_text(); vfe=a.vfe_source.read_text(); patch=a.patch.read_text()
    oracle=json.loads(a.oracle.read_text()); proof=json.loads(a.static_proof.read_text())
    if not oracle.get('accepted') or not proof.get('accepted'): die('input oracle/proof not accepted')
    if proof.get('oracle_sha256') != sha(a.oracle): die('static proof/oracle hash mismatch')
    c=oracle['closure']; layout=oracle['linux_layout']
    if (c['packets'],c['ordinary_register_writes'],c['dmi_commands'],c['unique_payloads'],c['caller_supplied_dynamic_value_fields']) != (4,2131,46,16,20):
        die('corpus closure drift')
    if c['cross_capture_new_dynamic_register'] != '0x8c period_cfg': die('period_cfg cross-capture proof missing')
    if not c['normalized_initial_equals_final']: die('normalized capture equivalence missing')
    if layout['windows_main_slot_stride_frozen'] or layout['windows_dmi_source_offsets_frozen']: die('oracle freezes Windows allocation geometry')
    if layout['main_arena_bytes'] != 0x4000 or layout['dmi_arena_bytes'] != 0x3a00: die('Linux arena geometry drift')

    required=[
      '#include <linux/unaligned.h>',
      '#define CAMSS_RTCDM1_CORPUS_PACKET_COUNT\t4',
      '#define CAMSS_RTCDM1_CORPUS_PAYLOAD_COUNT\t16',
      '#define CAMSS_RTCDM1_CORPUS_DMI_COUNT\t\t46',
      '#define CAMSS_RTCDM1_CORPUS_DYNAMIC_COUNT\t20',
      '#define CAMSS_RTCDM1_CORPUS_MAIN_SIZE\t\tSZ_16K',
      '#define CAMSS_RTCDM1_CORPUS_DMI_SIZE\t\t0x3a00',
      '#define CAMSS_RTCDM1_CORPUS_DYNAMIC_VALID\tGENMASK(19, 0)',
      'input->dynamic_valid != CAMSS_RTCDM1_CORPUS_DYNAMIC_VALID',
      'get_unaligned_le32(main + ref->field)',
      'get_unaligned_le32(main + patch->field)',
      'put_unaligned_le32((u32)dma, field);',
      'put_unaligned_le32(input->dynamic[i], field);',
      'memcpy(main + slot, input->main[i].data, input->main[i].size);',
      'memcpy(dmi + desc->offset, input->payload[i].data, desc->size);',
      'u32 slot = i * SZ_4K;',
      '(u64)d + size - 1 > U32_MAX',
      'camss_rtcdm1_corpus_recipe __used = {'
    ]
    for x in required: need(src,x,'source contract drift')

    # Exact packet lengths.
    pb=block(src,'camss_rtcdm1_corpus_packet_used')
    got=[int(x,16) for x in re.findall(r'0x([0-9a-fA-F]+)',pb)]
    exp=[x['used_bytes'] for x in layout['main_slots']]
    if got != exp: die(f'packet used table drift: {got!r} != {exp!r}')

    # Compact Linux payload layout; hashes stay out of kernel source.
    pbody=block(src,'camss_rtcdm1_corpus_payloads')
    got=[(int(a,16),int(b,16)) for a,b in re.findall(r'\.offset = 0x([0-9a-fA-F]+), \.size = 0x([0-9a-fA-F]+)',pbody)]
    exp=[(int(x['linux_offset'],16),x['bytes']) for x in oracle['payload_catalog']]
    if got != exp: die('payload compact-layout table drift')

    # 46 DMI fields map only to Linux payload IDs, never Windows source offsets.
    dbody=block(src,'camss_rtcdm1_corpus_dmi_refs')
    got=[(int(p),int(q),int(f,16)) for p,q,f in re.findall(r'\.packet = (\d+), \.payload = (\d+), \.field = 0x([0-9a-fA-F]+)',dbody)]
    exp=[(x['packet'],x['payload_id'],int(x['address_field_offset'],16)) for x in oracle['dmi_references']]
    if got != exp: die('DMI patch table drift')

    # 20 explicit caller values include period_cfg + the five prior live-volatile offsets.
    ybody=block(src,'camss_rtcdm1_corpus_dynamic')
    got=[(int(p),int(f,16),int(r,16)) for p,f,r in re.findall(r'\.packet = (\d+), \.field = 0x([0-9a-fA-F]+), \.reg = 0x([0-9a-fA-F]+)',ybody)]
    exp=[(x['packet'],int(x['value_field_offset'],16),int(x['register_offset'],16)) for x in oracle['dynamic_value_fields']]
    if got != exp: die('dynamic patch table drift')

    # No captured bytes, addresses, or Windows allocation geometry are embedded.
    if 'static const u8' in patch: die('0019 embeds captured byte arrays')
    if patch.lower().count('0xa000') != 1 or "does not reproduce Windows' 0xa000" not in patch:
        die('Windows 0xa000 main-slot stride frozen or policy comment drift')
    for d in oracle['dynamic_value_fields']:
        for key in ('initial_value','final_value'):
            val=d[key].lower()
            if val in patch.lower(): die('captured dynamic value frozen: '+val)
    # Final capture DMI IOVAs are also forbidden.
    patch_summary=json.loads((a.oracle.parent/'windows-ife-cdm/patch-dmi-summary.json').read_text())
    for pkt in patch_summary['packets']:
        for d in pkt['dmi']:
            if d['data_iova'].lower() in patch.lower(): die('Windows DMI IOVA frozen: '+d['data_iova'])

    # 0019 is memory materialization only: no RT-CDM/VFE MMIO, IRQ arm or FIFO submission.
    for bad in ('writel_relaxed(', 'readl_relaxed(', 'enable_irq(', 'disable_irq(',
                'camss_rtcdm1_windows_fifo0_commit(', 'camss_rtcdm1_windows_start(',
                'camss_rtcdm1_windows_open_init(', 'vfe_enable_v2(', 'vfe_buf_done('):
        if bad in patch: die('0019 connects hardware/runtime path: '+bad)
    if patch.count('--- a/drivers/media/platform/qcom/camss/camss.c') != 1 or patch.count('--- a/') != 1:
        die('0019 path set drift')

    # Existing X1E VFE1 PIX gate must remain fail-closed before stream lock.
    m=re.search(r'int vfe_enable_v2\(struct vfe_line \*line\)\n\{(.*?)\n\}',vfe,re.S)
    if not m: die('vfe_enable_v2 missing')
    b=m.group(1); gate=b.find('return -EOPNOTSUPP;'); lock=b.find('mutex_lock(&vfe->stream_lock)')
    if gate < 0 or lock < 0 or gate >= lock: die('PIX stream gate no longer precedes runtime setup')

    # Retention is the only external reference to materialize/release. The
    # recipe object itself must have no relocation/caller.
    rel=run('aarch64-linux-gnu-objdump','-r',str(a.object))
    h=['camss_rtcdm1_corpus_materialize','camss_rtcdm1_corpus_release']
    hrel=[ln.strip() for ln in rel.splitlines() if any(x in ln for x in h)]
    if len(hrel)!=2 or any('R_AARCH64_ABS64' not in x for x in hrel): die('materializer helper relocation set drift: '+repr(hrel))
    if 'camss_rtcdm1_corpus_recipe' in rel: die('compiled relocation references corpus recipe')
    if src.count('camss_rtcdm1_corpus_recipe') != 1: die('corpus recipe source reference count drift')
    nm=run('aarch64-linux-gnu-nm','-an',str(a.module))
    for x in h+['camss_rtcdm1_corpus_recipe']:
        if x not in nm: die('retained module symbol missing '+x)
    vermagic=run('modinfo','-F','vermagic',str(a.module)).strip()
    if vermagic != '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64': die('Golden vermagic drift: '+vermagic)

    out={
      'schema':'sp11-e003h-linux-rtcdm-corpus-materializer-inspection-v1','accepted':True,
      'source_sha256':sha(a.source),'object_sha256':sha(a.object),'module_sha256':sha(a.module),'patch_sha256':sha(a.patch),
      'oracle_sha256':sha(a.oracle),'static_proof_sha256':sha(a.static_proof),
      'corpus':{'packets':4,'commands':278,'ordinary_register_writes':2131,'dmi_commands':46,'unique_payloads':16,'caller_dynamic_values':20},
      'linux_layout':{'main_arena_bytes':0x4000,'main_slots':'4 x 4KiB','dmi_arena_bytes':0x3a00,'payload_alignment':64,
                      'windows_main_slot_stride_frozen':False,'windows_dmi_source_offsets_frozen':False},
      'dynamic_policy':{'period_cfg_0x8c_caller_supplied':True,'prior_live_volatile_offsets':['0x3b70','0x3d78','0x3d7c','0x3d80','0x3d84'],
                        'valid_mask_required':'0x000fffff','normalized_holes_must_be_zero':True},
      'runtime_isolation':{'recipe_source_reference_count':1,'recipe_compiled_relocation_present':False,'helper_relocations':hrel,
                           'mmio_or_irq_or_fifo_submission_added':False,'pix_stream_gate':'-EOPNOTSUPP before stream lock/IRQ/output'},
      'raw_corpus_embedded':False,'windows_iovas_frozen':False,
      'policy':'static-only materialization; no module load, RT-CDM FIFO0 submission, VFE1 PIX enable, sensor transmission or frame authorized'}
    txt=json.dumps(out,indent=2,sort_keys=True)+'\n'
    if a.output: a.output.write_text(txt)
    else: print(txt,end='')
    print('PASS: RT-CDM corpus materializer is Linux-addressed, dynamic-hole exact, retained-only and disconnected from MMIO/FIFO/runtime')

if __name__=='__main__': main()
