#!/usr/bin/env python3
import argparse, hashlib, json, re, subprocess
from pathlib import Path

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
def need(s, *parts):
    for p in parts:
        if p not in s: die('missing '+p)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--camss',type=Path,required=True)
    ap.add_argument('--header',type=Path,required=True)
    ap.add_argument('--patch',type=Path,required=True)
    ap.add_argument('--object',type=Path,required=True)
    ap.add_argument('--module',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    c=a.camss.read_text(); h=a.header.read_text(); p=a.patch.read_text()
    need(h,'diag_stage;','diag_fifo_seq;','diag_base;','diag_len_low20;','diag_required_irq;','diag_mmio_context;','diag_mmio_status;','diag_mmio_user_data;','diag_last_error;')
    need(c,'CAMSS_RTCDM_DIAG_RESET_WAIT','CAMSS_RTCDM_DIAG_FIFO_WAIT','CAMSS_RTCDM_DIAG_FIFO_DONE',
         'camss_rtcdm1_diag_set','E003h RT-CDM1 stage=%s error=%d fifo_seq=%u',
         'E003h PIX RT-CDM open/init failed','E003h PIX RT-CDM core start failed',
         'E003h PIX startup packet%u failed','E003h PIX prime packet%u BL%u failed',
         'E003h PIX steady BL%u failed')
    added=[x[1:] for x in p.splitlines() if x.startswith('+') and not x.startswith('+++')]
    if any('writel' in x for x in added): die('diagnostic patch adds RT-CDM MMIO write')
    if not any('readl_relaxed(rt->base + CAMSS_RTCDM_IRQ_CONTEXT_STATUS)' in x for x in added): die('raw context timeout snapshot absent')
    if not any('readl_relaxed(rt->base + CAMSS_RTCDM_IRQ0_STATUS)' in x for x in added): die('raw status timeout snapshot absent')
    if not any('readl_relaxed(rt->base + CAMSS_RTCDM_USR_DATA)' in x for x in added): die('raw userdata timeout snapshot absent')
    if 'module_param_named(e003h_pix_runtime_arm' not in c: die('0035 default gate missing')
    nm=subprocess.check_output(['nm','-an',str(a.object)],text=True)
    need(nm,'camss_rtcdm1_diag_set')
    out={
      'accepted':True,
      'schema':'sp11-e003h-rtcdm-stage-diagnostics-v1',
      'patch_sha256':sha(a.patch),
      'source_sha256':sha(a.camss),
      'header_sha256':sha(a.header),
      'object_sha256':sha(a.object),
      'module_sha256':sha(a.module),
      'timeout_boundaries':['preflight','reset-wait','core-start','fifo-wait sequence'],
      'semantic_submit_errors':['startup packet index','priming packet + BL index','steady BL index'],
      'failure_snapshot':['raw IRQ context','raw IRQ0 status','raw userdata','last ISR context/status/userdata','FIFO sequence/base/encoded-low20 input','required IRQ bit'],
      'new_mmio_writes':0,
      'diagnostic_mmio_reads_on_error_only':True,
      'runtime_authorized':False,
      'runtime_repeat_authorized':False,
    }
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('PASS: RT-CDM reset/FIFO timeout stage telemetry is read-only, semantic and runtime-blocked')
if __name__=='__main__': main()
