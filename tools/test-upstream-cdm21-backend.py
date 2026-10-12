#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Compile actual dormant CDM2.1 backend with hosted kernel/MMIO adapters."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src/upstream/isp-config"))
from test_cdm21_state import load_reference

PINS = {
    "camss-cdm-2-1.c": "73c317bb91b2bc37ea1e1cb21dd4cf73032aedc376aea697bd3fda09a44e828f",
    "camss-cdm-2-1.h": "8c304142631f82938b3883a1a454c89e340238baeed24d2a54a16892cca3c6a6",
    "sp11-cdm.h": "2d13187fdb4170779bbd811400ed4b0a6b2649377fc72ecbac9d5dc2cda8f53c",
    "sp11-cdm21-state.h": "64f0b9551bd080a656bc716a8d4d87f675d89247fa9bbd630c2711b3c8cb8fff",
}
PREFIX = r"""
#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include "sp11-cdm21-state.h"
#define __iomem
#define U64_MAX UINT64_MAX
typedef int irqreturn_t;
#define IRQ_NONE 0
#define IRQ_HANDLED 1
struct mutex { int held; };
typedef struct { int held; } spinlock_t;
struct completion { unsigned int done; };
static void mutex_init(struct mutex *m) { m->held = 0; }
static void mutex_lock(struct mutex *m) { assert(!m->held); m->held = 1; }
static void mutex_unlock(struct mutex *m) { assert(m->held); m->held = 0; }
static void spin_lock_init(spinlock_t *l) { l->held = 0; }
static void init_completion(struct completion *c) { c->done = 0; }
static void complete(struct completion *c) { c->done++; }
static void fake_lock(spinlock_t *l) { assert(!l->held); l->held = 1; }
static void fake_unlock(spinlock_t *l);
#define spin_lock_irqsave(l,f) do { (f)=0; fake_lock(l); } while (0)
#define spin_unlock_irqrestore(l,f) do { (void)(f); fake_unlock(l); } while (0)
static void reinit_completion(struct completion *c);
static unsigned long wait_for_completion_timeout(struct completion *c, unsigned long t);
static unsigned long msecs_to_jiffies(unsigned int t) { return t; }
static u32 readl(const void *ptr);
static void writel(u32 value, void *ptr);
static void synchronize_irq(int irq);
static void disable_irq(int irq);
"""
ADAPTER = r"""
struct scenario {
    u32 version, old_status, pending[2], error;
    unsigned int old_done, ack_count, order[4];
    int stuck_old_bank, initial_mask_bank, arm_mask_bank, final_mask_bank;
    int early_bank, late_bank, sticky_final_bank;
    bool immediate, pause_bad, timeout_even_complete, late_via_isr;
};
static struct scenario cfg;
static struct camss_cdm21 *live;
static u32 regs[0x348 / 4], clear_values[4];
static unsigned int reads, writes, syncs, disables, commands, reinitializations;
static unsigned int assertions, cases;
static bool pending_immediate, finished_wait;
#define CHECK(x) do { assertions++; if (!(x)) {     fprintf(stderr, "case %u line %d failed: %s\n", cases, __LINE__, #x); abort(); } } while (0)
static unsigned int offset(const void *p)
{
    uintptr_t n = (uintptr_t)p - (uintptr_t)regs;
    CHECK(n < sizeof(regs) && !(n & 3));
    return (unsigned int)n;
}
static int bank_for(unsigned int off, unsigned int first)
{
    unsigned int bank;
    for (bank = 0; bank < 4; bank++) if (off == first + bank * 0x100) return (int)bank;
    return -1;
}
static u32 readl(const void *ptr)
{
    unsigned int off = offset(ptr);
    int bank = bank_for(off, 0x30);
    reads++;
    CHECK(off == 0 || off == 0x1c || off == 0x6c || off == 0x70 ||
          bank >= 0 || bank_for(off, 0x44) >= 0);
    if (bank >= 0) {
        if (bank == cfg.initial_mask_bank && regs[off / 4] == 0 && !commands) return 1;
        if (bank == cfg.arm_mask_bank && regs[off / 4] == 1) return 0;
        if (bank == cfg.final_mask_bank && regs[off / 4] == 0 && commands) return 1;
    }
    if (off == 0x1c && cfg.pause_bad) return 0;
    return regs[off / 4];
}
static void writel(u32 value, void *ptr)
{
    unsigned int off = offset(ptr), bank;
    int mask_bank = bank_for(off, 0x30), clear_bank = bank_for(off, 0x34);
    writes++;
    if (mask_bank >= 0) {
        CHECK(value == 0 || value == 1);
        regs[off / 4] = value;
        if (value == 1 && mask_bank == cfg.early_bank) {
            regs[(0x44 + mask_bank * 0x100) / 4] |= 1;
            CHECK(camss_cdm21_isr(live->irq, live) == IRQ_NONE);
        }
    } else if (clear_bank >= 0) {
        clear_values[clear_bank] = value;
    } else if (off == 0x38) {
        CHECK(value == 1);
        for (bank = 0; bank < 4; bank++) {
            regs[(0x44 + bank * 0x100) / 4] &= ~clear_values[bank];
            clear_values[bank] = 0;
            if ((int)bank == cfg.stuck_old_bank && !commands)
                regs[(0x44 + bank * 0x100) / 4] |= 1;
            if ((int)bank == cfg.sticky_final_bank && finished_wait)
                regs[(0x44 + bank * 0x100) / 4] |= 1;
        }
    } else if (off == 0x1c) {
        CHECK(value == 3); /* Never resume, submit, change fetch cfg or reset location. */
        regs[off / 4] = value;
    } else if (off == 0x10) {
        CHECK(value == 1 && commands == 0);
        CHECK(live->irq_lock.held && live->active && live->issued && live->reset.armed);
        CHECK(syncs >= 1 && reinitializations == 1);
        CHECK(regs[0x1c / 4] == 3 && live->reset_complete.done == 0);
        for (bank = 0; bank < 4; bank++) {
            CHECK(regs[(0x30 + bank * 0x100) / 4] == 1);
            CHECK(regs[(0x44 + bank * 0x100) / 4] == 0);
        }
        commands++;
        pending_immediate = cfg.immediate;
    } else {
        CHECK(false);
    }
}
static void deliver(unsigned int bank, u32 status)
{
    regs[(0x44 + bank * 0x100) / 4] |= status;
    CHECK(camss_cdm21_isr(live->irq, live) == IRQ_HANDLED);
}
static void fake_unlock(spinlock_t *l)
{
    CHECK(l->held);
    l->held = 0;
    if (pending_immediate) {
        unsigned int bank;
        pending_immediate = false;
        for (bank = 0; bank < 4; bank++) regs[(0x44 + bank * 0x100) / 4] = 1;
        CHECK(camss_cdm21_isr(live->irq, live) == IRQ_HANDLED);
    }
}
static void reinit_completion(struct completion *c)
{
    CHECK(syncs >= 1 && !live->irq_lock.held);
    reinitializations++;
    c->done = 0;
}
static void synchronize_irq(int irq)
{
    CHECK(irq == live->irq && !live->irq_lock.held);
    syncs++;
    if (!commands && syncs == 1) {
        /* Model completion of old handler work while masked/draining. */
        live->reset_complete.done = cfg.old_done;
        CHECK(camss_cdm21_isr(irq, live) == IRQ_NONE);
    }
    if (commands && finished_wait && cfg.late_bank >= 0 && live->active) {
        regs[(0x44 + cfg.late_bank * 0x100) / 4] |= 0x10000;
        if (cfg.late_via_isr)
            CHECK(camss_cdm21_isr(irq, live) == IRQ_HANDLED);
    }
}
static void disable_irq(int irq)
{
    CHECK(irq == live->irq && !live->irq_lock.held);
    disables++;
    synchronize_irq(irq);
}
static unsigned long wait_for_completion_timeout(struct completion *c, unsigned long t)
{
    unsigned int n;
    CHECK(t == 300 && commands == 1 && !live->irq_lock.held);
    if (!cfg.immediate) for (n = 0; n < cfg.ack_count; n++) {
        unsigned int bank = cfg.order[n];
        deliver(bank, 6); /* Non-reset completion cannot advance reset. */
        if (!cfg.error) CHECK(c->done == 0);
        deliver(bank, 1 | cfg.error);
        if (!cfg.error) CHECK((c->done != 0) == (n == 3));
        deliver(bank, 1); /* Duplicates never supply the missing bank. */
        if (!cfg.error) CHECK((c->done != 0) == (n == 3));
    }
    finished_wait = true;
    return cfg.timeout_even_complete ? 0 : (c->done ? 1 : 0);
}
static void default_scenario(void)
{
    cfg = (struct scenario){.version=0x20010000, .ack_count=4,
        .order={0,1,2,3}, .stuck_old_bank=-1, .initial_mask_bank=-1,
        .arm_mask_bank=-1, .final_mask_bank=-1, .early_bank=-1,
        .late_bank=-1, .sticky_final_bank=-1};
}
static void setup(struct camss_cdm21 *cdm)
{
    unsigned int bank;
    memset(cdm, 0, sizeof(*cdm)); memset(regs, 0, sizeof(regs));
    memset(clear_values, 0, sizeof(clear_values));
    reads=writes=syncs=disables=commands=reinitializations=0;
    pending_immediate=finished_wait=false;
    regs[0]=cfg.version; regs[0x6c/4]=cfg.pending[0]; regs[0x70/4]=cfg.pending[1];
    for (bank=0;bank<4;bank++) {
        regs[(0x30+bank*0x100)/4]=0xffffffffU;
        regs[(0x44+bank*0x100)/4]=cfg.old_status;
    }
    live=cdm;
    CHECK(camss_cdm21_init(cdm,regs,sizeof(regs),19)==0);
    CHECK(reads==0 && writes==0);
    cdm->reset_complete.done=cfg.old_done;
}
static void run_case(int expected, unsigned int expected_commands)
{
    struct camss_cdm21 cdm;
    unsigned int before_reads, before_writes, bank;
    cases++;
    setup(&cdm);
    CHECK(camss_cdm21_reset_paused(&cdm)==expected);
    CHECK(commands==expected_commands);
    CHECK(!cdm.active && !cdm.issued && !cdm.reset.armed);
    CHECK(!cdm.irq_lock.held && !cdm.lock.held);
    CHECK(cdm.quarantined==(expected!=0));
    if (cfg.version!=0x20010000) {
        CHECK(reads==1 && writes==0 && syncs==0 && disables==0);
        CHECK(!cdm.irq_disabled);
    } else {
        CHECK(syncs>=2);
        CHECK(regs[0x1c/4]==3);
        for (bank=0;bank<4;bank++) CHECK(regs[(0x30+bank*0x100)/4]==0);
        CHECK(disables==(expected!=0) && cdm.irq_disabled==(expected!=0));
    }
    before_reads=reads; before_writes=writes;
    CHECK(camss_cdm21_isr(cdm.irq,&cdm)==IRQ_NONE);
    CHECK(camss_cdm21_isr(cdm.irq+1,&cdm)==IRQ_NONE);
    CHECK(camss_cdm21_isr(cdm.irq,NULL)==IRQ_NONE);
    CHECK(reads==before_reads && writes==before_writes);
    if (expected) {
        CHECK(camss_cdm21_reset_paused(&cdm)==-EIO);
        CHECK(reads==before_reads && writes==before_writes);
    }
}
int main(void)
{
    unsigned int a,b,c,d,old,pattern,n,bank,bit,order[4];
    u32 old_done[]={0,1,255,UINT_MAX};
    u32 old_status[]={0,1,7,0x3f0000,0xffffffffU};
    u32 versions[]={0,0x20000000,0x20010001,0x30010000,0xffffffffU};
    struct camss_cdm21 cdm={0};
    cases++;
    live=&cdm;
    CHECK(camss_cdm21_init(NULL,regs,sizeof(regs),19)==-EINVAL);
    CHECK(camss_cdm21_init(&cdm,NULL,sizeof(regs),19)==-EINVAL);
    CHECK(camss_cdm21_init(&cdm,regs,sizeof(regs)-1,19)==-EINVAL);
    CHECK(camss_cdm21_init(&cdm,regs,sizeof(regs),-1)==-EINVAL);
    CHECK(camss_cdm21_reset_paused(NULL)==-EINVAL);
    CHECK(camss_cdm21_reset_paused(&cdm)==-EINVAL);
    CHECK(camss_cdm21_isr(19,&cdm)==IRQ_NONE);
    for(a=0;a<4;a++)for(b=0;b<4;b++)for(c=0;c<4;c++)for(d=0;d<4;d++){
        if(a==b||a==c||a==d||b==c||b==d||c==d)continue;
        order[0]=a;order[1]=b;order[2]=c;order[3]=d;
        for(old=0;old<4;old++)for(pattern=0;pattern<5;pattern++){
            default_scenario();
            memcpy(cfg.order,order,sizeof(order));
            cfg.old_done=old_done[old];cfg.old_status=old_status[pattern];
            run_case(0,1);
        }
        for(n=0;n<4;n++){
            default_scenario();memcpy(cfg.order,order,sizeof(order));
            cfg.old_done=UINT_MAX;cfg.ack_count=n;
            run_case(-ETIMEDOUT,1);
        }
    }
    for(old=0;old<4;old++){
        default_scenario();cfg.old_done=old_done[old];cfg.immediate=true;
        run_case(0,1);
    }
    for(bit=3;bit<32;bit++){
        default_scenario();cfg.error=1U<<bit;run_case(-EIO,1);
    }
    for(bank=0;bank<4;bank++){
        default_scenario();cfg.stuck_old_bank=(int)bank;run_case(-EIO,0);
        default_scenario();cfg.initial_mask_bank=(int)bank;run_case(-EIO,0);
        default_scenario();cfg.arm_mask_bank=(int)bank;run_case(-EIO,0);
        default_scenario();cfg.final_mask_bank=(int)bank;run_case(-EIO,1);
        default_scenario();cfg.early_bank=(int)bank;run_case(-EIO,0);
        default_scenario();cfg.sticky_final_bank=(int)bank;run_case(-EIO,1);
        for(n=0;n<2;n++){
            default_scenario();cfg.late_bank=(int)bank;cfg.late_via_isr=(bool)n;
            run_case(-EIO,1);
            default_scenario();cfg.pending[bank/2]=(n?511U:1U)<<(16*(bank%2));
            run_case(-EBUSY,1);
        }
    }
    default_scenario();cfg.pause_bad=true;run_case(-EIO,0);
    default_scenario();cfg.timeout_even_complete=true;run_case(-ETIMEDOUT,1);
    for(n=0;n<5;n++){default_scenario();cfg.version=versions[n];run_case(-ENODEV,0);}
    cases++;
    default_scenario();setup(&cdm);
    cdm.reset.epoch=UINT64_MAX;
    CHECK(camss_cdm21_reset_paused(&cdm)==-EOVERFLOW);
    CHECK(commands==0 && cdm.quarantined && cdm.irq_disabled && disables==1);
    cases++;
    default_scenario();setup(&cdm);
    CHECK(camss_cdm21_init(&cdm,regs,sizeof(regs),19)==-EBUSY);
    CHECK(camss_cdm21_reset_paused(&cdm)==0 && cdm.reset.epoch==1);
    commands=syncs=reinitializations=0;finished_wait=false;
    CHECK(camss_cdm21_reset_paused(&cdm)==0 && cdm.reset.epoch==2);
    CHECK(disables==0 && !cdm.quarantined && !cdm.active && !cdm.issued);
    printf("{\"cases\":%u,\"assertions\":%u}\n",cases,assertions);
    return 0;
}
"""

