#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Reuse retained reset/ISR suite on candidate34, plus command-held reset gate."""
from pathlib import Path
import importlib.util,json,re,subprocess,sys
Q=Path(__file__).resolve().parent;R=Q.parents[3]
spec=importlib.util.spec_from_file_location('old',R/'tools/test-upstream-cdm21-backend.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
S=Path(sys.argv[1]);O=Path(sys.argv[2]);O.mkdir()
for n in ['sp11-cdm.h','sp11-cdm21-state.h','sp11-cdm21-command.h']:(O/n).write_bytes((S/n).read_bytes())
header=re.sub(r'^#include <linux/[^\n]*\n','',(S/'camss-cdm-2-1.h').read_text(),flags=re.M)
body=re.sub(r'^#include [^\n]*\n','',(S/'camss-cdm-2-1.c').read_text(),flags=re.M)
body=body[:body.index('int camss_cdm21_bind(')]
adapter=old.ADAPTER.replace('0x348','0x360')

# Reuse the October12 binding suite's stale-level-IRQ correction.
stale_old = "            CHECK(camss_cdm21_isr(live->irq, live) == IRQ_NONE);"
stale_new = """            CHECK(camss_cdm21_isr(live->irq, live) == IRQ_HANDLED);
            CHECK(live->reset.fault && live->reset.seen == 0 && live->reset_complete.done == 0);
            CHECK(regs[(0x44 + mask_bank * 0x100) / 4] == 0);
            CHECK(camss_cdm21_isr(live->irq, live) == IRQ_NONE);"""
assert adapter.count(stale_old)==1
adapter=adapter.replace(stale_old,stale_new)

anchor=r'    printf("{\"cases\":%u,\"assertions\":%u}\n",cases,assertions);'
assert adapter.count(anchor)==1
extra=r'''    cases++; default_scenario();setup(&cdm);cdm.command_held=true;
    CHECK(camss_cdm21_reset_paused(&cdm)==-EBUSY && commands==0 && writes==0);
    cases++; default_scenario();setup(&cdm);
    CHECK(camss_cdm21_reset_paused(&cdm)==0 && cdm.reset_ready);
'''
adapter=adapter.replace(anchor,extra+anchor)
power='struct camss_cdm21_power { struct camss_cdm21 *cdm; bool initialized,held,touched,fault; };\nstatic __attribute__((unused)) void enable_irq(int irq) {(void)irq;}\n'
text=old.PREFIX+'\n'+header+'\n'+power+'\n'+adapter+'\n'+body
(O/'test.c').write_text(text)
runs=[]
for cc in ['gcc','clang']:
 exe=O/cc;p=subprocess.run([cc,'-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+str(O),str(O/'test.c'),'-o',str(exe)],text=True,capture_output=True)
 if p.returncode:raise RuntimeError(p.stderr)
 p=subprocess.run([str(exe)],text=True,capture_output=True)
 (O/(cc+'.log')).write_text(p.stdout+p.stderr)
 if p.returncode:raise RuntimeError(p.stderr)
 runs.append({'compiler':cc,'result':json.loads(p.stdout),'sanitizers':['ASan','UBSan']})
result={'status':'PASS_REUSED_ACTUAL_RESET_ISR_BODY_SUITE','runs':runs,'retained_fixture':'tools/test-upstream-cdm21-backend.py','hardware':False}
(O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
