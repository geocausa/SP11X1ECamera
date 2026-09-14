#!/usr/bin/env python3
from pathlib import Path
import json
D=Path(__file__).resolve().parent
def need(v,m):
    if not v: raise AssertionError(m)
p=json.loads((D/'PROVENANCE.json').read_text())
need(p['hexagon']['combined_object_sha256']=='4d413d54fb29d898b0a662edcc957eb02ccf4769e7036aa4c986b0c8be6afc48','object authority')
need(p['trust']=={'signed':False,'production_admitted':False,'runtime_authorized':False,'verification_bypass_allowed':False},'trust boundary')
wire=(D/'sp11-securepd-camera-wire.c').read_text();native=(D/'sp11-securepd-native-binding.c').read_text();proxy=(D/'sp11-loadalgo-camera-proxy.c').read_text();worker=(D/'sp11-parity-worker.c').read_text()
for tok in ('sizeof(struct sp11_securepd_gaussian_packet) == 96','sizeof(struct sp11_securepd_camera_control) == 32','sp11_parity_worker_run'):need(tok in wire,'wire '+tok)
for tok in ('SP11_QURT_MEM_CACHE_WRITEBACK','SP11_SECUREPD_MAP_PERMISSION_RW','"s2p_algo"','"p2s_algo"','secure_pd_thread_create','void algo_main'):need(tok in native,'native '+tok)
for tok in ('c->src_offset=0','c->dst_offset=0','c->heap_offset=0','c->mode_static=0'):need(tok in proxy,'proxy '+tok)
need('../../e004' not in wire and '../../e004' not in worker and '../../e004' not in (D/'sp11-securepd-camera-wire.h').read_text(),'historical relative include remains')
b=(D/'build-offline.sh').read_text();need('SIGNED=NO ADMITTED=NO RUNTIME=NO' in b,'offline marker');need('4d413d54fb29d898b0a662edcc957eb02ccf4769e7036aa4c986b0c8be6afc48' in b,'build hash gate')
print('SP11 PROTECTED WORKER SOURCE VERIFY: PASS OFFLINE_ONLY=YES')
