#!/usr/bin/env python3
import argparse, hashlib, json, shutil, subprocess, tempfile
from pathlib import Path
BASE='df79291cde9784233204970155dcf3d30c1e5ef46d90b175e8bbf50afe0d4536'
def die(s): raise SystemExit('FAIL: '+s)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(s,*xs):
 for x in xs:
  if x not in s: die('missing trigger contract: '+x[:100])
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--source',type=Path,required=True); ap.add_argument('--object',type=Path,required=True); ap.add_argument('--module',type=Path,required=True); ap.add_argument('--patch',type=Path,required=True); ap.add_argument('--base-source',type=Path,required=True); ap.add_argument('-o','--output',type=Path,required=True); a=ap.parse_args()
 s=a.source.read_text()
 if sha(a.base_source)!=BASE: die('0034 base drift')
 need(s,
  'static bool camss_x1e_pix_runtime_arm;',
  'module_param_named(e003h_pix_runtime_arm, camss_x1e_pix_runtime_arm, bool, 0400);',
  '#define CAMSS_X1E_PIX_TRIGGER_FW "sp11/e003h/E003H_PIX_ORACLE_CAPSULE.bin"',
  'static DEVICE_ATTR_WO(e003h_pix_run_once);',
  'if (!camss_x1e_pix_runtime_arm || !sysfs_streq(buf, "RUN"))',
  'request_firmware_direct(&fw, CAMSS_X1E_PIX_TRIGGER_FW, dev)',
  'if (vb2_get_num_buffers(&video->vb2_q) != 2)',
  'camss_x1e_pix_trigger_sync(camss, video0, true)',
  'camss_x1e_pix_trigger_sync(camss, video1, true)',
  'ret = camss_x1e_pix_gate_run_once(camss, &req, &result);',
  'if (!result.teardown_safe)',
  'dma_sync_sgtable_for_device(camss->dev, sgt, DMA_FROM_DEVICE);',
  'dma_sync_sgtable_for_cpu(camss->dev, sgt, DMA_FROM_DEVICE);',
  'if (camss_x1e_pix_runtime_arm && camss->res->version == CAMSS_X1E80100) {\n\t\tret = device_create_file(dev, &dev_attr_e003h_pix_run_once);',
  'device_remove_file(&pdev->dev, &dev_attr_e003h_pix_run_once);')
 # Trigger must not invoke normal vb2 queue/start APIs.
 block=s[s.index('static ssize_t e003h_pix_run_once_store'):s.index('static DEVICE_ATTR_WO(e003h_pix_run_once);')]
 for bad in ('vb2_ioctl_streamon','video_start_streaming','video_buf_queue(','vfe_enable_v2(','QBUF'):
  if bad in block: die('forbidden normal streaming path in trigger: '+bad)
 nm=subprocess.check_output(['nm','-an',str(a.object)],text=True)
 for sym in ('camss_x1e_pix_runtime_arm','dev_attr_e003h_pix_run_once','e003h_pix_run_once_store','camss_x1e_pix_gate_run_once'):
  if sym not in nm: die('missing object symbol '+sym)
 rel=subprocess.check_output(['objdump','-r',str(a.object)],text=True)
 store=[x for x in rel.splitlines() if 'e003h_pix_run_once_store' in x]
 if len(store)!=1 or 'R_AARCH64_ABS64' not in store[0]: die('sysfs store relocation drift')
 modinfo=subprocess.check_output(['modinfo',str(a.module)],text=True)
 if 'e003h_pix_runtime_arm:Arm the disposable SP11 E003h one-shot PIX sysfs trigger (bool)' not in modinfo: die('module param missing')
 with tempfile.TemporaryDirectory() as td:
  tree=Path(td)/'tree'; (tree/'drivers/media/platform/qcom/camss').mkdir(parents=True); shutil.copy2(a.base_source,tree/'drivers/media/platform/qcom/camss/camss.c')
  subprocess.run(['patch','-p1','-i',str(a.patch.resolve())],cwd=tree,check=True,stdout=subprocess.DEVNULL)
  f=tree/'drivers/media/platform/qcom/camss/camss.c'
  if sha(f)!=sha(a.source): die('forward reconstruction mismatch')
  subprocess.run(['patch','-R','-p1','-i',str(a.patch.resolve())],cwd=tree,check=True,stdout=subprocess.DEVNULL)
  if sha(f)!=BASE: die('reverse reconstruction mismatch')
 out={'accepted':True,'schema':'sp11-e003h-pix-disposable-trigger-v1','base_0034_source_sha256':BASE,'source_sha256':sha(a.source),'object_sha256':sha(a.object),'module_sha256':sha(a.module),'patch_sha256':sha(a.patch),'module_param':'e003h_pix_runtime_arm','module_param_default':False,'module_param_runtime_writable':False,'sysfs_attribute':'e003h_pix_run_once','sysfs_command':'RUN','firmware':'sp11/e003h/E003H_PIX_ORACLE_CAPSULE.bin','buffers':'exactly two preallocated vb2 buffers 0/1; no QBUF/STREAMON','dma_preflight':'mapped SG must be contiguous and cache-synced device->CPU around one-shot','runtime_reachable_when_armed':True,'runtime_reachable_by_default':False,'runtime_authorized':False}
 a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print('PASS: disposable PIX trigger is param-gated, exact-one-shot and default-unarmed')
if __name__=='__main__': main()
