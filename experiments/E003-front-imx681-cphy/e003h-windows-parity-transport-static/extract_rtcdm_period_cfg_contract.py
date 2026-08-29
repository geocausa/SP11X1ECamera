#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, json, re
OWN_SHA='402510679bae860f801166bd7ff36834ca8284650aa29d64f1c08d7c6afda856'
PRODUCER_SHA='a70534c7a13a374e8f8258e0c134d56bcf182d4d64be1d33b0b7ffbf4b1fde0d'

def die(s): raise SystemExit('FAIL: '+s)
def sha(b): return hashlib.sha256(b).hexdigest()
def pair(vals,label):
    if len(vals)!=4: die(label+' packet count drift')
    p0=vals[0]; tail=vals[1:]
    if len(set(tail))!=1: die(label+' packets 1/2/3 period_cfg differ')
    if p0==tail[0]: die(label+' packet0 unexpectedly equals packets1/2/3')
    return {'packet0':f'0x{p0:08x}','packets123':f'0x{tail[0]:08x}'}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--ownership-oracle',type=Path,required=True); ap.add_argument('--producer-log',type=Path,required=True); ap.add_argument('-o','--output',type=Path,required=True); a=ap.parse_args()
    ob=a.ownership_oracle.read_bytes(); pb=a.producer_log.read_bytes()
    if sha(ob)!=OWN_SHA: die('ownership oracle identity drift')
    if sha(pb)!=PRODUCER_SHA: die('producer log identity drift')
    own=json.loads(ob)
    if not own.get('accepted') or own['closure'].get('qccamisp_0x26838_changes_these_fields') is not False: die('KMD pass-through proof missing')
    pf=own['period_fields']
    initial=[int(x['initial_value'],16) for x in pf]
    final=[int(x['final_value'],16) for x in pf]
    fresh=[int(own['fresh_kmd_entry_values'][str(i)]['0x8c'],16) for i in range(4)]
    text=pb.decode('utf-16')
    found={}
    for m in re.finditer(r'PRE p=(\d).*?period=([0-9a-fA-F]{8})',text): found[int(m.group(1))]=int(m.group(2),16)
    if sorted(found)!=[0,1,2,3]: die('producer log period packet set drift: '+repr(sorted(found)))
    producer=[found[i] for i in range(4)]
    starts={'initial_corpus':pair(initial,'initial'),'final_corpus':pair(final,'final'),'fresh_kmd':pair(fresh,'fresh KMD'),'producer_pass':pair(producer,'producer pass')}
    out={
      'schema':'sp11-e003h-rtcdm-period-cfg-contract-v1','accepted':True,
      'source_oracles':{'startup_ownership_sha256':sha(ob),'producer_log_sha256':sha(pb)},
      'observed_starts':starts,
      'contract':{
        'register':'0x8c period_cfg','logical_values_per_start':2,
        'packet_mapping':{'0':'packet0','1':'packets123','2':'packets123','3':'packets123'},
        'packets_1_2_3_equal_in_every_observed_start':True,
        'packet0_distinct_from_packets123_in_every_observed_start':True,
        'qccamisp_0x26838_mutates_period_cfg':False,
        'ownership':'already populated at qccamisp DEVICE_START/IFE 0x803 entry; kernel transport treats the two values as opaque upstream caller inputs'
      },
      'linux_consequence':{
        'materializer_dynamic_values':2,
        'materializer_patch_sites':4,
        'rule':'caller supplies packet0 and packets123 period_cfg values; packets 1/2/3 must be materialized from one shared caller value',
        'captured_windows_period_values_must_not_be_embedded':True
      },
      'safety':{'runtime_authorized':False,'fifo0_submission_authorized':False,'vfe1_pix_authorized':False}
    }
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('PASS: four Windows starts prove two logical period_cfg inputs: packet0 and one shared packets1/2/3 value; KMD transport does not mutate them')
if __name__=='__main__': main()