def load_candidate(root):
    path = root / "drivers/media/platform/qcom/camss"
    result = {}
    for name, pin in PINS.items():
        file = path / name
        if file.is_symlink() or not file.is_file():
            raise ValueError("candidate missing/symlink: " + name)
        data = file.read_bytes()
        if hashlib.sha256(data).hexdigest() != pin:
            raise ValueError("candidate pin mismatch: " + name)
        result[name] = data.decode()
    return result

def validate_descriptors(ref, source):
    reg = ref["cam_cdm_hw_reg_2_1.h"]
    for field, value in {"rst_cmd":0x10, "core_en":0x1c, "cdm_status":0,
                         "num_bl_fifo":4, "num_bl_fifo_irq":4}.items():
        found = re.search(r"\." + field + r"\s*=\s*(0x[0-9a-f]+|[0-9]+)", reg)
        if not found or int(found.group(1),0) != value: raise ValueError("public field " + field)
    for bank in range(4):
        block = re.search(r"cdm_hw_2_1_irq"+str(bank)+r"\s*=\s*\{(.*?)\};",reg,re.S).group(1)
        for field, first in {"irq_mask":0x30,"irq_clear":0x34,"irq_status":0x44}.items():
            found=re.search(r"\."+field+r"\s*=\s*(0x[0-9a-f]+)",block)
            if not found or int(found.group(1),0)!=first+bank*0x100: raise ValueError("public IRQ descriptor")
    if not re.search(r"CAM_CDM_HW_RESET_TIMEOUT\s+300",ref["cam_cdm.h"]):raise ValueError("public timeout")
    for token in ("uint32_t val = 0x1", "val |= 0x2", "int reset_val = 1"):
        if token not in ref["cam_cdm_hw_core.c"]:raise ValueError("public command policy")
    own_values={"CDM21_HW_VERSION":0,"CDM21_RESET_CMD":0x10,"CDM21_CORE_EN":0x1c,
                "CDM21_IRQ_CLEAR_CMD":0x38,"CDM21_PENDING0":0x6c,"CDM21_PENDING1":0x70,
                "CDM21_REQUIRED_SPAN":0x348,"CDM21_RESET_TIMEOUT_MS":300,
                "CDM21_PAUSE_REQUEST":3,"CDM21_RESET_ACK":1}
    for name,value in own_values.items():
        found=re.search(r"#define "+name+r"\s+(0x[0-9a-f]+|[0-9]+)",source)
        if not found or int(found.group(1),0)!=value:raise ValueError("own constant "+name)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--candidate",type=Path,required=True)
    parser.add_argument("--reference",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    ref=load_reference(args.reference)
    own=load_candidate(args.candidate)
    validate_descriptors(ref,own["camss-cdm-2-1.c"])
    header=re.sub(r"^#include <linux/[^\n]*\n","",own["camss-cdm-2-1.h"],flags=re.M)
    body=re.sub(r"^#include [^\n]*\n","",own["camss-cdm-2-1.c"],flags=re.M)
    runs=[]
    with tempfile.TemporaryDirectory(prefix="sp11-cdm21-backend-") as tmp:
        tmp=Path(tmp)
        for name in ("sp11-cdm.h","sp11-cdm21-state.h"):(tmp/name).write_text(own[name])
        (tmp/"test.c").write_text(PREFIX+"\n"+header+"\n"+ADAPTER+"\n"+body)
        for cc in ("gcc","clang"):
            exe=tmp/cc
            argv=[cc,"-std=gnu11","-O1","-g","-Wall","-Wextra","-Werror","-fsanitize=address,undefined",
                  "-fno-omit-frame-pointer","-I",str(tmp),str(tmp/"test.c"),"-o",str(exe)]
            p=subprocess.run(argv,capture_output=True,text=True)
            if p.returncode:raise RuntimeError(p.stdout+p.stderr)
            p=subprocess.run([str(exe)],capture_output=True,text=True)
            if p.returncode:raise RuntimeError(cc+" "+p.stdout+p.stderr)
            runs.append({"compiler":cc,"argv":argv,"counts":json.loads(p.stdout),"stderr":p.stderr})
        rejected=[]
        for name in PINS:
            for mode in ("changed","missing","symlink"):
                fixture=tmp/(name+"-"+mode)/"drivers/media/platform/qcom/camss"
                fixture.mkdir(parents=True)
                for other in PINS:(fixture/other).write_text(own[other])
                load_candidate(fixture.parents[4])  # Positive control before each mutation.
                target=fixture/name
                if mode=="changed":target.write_text(target.read_text()+"\n")
                else:
                    target.unlink()
                    if mode=="symlink":target.symlink_to(args.candidate/"drivers/media/platform/qcom/camss"/name)
                try:load_candidate(fixture.parents[4])
                except ValueError as error:
                    if name not in str(error):raise AssertionError("wrong rejection reason")
                    rejected.append({"file":name,"mode":mode,"positive_control_passed":True})
                else:raise AssertionError("bad candidate accepted")
    result={"schema":"sp11-cdm21-backend-host-validation-v1","status":"PASS_SOURCE_ONLY",
            "candidate_pins":PINS,"reference":"exact pinned public CDM2.1 descriptor and command/timeout definitions",
            "executed":"complete unchanged own backend C with hosted kernel/MMIO adapters; no real IRQ concurrency",
            "runs":runs,"candidate_rejections":rejected,"installed":False,"hardware_qualified":False,
            "dma_retirement_proven":False}
    with args.output.open("x") as out:json.dump(result,out,indent=2);out.write("\n")
    print(json.dumps(result))
if __name__=="__main__":main()
