#!/usr/bin/env python3
import hashlib, json, pathlib, re
D=pathlib.Path(__file__).resolve().parent
SRC=pathlib.Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss')
pre=D/'preimage'
read=lambda p:pathlib.Path(p).read_text()
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
post={f:read(SRC/f) for f in ['camss.c','camss.h','camss-video.c','camss-video.h','camss-csid-680.c','camss-csid.h','camss-vfe-680.c','camss-vfe.c','camss-vfe.h']}
old={f:read(pre/f) for f in post}
changed=[f for f in post if post[f]!=old[f]]
assert changed == ['camss.c','camss-video.c','camss-video.h'], changed
# Hardware source files remain byte-identical.
hw=['camss-csid-680.c','camss-csid.h','camss-vfe-680.c','camss-vfe.c','camss-vfe.h']
assert all(post[f]==old[f] for f in hw)
# Camera-programming call counts must not change.
terms=['writel(','readl(','camss_x1e_pix_rtcdm_submit_epoch0_batch(',
       'camss_x1e_pix_submit_prime(','camss_x1e_pix_submit_startup(',
       'vfe680_x1e_pix_runtime_bus_update(','vfe680_x1e_pix_runtime_rebind(',
       'csid680_x1e_front_ipp_enable(','csid680_x1e_front_ipp_stop(']
deltas={t:{'pre':old['camss.c'].count(t),'post':post['camss.c'].count(t)} for t in terms}
assert all(x['pre']==x['post'] for x in deltas.values()), deltas
s=post['camss.c']
a=s.index('/*\n * E003h 0072 steady-IQ provider FIFO.')
b=s.index('static int camss_x1e_pix_trigger_buffer',a)
provider=s[a:b]
forbidden=['writel(','readl(','camss_rtcdm1_windows_fifo0_commit(',
           'camss_x1e_pix_rtcdm_submit_epoch0_batch(',
           'vfe680_x1e_pix_runtime_bus_update(','csid680_x1e_front_ipp_enable(',
           'v4l2_subdev_call(']
assert not any(t in provider for t in forbidden)
# Provider semantics.
need=[
 'CAMSS_X1E_PIX_IQ_QUEUE_DEPTH_MAX\t8',
 'CAMSS_X1E_PIX_IQ_FIRST_STEADY_REQUEST\t5',
 'request_id != video->x1e_pix_iq_last_enqueued + 1',
 'packet->request_id != video->x1e_pix_iq_last_dequeued + 1',
 'video->x1e_pix_iq_depth >= CAMSS_X1E_PIX_IQ_QUEUE_DEPTH_MAX',
 'video->x1e_pix_iq_closed',
 'memcpy(packet->capsule, capsule, capsule_size)',
 'camss_x1e_pix_capsule_parse(packet->capsule, packet->capsule_size',
]
assert all(x in provider for x in need), [x for x in need if x not in provider]
# Compatibility path must route request5 through provider, not a direct fw5 pointer.
worker=s[s.index('static void camss_x1e_pix_v4l2_live_work'):s.index('int camss_x1e_pix_v4l2_start',s.index('static void camss_x1e_pix_v4l2_live_work'))]
assert 'fw5' not in worker
assert 'camss_x1e_pix_iq_provider_seed_firmware' in worker
assert 'camss_x1e_pix_iq_provider_next(video, 5' in worker
assert 'req.capsule_next = iq5->capsule;' in worker
assert 'req.capsule_next_size = iq5->capsule_size;' in worker
# Stop wakes both buffer and IQ waits.
vs=post['camss-video.c']
assert 'wake_up_all(&video->x1e_pix_iq_wait);' in vs
# No request6 execution contract appears in provider/worker delta.
assert 'provider_next(video, 6' not in s
# Existing 0071 live-requeue hardware schedule remains present.
for marker in ['camss_x1e_pix_runner_frames(camss, &req, &result, 5)',
               'req.live_requeue = true;',
               'CAMSS_X1E_PIX_TRIGGER_FW_R5']:
    assert marker in worker or marker in s
out={
 'schema':'sp11-e003h-iq-provider-0072-static-v1',
 'accepted':True,
 'runtime_authorized':False,
 'request6_runtime_authorized':False,
 'base_runtime_commit':'bb2f78f6c1abeee7026b863a17d19264c56e1816',
 'changed_camss_files':changed,
 'hardware_source_sha256':{f:sha(SRC/f) for f in hw},
 'hardware_call_count_deltas':{t:{**v,'delta':v['post']-v['pre']} for t,v in deltas.items()},
 'provider':{
   'first_request_id':5,
   'max_depth':8,
   'owns_capsule_copy':True,
   'strict_monotonic_enqueue':True,
   'strict_monotonic_dequeue':True,
   'bounded_wait':True,
   'stop_wakes_waiter':True,
   'direct_mmio':False,
   'rtcdm_submission':False,
   'sensor_csid_vfe_operation':False,
   'external_userspace_entrypoint':False,
   'compatibility_seed':'existing exact request5 firmware capsule only',
 },
 'worker':{
   'request4_bootstrap_unchanged':True,
   'request5_passes_provider_fifo':True,
   'frame_limit':5,
   'live_requeue_retained':True,
   'request6_used':False,
 },
 'module_sha256':sha(D/'qcom-camss.ko'),
 'patch_sha256':sha(D/'0072-iq-provider.patch'),
}
(D/'0072-static-inspection.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True))
