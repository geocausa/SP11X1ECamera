#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json
from pathlib import Path

def sha(b): return hashlib.sha256(b).hexdigest()
def load(path):
    s=importlib.util.spec_from_file_location('tlbg',path);m=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(m);return m

def main():
    here=Path(__file__).resolve().parent
    repo=here.parents[3]
    cap=repo.parent/'.local-oracles/oracle-live-20260904-front-atomic'
    P=load(here/'titan680-tlbg-parser.py')
    want={4:'9778a7315a7f052042252717e5454f4f508bf202a1d301f766183bd40b8c741f',
          5:'ed4123ce369f614276cc1aca6436636f8dcd19b544063250af12aedeff488d9d',
          6:'ab2effdc589836fa5d1ab16e2fd68a57d9605e2a024edf9415d1ec8515dbe63c'}
    result={'schema':'sp11-e003i-titan680-tlbg-parser-v1','accepted':True,
            'device_mft_sha256':'c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35',
            'native_authority':{'stats_parser':'CamX::TitanStatsParser::ParseTintlessBGStats',
                                'config_helper_rva':'0x5f07b8','single_ife_helper_rva':'0x5f09d0',
                                'titan680_special_helper_rva':'0x5f23a0','hardware_version':'0x60800'},
            'raw':{'regions':P.REGIONS,'record_bytes':P.RAW_RECORD_BYTES,'bytes':P.RAW_BYTES},
            'parsed':{'flags':3,'record_bytes':P.PARSED_RECORD_BYTES,'full_bytes':P.PARSED_FULL_BYTES,
                      'oracle_bounded_bytes':P.PARSED_BOUNDED_BYTES},'requests':{},
            'safety':{'offline_only':True,'linux_camera_runtime':False}}
    for req in (4,5,6):
        x=(cap/f'req{req}_x2_stats.bin').read_bytes()
        if len(x)!=P.PARSED_BOUNDED_BYTES or sha(x)!=want[req]: raise RuntimeError(f'R{req} x2 fixture drift')
        raw=P.synthesize_raw_from_bounded_parsed(x)
        got=P.parse_titan680_tlbg(raw)
        if got[:len(x)] != x: raise RuntimeError(f'R{req} raw->parsed round-trip mismatch')
        result['requests'][str(req)]={'parsed_sha256':sha(x),'synthetic_raw_sha256':sha(raw),
                                     'roundtrip_bounded_sha256':sha(got[:len(x)]),'roundtrip_exact':True}
        print(f'R{req} TITAN680_TLBG_PARSE PASS raw={sha(raw)} parsed={sha(x)}')
    (here/'PARSER-PROOF.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('TITAN680_TLBG_PARSER=PASS')
if __name__=='__main__': main()
