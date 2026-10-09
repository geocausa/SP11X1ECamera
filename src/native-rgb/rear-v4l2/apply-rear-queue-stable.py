#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
from pathlib import Path
HERE=Path(__file__).resolve().parent
def apply(camss):
 camss=Path(camss)
 (camss/"native-rear-queue.inc").write_bytes((HERE/"native-rear-queue-stable.inc").read_bytes())
 p=camss/"camss-vfe-e008k-rear-runner.inc";s=p.read_text()
 anchor=" u32 queue_handoffs, queue_updates;"
 assert s.count(anchor)==1
 p.write_text(s.replace(anchor," u32 queue_handoffs, queue_updates, queue_snapshot_retries;",1))
 return dict(snapshot_retry_only_errno="EAGAIN",maximum_snapshot_attempts=256,
             drain_exact_owner_each_attempt=True,retain_mappings_until_original_full_proof=True,
             other_errors_fatal=True,address_reprogram_on_retry=False,command_resubmission=False,IRQ_disable=False)
