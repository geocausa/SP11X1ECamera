#!/usr/bin/env python3
import argparse, hashlib, json, re, subprocess
from pathlib import Path

def die(s): raise SystemExit('FAIL: '+s)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(s,*parts):
    for p in parts:
        if p not in s: die('missing '+p)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,required=True); ap.add_argument('--header',type=Path,required=True)
    ap.add_argument('--patch',type=Path,required=True); ap.add_argument('--module',type=Path,required=True)
    ap.add_argument('--oracle',type=Path,required=True); ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args(); s=a.source.read_text(); h=a.header.read_text(); p=a.patch.read_text(); o=json.loads(a.oracle.read_text())
    if not o.get('accepted') or o.get('mask')!='0x00070007': die('oracle not accepted/mask drift')
    need(h,'u32 last_irq_status1;','u32 last_irq_status2;','u32 last_irq_status3;')
    for n,off in [(1,'0x134'),(1,'0x138'),(1,'0x144'),(2,'0x234'),(2,'0x238'),(2,'0x244'),(3,'0x334'),(3,'0x338'),(3,'0x344')]:
        need(s,off)
    need(s,
      'status0 = readl_relaxed(rt->base + CAMSS_RTCDM_IRQ0_STATUS);',
      'status1 = readl_relaxed(rt->base + CAMSS_RTCDM_IRQ1_STATUS);',
      'status2 = readl_relaxed(rt->base + CAMSS_RTCDM_IRQ2_STATUS);',
      'status3 = readl_relaxed(rt->base + CAMSS_RTCDM_IRQ3_STATUS);',
      'clear0 = status0 & CAMSS_RTCDM_IRQ_KNOWN;',
      'clear1 = status1 & CAMSS_RTCDM_IRQ_KNOWN;',
      'clear2 = status2 & CAMSS_RTCDM_IRQ_KNOWN;',
      'clear3 = status3 & CAMSS_RTCDM_IRQ_KNOWN;',
      'if (!clear0)',
      'writel_relaxed(clear0, rt->base + CAMSS_RTCDM_IRQ0_CLEAR);',
      'writel_relaxed(clear1, rt->base + CAMSS_RTCDM_IRQ1_CLEAR);',
      'writel_relaxed(clear2, rt->base + CAMSS_RTCDM_IRQ2_CLEAR);',
      'writel_relaxed(clear3, rt->base + CAMSS_RTCDM_IRQ3_CLEAR);',
      'writel_relaxed(1, rt->base + CAMSS_RTCDM_IRQ0_CLEAR_CMD);',
      'writel_relaxed(1, rt->base + CAMSS_RTCDM_IRQ1_CLEAR_CMD);',
      'writel_relaxed(1, rt->base + CAMSS_RTCDM_IRQ2_CLEAR_CMD);',
      'writel_relaxed(1, rt->base + CAMSS_RTCDM_IRQ3_CLEAR_CMD);',
      'if (clear0 & (CAMSS_RTCDM_IRQ_RESET_DONE | CAMSS_RTCDM_IRQ_BL_DONE))')
    # Exact Windows correction must not reintroduce IRQ_CONTEXT_STATUS in ISR.
    isr=s[s.index('static irqreturn_t camss_rtcdm1_isr'):s.index('static int camss_rtcdm1_windows_preflight')]
    if 'CAMSS_RTCDM_IRQ_CONTEXT_STATUS' in isr: die('IRQ_CONTEXT_STATUS gate/read in ISR')
    # Incremental writes are restricted to Windows-proven FIFO1/2/3 CLEAR + CLEAR_CMD.
    added=[x[1:] for x in p.splitlines() if x.startswith('+') and not x.startswith('+++')]
    writes=[x.strip() for x in added if re.search(r'\bwritel_relaxed\b',x)]
    allowed={
      'writel_relaxed(clear0, rt->base + CAMSS_RTCDM_IRQ0_CLEAR);',
      'writel_relaxed(1, rt->base + CAMSS_RTCDM_IRQ0_CLEAR_CMD);',
      'writel_relaxed(clear1, rt->base + CAMSS_RTCDM_IRQ1_CLEAR);',
      'writel_relaxed(clear2, rt->base + CAMSS_RTCDM_IRQ2_CLEAR);',
      'writel_relaxed(clear3, rt->base + CAMSS_RTCDM_IRQ3_CLEAR);',
      'writel_relaxed(1, rt->base + CAMSS_RTCDM_IRQ1_CLEAR_CMD);',
      'writel_relaxed(1, rt->base + CAMSS_RTCDM_IRQ2_CLEAR_CMD);',
      'writel_relaxed(1, rt->base + CAMSS_RTCDM_IRQ3_CLEAR_CMD);',
    }
    extra=set(writes)-allowed
    if extra: die('unproven incremental MMIO write: '+repr(sorted(extra)))
    missing=allowed-set(writes)
    if missing: die('missing proven incremental clear write: '+repr(sorted(missing)))
    # Runtime gate/trigger must remain unchanged and no new authorization switch appears.
    need(s,'static bool camss_x1e_pix_runtime_arm;','module_param_named(e003h_pix_runtime_arm, camss_x1e_pix_runtime_arm, bool, 0400);')
    if any('runtime_authorized' in x for x in added): die('runtime authorization added in source')
    vermagic=subprocess.check_output(['modinfo','-F','vermagic',str(a.module)],text=True).strip()
    if not vermagic.startswith('7.1.5-sp11-render-parity-v4+'): die('vermagic drift')
    out={
      'accepted':True,'schema':'sp11-e003h-linux-rtcdm1-multififo-irq-v1',
      'oracle_sha256':sha(a.oracle),'patch_sha256':sha(a.patch),'source_sha256':sha(a.source),
      'header_sha256':sha(a.header),'module_sha256':sha(a.module),'vermagic':vermagic,
      'status_reads':['FIFO0 +0x44','FIFO1 +0x144','FIFO2 +0x244','FIFO3 +0x344'],
      'dispatch_gate':'masked FIFO0 status only','status_mask':'0x00070007',
      'clear_values':['FIFO0 +0x34','FIFO1 +0x134','FIFO2 +0x234','FIFO3 +0x334'],
      'clear_commands':['FIFO0 +0x38','FIFO1 +0x138','FIFO2 +0x238','FIFO3 +0x338'],
      'completion_source':'masked FIFO0 reset-done/BL-done only',
      'other_fifo_semantics_invented':False,'irq_context_status_gate':False,
      'incremental_new_mmio_writes':sorted(allowed),
      'runtime_authorized':False,'runtime_repeat_authorized':False,
    }
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('PASS: Linux RT-CDM1 ISR mirrors Windows four-FIFO status/ack gate; runtime remains blocked')
if __name__=='__main__': main()
