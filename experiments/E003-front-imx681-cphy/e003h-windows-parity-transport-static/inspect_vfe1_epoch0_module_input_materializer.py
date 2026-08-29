#!/usr/bin/env python3
import argparse, hashlib, json, re, subprocess, tempfile
from pathlib import Path

BATCH_ORACLE_SHA='3bcf4efe34c891dcc6bc78c3cefc94d916ffd71e27dab81e75493f9ed320dce4'
PRODUCER_ORACLE_SHA='cbd8908d967f4831e67f8eb3c36ae9799c4bcb42e1923f0ee34c2152841c03ef'
PROOF_SHA='7c4b37c2579bd1bf4eae8e1756a7557cad9505929bbc21a986855209af94b4bc'
BASE_SOURCE_SHA='fd1baf78bcba6f3cf926f66ea7fcb8b212e0659048a9187ed67011a5066c20c5'
EXPECTED=[(0x958,24,14,56,472),(0x868,20,12,45,436),(0x83c,14,12,43,429),(0x6b8,10,8,35,352),(0x5a4,6,2,22,315)]
EXPECTED_MODULES={
 'DemuxBLS141':{'regs':['0x3b70','0x3b74'],'dmi':[]},
 'PDPC311':{'regs':['0x3d58','0x3d5c','0x3d78','0x3d7c','0x3d80','0x3d84'],'dmi':['0x3d08:1:0x200']},
 'LSC411':{'regs':['0x4358','0x435c'],'dmi':['0x4308:1:0x374','0x4308:2:0x374','0x4308:3:0x374']},
 'WB201':{'regs':['0x456c','0x4570'],'dmi':[]},
 'GIC311':{'regs':['0x4758','0x475c'],'dmi':['0x4708:1:0x200']},
 'BPCABF411':{'regs':['0x4958','0x495c'],'dmi':['0x4908:1:0x100']},
 'GTM131':{'regs':['0x5a58','0x5a5c'],'dmi':['0x5a08:1:0x800']},
 'Gamma151':{'regs':['0x5f58','0x5f5c'],'dmi':['0x5f08:1:0x400','0x5f08:2:0x400','0x5f08:3:0x400']},
 'DSX101':{'regs':['0xa058','0xa05c','0xa258','0xa25c'],'dmi':['0xa008:1:0x300','0xa008:2:0x300','0xa208:1:0x180','0xa208:2:0x180']},
}

