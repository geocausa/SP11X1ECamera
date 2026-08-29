#!/usr/bin/env python3
import argparse,hashlib,json,re,subprocess
from pathlib import Path

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
def need(s,*xs):
    for x in xs:
        if x not in s: die('missing '+x)

def main():
    ap=argparse.ArgumentParser();
    ap.add_argument('--source',type=Path,required=True); ap.add_argument('--patch',type=Path,required=True)
    ap.add_argument('--oracle',type=Path,required=True); ap.add_argument('--object',type=Path,required=True); ap.add_argument('--module',type=Path,required=True); ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args(); s=a.source.read_text(); p=a.patch.read_text(); o=json.loads(a.oracle.read_text())
    if not o.get('accepted') or o.get('irq_context_status_0x2c_read_in_handler') is not False or o.get('status_mask')!='0x00070007': die('Windows IRQ oracle not accepted')
    start=s.index('static irqreturn_t camss_rtcdm1_isr'); end=s.index('\n}\n',start)+3; isr=s[start:end]
    need(isr,'status = readl_relaxed(rt->base + CAMSS_RTCDM_IRQ0_STATUS);','clear_status = status & CAMSS_RTCDM_IRQ_KNOWN;','writel_relaxed(clear_status, rt->base + CAMSS_RTCDM_IRQ0_CLEAR);','writel_relaxed(1, rt->base + CAMSS_RTCDM_IRQ0_CLEAR_CMD);')
    if 'readl_relaxed(rt->base + CAMSS_RTCDM_IRQ_CONTEXT_STATUS)' in isr or 'context & BIT(0)' in isr: die('unproven context gate remains in ISR')
    if 'writel_relaxed(status, rt->base + CAMSS_RTCDM_IRQ0_CLEAR)' in isr: die('raw status clear remains')
    added=[x[1:] for x in p.splitlines() if x.startswith('+') and not x.startswith('+++')]
    # Only expected MMIO behavior change: clear value becomes masked known status; no new register target.
    writes=[x.strip() for x in added if 'writel_relaxed' in x]
    allowed=['writel_relaxed(clear_status, rt->base + CAMSS_RTCDM_IRQ0_CLEAR);','writel_relaxed(1, rt->base + CAMSS_RTCDM_IRQ0_CLEAR_CMD);']
    if writes != allowed: die('unexpected added MMIO writes: '+repr(writes))
    nm=subprocess.check_output(['nm','-an',str(a.object)],text=True)
    need(nm,'camss_rtcdm1_isr')
    out={
      'accepted':True,'schema':'sp11-e003h-linux-rtcdm1-irq-parity-v1',
      'windows_irq_oracle_sha256':sha(a.oracle),'patch_sha256':sha(a.patch),'source_sha256':sha(a.source),'object_sha256':sha(a.object),'module_sha256':sha(a.module),
      'irq_status_source':'FIFO0 IRQ0_STATUS +0x44 directly','irq_context_gate':False,'clear_value':'raw_status & 0x00070007','clear_cmd':1,
      'unknown_or_error_policy':'record raw status; disable IRQ/fault on unknown or known error bits after known status acknowledgement',
      'added_mmio_write_targets':['IRQ0_CLEAR +0x34','IRQ0_CLEAR_CMD +0x38'],'runtime_authorized':False,
      'timeout_cause_interpretation':'Previous Linux IRQ_CONTEXT_STATUS bit0 prerequisite was not present in exact Windows handler and could suppress reset/BL completion. It is a plausible cause of the first timeout, not proven without a new diagnostic.'
    }
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print('PASS: Linux RT-CDM1 ISR matches exact Windows FIFO0 status/clear semantics and remains runtime-blocked')
if __name__=='__main__': main()
