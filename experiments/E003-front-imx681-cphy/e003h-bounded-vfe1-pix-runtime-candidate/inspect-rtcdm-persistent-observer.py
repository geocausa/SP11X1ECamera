#!/usr/bin/env python3
import argparse, hashlib, json, re, subprocess
from pathlib import Path

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
def need(s,*parts):
    for p in parts:
        if p not in s: die('missing '+p)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,required=True); ap.add_argument('--header',type=Path,required=True)
    ap.add_argument('--patch',type=Path,required=True); ap.add_argument('--module',type=Path,required=True)
    ap.add_argument('--watcher',type=Path,required=True); ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args(); s=a.source.read_text(); h=a.header.read_text(); p=a.patch.read_text(); w=a.watcher.read_text()
    need(h,'u32 diag_transition_seq;')
    need(s,
         'CAMSS_RTCDM_DIAG_RESET_COMMAND', 'CAMSS_RTCDM_DIAG_CORE_STARTING',
         'smp_store_release(&rt->diag_transition_seq, seq);',
         'sysfs_notify(&camss->dev->kobj, NULL, "e003h_pix_rtcdm_diag");',
         'static DEVICE_ATTR_RO(e003h_pix_rtcdm_diag);',
         'device_create_file(dev, &dev_attr_e003h_pix_rtcdm_diag);',
         'device_remove_file(&pdev->dev, &dev_attr_e003h_pix_rtcdm_diag);')
    # Read-only observer must publish pre-write stages around dangerous boundaries.
    reset_mark=s.index('CAMSS_RTCDM_DIAG_RESET_COMMAND'); reset_write=s.index('writel_relaxed(CAMSS_RTCDM_WINDOWS_RESET_MASK', reset_mark)
    if reset_mark > reset_write: die('reset stage after write')
    start_mark=s.index('CAMSS_RTCDM_DIAG_CORE_STARTING'); core_write=s.index('writel_relaxed(CAMSS_RTCDM_WINDOWS_IRQ0_MASK', start_mark)
    if start_mark > core_write: die('core-start stage after write')
    fifo_mark=s.index('CAMSS_RTCDM_DIAG_FIFO_WAIT', s.index('static int camss_rtcdm1_windows_fifo0_commit'))
    fifo_write=s.index('writel_relaxed(base, rt->base + CAMSS_RTCDM_FIFO0_BASE)', fifo_mark)
    if fifo_mark > fifo_write: die('fifo-wait stage after write')
    # Incremental patch must add no hardware MMIO write primitive at all.
    added=[x for x in p.splitlines() if x.startswith('+') and not x.startswith('+++')]
    added_writes=[x for x in added if re.search(r'\b(writel|writeq|regmap_write)\b',x)]
    if added_writes: die('observer patch adds MMIO write: '+repr(added_writes))
    # Trigger remains explicit RUN and observer is gated by same false-default arm parameter.
    arm=s.index('if (camss_x1e_pix_runtime_arm && camss->res->version == CAMSS_X1E80100)')
    diag_create=s.index('device_create_file(dev, &dev_attr_e003h_pix_rtcdm_diag);')
    if diag_create < arm: die('diag attribute not arm-gated')
    need(s,'if (!camss_x1e_pix_runtime_arm || !sysfs_streq(buf, "RUN"))')
    need(w,'os.fdatasync(fd)','select.POLLPRI','poll.poll(1)','READY\\n')
    if any(x in w for x in ('/dev/mem','mmap.mmap','ioctl','RUN\\n')): die('watcher contains hardware/trigger action')
    vermagic=subprocess.check_output(['modinfo','-F','vermagic',str(a.module)],text=True).strip()
    if not vermagic.startswith('7.1.5-sp11-render-parity-v4+'): die('vermagic drift')
    out={
      'accepted':True,'schema':'sp11-e003h-rtcdm-persistent-stage-observer-v1',
      'patch_sha256':sha(a.patch),'source_sha256':sha(a.source),'header_sha256':sha(a.header),
      'module_sha256':sha(a.module),'watcher_sha256':sha(a.watcher),'vermagic':vermagic,
      'read_only_sysfs':True,'observer_created_only_when_runtime_arm_parameter_true':True,
      'transition_sequence_published':True,'sysfs_poll_notification':True,
      'persistent_userspace_fsync_per_changed_snapshot':True,
      'prewrite_markers':['reset-command','core-starting','fifo-wait'],
      'new_mmio_writes':0,'trigger_semantics_changed':False,
      'runtime_authorized':False,'runtime_repeat_authorized':False,
      'purpose':'preserve the last observable existing RT-CDM software stage across a future unclean reset; does not prove hardware completion',
    }
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('PASS: persistent RT-CDM stage observer is read-only, fsync-backed, arm-gated and adds no MMIO write')
if __name__=='__main__': main()
