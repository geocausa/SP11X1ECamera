#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Check complete same-boot camera kernel logs, including module teardown."""
import argparse,json
from pathlib import Path
from kernel_log_window import entries,make_boundary,window
PATTERNS=('BUG:','Oops:','Kernel panic','Unable to handle kernel',
          'general protection fault','use-after-free','KASAN:','DMA-API:',
          'WARNING:','status stuck at','failed to enable xclk',
          'power-on cleanup failed','failed to disable avdd',
          'failed to disable dovdd','remove power-off failed',
          'Stream teardown fault','CSID quiesce failed','RDI pause failed','Missing ready buf','Received completion for invalid port',
          'Received wm done for unmapped index','Received completion for invalid output count',
          'Invalid completion group')
def analyse(before,after,before_boot_id,after_boot_id):
    delta=window(after,make_boundary(before,before_boot_id),after_boot_id)
    records=list(entries(delta))
    counts={pattern:sum(pattern in record for _,record in records) for pattern in PATTERNS}
    return {'status':'FAIL_FINAL_KERNEL_LOG' if any(counts.values()) else 'PASS_FINAL_KERNEL_LOG',
            'scope':'same-boot records after initial boundary, including module teardown',
            'new_records':len(records),'signature_counts':counts}
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before',required=True,type=Path)
    parser.add_argument('--after',required=True,type=Path)
    parser.add_argument('--before-boot-id',required=True)
    parser.add_argument('--after-boot-id',required=True)
    args=parser.parse_args()
    result=analyse(args.before.read_text(),args.after.read_text(),
                   args.before_boot_id,args.after_boot_id)
    print(json.dumps(result))
    raise SystemExit(result['status']!='PASS_FINAL_KERNEL_LOG')
if __name__=='__main__':main()
