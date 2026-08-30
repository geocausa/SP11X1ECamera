#!/usr/bin/env python3
import hashlib, json, re
from pathlib import Path

D=Path(__file__).resolve().parent
ROOT=D.parent
EXPECTED={
 'boundary':('E003H_RTCDM_BL_BOUNDARIES_20260830.log',174214,'8e285eaf8bd8ace1cd5f82b59b4209a3824dc67b78bf0f317cbb123e91568c19'),
 'content':('E003H_RTCDM_BL_CONTENT_FIRSTSTART_20260830.log',3656,'8fcde86f2577caaf292df6ce535b98efb5d5140a8eeef8afeee827805a928a9f'),
 'post':('E003H_RTCDM_POST_ENABLE_RUP_MASKS_20260830.log',145562,'3f84acd8bdb9915241a96f18d1cf8f28d07ef37487668b360a1796f261373037'),
 'static':('E003H_RUP_COMMIT_FUNC_20260830.txt',32324,'fce1aabcc6310f0a6eafc2b55475ac5bc81e6dea584eeded9cae428cf7841e5d'),
}
QCCAMISP_SHA='64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c'
OLD_CSID_ORACLE_SHA='01960da41376809d694c6aa2336ecef6ff4c010abfa29e4674b1a68d303c3cda'
OLD_ORDER_ORACLE_SHA='0a2cec61ba2707ebf5b4899128d99c1f79aa931605383c24bd0b98d99f23ae1e'

def die(x): raise SystemExit('FAIL: '+x)
def sha(b): return hashlib.sha256(b).hexdigest()
def load(k):
    n,z,h=EXPECTED[k]; p=D/n; b=p.read_bytes()
    if len(b)!=z: die(f'{k} bytes {len(b)} != {z}')
    if sha(b)!=h: die(f'{k} sha drift {sha(b)} != {h}')
    try: s=b.decode('utf-16')
    except UnicodeError as e: die(f'{k} UTF-16 decode: {e}')
    return s

def events(s): return [x.strip() for x in s.splitlines() if x.strip().startswith('EV ')]
def need(cond,msg):
    if not cond: die(msg)

def parse_commit(line):
    f=dict(re.findall(r'([a-z0-9]+)=([0-9a-f]+)',line,re.I))
    return {k:v.lower() for k,v in f.items()}

