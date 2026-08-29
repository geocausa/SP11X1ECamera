#!/usr/bin/env python3
import argparse, hashlib, importlib.util, json, re, struct
from pathlib import Path

def die(s): raise SystemExit('FAIL: '+s)
def sha(b): return hashlib.sha256(b).hexdigest()
def load_py(path,name):
    spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def array_words(src,name):
    m=re.search(r'static const u32\s+'+re.escape(name)+r'\[\]\s*=\s*\{(.*?)\};',src,re.S)
    if not m: die('source array missing: '+name)
    words=[]
    for x in re.findall(r'0x[0-9a-fA-F]+|\b\d+\b',m.group(1)):
        words.append(int(x,0))
    return words

def le(words): return b''.join(struct.pack('<I',x) for x in words)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--extractor',type=Path,required=True)
    ap.add_argument('--log',type=Path,required=True)
    ap.add_argument('--priming-oracle',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args(); src=a.source.read_text()
    ext=load_py(a.extractor,'e003h_epoch0_batch_extract_verify')
    _, batches=ext.parse_log(a.log)
    if len(batches)<4: die('selector-2 batch census too small')
    po=json.loads(a.priming_oracle.read_text())
    if not po.get('accepted') or po['replay']['packet_count']!=4: die('priming replay oracle drift')

    cv=le(array_words(src,'change_vfe1'))
    cc=le(array_words(src,'change_companion'))
    common=le(array_words(src,'companion_common'))
    p0=le(array_words(src,'companion_packet0'))
    irq=le(array_words(src,'irq_prefix'))
    if [len(cv),len(cc),len(common),len(p0),len(irq)] != [4,4,16,60,16]:
        die('source companion array sizes drift')

    expected_main=[0xe94,0xe34,0x904,0x4e8]
    expected_count=[4,5,5,5]
    rows=[]
    for i in range(4):
        b=batches[i]; rec=b['records']
        if b['batch']!=i or b['count']!=expected_count[i]: die(f'batch {i} count drift')
        if rec[1]['bytes']!=expected_main[i]: die(f'batch {i} main length drift')
        oracle=po['replay']['packets'][i]
        if sha(rec[1]['data']) != oracle['replay_sha256']: die(f'batch {i} main replay hash drift')
        tests=[('bl0',rec[0]['data'],cv),('bl2',rec[2]['data'],cc)]
        if i==0:
            tests.append(('bl3',rec[3]['data'],p0))
        else:
            tests += [('bl3',rec[3]['data'],common),('bl4',rec[4]['data'],irq+struct.pack('<I',i))]
        for name,got,want in tests:
            if got!=want: die(f'batch {i} {name} byte mismatch')
        rows.append({
            'packet':i,'bl_count':b['count'],'main_bytes':rec[1]['bytes'],
            'main_sha256':sha(rec[1]['data']),
            'companion_sha256':[sha(x['data']) for j,x in enumerate(rec) if j!=1],
            'genirq_userdata': None if i==0 else i,
        })

    source_need=[
        'out->bl_dma[packet][1] = main->packet_dma[packet];',
        'out->bl_len[packet][1] = main->packet_len[packet];',
        'out->bl_count[packet] = 4;', 'out->bl_count[packet] = 5;',
        'put_unaligned_le32(packet, bl4 + sizeof(irq_prefix));',
        'prime->bl_len[packet][i] - 1',
        '.submit_prime = camss_x1e_pix_submit_prime,',
    ]
    for x in source_need:
        if x not in src: die('source contract missing: '+x)
    if 'camss_x1e_pix_runner_once' in src: die('callable PIX runner unexpectedly present')

    out={
        'accepted':True,'schema':'sp11-e003h-pix-priming-full-batch-v1',
        'source_sha256':sha(a.source.read_bytes()),
        'selector2_log_sha256':sha(a.log.read_bytes()),
        'extractor_sha256':sha(a.extractor.read_bytes()),
        'priming_oracle_sha256':sha(a.priming_oracle.read_bytes()),
        'packet_bl_counts':expected_count,'packet_main_bytes':[hex(x) for x in expected_main],
        'packets':rows,
        'main_bl_ownership':'reuse already-materialized priming main with Linux-patched DMI IOVAs',
        'companion_ownership':'Linux-owned coherent companion arena; synthesized byte-identically to Windows',
        'fifo_length_rule':'byte_count - 1 for every BL',
        'genirq_rule':'packet1..3 userdata equals selector-2 requestId 1..3; packet0 has no GEN_IRQ BL',
        'callable_runner_present':False,
        'runtime_authorized':False,
    }
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('PASS: four complete selector-2 priming batches match Windows companions byte-for-byte; runner remains absent')
if __name__=='__main__': main()
