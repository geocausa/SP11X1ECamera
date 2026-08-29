#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, importlib.util, json, re, struct

LOG_SHA = {
    'E003H_VFE1_DYNFIELD_CADENCE_20260829.log': 'c450fe3e9053a2e2fc522a46f0fea9ea85d4d21ae921eb9c6c159e6baf60546a',
    'E003H_VFE1_DYNFIELD_KMD_PASS_20260829.log': 'f721edb7dadc4f3c551f3b933b633e4882b9fead793c9f9e7960ff863334346f',
    'E003H_VFE1_DYNFIELD_PRODUCER_20260829.log': 'a70534c7a13a374e8f8258e0c134d56bcf182d4d64be1d33b0b7ffbf4b1fde0d',
}
PERIOD = 0x8c
LIVE_MUTABLE = [0x3b70, 0x3d78, 0x3d7c, 0x3d80, 0x3d84]

def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(p): return sha_bytes(Path(p).read_bytes())
def die(s): raise SystemExit('FAIL: ' + s)
def hx(v): return f'0x{v:x}'

def load(path, name):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def decode_utf16(p): return p.read_bytes().decode('utf-16').splitlines()

def parse_kmd(lines):
    before={}; after={}
    full=re.compile(r'^(BEFORE p=?([0-2])|AFTER p([0-2]))(?: main=[0-9a-f]+)? b70=([0-9a-f]+) d78=([0-9a-f]+) d7c=([0-9a-f]+) d80=([0-9a-f]+) d84=([0-9a-f]+) period=([0-9a-f]+)$',re.I)
    p3=re.compile(r'^(BEFORE p3|AFTER p3) b70=([0-9a-f]+) period=([0-9a-f]+)$',re.I)
    for l in lines:
        m=full.match(l)
        if m:
            label=m.group(1); pi=int(m.group(2) if m.group(2) is not None else m.group(3))
            vals={'0x3b70':int(m.group(4),16),'0x3d78':int(m.group(5),16),'0x3d7c':int(m.group(6),16),
                  '0x3d80':int(m.group(7),16),'0x3d84':int(m.group(8),16),'0x8c':int(m.group(9),16)}
            (before if label.startswith('BEFORE') else after)[pi]=vals
            continue
        m=p3.match(l)
        if m:
            vals={'0x3b70':int(m.group(2),16),'0x8c':int(m.group(3),16)}
            (before if m.group(1).startswith('BEFORE') else after)[3]=vals
    if set(before)!=set(range(4)) or set(after)!=set(range(4)): die('KMD before/after packet coverage drift')
    if before != after: die('qccamisp +0x26838 changed dynamic/startup fields')
    return before

