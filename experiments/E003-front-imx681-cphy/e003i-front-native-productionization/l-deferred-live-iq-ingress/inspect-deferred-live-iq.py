#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, re, shutil, subprocess, tempfile
HERE=Path(__file__).resolve().parent
BASE=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/e003i-front-production-src')
CAMSS=BASE/'drivers/media/platform/qcom/camss/camss.c'
VIO=BASE/'drivers/media/v4l2-core/v4l2-ioctl.c'
VIDEO=BASE/'drivers/media/platform/qcom/camss/camss-video.c'
M=json.loads((HERE/'BUILD-MANIFEST.json').read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
if M['schema']!='sp11-e003i-deferred-live-iq-ingress-v1': raise SystemExit('manifest schema drift')
# The canonical D source is restored after generating this checkpoint.
if sha(CAMSS)!=M['base_camss_sha256']: raise SystemExit('E003i-D base camss drift')
if sha(HERE/'0010-media-qcom-camss-defer-live-iq-r5-r6.patch')!=M['patch_sha256']: raise SystemExit('patch drift')
tmp=Path(tempfile.mkdtemp(prefix='e003i-l-'))
try:
    dst=tmp/'drivers/media/platform/qcom/camss/camss.c'; dst.parent.mkdir(parents=True); shutil.copy2(CAMSS,dst)
    subprocess.run(['patch','-p1','-i',str(HERE/'0010-media-qcom-camss-defer-live-iq-r5-r6.patch')],cwd=tmp,check=True,stdout=subprocess.DEVNULL)
    if sha(dst)!=M['deferred_camss_sha256']: raise SystemExit('patched camss SHA drift')
    s=dst.read_text()
    req=[
      'x1e_pix_iq_depth != 1','x1e_pix_iq_last_enqueued != 4',
      'bool deferred_live_iq;','req->live_video, 5, &materialized_next->steady',
      'req->live_video, 6, &materialized_next_next->steady',
      'Do not sleep across a live Epoch0 boundary','if (video->vb2_q.streaming)',
      'if (frame_limit >= 5 && !deferred_live_iq)'
    ]
    for x in req:
        if x not in s: raise SystemExit('missing deferred marker: '+x)
    if 'CAMSS_X1E_PIX_IQ_WAIT_TIMEOUT_US, &iq5' in s or 'CAMSS_X1E_PIX_IQ_WAIT_TIMEOUT_US, &iq6' in s:
        raise SystemExit('R5/R6 still dequeued before runner')
    vio=VIO.read_text(); vid=VIDEO.read_text()
    for x in ('VIDIOC_STREAMON, v4l_streamon, v4l_print_buftype, INFO_FL_PRIO | INFO_FL_QUEUE',
              'VIDIOC_S_EXT_CTRLS, v4l_s_ext_ctrls'):
        if x not in vio: raise SystemExit('V4L2 lock evidence drift: '+x)
    if 'q->lock = &video->q_lock;' not in vid or 'vdev->lock = &video->lock;' not in vid:
        raise SystemExit('CAMSS lock assignment drift')
    print('E003I_DEFERRED_LIVE_IQ_INSPECT=PASS')
    print('R4_ONLY_PREPRIME=true')
    print('R5_R6_DEFERRED=true')
    print('GATE_WAIT_POLICY=nonblocking')
    print('V4L2_CONTROL_CONCURRENT_WITH_WORKER=true')
    print('RUNTIME_AUTHORIZED=false')
finally:
    shutil.rmtree(tmp)
