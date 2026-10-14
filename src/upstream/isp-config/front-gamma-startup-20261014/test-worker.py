#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
from pathlib import Path
import hashlib,json,math,resource,subprocess,sys,yaml
Q=Path(__file__).resolve().parent;R=Q.parents[3]
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 O=Path(sys.argv[1]);O.mkdir()
 baseline=json.loads((R/'src/upstream/isp-config/measured-front-reuse-20261014/baseline-audit.json').read_text())
 closure={
 'sp11-front-gamma-startup.h':Q/'sp11-front-gamma-startup.h',
 'native-front-gamma.h':R/'src/native-rgb/native-front-gamma.h',
 'native-front-isp-params.h':R/'src/native-rgb/native-front-isp-params.h',
 'sp11-front-cold-fields.h':R/'src/upstream/isp-config/cold-front-fields-20261014/sp11-front-cold-fields.h',
 'sp11-front-measured-config.h':R/'src/upstream/isp-config/measured-front-reuse-20261014/sp11-front-measured-config.h',
 'sp11-cdm.h':R/'src/upstream/isp-config/sp11-cdm.h'}
 for n,p in closure.items():(O/n).write_bytes(p.read_bytes())
 for n in ['native-front-gamma.h','native-front-isp-params.h']:
  assert sha(closure[n])==sha(Path(baseline['native_stage'])/n),'native baseline codec differs'
 for n in ['native-front-param-state.h','native-front-params.h','test-front-gamma.c','test-front-isp-params.c']:
  (O/n).write_bytes((R/'src/native-rgb'/n).read_bytes())
 (O/'test-host.c').write_bytes((Q/'test-host.c').read_bytes())
 tuning=R/'src/native-rgb/front-ae/tuning/imx681-front-v15.yaml'
 assert sha(tuning)==baseline['repository_pins'][str(tuning.relative_to(R))]
 data=yaml.safe_load(tuning.read_text())
 points=[]
 for n in ['gamma_r','gamma_g','gamma_b']:
  row=data[n];assert len(row)==257
  points.extend(math.floor(float(v)+0.5) for v in row)
 assert all(0<=v<=1023 for v in points)
 import struct
 own_input=struct.pack('<771H',*points)
 source=(Q/'sp11-front-gamma-startup.h').read_text()
 mutations={
 'early_publication':source.replace('\tif (!out || !policy || !points || !workspace ||','\tif (out)\n\t\tout[0] = 0;\n\tif (!out || !policy || !points || !workspace ||',1),
 'bypass_domain':source.replace('ret = sp11_front_cold_fields(checked, sizeof(checked), policy);','ret = 0;\n\t(void)checked;'),
 'missing_point_output_overlap':source.replace('sp11_cdm_overlap(out, NF_GAMMA_BYTES, points,\n\t\t\t     count * sizeof(*points))','false'),
 'shifted_payload_output':source.replace('NF_GAMMA_WORD_COUNT, out, NF_GAMMA_BYTES','NF_GAMMA_WORD_COUNT, out + 4, NF_GAMMA_BYTES')}
 assert all(s!=source for s in mutations.values())
 runs=[];prior=[]
 for cc in ['gcc','clang']:
  for label,s in [('actual',source),*mutations.items()]:
   (O/'sp11-front-gamma-startup.h').write_text(s)
   exe=O/(cc+'-'+label)
   cmd=[cc,'-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+str(O),str(O/'test-host.c'),'-o',str(exe)]
   p=subprocess.run(cmd,capture_output=True,text=True);assert p.returncode==0,p.stderr[-2500:]
   p=subprocess.run([str(exe)],input=own_input,capture_output=True,timeout=30)
   (O/(cc+'-'+label+'.log')).write_bytes(p.stdout+p.stderr)
   if label=='actual':
    assert p.returncode==0,p.stderr[-2500:].decode()
    result=json.loads(p.stdout);assert result['own_v15_curves']==1
    runs.append({'compiler':cc,'ASan_UBSan':True,'result':result})
   else:assert p.returncode!=0,'unsafe mutation survived '+label
  for name in ['test-front-gamma.c','test-front-isp-params.c']:
   exe=O/(cc+'-'+name[:-2])
   p=subprocess.run([cc,'-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+str(O),str(O/name),'-o',str(exe)],capture_output=True,text=True)
   assert p.returncode==0,p.stderr[-2500:]
   p=subprocess.run([str(exe)],capture_output=True,text=True,timeout=15)
   assert p.returncode==0,p.stderr[-2500:]
   prior.append({'compiler':cc,'unchanged_test':name,'result':p.stdout.strip()})
 (O/'sp11-front-gamma-startup.h').write_text(source)
 refs=['src/native-rgb/native-front-gamma.h','src/native-rgb/native-front-isp-params.h',
 'src/native-rgb/front-ae/camss-x1e-ipa.cpp','src/native-rgb/native-front-gamma-kernel.inc',
 'src/native-rgb/native-front-nv12-commands.h','src/native-rgb/front-pattern/native-front-cst.inc',
 'src/native-rgb/test-front-gamma.c','src/native-rgb/test-front-isp-params.c']
 result={'schema':'sp11-front-gamma-startup-source-v1',
 'status':'PASS_STARTUP_BYTES_EQUAL_WORKING_NATIVE_TONE_BRIDGE',
 'compiler_runs':runs,'compiled_mutations_rejected_each':list(mutations),
 'unchanged_prior_tests':prior,'header_pins':{n:sha(p) for n,p in closure.items()},
 'prior_reference_pins':{n:sha(R/n) for n in refs},
 'own_v15_tuning_sha256':sha(tuning),'own_curve_samples':771,'native_gamma_words':768,
 'native_gamma_bytes':3072,'semantic_input_bits':10,'native_base_delta_bits':12,
 'scale_formula':'(value*4095+511)/1023','endpoint_input_max':1023,'endpoint_output_max':4095,
 'working_native_baseline_codecs_unchanged':True,'own_tone_curves_exported':False,
 'large_kernel_stack_workspace':False,'private_startup_or_tuning_read':False,
 'calibration_remeasured':False,'runtime_changed':False,'hardware':False,
 'limits':['Numerical Gamma leaf only; no source/physical proof of the complete CST/core precision chain',
 'No DMI bank/selector/address/lifetime or module activation or loader replacement',
 'Caller must own workspace outside the kernel stack and immutable input/output extents']}
 (O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'status':result['status'],'compiler_results':[x['result'] for x in runs],'runtime_changed':False}))
if __name__=='__main__':main()
