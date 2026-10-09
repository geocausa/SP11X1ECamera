#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Hosted qualification of actual staged candidate60 sources; no hardware access."""
from pathlib import Path
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[3];N=ROOT/"src/native-rgb";B=ROOT.parents[1]/"02-kernel/native-rgb-rear-generation-20261007-73";C=B/"camss"
def main():
 pairs=[
 ("rear-v4l2/test-rear-source-stop-v20.py","source-stop-order-hosted-01.json"),
 ("rear-v4l2/test-rear-statistics-v20.py","statistics-hosted-02.json"),
 ("rear-v4l2/test-rear-live-controls-v20.py","live-controls-hosted-01.json"),
 ("rear-v4l2/test-rear-photometric-v20.py","photometric-hosted-01.json"),
 ("rear-v4l2/test-rear-sensor-controls-v20.py","sensor-controls-hosted-03.json"),
 ("rear-v4l2/test-rear-private-optical-v20.py","private-optical-hosted-03.json"),
 ("rear-v4l2/test-rear-startup-spare-v20.py","startup-spare-hosted-01.json"),
 ("rear-windows-ccif/validate-registers.py","csr-whitelist-hosted-01.json"),
 ("rear-generation/test-noc-clock.py","noc-clock-hosted-01.json"),
 ("rear-generation/test-clean-lifecycle.py","clean-lifecycle-hosted-01.json"),
 ("test-rear-csid-config.py","transport-hosted-01.json"),
 ("test-rear-sensor-modes.py","sensor-mode-hosted-01.json"),
 ("test-rear-vfe-config.py","vfe-hosted-02.json"),
 ("test-rear-startup-geometry.py","linear-geometry-hosted-01.json"),
 ("rear-linear-nv12/test-layout.py","linear-nv12-hosted-01.json"),
 ("rear-v4l2/test-live-retire-reclaim.py","public-reclaim-hosted-01.json"),
 ("rear-v4l2/test-video-lease.py","lease-hosted-01.json"),
 ("rear-v4l2/test-video-dma.py","dma-hosted-01.json"),
 ("rear-v4l2/test-public-lifecycle.py","public-lifecycle-hosted-01.json"),
 ("rear-v4l2/test-events.py","event-queue-hosted-01.json"),
 ("rear-v4l2/test-live-observe.py","live-observe-hosted-01.json"),
 ("rear-v4l2/test-live-retire.py","live-retire-hosted-01.json"),
 ("rear-v4l2/test-command-receipts.py","command-receipts-hosted-01.json"),
 ("rear-v4l2/test-command-fifo.py","command-fifo-hosted-01.json"),
 ("rear-v4l2/test-command-retire.py","command-retire-hosted-01.json"),
 ("rear-v4l2/test-rear-waitqueue.py","waitqueue-hosted-01.json"),
 ("rear-v4l2/test-output-update.py","output-update-hosted-01.json"),
 ("rear-v4l2/test-rear-session.py","session-gate-hosted-01.json"),
 ("rear-v4l2/test-rear-snapshot.py","snapshot-retry-hosted-01.json"),
 ("rear-v4l2/test-rear-queue.py","rear-queue-hosted-01.json"),
 ("rear-v4l2/test-rear-cadence-records-v20.py","compiled-records-hosted-01.json"),
 ("rear-v4l2/test-rear-cadence-scope-v20.py","session-scope-hosted-01.json"),
 ("rear-v4l2/test-rear-cadence-owner-v20.py","command-owner-parser-hosted-02.json"),
 ("rear-v4l2/test-rear-cadence-v20.py","cadence-parser-hosted-01.json"),
 ("rear-v4l2/test-rear-dma-timing-v20.py","dma-timing-hosted-01.json"),
 ("rear-v4l2/test-rear-full-cache-v20.py","full-cache-hosted-02.json"),
 ("rear-v4l2/test-rear-gap-timing-v20.py","gap-timing-hosted-01.json"),
 ("rear-v4l2/test-rear-soak-probe-v20.py","soak-probe-hosted-01.json"),
 ("rear-v4l2/test-rear-duration-total-v20.py","duration-total-hosted-01.json")]
 for source,report in pairs:
  script=N/source;assert script.exists(),source
  if (B/report).exists():
   prior=json.loads((B/report).read_text());assert prior["status"].startswith("PASS"),prior
   print(report+":RETAINED_PASS",flush=True);continue
  arg="--source" if source.endswith("test-noc-clock.py") else "--staged"
  target=C
  if source.endswith("test-noc-clock.py"):target=C/"native-rear-noc-clock.inc"
  if source.endswith("test-rear-sensor-modes.py"):arg="--source";target=B/"ov13858/ov13858.c"
  args=[sys.executable,str(script),arg,str(target),"--report",str(B/report)]
  if source.endswith("validate-registers.py"):args=[sys.executable,str(script),"--report",str(B/report)]
  if source.endswith("test-rear-startup-geometry.py"):args+=["--linear-full-nv12"]
  log=B/(report+".log")
  attempt=1
  while log.exists():
   attempt+=1;log=B/(report+".retry-%02d.log"%attempt)
  with log.open("x") as f:subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,check=True,cwd=ROOT)
  print(report+":PASS",flush=True)
 for source in ["test-rear-cadence-runtime-v20.py","test-rear-cadence-session-parser-v20.py"]:
  report="offline-runner-01.json" if "runtime-v20" in source else "restart-runtime-hosted-01.json"
  if (B/report).exists():
   assert json.loads((B/report).read_text())["status"].startswith("PASS")
   print(source+":RETAINED_PASS",flush=True);continue
  log=B/(source+".log")
  attempt=1
  while log.exists():
   attempt+=1;log=B/(source+".retry-%02d.log"%attempt)
  with log.open("x") as f:subprocess.run([sys.executable,str(N/"rear-v4l2"/source)],stdout=f,stderr=subprocess.STDOUT,check=True,cwd=ROOT)
  print(source+":PASS",flush=True)
 print("PASS_REAR60_41_SOURCE_CHECKS_NO_INSTALL",flush=True)
if __name__=="__main__":main()