def main():
    bnd=load('boundary'); con=load('content'); post=load('post'); sta=load('static')
    # Independent prior same-machine CSID oracle remains the physical/register anchor.
    old=(ROOT/'windows-csid1-ipp-start-oracle.json').read_bytes()
    order=(ROOT/'windows-csid1-config-rup-enable-order-oracle.json').read_bytes()
    need(sha(old)==OLD_CSID_ORACLE_SHA,'prior CSID oracle hash drift')
    need(sha(order)==OLD_ORDER_ORACLE_SHA,'prior order oracle hash drift')
    src=(ROOT/'extract_csid1_ipp_start_oracle.py').read_text()
    need('CSID1_BASE = 0x0acb9000' in src,'CSID1 physical base anchor drift')

    # Static qccamisp generic queue commit: base, encoded length, trigger.
    for x in (
      '=== code RVA 0x28884 @ 140028884 func=FUN_140028480@140028480 ===',
      '*(uint *)(*(longlong *)(puVar11 + 0x12) + 0x50) = uVar1;',
      '*(uint *)(*(longlong *)(puVar11 + 0x12) + 0x54) = uVar2 & 0xfffff | 0x100000;',
      '*(undefined4 *)(*(longlong *)(puVar11 + 0x12) + 0x58) = 1;',
    ): need(x in sta,'static queue contract missing '+x)

    ce=events(con)
    need(ce and ce[0]=='EV CFGDONE id=00000001 ctrl=00000000 irq=3c1c7004 top=00000001','content CFGDONE drift')
    need(ce[-1]=='EV ENABLE_ENTER id=00000001 sel=00000005 ctrl=00000000 irq=3c1c7004 top=00000001','content enable boundary drift')
    cc=[parse_commit(x) for x in ce if x.startswith('EV COMMIT')]
    need(len(cc)==9,f'expected 9 pre-enable commits, got {len(cc)}')
    expected=[
      ('00100003','0800f000'), ('00100e93','03000001'), ('00100003','08057000'), ('0010003b','03000001'),
      ('00100003','0800f000'), ('00100e33','03000001'), ('00100003','08057000'), ('0010000f','03000002'),
      ('00100013','04000001'),
    ]
    need([(x.get('lenenc'),x.get('w0')) for x in cc]==expected,'pre-enable BL base/length/content sequence drift')
    need(cc[0].get('w1')=='0803c000' and cc[0].get('w2')=='08057000','replay0 arena adjacency drift')
    need(cc[4].get('w1')=='0803c000' and cc[4].get('w2')=='08057000','replay1 arena adjacency drift')
    need(cc[8].get('w1')=='00000018' and cc[8].get('w2')=='01f501f5','replay1 RUP/AUP drift')
    need(not any(x.get('w0')=='0803c000' for x in cc),'0x0803c000 unexpectedly submitted pre-enable')

    pe=events(post)
    need(sum(x.startswith('EV ENABLE_ENTER') for x in pe)==1,'post trace enable-enter count drift')
    need(sum(x.startswith('EV ENABLE_DONE') for x in pe)==1,'post trace enable-done count drift')
    ei=next(i for i,x in enumerate(pe) if x.startswith('EV ENABLE_ENTER'))
    ed=next(i for i,x in enumerate(pe) if x.startswith('EV ENABLE_DONE'))
    need(pe[ei]=='EV ENABLE_ENTER id=00000001 sel=00000005','hidden/non-IPP CSID path enable observed')
    need(ed==ei+1,'enable done ordering drift')
    pc=[parse_commit(x) for x in pe if x.startswith('EV COMMIT')]
    # Every submitted 20-byte REG_RANDOM+GEN_IRQ block in the bounded capture uses the combined all-path RUP/AUP value.
    rups=[x for x in pc if x.get('lenenc')=='00100013' and x.get('w0')=='04000001' and x.get('w1')=='00000018']
    need(len(rups)>=3,'insufficient submitted RUP/AUP blocks')
    need(all(x.get('w2')=='01f501f5' for x in rups),'split/non-combined RUP/AUP block submitted')
    tags=[int(x.get('w4','ffffffff'),16) for x in rups[:4]]
    need(tags[:3]==[1,2,3],f'first replay RUP tags drift {tags[:3]}')
    need(not any(x.get('w0')=='0803c000' for x in pc),'0x0803c000 unexpectedly submitted post-enable')

    be=events(bnd)
    need(any(x.startswith('EV CFGDONE id=00000001') for x in be),'boundary CFGDONE absent')
    need(sum(x.startswith('EV ENABLE_ENTER id=00000001 sel=00000005') for x in be)==1,'boundary selector-5 count drift')
    # Encoded lengths seen live corroborate static length-1 semantics for the fixed BLs.
    for enc in ('00100003','0010000f','00100013'):
        need(any(('lenenc='+enc) in x for x in be if x.startswith('EV COMMIT')),f'live lenenc {enc} absent')

    out={
      'schema':'sp11-e003h-windows-rtcdm-bl-boundaries-v1','accepted':True,'date':'2026-08-30',
      'machine':'same SP11 X1E80100 Windows oracle','driver':{'name':'qccamisp8380.sys','sha256':QCCAMISP_SHA},
      'qccamisp_static_commit':{
        'function_rva':'0x28480','mmio_commit_instruction_rva':'0x28884',
        'fifo0_base_register_offset':'0x50','fifo0_length_register_offset':'0x54','fifo0_trigger_register_offset':'0x58',
        'length_encoding':'(BL byte length - 1) in low 20 bits, OR 0x00100000',
        'proved_examples':{'0x00100003':4,'0x0010000f':16,'0x00100013':20},
      },
      'first_start_pre_enable':{
        'order':['CSID1 configure CTRL=0','CHANGE_BASE VFE1 0x0000f000','priming main0','CHANGE_BASE CSID1 0x00057000','CSID companion0','CHANGE_BASE VFE1 0x0000f000','priming main1','CHANGE_BASE CSID1 0x00057000','CSID companion1','REG_RANDOM CSID1 +0x18=0x01f501f5 + GEN_IRQ tag1','CSID1 enable selector5'],
        'adjacent_0x0803c000_submitted':False,
        'arena_layout_note':'At both VFE1 CHANGE_BASE commits, the live arena contains 0x0800f000 at +0, 0x0803c000 at +4, 0x08057000 at +8. Hardware commit length is exactly four bytes at +0, then later exactly four bytes at +8; +4 is skipped.',
        'combined_rup_aup':'0x01f501f5',
      },
      'post_enable':{
        'only_csid1_path_selector_enabled':5,'selector_meaning':'IPP','hidden_rdi_or_ppp_enable_observed':False,
        'replay2_rup_aup':'0x01f501f5','replay3_rup_aup':'0x01f501f5','steady_rup_aup':'0x01f501f5',
        'lower_only_0x000001f5_submitted':False,'upper_only_0x01f50000_submitted':False,
      },
      'physical_crosscheck':{
        'rtcdm_anchor':'0x0ac62000','vfe1_change_base':'0x0000f000','vfe1_physical':'0x0ac71000',
        'csid1_change_base':'0x00057000','csid1_physical':'0x0acb9000',
        'note':'CSID1 physical base is independently pinned by the existing same-machine CSID oracle; this session also manually observed PFN 0xacb9 via !pte.'
      },
      'corrections_to_prior_interpretation':[
        'The old manual dd arena sequence 0800f000 0803c000 08057000 must not be decoded as one submitted command stream.',
        '0x0803c000 is adjacent arena data skipped by the FIFO BL descriptors; do not add it to Linux.',
        'Adjacent lower-only/upper-only RUP values are not replay2/replay3 submissions; actual submitted replay1/replay2/replay3 and steady RUP/AUP blocks use 0x01f501f5.'
      ],
      'linux_consequence':'Retain the current Linux BL boundary model: 4-byte 0x0800f000 wrapper, main list, 4-byte 0x08057000 companion base, companion list, and combined 0x01f501f5 RUP/AUP+GEN_IRQ. No 0x0803c000 or split-mask delta is justified.',
      'raw_evidence':{k:{'file':EXPECTED[k][0],'bytes':EXPECTED[k][1],'sha256':EXPECTED[k][2]} for k in EXPECTED},
      'prior_oracles':{'windows_csid1_ipp_start_sha256':OLD_CSID_ORACLE_SHA,'windows_config_rup_enable_order_sha256':OLD_ORDER_ORACLE_SHA},
      'runtime_authorized':False,
      'next_gate':'Find the first Windows CSID1 state transition after sensor-on that produces RUP_DONE/CAMIF/Epoch; current BL content, boundaries, bases, masks, and active path set are closed.'
    }
    p=D/'windows-rtcdm-bl-boundaries-oracle.json'; p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))
    print('PASS: Windows RT-CDM BL boundaries and submitted CSID RUP/AUP content are exact')

if __name__=='__main__': main()
