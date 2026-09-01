#!/usr/bin/env python3
import hashlib, json, pathlib, re, subprocess
R=pathlib.Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
S=pathlib.Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss')
D=R/'experiments/E003-front-imx681-cphy/e003h-v4l2-one-frame-0065-static'
sha=lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
patch=(D/'0065-v4l2-one-frame.patch').read_text()
video=(S/'camss-video.c').read_text(); core=(S/'camss.c').read_text(); vfe=(S/'camss-vfe.c').read_text()
base=R/'experiments/E003-front-imx681-cphy/e003h-csid-bufdone-video-0064-candidate/runtime-0064-analysis.json'
b=json.loads(base.read_text())
added='\n'.join(x[1:] for x in patch.splitlines() if x.startswith('+') and not x.startswith('+++'))
for token in ('readl(', 'readl_relaxed(', 'writel(', 'writel_relaxed(', 'ioread', 'iowrite', 'clk_set_rate(', 'regmap_write('):
    assert token not in added, token
assert b['accepted'] and b['classification']['first_complete_linux_front_camera_frame_achieved']
assert b['qc10c']['y_written_equivalent_lines']==1440 and b['qc10c']['c_written_equivalent_lines']==720
assert 'return -EOPNOTSUPP;' in vfe and 'current v2 output plumbing maps PIX line 3' in vfe
assert 'video_is_x1e_front_pix(video)' in video
assert 'camss_x1e_pix_v4l2_start(video, count)' in video
assert 'video->x1e_pix_runner_pinned' in video and 'video->x1e_pix_runner_stopped' in video
assert 'if (!camss_x1e_pix_runtime_arm || !video || !video->camss || count != 2)' in core
assert 'vb->state != VB2_BUF_STATE_ACTIVE' in core
assert 'camss_x1e_pix_runner_once(camss, &req, &result)' in core
assert 'vb2_buffer_done(&video0->vb.vb2_buf, VB2_BUF_STATE_DONE)' in core
assert 'E003h 0065 teardown unsafe; DMA ownership pinned until reboot' in core
assert 'vfe_buf_add_pending(output, video1)' in core
assert sha(S/'camss-csid-680.c')=='753799beba3d91e6654c62f961a5ab4e652da2775320be7c4c0b8de86e0a3410'
assert sha(S/'camss-vfe-680.c')=='36a07ad05f2ea5fdb5d1fcb168eb730cc8fe640b14a21dcb8bb22427c5398d81'
assert subprocess.check_output(['modinfo','-F','vermagic',str(D/'qcom-camss.ko')],text=True).strip()=='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
out={
 'schema':'sp11-e003h-v4l2-one-frame-0065-static-v1','date':'2026-09-01','accepted':True,'runtime_authorized':False,
 'base_0064_analysis_sha256':sha(base),'patch_sha256':sha(D/'0065-v4l2-one-frame.patch'),'module_sha256':sha(D/'qcom-camss.ko'),
 'build_log_sha256':sha(D/'CAMSS-0065-BUILD.raw.txt'),'helper_sha256':sha(D/'e003h-v4l2-one-frame'),'helper_source_sha256':sha(D/'e003h-v4l2-one-frame.c'),
 'unchanged_hardware_sources':{'camss-csid-680.c':sha(S/'camss-csid-680.c'),'camss-vfe-680.c':sha(S/'camss-vfe-680.c'),'camss-vfe.c':sha(S/'camss-vfe.c')},
 'delta':{
   'hardware_delta':'NONE','new_mmio_reads':0,'new_mmio_writes':0,'new_register_values':0,'new_irq_programming':False,
   'new_sensor_programming':False,'new_csid_programming':False,'new_vfe_bus_programming':False,'new_rtcdm_payload':False,
   'generic_x1e_pix_one_wm_guard_retained':True,'diagnostic_arm_required':True,'qbuf_count_exact':2,
   'buffer_state_required':'VB2_BUF_STATE_ACTIVE','ioctl_path':'QBUF -> STREAMON -> DQBUF -> STREAMOFF',
   'runner':'unchanged proven 0064 first-frame runner','completed_buffer':'slot0 via vb2_buffer_done(DONE)',
   'slot1':'returned to pending queue for STREAMOFF flush','normal_success_hardware_already_stopped_before_vb2_done':True,
   'unsafe_teardown':'DMA/buffer/power ownership pinned until mandatory reboot'
 },
 'next':'Build unarmed Golden-safe 0065 candidate; run one ordinary V4L2 one-frame transaction exactly once.'
}
(D/'0065-static-inspection.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
(D/'0065-STATIC-INSPECTION.txt').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True))
