#!/usr/bin/env python3
from pathlib import Path
import argparse,json,re,subprocess,sys

HERE=Path(__file__).resolve().parent
def need(v,m):
    if not v: raise AssertionError(m)

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
need(lr['status']=='PASS_WINDOWS_LSC_R4_R24_CLEANROOM_REPLAY','LSC status')
need(lr['requests']==list(range(4,25)) and lr['clean_lsc_replay']=='21/21 byte-exact LSC0/LSC1/LSC2/GIC','LSC coverage')
need(ar['status']=='PASS_WINDOWS_AWB_R4_R24_21_OF_21_BIT_EXACT','AWB status')
need(ar['requests']==list(range(4,25)) and ar['bit_exact']=='21/21','AWB coverage')

log=a.oracle_log.read_text(errors='replace').replace('\r','')
need(len(re.findall(r'^GD_BREAKPOINTS_ARMED R4_R24 COMBINED_AWB_LSC$',log,re.M))==1,'armed marker')
need(log.count('GD_CAPTURE_COMPLETE R=24 AWB=YES LSC=YES')==1,'combined completion')
need(len(re.findall(r'^GD_GA req=',log,re.M))==21,'21 GA rows')
need(len(re.findall(r'^GD_PUB req=',log,re.M))==21,'21 PUB rows')
need(len(re.findall(r'^GD_ENTRY R=',log,re.M))==21,'21 entry rows')
need(len(re.findall(r'^GD_STAGE R=',log,re.M))==21,'21 stage rows')
need('GD_FAIL' not in log,'debugger fail marker')

hs=a.holder_output.read_text(errors='replace').replace('\r','')
need(hs.count('GD_HOLDER_BEGIN')==1,'holder begin')
need(hs.count('START_BEGIN')==1 and hs.count('START_STATUS=Success')==1,'one holder start')
need(hs.count('STOP_PASS')==1 and hs.count('GD_HOLDER_END')==1,'holder stop')
need('job_exit_code=0' in hs,'holder exit')

out={
  'schema':'sp11-e003i-gd-windows-r4-r24-combined-oracle-v1',
  'status':'PASS_WINDOWS_COMBINED_R4_R24_AWB_LSC',
  'requests':list(range(4,25)),
  'windows_stream_count':1,
  'holder_stop':'PASS',
  'awb_authority':'21/21 bit-exact dynamic calibration/GainAdj/publication',
  'lsc_tintless_authority':'21/21 byte-exact sequential clean-room LSC0/LSC1/LSC2/GIC',
  'combined_r24_completion':True,
  'same_stream_awb_and_lsc':True,
  'continuous_aec_claimed':False,
  'awb_result':ar,
  'lsc_result':lr,
}
a.result.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print('GD_COMBINED_WINDOWS_ORACLE=PASS R4_R24 STREAMS=1')
