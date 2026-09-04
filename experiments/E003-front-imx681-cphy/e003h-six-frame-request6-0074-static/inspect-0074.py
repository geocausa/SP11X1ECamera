#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, pathlib, re, subprocess, tempfile

HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE0072=ROOT/'experiments/E003-front-imx681-cphy/e003h-iq-provider-0072-static'
ATOMIC=ROOT/'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static'
OUT=HERE/'0074-static-inspection.json'

def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v: raise RuntimeError(m)

expected_pre={
 'camss.c':'788243cbf08d1f8cc1500a8c7177e30095875bd3b3be54bf0ac0fdec106dba91',
 'camss-csid-680.c':'9c79fec22fc63738dd05b33aa7d43f4a68be4935b522fa35354a0170c498ae90',
 'camss-csid.h':'bd8f68b623f2e8e5a2c624fdd8ce7a901c7fc11fa35a2efbd04f8273fca3aee2',
 'camss.h':'da2941a9d2afa6250773c682027fc70512e32daa69a9478cb372ecaa74be37c0',
 'camss-vfe-680.c':'99b7f9c18456e1926a5ad82b56a9b025a798add797c09490b645d9907b3a3208',
 'camss-vfe.c':'98474729d5036a4e1770e3ab7d275ccaaba143b22202468e4ad8b93c0cbec2cb',
 'camss-vfe.h':'440b03e1d2701c311cddc6beeae70bccfea5f472f75790a1879167d66395e857',
 'camss-video.c':'6da7b6881e267f02775818a5a9bcf3bf1f14e38c5528d467d23b2ba540228c5d',
 'camss-video.h':'071d4fd368dfb6145842b5c7da3c270cf2b3abf15fc919777be2c68cc7e5ac8c',
}
for n,h in expected_pre.items(): need(sha(HERE/'preimage'/n)==h,f'0072 preimage drift {n}')

patch=(HERE/'0074-six-frame-request6.patch').read_text()
need('--- a/camss.c' in patch and '+++ b/camss.c' in patch,'patch path drift')
for forbidden in ('camss-vfe-680.c','camss-csid-680.c','camss-video.c','camss-video.h','x1-microsoft-denali'):
    need(forbidden not in patch,f'unexpected hardware/source delta: {forbidden}')

# Mechanically reapply the 0074 patch to the preserved accepted-0072 camss.c.
with tempfile.TemporaryDirectory() as td:
    td=pathlib.Path(td); (td/'camss.c').write_bytes((HERE/'preimage/camss.c').read_bytes())
    subprocess.check_call(['patch','-p1','-i',str(HERE/'0074-six-frame-request6.patch')],cwd=td,
                          stdout=subprocess.DEVNULL)
    need(sha(td/'camss.c')==sha(HERE/'postimage/camss.c'),'postimage is not patch reproduction')

c=(HERE/'postimage/camss.c').read_text()
checks={
 'frame_limit_6': 'frame_limit != 6' in c and 'camss_x1e_pix_runner_frames(camss, &req, &result, 6)' in c,
 'request_ids_4_5_6': all(x in c for x in ('inputs->steady.request_id != 4','inputs_next->steady.request_id != 5','inputs_next_next->steady.request_id != 6')),
 'fifo_5_then_6': c.find('camss_x1e_pix_iq_provider_next(video, 5') < c.find('camss_x1e_pix_iq_provider_next(video, 6'),
 'r6_firmware': 'E003H_PIX_ORACLE_CAPSULE_R6.bin' in c,
 'second_requeue': 'video_requeued_next' in c and 'live_requeue_next_acquired' in c and 'sixth != req->video[1]' in c,
 'slot1_request6': 'slot1_reused_again' in c and 'materialized_next_next->steady' in c,
 'sixth_retire': 'video_done_sixth' in c and 'video_sixth_seen' in c and 'slot1_reusable_third' in c,
 'no_same_boot_loop': 'for (;;)' not in c[c.find('static void camss_x1e_pix_v4l2_live_work'):c.find('static int camss_x1e_pix_trigger_buffer') if c.find('static int camss_x1e_pix_trigger_buffer')>0 else len(c)],
}
need(all(checks.values()),f'kernel structural checks failed {checks}')

h=(HERE/'e003h-v4l2-six-frame.c').read_text()
need('#define FRAME_COUNT 6U' in h,'helper frame count')
need('{ 0, 1, 2, 3, 0, 1 }' in h,'helper ordering')
need('if (i == 0 || i == 1)' in h,'helper dual requeue')
need('output5.qc10c' in h and 'save_file(argv[7], map[1]' in h,'helper six outputs')
need('pin_until_reboot' in h,'helper failure pin policy')

vermagic=subprocess.check_output(['modinfo','-F','vermagic',str(HERE/'qcom-camss.ko')],text=True).strip()
need(vermagic.startswith('7.1.5-sp11-render-parity-v4+ '),'vermagic drift')

m=json.loads((ATOMIC/'atomic-runtime-capsules-manifest.json').read_text())
need(m['accepted'],'atomic manifest not accepted')
expected_caps={
 '4':'1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa',
 '5':'8e447a662a47e47db7dd211d6a109d590531309f944e52b729a4351b5a00da11',
 '6':'c88e7a75f228fac7b69a4a122fd618aa054bdbf98e83ff541be9c20177844583',
}
for rid,hv in expected_caps.items():
    need(m['requests'][rid]['output_sha256']==hv,f'atomic R{rid} manifest drift')
    need(sha(ATOMIC/'atomic-runtime-capsules'/f'E003H_PIX_ORACLE_CAPSULE_ATOMIC_R{rid}.bin')==hv,f'atomic R{rid} file drift')

result={
 'schema':'sp11-e003h-six-frame-request6-0074-static-v1',
 'accepted':True,
 'runtime_authorized':False,
 'request6_runtime_authorized':False,
 'base':'accepted E003h 0072 five-frame IQ-provider runtime',
 'source_delta_files':['camss.c'],
 'hardware_delta':'EXACTLY_ONE_STEADY_REQUEST6_PLUS_SLOT1_REBIND_AND_SECOND_LIVE_REQUEUE',
 'forbidden_delta':{'sensor':False,'csiphy':False,'csid_recipe':False,'vfe_recipe':False,'dt':False,'startup_priming':False,'unrelated_mmio':False},
 'expected_indices':[0,1,2,3,0,1],
 'expected_sequences':[0,1,2,3,4,5],
 'request_ids':[4,5,6],
 'provider_dequeue_ids':[5,6],
 'kernel_checks':checks,
 'qcom_camss_sha256':sha(HERE/'qcom-camss.ko'),
 'helper_source_sha256':sha(HERE/'e003h-v4l2-six-frame.c'),
 'helper_sha256':sha(HERE/'e003h-v4l2-six-frame'),
 'vermagic':vermagic,
 'atomic_capsules_sha256':expected_caps,
 'failure_policy':'No same-boot retry. Any runtime ambiguity, timeout, ordering mismatch, RT-CDM fault or teardown uncertainty consumes the one-shot and requires external Golden reboot.',
}
OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps(result,indent=2,sort_keys=True))
