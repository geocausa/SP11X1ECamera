#!/usr/bin/env python3
import argparse, hashlib, json, re, subprocess, tempfile
from pathlib import Path

BASE_SHA = {
    'camss.c': '1111d3e88b88729a8851a60f31ef1bbc877dc127ccb9d4cb998311f5ba7834f5',
    'camss-vfe-680.c': 'cdbd58c0276df79605d51a81784a6ba37cf8b0f1b1eb32e2693d1a1e9b0a97c6',
    'camss-vfe.h': 'cbae10aa8d6ac29dbbfbd11182e63fc33748530eb6ca09f8e7b50ff3285813fa',
}

def die(s): raise SystemExit('FAIL: ' + s)
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def between(s,a,b):
    i=s.find(a)
    if i < 0: die('missing source anchor: '+a)
    j=s.find(b,i+len(a))
    if j < 0: die('missing source tail: '+b)
    return s[i:j]
def ordered(text, needles, label):
    pos=[]; start=0
    for n in needles:
        i=text.find(n,start)
        if i < 0: die(f'{label}: missing/out-of-order {n}')
        pos.append(i); start=i+len(n)
    return pos

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--camss',type=Path,required=True)
    ap.add_argument('--vfe680',type=Path,required=True)
    ap.add_argument('--vfeh',type=Path,required=True)
    ap.add_argument('--camss-object',type=Path,required=True)
    ap.add_argument('--linked-object',type=Path,required=True)
    ap.add_argument('--module',type=Path,required=True)
    ap.add_argument('--patch',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    src=a.camss.read_text(); vfe=a.vfe680.read_text(); vh=a.vfeh.read_text()
    runner=between(src,'static int camss_x1e_pix_runner_once(',
                   'struct camss_x1e_pix_runner_static_ops')

    start_order=[
      'camss_x1e_pix_submit_startup(camss, &materialized->startup, 0)',
      'camss_x1e_pix_submit_prime(camss, &materialized->prime, 0)',
      'camss_x1e_pix_submit_startup(camss, &materialized->startup, 1)',
      'vfe680_x1e_pix_runtime_bus_prepare(vfe, pix)',
      'camss_x1e_pix_submit_prime(camss, &materialized->prime, 1)',
      'camss_x1e_pix_submit_startup(camss, &materialized->startup, 2)',
      'camss_x1e_pix_submit_startup(camss, &materialized->startup, 3)',
      'camss_x1e_pix_runner_stream(&csid->subdev, true)',
      'camss_x1e_pix_runner_stream(&csiphy->subdev, true)',
      'camss_x1e_pix_runner_stream(req->sensor, true)',
      'vfe680_x1e_pix_runtime_poll_epoch0(vfe,',
      'vfe680_x1e_pix_runtime_bus_update(vfe, pix, 1)',
      'camss_x1e_pix_submit_prime(camss, &materialized->prime, 2)',
      'vfe680_x1e_pix_runtime_poll_video(vfe,',
      'vfe680_x1e_pix_runtime_retire_video(pix, 0, &result->video_done)',
    ]
    start_pos=ordered(runner,start_order,'first-frame start')
    forbidden=[
      'camss_x1e_pix_submit_prime(camss, &materialized->prime, 3)',
      'camss_x1e_pix_rtcdm_submit_epoch0_batch(camss, &materialized->steady)',
      'camss_x1e_pix_rtcdm_submit_epoch0_batch(camss,',
      'camss_x1e_pix_runner_stream(&vfe->line[VFE_LINE_PIX].subdev',
    ]
    for n in forbidden:
        if n in runner: die('forbidden runner call: '+n)
    if '.callable_runner_authorized = false' not in src:
        die('0031 runtime-authorization lock not preserved')

    normal=between(runner,'if (frame_done) {','} else {')
    rollback=between(runner,'} else {','result->teardown_safe = teardown_safe;')
    normal_order=[
      'camss_x1e_pix_runner_stream(&csid->subdev, false)',
      'vfe680_x1e_pix_runtime_bus_stop(vfe, pix)',
      'camss_x1e_pix_rtcdm_stop_close(camss)',
      'camss_x1e_pix_runner_stream(&csiphy->subdev, false)',
      'camss_x1e_pix_runner_stream(req->sensor, false)',
    ]
    rollback_order=[
      'camss_x1e_pix_runner_stream(req->sensor, false)',
      'camss_x1e_pix_runner_stream(&csiphy->subdev, false)',
      'camss_x1e_pix_runner_stream(&csid->subdev, false)',
      'vfe680_x1e_pix_runtime_bus_stop(vfe, pix)',
      'camss_x1e_pix_rtcdm_stop_close(camss)',
    ]
    ordered(normal,normal_order,'normal stop')
    ordered(rollback,rollback_order,'rollback')
    for n in ('result->video_done = NULL;',
              'DMA/power intentionally pinned until reboot',
              'return ret ? ret : -EIO;'):
        if n not in runner: die('fail-closed teardown marker missing: '+n)
    if runner.find('if (!teardown_safe)') > runner.find('vfe680_x1e_pix_runtime_release(vfe, pix)'):
        die('DMA release occurs before teardown-safe gate')

    bridge_need=[
      'int vfe680_x1e_pix_runtime_alloc(',
      'void vfe680_x1e_pix_runtime_release(',
      'int vfe680_x1e_pix_runtime_bus_prepare(',
      'int vfe680_x1e_pix_runtime_bus_update(',
      'void vfe680_x1e_pix_runtime_bus_stop(',
      'int vfe680_x1e_pix_runtime_poll_epoch0(',
      'int vfe680_x1e_pix_runtime_poll_video(',
      'int vfe680_x1e_pix_runtime_retire_video(',
    ]
    for n in bridge_need:
        if n not in vfe or n not in vh: die('bridge/prototype missing: '+n)
    if 'if (index != expected_slot || !done || reusable)' not in vfe:
        die('VIDEO retirement does not reject premature slot reuse')
    if re.search(r'EXPORT_SYMBOL[^\n]*vfe680_x1e_pix_runtime',vfe):
        die('private bridge exported')

    nm_camss=subprocess.check_output(['llvm-nm','-an',str(a.camss_object)],text=True)
    nm_linked=subprocess.check_output(['llvm-nm','-an',str(a.linked_object)],text=True)
    if ' camss_x1e_pix_runner_once' not in nm_camss or ' camss_x1e_pix_runner_recipe' not in nm_camss:
        die('runner/recipe symbols missing')
    for n in [x.split('(')[0].split()[-1] for x in bridge_need]:
        if n not in nm_linked: die('linked bridge symbol missing: '+n)

    rel=subprocess.check_output(['llvm-objdump','-r',str(a.camss_object)],text=True)
    runner_refs=[x for x in rel.splitlines() if 'camss_x1e_pix_runner_once' in x]
    if len(runner_refs)!=1 or 'R_AARCH64_ABS64' not in runner_refs[0]:
        die('runner retention relocation is not exactly one ABS64')
    if any('camss_x1e_pix_runner_recipe' in x for x in rel.splitlines()):
        die('runtime relocation references runner recipe')
    bridge_counts={
      'vfe680_x1e_pix_runtime_alloc':1,
      'vfe680_x1e_pix_runtime_release':1,
      'vfe680_x1e_pix_runtime_bus_prepare':1,
      'vfe680_x1e_pix_runtime_bus_update':1,
      'vfe680_x1e_pix_runtime_poll_epoch0':1,
      'vfe680_x1e_pix_runtime_poll_video':1,
      'vfe680_x1e_pix_runtime_retire_video':1,
      'vfe680_x1e_pix_runtime_bus_stop':3,
    }
    for sym,count in bridge_counts.items():
        got=sum(sym in x for x in rel.splitlines())
        if got!=count: die(f'{sym} relocation count {got} != {count}')

    current={'camss.c':sha(a.camss),'camss-vfe-680.c':sha(a.vfe680),'camss-vfe.h':sha(a.vfeh)}
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); d=root/'drivers/media/platform/qcom/camss'; d.mkdir(parents=True)
        for name,path in [('camss.c',a.camss),('camss-vfe-680.c',a.vfe680),('camss-vfe.h',a.vfeh)]:
            (d/name).write_bytes(path.read_bytes())
        subprocess.run(['patch','-s','-R','-d',td,'-p1'],input=a.patch.read_bytes(),check=True)
        reverse={name:sha(d/name) for name in BASE_SHA}
        if reverse!=BASE_SHA: die('reverse reconstruction != published 0032 base')
        subprocess.run(['patch','-s','-d',td,'-p1'],input=a.patch.read_bytes(),check=True)
        forward={name:sha(d/name) for name in BASE_SHA}
        if forward!=current: die('forward reconstruction != current source')

    out={
      'accepted':True,'schema':'sp11-e003h-pix-first-frame-runner-unarmed-v1',
      'patch_sha256':sha(a.patch),'source_sha256':current,
      'camss_object_sha256':sha(a.camss_object),'linked_object_sha256':sha(a.linked_object),
      'module_sha256':sha(a.module),'base_0032_sha256':BASE_SHA,
      'reverse_reconstruction_sha256':reverse,'forward_reconstruction_sha256':forward,
      'first_frame_call_order':start_order,
      'prime_indices_submitted':[0,1,2],'prime3_submitted':False,'steady_batch_submitted':False,
      'bus_update_slot':1,'video_retire_slot':0,
      'normal_stop_order':normal_order,'rollback_order':rollback_order,
      'teardown_failure_policy':'do not free DMA or drop pipeline power; pin until reboot',
      'runner_recipe_relocations':1,'runner_recipe_runtime_references':0,
      'generic_vfe1_pix_s_stream_called':False,
      'epoch0_timeout_us':500000,'video_timeout_us':500000,
      'timeout_policy':'bounded experiment safety limits, not claimed Windows timing constants',
      'callable_runner_authorized_flag':False,
      'runtime_reachable':False,
    }
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('PASS: first-frame PIX runner is exact-prefix, fail-closed, reconstructable and retained-only')
if __name__=='__main__': main()