def parse_cadence(lines):
    samples=[]; cur=None
    for l in lines:
        m=re.match(r'^===CADENCE([123])===$',l)
        if m: cur={'sample':int(m.group(1))}; samples.append(cur); continue
        if cur is None: continue
        m=re.match(r'^# ac7108c ([0-9a-f]+)$',l,re.I)
        if m: cur['period']=int(m.group(1),16); continue
        m=re.match(r'^# ac74b70 ([0-9a-f]+)$',l,re.I)
        if m: cur['b70']=int(m.group(1),16); continue
        m=re.match(r'^# ac74d78 ([0-9a-f]+) ([0-9a-f]+) ([0-9a-f]+) ([0-9a-f]+)$',l,re.I)
        if m: cur['d78_84']=[int(m.group(i),16) for i in range(1,5)]
    if len(samples)!=3 or any(set(x)!={'sample','period','b70','d78_84'} for x in samples): die('cadence sample parse drift')
    if {x['period'] for x in samples}!={0}: die('live period_cfg did not read back zero')
    if len({x['b70'] for x in samples})!=1: die('live +0x3b70 changed across bounded cadence samples')
    if len({tuple(x['d78_84']) for x in samples})<2: die('live +0x3d78..84 did not change')
    return samples

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--windows-dir',type=Path,required=True)
    ap.add_argument('--dynamic-dir',type=Path,required=True)
    ap.add_argument('--old-oracle',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()

    for fn,exp in LOG_SHA.items():
        p=a.dynamic_dir/fn
        if not p.exists() or sha_file(p)!=exp: die('dynamic log identity drift: '+fn)
    old=json.loads(a.old_oracle.read_text())
    if not old.get('accepted') or old['closure']['caller_supplied_dynamic_value_fields']!=20: die('0019 oracle closure drift')

    fields=old['dynamic_value_fields']
    period=[x for x in fields if int(x['register_offset'],16)==PERIOD]
    template=[x for x in fields if int(x['register_offset'],16)!=PERIOD]
    if len(period)!=4 or len(template)!=16: die('20-field split drift')
    if {int(x['register_offset'],16) for x in template} != set(LIVE_MUTABLE): die('startup-template register set drift')
    if any(x['initial_value']!=x['final_value'] for x in template): die('startup-template field changed across independent command captures')
    if any(x['initial_value']==x['final_value'] for x in period): die('period_cfg unexpectedly invariant across independent command captures')

    kmd=parse_kmd(decode_utf16(a.dynamic_dir/'E003H_VFE1_DYNFIELD_KMD_PASS_20260829.log'))
    cadence=parse_cadence(decode_utf16(a.dynamic_dir/'E003H_VFE1_DYNFIELD_CADENCE_20260829.log'))

    # Recompute the independent startup-capture normalization, but zero only
    # Linux-rewritten DMI addresses and the four start-dependent period words.
    mod=load(a.old_oracle.parent/'extract_rtcdm_corpus_materializer.py','e003h_0019_extract')
    initial=[(a.windows_dir/f'packet{i}-main-cdm.bin').read_bytes() for i in range(4)]
    final,_=mod.final_main_streams(a.windows_dir)
    dmi={i:[] for i in range(4)}
    for r in old['dmi_references']: dmi[r['packet']].append(int(r['address_field_offset'],16))
    pp={x['packet']:int(x['value_field_offset'],16) for x in period}
    refined=[]
    for pi in range(4):
        x=bytearray(initial[pi]); y=bytearray(final[pi])
        for o in dmi[pi]: x[o:o+4]=b'\0'*4; y[o:o+4]=b'\0'*4
        x[pp[pi]:pp[pi]+4]=b'\0'*4; y[pp[pi]:pp[pi]+4]=b'\0'*4
        if x!=y: die(f'packet {pi} differs after DMI+period-only normalization')
        refined.append({'packet':pi,'used_bytes':len(x),'normalized_sha256':sha_bytes(x),
                        'period_field_offset':hx(pp[pi]),
                        'period_initial':period[pi]['initial_value'],'period_final':period[pi]['final_value']})

    # Fresh KMD capture must reproduce the invariant startup-template words.
    for x in template:
        pi=x['packet']; ro=hx(int(x['register_offset'],16))
        if ro not in kmd[pi]: die(f'fresh KMD packet {pi} missing {ro}')
        if kmd[pi][ro] != int(x['initial_value'],16): die(f'fresh KMD startup-template value drift p{pi} {ro}')

    out={
      'schema':'sp11-e003h-rtcdm-startup-dynamic-ownership-oracle-v1','accepted':True,
      'source_oracles':{
        '0019_materializer_oracle_sha256':sha_file(a.old_oracle),
        'kmd_pass_log_sha256':LOG_SHA['E003H_VFE1_DYNFIELD_KMD_PASS_20260829.log'],
        'cadence_log_sha256':LOG_SHA['E003H_VFE1_DYNFIELD_CADENCE_20260829.log'],
        'producer_log_sha256':LOG_SHA['E003H_VFE1_DYNFIELD_PRODUCER_20260829.log']},
      'closure':{
        'previous_dynamic_holes':20,'refined_dynamic_holes':4,'dmi_address_holes':46,'total_normalized_holes':50,
        'period_cfg_register':'0x8c','startup_template_invariant_live_mutable_fields':16,
        'dmi_plus_period_only_normalization_equal_across_independent_windows_captures':True,
        'qccamisp_0x26838_changes_these_fields':False},
      'period_fields':period,
      'startup_template_fields':template,
      'refined_main_slots':refined,
      'fresh_kmd_entry_values':{str(k):{r:f'0x{v:08x}' for r,v in vals.items()} for k,vals in kmd.items()},
      'live_cadence_samples':[{'sample':x['sample'],'period_cfg':f"0x{x['period']:08x}",'+0x3b70':f"0x{x['b70']:08x}",
                               '+0x3d78..84':[f'0x{v:08x}' for v in x['d78_84']]} for x in cadence],
      'ownership':{
        'period_cfg_0x8c':'upstream_start_dynamic_caller_input; changes across starts/captures; live readback zero after startup',
        '0x3b70_0x3d78_0x3d7c_0x3d80_0x3d84':'exact startup-template values; invariant across independent startup corpora/fresh KMD; do not use as post-start live-state constants',
        '0x3d78_0x3d84_live_behavior':'hardware-visible values mutate during streaming; later update/readback semantics remain outside this materializer'},
      'safety':{'runtime_authorized':False,'fifo0_submission_authorized':False,'vfe1_pix_authorized':False,
                'materializer_rule':'zero only 46 DMI address fields + four period_cfg fields; retain the 16 invariant startup words in exact caller-provided templates'}}
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('PASS: dynamic ownership narrows from 20 to 4 caller fields; 16 startup words remain exact template data, not live-state defaults')
    print('refined hashes:', ', '.join(x['normalized_sha256'] for x in refined))

if __name__=='__main__': main()
