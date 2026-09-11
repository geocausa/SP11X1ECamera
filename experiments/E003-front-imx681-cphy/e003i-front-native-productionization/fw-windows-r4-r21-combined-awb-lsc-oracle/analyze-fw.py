#!/usr/bin/env python3
from pathlib import Path
import argparse,json,re,subprocess,sys

HERE=Path(__file__).resolve().parent

def need(v,m):
    if not v:
        raise AssertionError(m)

ap=argparse.ArgumentParser()
ap.add_argument('capture_dir',type=Path)
ap.add_argument('oracle_log',type=Path)
ap.add_argument('holder_output',type=Path)
ap.add_argument('--result',type=Path,default=HERE/'RESULT.json')
a=ap.parse_args()

lsc=HERE/'LSC-RESULT.json'
awb=HERE/'AWB-RESULT.json'
subprocess.run([sys.executable,str(HERE/'analyze-lsc.py'),str(a.capture_dir),'--result',str(lsc)],check=True)
subprocess.run([sys.executable,str(HERE/'analyze-awb.py'),str(a.oracle_log),'--result',str(awb)],check=True)

lr=json.loads(lsc.read_text())
ar=json.loads(awb.read_text())
need(lr['status']=='PASS_WINDOWS_LSC_R4_R21_CLEANROOM_REPLAY','LSC status')
need(lr['requests']==list(range(4,22)) and lr['clean_lsc_replay']=='18/18 byte-exact LSC0/LSC1/LSC2/GIC','LSC coverage')
need(ar['status']=='PASS_WINDOWS_AWB_R4_R21_18_OF_18_BIT_EXACT','AWB status')
need(ar['requests']==list(range(4,22)) and ar['bit_exact']=='18/18','AWB coverage')

log=a.oracle_log.read_text(errors='replace').replace('\r','')
need(len(re.findall(r'^FW_BREAKPOINTS_ARMED R4_R21 COMBINED_AWB_LSC$',log,re.M))==1,'armed marker')
need(log.count('FW_CAPTURE_COMPLETE R=21 AWB=YES LSC=YES')==1,'combined completion')
need(len(re.findall(r'^FW_GA req=',log,re.M))==18,'18 GA rows')
need(len(re.findall(r'^FW_PUB req=',log,re.M))==18,'18 PUB rows')
need(len(re.findall(r'^FW_ENTRY R=',log,re.M))==18,'18 entry rows')
need(len(re.findall(r'^FW_STAGE R=',log,re.M))==18,'18 stage rows')
need('FW_FAIL' not in log,'debugger fail marker')

hs=a.holder_output.read_text(errors='replace').replace('\r','')
need(hs.count('FW_HOLDER_BEGIN')==1,'holder begin')
need(hs.count('START_BEGIN')==1 and hs.count('START_STATUS=Success')==1,'one holder start')
need(hs.count('STOP_PASS')==1 and hs.count('FW_HOLDER_END')==1,'holder stop')
need('job_exit_code=0' in hs,'holder exit')

out={
  'schema':'sp11-e003i-fw-windows-r4-r21-combined-oracle-v1',
  'status':'PASS_WINDOWS_COMBINED_R4_R21_AWB_LSC',
  'requests':list(range(4,22)),
  'windows_stream_count':1,
  'holder_stop':'PASS',
  'awb_authority':'18/18 bit-exact dynamic calibration/GainAdj/publication',
  'lsc_tintless_authority':'18/18 byte-exact sequential clean-room LSC0/LSC1/LSC2/GIC',
  'combined_r21_completion':True,
  'same_stream_awb_and_lsc':True,
  'continuous_aec_claimed':False,
  'awb_result':ar,
  'lsc_result':lr,
}
a.result.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print('FW_COMBINED_WINDOWS_ORACLE=PASS R4_R21 STREAMS=1')
