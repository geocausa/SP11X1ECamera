#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,subprocess
D=Path(__file__).resolve().parent
R=D.parents[2]
def need(v,m):
    if not v: raise AssertionError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=json.loads((D/'RESULT.json').read_text());e=json.loads((D/'evidence/SOAK-SUMMARY.json').read_text());p=json.loads((D/'ATTEMPT1-PASS.json').read_text())
need(r['status']=='PASS_CAPTURE_RGB_ALTERNATING_SOAK_GOLDEN_RETURN_RETIRED','status')
need(e['status']=='PASS_CAPTURE_E004DN_RGB_ALTERNATING_SOAK_GOLDEN_RETURN_RETIRED','evidence status')
need(p['status']=='PASS_CAPTURE_E004DN_RGB_ALTERNATING_SOAK','attempt status')
need(r['candidate_boot_id']==e['candidate_boot_id']=='63634d5b-01d8-4faa-922b-96a35322958e','candidate boot')
need(r['golden_return_boot_id']==e['golden_return_boot_id']=='9dc8cdc6-d8d4-40fc-ba09-fdd7ab4ebace','golden boot')
need(r['legs']==['rear','front','rear','front','rear','front'] and r['cross_camera_transitions']==5,'legs')
need(r['front_frames_each']==[27,27,27] and r['rear_frames_each']==8,'frames')
need(r['rear_colorbar_exact'] and e['rear_colorbar_sha256']=='6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346','rear colorbar')
need(r['awb_selection_modes']=={'triangle':72,'centroid':0,'two_vertex':0} and r['awb_fallback_rows']==0,'awb modes')
need(r['all_source_runtime_suspend'] and r['kernel_health']=='PASS' and r['final_route_state']=='neutral','health')
need(not r['same_boot_retry_authorized'] and not p['same_boot_retry_performed'],'retry')
need(r['golden_return']=='PASS' and r['candidate_retired'] is True,'lifecycle')
need((D/'GOLDEN-RETURN.txt').is_file() and 'status=PASS_GOLDEN_RETURN' in (D/'GOLDEN-RETURN.txt').read_text(),'golden record')
need((D/'RETIRE.txt').is_file() and 'status=PASS_CANDIDATE_RETIRED' in (D/'RETIRE.txt').read_text(),'retire record')
for n,h in [(1,'f94a7b2d536aa6acf467acc508ef0f2cbbe62de1a006659e1800dcbd6afe6845'),(2,'107ed50f47cab40411761aea4ead0f47a26da7af4adc970816cec8014c90ea6f'),(3,'32b6f9b8d1e210c24d5a121d1ef7e4808b1648fa1d5d16461c13f0dcadfa4ede')]:
    need(sha(D/f'evidence/FRONT{n}-PRODUCER-RESULT.json')==h,f'front{n} producer hash')
need(sha(D/'evidence/LIVE-RESULT.json')==sha(D/'runtime-output/LIVE-RESULT.json'),'live result compact copy')
print('E004dn CLOSE VERIFY: PASS (six-leg RGB soak + Golden return + retired candidate)')