def die(s): raise SystemExit('FAIL: '+s)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(*a): return subprocess.check_output(a,text=True,stderr=subprocess.STDOUT)
def need(s,x,label):
    if x not in s: die(f'{label}: missing {x}')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,required=True); ap.add_argument('--base-source',type=Path,required=True)
    ap.add_argument('--vfe-source',type=Path,required=True); ap.add_argument('--object',type=Path,required=True); ap.add_argument('--module',type=Path,required=True)
    ap.add_argument('--patch',type=Path,required=True); ap.add_argument('--batch-oracle',type=Path,required=True); ap.add_argument('--producer-oracle',type=Path,required=True)
    ap.add_argument('--proof',type=Path,required=True); ap.add_argument('--build-log',type=Path,required=True); ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    if sha(a.base_source)!=BASE_SOURCE_SHA: die('0024 base source identity drift')
    if sha(a.batch_oracle)!=BATCH_ORACLE_SHA: die('0024 batch oracle identity drift')
    if sha(a.producer_oracle)!=PRODUCER_ORACLE_SHA: die('upstream producer oracle identity drift')
    if sha(a.proof)!=PROOF_SHA: die('materializer proof identity drift')
    batch=json.loads(a.batch_oracle.read_text()); prod=json.loads(a.producer_oracle.read_text()); proof=json.loads(a.proof.read_text())
    if not batch.get('accepted') or not prod.get('accepted') or not proof.get('accepted'): die('upstream evidence not accepted')
    got=[(v['main_bytes'],len(v['dynamic_register_fields']),v['dmi_count'],v['command_count'],v['register_write_count']) for v in batch['main_bl_variants']]
    if got!=EXPECTED: die(f'variant census drift {got!r}')
    for name,exp in EXPECTED_MODULES.items():
        gotm=prod['module_map'].get(name)
        if not gotm or gotm.get('dynamic_registers')!=exp['regs'] or gotm.get('dmi')!=exp['dmi']:
            die(f'producer module map drift: {name}')
    pg=[(int(v['variant'],16),v['commands'],v['register_writes'],v['dmi_commands'],v['bl_lengths']) for v in proof['variants']]
    expected_pg=[(n,c,w,d,[4,n,4,16,20]) for n,_,d,c,w in EXPECTED]
    if pg!=expected_pg: die(f'proof topology drift {pg!r}')
    if proof['windows_addresses_reused'] or proof['captured_payload_bytes_embedded'] or proof['fifo_submission_performed']: die('proof safety drift')

    src=a.source.read_text(); patch=a.patch.read_text()
    required=[
      '#define CAMSS_X1E_EPOCH0_CMD_SIZE\t\tSZ_4K','#define CAMSS_X1E_EPOCH0_DMI_SIZE\t\t0x3000',
      '#define CAMSS_X1E_EPOCH0_MODULE_REG_MAX\t6','#define CAMSS_X1E_EPOCH0_MODULE_PAYLOAD_MAX\t4',
      'struct camss_x1e_epoch0_input {','u64 request_id;','u32 subrequest;',
      'if (!input || !input->normalized_main.data || !input->request_id ||','input->subrequest)',
      'module->value_valid != expected_value[i] ||','module->payload_valid != expected_payload[i]',
      'get_unaligned_le32(main + patch->field))','put_unaligned_le32(lower_32_bits(input->request_id),',
      'camss_rtcdm1_corpus_alloc(camss->dev,','CAMSS_X1E_EPOCH0_CMD_SIZE,','CAMSS_X1E_EPOCH0_DMI_SIZE,',
      'camss_x1e_epoch0_recipe __used = {','.materialize = camss_x1e_epoch0_materialize,','.release = camss_x1e_epoch0_release,',
      'static_assert(ARRAY_SIZE(camss_x1e_epoch0_payloads) == 14);',
      'static_assert(ARRAY_SIZE(camss_x1e_epoch0_reg_v0) == 24);','static_assert(ARRAY_SIZE(camss_x1e_epoch0_dmi_v0) == 14);',
      'static_assert(ARRAY_SIZE(camss_x1e_epoch0_reg_v1) == 20);','static_assert(ARRAY_SIZE(camss_x1e_epoch0_dmi_v1) == 12);',
      'static_assert(ARRAY_SIZE(camss_x1e_epoch0_reg_v2) == 14);','static_assert(ARRAY_SIZE(camss_x1e_epoch0_dmi_v2) == 12);',
      'static_assert(ARRAY_SIZE(camss_x1e_epoch0_reg_v3) == 10);','static_assert(ARRAY_SIZE(camss_x1e_epoch0_dmi_v3) == 8);',
      'static_assert(ARRAY_SIZE(camss_x1e_epoch0_reg_v4) == 6);','static_assert(ARRAY_SIZE(camss_x1e_epoch0_dmi_v4) == 2);',
    ]
    for x in required: need(src,x,'source contract drift')
    for n,regs,dmis,_,_ in EXPECTED:
        need(src,f'.main_bytes = 0x{n:04x}',f'variant 0x{n:x}')
    # Compact Linux-only DMI offsets and exact payload sizes.
    for x in ('0x0000, .size = 0x0200','0x0200, .size = 0x0374','0x0580, .size = 0x0374','0x0900, .size = 0x0374',
              '0x0c80, .size = 0x0200','0x0e80, .size = 0x0100','0x0f80, .size = 0x0800','0x1780, .size = 0x0400',
              '0x1b80, .size = 0x0400','0x1f80, .size = 0x0400','0x2380, .size = 0x0300','0x2680, .size = 0x0300',
              '0x2980, .size = 0x0180','0x2b00, .size = 0x0180'):
        need(src,x,'DMI compact layout drift')
    # Companion encodings mechanically match 0024; no captured main/payload byte arrays in patch.
    for x in ('0x0800f000','0x08057000','0x03000002','0x0000035c','0x0eff0000','0x086f0000','0x04000001','0x01f501f5','0x06000000'):
        need(src,x,'companion BL encoding drift')
    for forbidden in ('+static const u8 ', '+static const unsigned char ', '0x17a', '0x17b', 'fifo0_commit(', 'writel(', 'readl(', 'enable_irq(', 'request_irq(', 'vfe_enable_v2(', 'csid_set_stream'):
        if forbidden in patch: die('0025 embeds captured/runtime behavior: '+forbidden)
    if patch.count('--- a/drivers/media/platform/qcom/camss/camss.c')!=1 or patch.count('--- a/')!=1: die('0025 path set drift')

    # Patch round trip is byte exact against the accepted 0024 source.
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); f=root/'drivers/media/platform/qcom/camss/camss.c'; f.parent.mkdir(parents=True); f.write_bytes(a.base_source.read_bytes())
        subprocess.check_call(['patch','-d',str(root),'-p1'],stdin=a.patch.open('rb'),stdout=subprocess.DEVNULL)
        if f.read_bytes()!=a.source.read_bytes(): die('forward reconstruction mismatch')
        subprocess.check_call(['patch','-d',str(root),'-p1','-R'],stdin=a.patch.open('rb'),stdout=subprocess.DEVNULL)
        if f.read_bytes()!=a.base_source.read_bytes(): die('reverse reconstruction mismatch')

    # Existing VFE1 PIX hard gate stays before stream lock/IRQ/output work.
    vfe=a.vfe_source.read_text(); m=re.search(r'int vfe_enable_v2\(struct vfe_line \*line\)\n\{(.*?)\n\}',vfe,re.S)
    if not m: die('vfe_enable_v2 missing')
    body=m.group(1); gate=body.find('return -EOPNOTSUPP;'); lock=body.find('mutex_lock(&vfe->stream_lock)')
    if gate<0 or lock<0 or gate>=lock: die('VFE1 PIX fail-close drift')

    rel=run('aarch64-linux-gnu-objdump','-r',str(a.object))
    if rel.count('R_AARCH64_ABS64   camss_x1e_epoch0_materialize')!=1 or rel.count('R_AARCH64_ABS64   camss_x1e_epoch0_release')!=1: die('recipe retention relocation drift')
    if 'R_AARCH64_' in '\n'.join(line for line in rel.splitlines() if 'camss_x1e_epoch0_recipe' in line): die('runtime relocation to recipe')
    nm=run('aarch64-linux-gnu-nm','-an',str(a.object)); nmm=run('aarch64-linux-gnu-nm','-an',str(a.module))
    for sym in ('camss_x1e_epoch0_recipe','camss_x1e_epoch0_materialize','camss_x1e_epoch0_release'):
        if sym not in nm or sym not in nmm: die('retained symbol missing '+sym)
    dis=run('aarch64-linux-gnu-objdump','-dr',str(a.object))
    mm=re.search(r'<camss_x1e_epoch0_materialize>:(.*?)(?=\n[0-9a-f]+ <|\Z)',dis,re.S)
    if not mm: die('materializer disassembly missing')
    calls=set(re.findall(r'R_AARCH64_CALL26\s+([^\s+]+)',mm.group(1)))
    allowed={'memcpy','__stack_chk_fail','__ubsan_handle_out_of_bounds','__ubsan_handle_load_invalid_value'}
    # Local resolved calls appear as direct symbol text rather than relocations.
    if 'camss_rtcdm1_corpus_alloc' not in mm.group(1) or 'camss_x1e_epoch0_release' not in mm.group(1): die('expected memory helper calls missing')
    for bad in ('camss_rtcdm1_windows_fifo0_commit','camss_rtcdm1_windows_start','camss_rtcdm1_windows_open_init','writel','readl','enable_irq','vfe_enable','csid_set_stream'):
        if bad in mm.group(1): die('materializer hardware call '+bad)

    build=a.build_log.read_text(); diag=[x for x in build.splitlines() if re.search(r'(^|:)\s*(warning|error):',x,re.I)]
    if diag: die('compiler diagnostics '+repr(diag[:4]))
    vermagic=run('modinfo','-F','vermagic',str(a.module)).strip()
    if not vermagic.startswith('7.1.5-sp11-render-parity-v4+'): die('Golden vermagic drift')
    out={'schema':'sp11-e003h-vfe1-epoch0-module-input-materializer-inspection-v1','accepted':True,
         'batch_oracle_sha256':BATCH_ORACLE_SHA,'producer_oracle_sha256':PRODUCER_ORACLE_SHA,'proof_sha256':PROOF_SHA,
         'base_source_sha256':BASE_SOURCE_SHA,'source_sha256':sha(a.source),'object_sha256':sha(a.object),'module_sha256':sha(a.module),
         'patch_sha256':sha(a.patch),'build_log_sha256':sha(a.build_log),'vermagic':vermagic,
         'materializer':{'variants':5,'linux_cmd_arena_bytes':0x1000,'linux_dmi_arena_bytes':0x3000,'dmi_payload_slots':14,
                         'request_rule':'GEN_IRQ userdata = low32(request_id), subrequest must be zero','captured_main_template_embedded':False,
                         'captured_payload_embedded':False,'windows_iova_embedded':False,'fifo0_submission':False,'direct_mmio':False},
         'runtime_isolation':{'recipe_abs64_relocations':2,'relocation_to_recipe':False,'pix_stream_gate':'-EOPNOTSUPP before stream lock/IRQ/output'},
         'reconstruction':{'forward_byte_exact':True,'reverse_byte_exact':True},
         'policy':'unreachable consumer/materializer only; caller must supply normalized shape plus named module outputs; no CamX algorithm reimplementation claimed and no front hardware execution authorized'}
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('PASS: 0025 materializes all five steady Epoch0 shapes from named module inputs into Linux-owned arenas and remains unreachable/no-submit')

if __name__=='__main__': main()
