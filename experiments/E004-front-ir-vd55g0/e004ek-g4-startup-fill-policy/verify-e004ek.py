#!/usr/bin/env python3
from pathlib import Path
import hashlib,subprocess,tempfile
D=Path(__file__).resolve().parent; R=D.parents[2]; RT=R/'src/front-imx681/userspace/runtime'; L=R/'src/front-imx681/bin/front-imx681-launcher.py'
def need(v,m):
    if not v: raise AssertionError(m)
with tempfile.TemporaryDirectory(prefix='e004ek-') as td:
    exe=Path(td)/'unit'
    subprocess.run(['cc','-O2','-std=c11','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off','-I'+str(RT),str(D/'test-policy.c'),str(RT/'production-write-policy.c'),'-o',str(exe)],check=True,cwd=R)
    out=subprocess.check_output([str(exe)],text=True)
    need('E004EK_POLICY_UNIT=PASS' in out,'unit marker')
s=(RT/'front-imx681-production-capture.c').read_text(); p=(RT/'production-write-policy.c').read_text(); l=L.read_text()
need('PROD_G4_STARTUP_FILL_ALLOW' in s,'runtime allow marker')
need('source_generation == 4U && !g4_startup_fill' in s,'G4 mismatch fail closed')
need('ctx->startup_fill_write_count++' in s,'startup fill accounting')
need('audit.startup_fill_write_count != 1U || audit.later_native_write_count != 0U' in s,'mode final invariant')
need('g4-startup-fill-shadow' in p and 'g4-startup-fill-shadow' in l,'policy exposed')
need("a.post_g3_write_policy!='shadow' and not a.allow_one_native_write" in l,'explicit execution authorization retained')
need('SP11_FRONT_POST_G3_CAP_RELEASE_ONE_SHOT' in p and 'SP11_FRONT_POST_G3_SHADOW' in p,'old policies retained')
print(out.strip())
print('E004EK_VERIFY=PASS DEFAULTS_UNCHANGED=YES SYNTHETIC_DELTA=NO')
