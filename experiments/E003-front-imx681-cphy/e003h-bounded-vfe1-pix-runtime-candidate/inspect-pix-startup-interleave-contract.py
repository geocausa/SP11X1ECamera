#!/usr/bin/env python3
import argparse, hashlib, json, subprocess
from pathlib import Path

def die(s): raise SystemExit('FAIL: '+s)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--source',type=Path,required=True); ap.add_argument('--object',type=Path,required=True); ap.add_argument('--oracle',type=Path,required=True); ap.add_argument('-o','--output',type=Path,required=True); a=ap.parse_args()
 s=a.source.read_text(); o=json.loads(a.oracle.read_text())
 if not o.get('accepted') or not o['closures']['startup_priming_bus_csid_interleave_closed']: die('oracle not closed')
 need=[
  '#define CAMSS_X1E_PIX_HW_HOST_STAGE_COUNT\t16',
  'CAMSS_X1E_PIX_HW_STARTUP_PACKET0,\n\t\tCAMSS_X1E_PIX_HW_PRIMING_REPLAY0,\n\t\tCAMSS_X1E_PIX_HW_STARTUP_PACKET1,\n\t\tCAMSS_X1E_PIX_HW_BUS_PREPARE,\n\t\tCAMSS_X1E_PIX_HW_PRIMING_REPLAY1,\n\t\tCAMSS_X1E_PIX_HW_STARTUP_PACKET2,\n\t\tCAMSS_X1E_PIX_HW_STARTUP_PACKET3,\n\t\tCAMSS_X1E_PIX_HW_CSID1_IPP_START,\n\t\tCAMSS_X1E_PIX_HW_ISP_START_DONE,\n\t\tCAMSS_X1E_PIX_HW_CSIPHY2_START,\n\t\tCAMSS_X1E_PIX_HW_SENSOR_START,\n\t\tCAMSS_X1E_PIX_HW_PRIMING_REPLAY2,\n\t\tCAMSS_X1E_PIX_HW_PRIMING_REPLAY3,\n\t\tCAMSS_X1E_PIX_HW_STEADY_READY,',
  '.replay01_vs_csid_start_closed = true,',
  '.replay23_vs_mipi_sensor_start_closed = true,',
  '.startup_priming_interleave_closed = true,',
  '.callable_runner_authorized = false,',
 ]
 for x in need:
  if x not in s: die('missing source contract: '+x[:80])
 nm=subprocess.check_output(['nm','-an',str(a.object)],text=True)
 if ' camss_x1e_pix_hw_order_contract' not in nm: die('retained contract symbol missing')
 rel=subprocess.check_output(['objdump','-r',str(a.object)],text=True)
 refs=[x for x in rel.splitlines() if 'camss_x1e_pix_hw_order_contract' in x]
 if refs: die('contract has runtime relocation reference')
 out={
  'accepted':True,'schema':'sp11-e003h-pix-startup-interleave-contract-v1',
  'source_sha256':sha(a.source),'object_sha256':sha(a.object),'oracle_sha256':sha(a.oracle),
  'host_stage_count':16,
  'host_order':['RTCDM open/start','IFE1 resource held','startup0','priming0','startup1','BUS prepare','priming1','startup2','startup3','CSID1 IPP start','ISP_START_DONE','CSIPHY2 start','sensor start','priming2','priming3','steady ready'],
  'contract_relocation_references':0,'callable_runner_authorized':False,'runtime_reachable':False,
 }
 a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print('PASS: 16-stage PIX startup/priming interleave retained; callable runner still unauthorized')
if __name__=='__main__': main()
