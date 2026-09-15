#!/usr/bin/env python3
from pathlib import Path
import hashlib, re, subprocess, tempfile
D=Path(__file__).resolve().parent
REPO=D.parents[2]
R=REPO/'src/front-imx681/userspace/runtime'
FIX=D/'evidence/E004EG-G1-STATS3A.bin'
def need(v,m):
    if not v: raise AssertionError(m)
def run(cmd): return subprocess.run(cmd,cwd=REPO,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True).stdout
need(hashlib.sha256(FIX.read_bytes()).hexdigest()=='e69ccbd53a4456d126da0c47afc89622524e414dae5d2023c4f13fc9fd8d2c18','G1 fixture hash')
# Exact fresh Windows request-4 range proof.
with tempfile.TemporaryDirectory(prefix='e004eh-') as td:
    td=Path(td); rp=td/'r4-range-proof'; g1=td/'replay-g1'
    subprocess.run(['cc','-O2','-std=c11','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off','-I'+str(R),str(D/'r4-range-proof.c'),str(R/'native-target-aggregate.c'),'-lm','-o',str(rp)],check=True,cwd=REPO)
    rout=subprocess.check_output([str(rp)],text=True)
    need('WINDOWS_RANGE=0x42809ffb' in rout,'range oracle')
    need('OLD_POINT=0x43b62909' in rout,'old point collapse discriminator')
    sources=['native-raw-aec-loop.c','native-stats3a.c','native-effective-analyzers.c','native-bhist-bank4.c','native-aec-request-loop.c','native-internal-cap.c','native-final-exposure.c','native-final-target.c','native-aec-tail.c','native-target-aggregate.c','native-convergence.c','native-t681.c','native-aec-state.c','native-log103.c']
    cmd=['cc','-O2','-std=c11','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off','-I'+str(R),str(D/'replay-g1.c')]+[str(R/x) for x in sources]+['-lm','-o',str(g1)]
    subprocess.run(cmd,check=True,cwd=REPO)
    gout=subprocess.check_output([str(g1),str(FIX)],text=True)
    need('G1_CONV_SHORT=84034875' in gout,'corrected G1 convergence')
    need('G1_CAP_SHORT=84034875' in gout,'G1 not capped')
    need('G1_RETAINED_SHORT=84034869' in gout,'G1 retained')
    need('E004EH_G1_INTERVAL_REPLAY=PASS' in gout,'G1 marker')
old=(REPO/'experiments/E004-front-ir-vd55g0/e004eg-static-full-light-windows-linux-parity/evidence/linux/OFFLINE-AEC-REPLAY.txt').read_text()
oldg1=next(x for x in old.splitlines() if x.startswith('G=1 '))
need('CONV=154912929,' in oldg1,'old point G1 authority')
# Source guards: range-aware final aggregation must be canonical; no production use of point aggregator.
ft=(R/'native-final-target.c').read_text(); eff=(R/'native-effective-analyzers.c').read_text(); agg=(R/'native-target-aggregate.c').read_text()
need(ft.count('e003i_method11_range_aggregate')==3,'three final range aggregators')
need('e003i_method11_point_aggregate' not in ft,'point aggregator removed from production final targets')
for marker in ('out->sat_prev.low = 0.0f','out->dark_prev.low =','out->dark_prev.high =','out->illuminance.low = 0.0f','out->short_sat_prev.low = 0.0f'):
    need(marker in eff,'effective analyzer range marker '+marker)
for marker in ('upper <= ranges[i].low','lower >= ranges[i].high'):
    need(marker in agg,'generic method11 range rule '+marker)

rj=__import__('json').loads((D/'RESULT.json').read_text())
need(rj['camera_stack_manifest_sha256']=='cc1faed4358863b3b5714e2f5310649557ccddec5c1ccef8fc60acefef3569e1','stack manifest result')
need(rj['front_package_manifest_sha256']=='1aa738e45692faf41dfb0469e5fd7f542e304d33b127c7257106c9b7f4ad6da2','front manifest result')
life=(D/'evidence/PACKAGE-ROOT-LIFECYCLE.txt').read_text()
for marker in ('SP11 CAMERA STACK INSTALLED ROOT VERIFY: PASS ACTIVATED=NO','TAMPER_VERIFY_RC=1','SENTINEL_PRESERVED=YES','PACKAGE_PATHS_REMOVED=YES'):
    need(marker in life,'lifecycle '+marker)
installer=(REPO/'src/sp11-camera-stack/install-live-unactivated.sh').read_text()
need('STACK_SHA=cc1faed4358863b3b5714e2f5310649557ccddec5c1ccef8fc60acefef3569e1' in installer,'live installer stack pin')

print(rout.strip())
print(gout.strip())
print('OLD_G1_CONV_SHORT=154912929')
print('E004EH_VERIFY=PASS ROOT_CAUSE=METHOD11_POINT_COLLAPSE')
