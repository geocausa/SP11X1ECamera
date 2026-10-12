#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Actual binding/reset C with hosted managed-resource and IRQ-depth models."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import tempfile

MODEL_PIN="7ad3f6aad2f658066a58d0cc878e3df59d88b27a227d30900a323aa5d13e7729"
PINS={
 "camss-cdm-2-1.c":"30ba7eae789c61b8aa6401a4d5540790b15d3ef2724c4ee6eb4481ad0173fe20",
 "camss-cdm-2-1.h":"d26d07fee1bd165bc5b2abf8fafa0f4cf0fcc3147907adfe8ebd2a03c1022b80",
 "sp11-cdm.h":"2d13187fdb4170779bbd811400ed4b0a6b2649377fc72ecbac9d5dc2cda8f53c",
 "sp11-cdm21-state.h":"64f0b9551bd080a656bc716a8d4d87f675d89247fa9bbd630c2711b3c8cb8fff",
}
EXTRA_PREFIX=r"""
typedef uint64_t resource_size_t;
struct device { int tag; };
struct platform_device { struct device dev; };
struct resource { resource_size_t start, end; };
#define IORESOURCE_MEM 0x200
#define GFP_KERNEL 0 /* Test-only allocation token. */
#define IRQF_NO_AUTOEN 0x00080000
#define EPROBE_DEFER 517
#define IS_ERR(p) ((uintptr_t)(p) >= (uintptr_t)-4095)
#define PTR_ERR(p) ((int)(intptr_t)(p))
static unsigned int irq_depth, enables;
static void enable_irq(int irq);
static struct resource *platform_get_resource_byname(struct platform_device *, unsigned int, const char *);
static int platform_get_irq_byname(struct platform_device *, const char *);
static resource_size_t resource_size(const struct resource *r) { return r->end-r->start+1; }
static void *devres_open_group(struct device *, void *, int);
static void devres_remove_group(struct device *, void *);
static int devres_release_group(struct device *, void *);
static void *devm_ioremap_resource(struct device *, struct resource *);
static void *devm_kzalloc(struct device *, size_t, int);
static int devm_request_irq(struct device *, int, irqreturn_t (*)(int,void *),
                           unsigned long, const char *, void *);
"""
BIND_ADAPTER=r"""
static struct platform_device device;
static struct resource memory;
static struct camss_cdm21 *managed;
static bool missing_mem, group_bad, alloc_bad, reserved, registered;
static bool group_opened;
static int map_error, irq_error, request_error, group_cookie;
static unsigned int group_start, ledger[8], ledger_count, cleanup[8], cleanup_count;
static unsigned int gets, irq_gets, groups, maps, allocations, requests, releases, commits;
static unsigned int binding_cases;
static struct camss_cdm21_resource_names names={"owned-regs","owned-irq"};

static void enable_irq(int irq)
{
    unsigned int bank;
    CHECK(irq==live->irq && irq_depth==1 && live->irq_disabled);
    CHECK(!live->irq_lock.held && live->active && !live->issued && live->reset.armed);
    CHECK(syncs>=1 && reinitializations==1 && commands==0);
    for(bank=0;bank<4;bank++){
        CHECK(regs[(0x30+bank*0x100)/4]==0);
        CHECK(regs[(0x44+bank*0x100)/4]==0);
    }
    enables++; irq_depth=0;
}
static void append(unsigned int kind)
{
    CHECK(ledger_count<8);
    ledger[ledger_count++]=kind;
}
static struct resource *platform_get_resource_byname(struct platform_device *p,
                                                   unsigned int type,const char *name)
{
    CHECK(p==&device && type==IORESOURCE_MEM && !strcmp(name,"owned-regs"));
    gets++;
    return missing_mem?NULL:&memory;
}
static int platform_get_irq_byname(struct platform_device *p,const char *name)
{
    CHECK(p==&device && !strcmp(name,"owned-irq"));
    irq_gets++;
    return irq_error?irq_error:19;
}
static void *devres_open_group(struct device *d,void *id,int gfp)
{
    CHECK(d==&device.dev && !id && gfp==GFP_KERNEL && !group_opened);
    groups++;
    if(group_bad)return NULL;
    group_opened=true; group_start=ledger_count;
    return &group_cookie;
}
static void devres_remove_group(struct device *d,void *id)
{
    CHECK(d==&device.dev && id==&group_cookie && group_opened);
    commits++; group_opened=false;
}
static void pop_resource(void)
{
    unsigned int kind;
    CHECK(ledger_count>1 && cleanup_count<8);
    kind=ledger[--ledger_count];cleanup[cleanup_count++]=kind;
    if(kind==4){
        CHECK(registered && managed && managed->initialized && !managed->active);
        registered=false;
    } else if(kind==3){
        CHECK(!registered && managed);
        free(managed);managed=NULL;live=NULL;
    } else if(kind==2){
        CHECK(!registered && !managed && reserved);
    } else if(kind==1){
        CHECK(!registered && !managed && reserved);
        reserved=false;
    } else CHECK(false);
}
static int devres_release_group(struct device *d,void *id)
{
    CHECK(d==&device.dev && id==&group_cookie && group_opened);
    releases++;
    while(ledger_count>group_start)pop_resource();
    group_opened=false;
    return 0;
}
static void *devm_ioremap_resource(struct device *d,struct resource *r)
{
    CHECK(d==&device.dev && r==&memory && group_opened);
    maps++;
    if(map_error)return (void *)(intptr_t)map_error;
    if(reserved)return (void *)(intptr_t)-EBUSY;
    reserved=true;append(1);append(2);
    return regs;
}
static void *devm_kzalloc(struct device *d,size_t size,int gfp)
{
    CHECK(d==&device.dev && size==sizeof(*managed) && gfp==GFP_KERNEL && group_opened);
    allocations++;
    if(alloc_bad)return NULL;
    CHECK(!managed);
    managed=calloc(1,size);CHECK(managed!=NULL);live=managed;append(3);
    return managed;
}
static int devm_request_irq(struct device *d,int irq,irqreturn_t (*handler)(int,void *),
                           unsigned long flags,const char *label,void *data)
{
    struct camss_cdm21 *cdm=data;
    CHECK(d==&device.dev && irq==19 && handler==camss_cdm21_isr);
    CHECK(flags==IRQF_NO_AUTOEN && !strcmp(label,"camss-cdm21"));
    CHECK(cdm==managed && cdm->initialized && cdm->irq_disabled &&
          cdm->base==regs && cdm->irq==irq && !cdm->active && !cdm->issued);
    requests++;
    if(request_error)return request_error;
    registered=true;irq_depth=1;append(4);
    CHECK(handler(irq,data)==IRQ_NONE);
    CHECK(reads==0 && writes==0);
    return 0;
}
static void binding_setup(void)
{
    CHECK(!reserved && !registered && !managed && !group_opened);
    default_scenario();memset(regs,0,sizeof(regs));memset(clear_values,0,sizeof(clear_values));
    missing_mem=group_bad=alloc_bad=false;map_error=irq_error=request_error=0;
    gets=irq_gets=groups=maps=allocations=requests=releases=commits=0;
    reads=writes=syncs=disables=commands=reinitializations=enables=irq_depth=0;
    pending_immediate=finished_wait=false;
    memory=(struct resource){0x1000,0x1347};
    ledger_count=1;ledger[0]=99;cleanup_count=0;live=NULL;
}
static void modeled_detach(void)
{
    while(ledger_count>1)pop_resource();
    CHECK(cleanup_count==4 && cleanup[0]==4 && cleanup[1]==3 &&
          cleanup[2]==2 && cleanup[3]==1);
    CHECK(!reserved && !registered && !managed && !group_opened);
}
static void bind_error(int expected)
{
    struct camss_cdm21 *out=(void *)(uintptr_t)0x100;
    binding_cases++;
    CHECK(camss_cdm21_bind(&device,&names,&out)==expected);
    CHECK(out==(void *)(uintptr_t)0x100);
    CHECK(reads==0 && writes==0 && enables==0 && disables==0);
    CHECK(ledger_count==1 && ledger[0]==99 && !reserved && !registered && !managed);
    CHECK(!group_opened && commits==0);
}
static struct camss_cdm21 *bind_ok(void)
{
    struct camss_cdm21 *out=NULL;
    binding_cases++;
    CHECK(camss_cdm21_bind(&device,&names,&out)==0);
    CHECK(out==managed && out->initialized && out->irq_disabled);
    CHECK(groups==1 && commits==1 && releases==0 && ledger_count==5);
    CHECK(reads==0 && writes==0 && enables==0 && disables==0 && irq_depth==1);
    return out;
}
static void bound_reset_case(int expected,unsigned int expect_enables,unsigned int expect_commands)
{
    struct camss_cdm21 *cdm=bind_ok();
    unsigned int bank, before_reads, before_writes;
    regs[0]=cfg.version;regs[0x6c/4]=cfg.pending[0];regs[0x70/4]=cfg.pending[1];
    for(bank=0;bank<4;bank++){
        regs[(0x30+bank*0x100)/4]=0xffffffffU;
        regs[(0x44+bank*0x100)/4]=cfg.old_status;
    }
    cdm->reset_complete.done=UINT_MAX;
    CHECK(camss_cdm21_reset_paused(cdm)==expected);
    CHECK(enables==expect_enables && commands==expect_commands);
    CHECK(!cdm->active && !cdm->issued && !cdm->reset.armed);
    CHECK(cdm->quarantined==(expected!=0));
    CHECK(irq_depth==(expected!=0) && cdm->irq_disabled==(expected!=0));
    CHECK(disables==((expected!=0)?expect_enables:0));
    if(expected){
        before_reads=reads;before_writes=writes;
        CHECK(camss_cdm21_reset_paused(cdm)==-EIO);
        CHECK(reads==before_reads && writes==before_writes);
    }
    modeled_detach();
}
static void binding_main(void)
{
    unsigned int size,bank,n;
    int map_errors[]={-ENOMEM,-EBUSY,-EPROBE_DEFER};
    int irq_errors[]={-ENODEV,-EINVAL,-EPROBE_DEFER};
    int req_errors[]={-EBUSY,-ENOMEM,-EINVAL,-EPROBE_DEFER};
    struct camss_cdm21 *out=(void *)(uintptr_t)0x100;
    struct camss_cdm21_resource_names invalid;
    binding_setup();binding_cases++;
    CHECK(camss_cdm21_bind(NULL,&names,&out)==-EINVAL);
    CHECK(camss_cdm21_bind(&device,NULL,&out)==-EINVAL);
    CHECK(camss_cdm21_bind(&device,&names,NULL)==-EINVAL);
    for(n=0;n<4;n++){
        invalid=names;
        if(n==0)invalid.registers=NULL;
        if(n==1)invalid.registers="";
        if(n==2)invalid.irq=NULL;
        if(n==3)invalid.irq="";
        CHECK(camss_cdm21_bind(&device,&invalid,&out)==-EINVAL);
        CHECK(out==(void *)(uintptr_t)0x100);
    }
    CHECK(gets==0 && groups==0 && reads==0 && writes==0);
    binding_setup();missing_mem=true;bind_error(-ENODEV);
    CHECK(gets==1 && irq_gets==0 && groups==0);
    for(size=0;size<0x348;size++){
        binding_setup();memory.end=memory.start+size-1;bind_error(-EINVAL);
        CHECK(irq_gets==0 && groups==0);
    }
    binding_setup();memory.start=0x1001;bind_error(-EINVAL);
    binding_setup();memory.end=memory.start-1;bind_error(-EINVAL);
    binding_setup();memory.start=0;memory.end=UINT64_MAX;bind_error(-EINVAL);
    for(n=0;n<3;n++){
        binding_setup();irq_error=irq_errors[n];bind_error(irq_error);
        CHECK(groups==0 && maps==0);
    }
    binding_setup();group_bad=true;bind_error(-ENOMEM);
    CHECK(groups==1 && releases==0 && maps==0);
    for(n=0;n<3;n++){
        binding_setup();map_error=map_errors[n];bind_error(map_error);
        CHECK(groups==1 && maps==1 && releases==1 && allocations==0);
    }
    binding_setup();alloc_bad=true;bind_error(-ENOMEM);
    CHECK(releases==1 && cleanup_count==2 && cleanup[0]==2 && cleanup[1]==1);
    for(n=0;n<4;n++){
        binding_setup();request_error=req_errors[n];bind_error(request_error);
        CHECK(releases==1 && cleanup_count==3 && cleanup[0]==3 && cleanup[1]==2 && cleanup[2]==1);
    }
    for(n=0;n<3;n++){
        binding_setup();memory.end+=n?((n==1)?1:0x1000):0;
        (void)bind_ok();modeled_detach();
    }
    binding_setup();
    {
        struct camss_cdm21 *first=bind_ok();
        unsigned int before=ledger_count;
        out=(void *)(uintptr_t)0x100;
        binding_cases++;
        CHECK(camss_cdm21_bind(&device,&names,&out)==-EBUSY);
        CHECK(out==(void *)(uintptr_t)0x100 && managed==first && ledger_count==before);
        CHECK(registered && reserved && releases==1 && cleanup_count==0);
        modeled_detach();
    }
    binding_setup();bound_reset_case(0,1,1);
    binding_setup();cfg.immediate=true;bound_reset_case(0,1,1);
    binding_setup();cfg.version=0x30010000;bound_reset_case(-ENODEV,0,0);
    binding_setup();cfg.pause_bad=true;bound_reset_case(-EIO,0,0);
    for(bank=0;bank<4;bank++){
        binding_setup();cfg.stuck_old_bank=(int)bank;bound_reset_case(-EIO,0,0);
        binding_setup();cfg.initial_mask_bank=(int)bank;bound_reset_case(-EIO,0,0);
        binding_setup();cfg.arm_mask_bank=(int)bank;bound_reset_case(-EIO,1,0);
        binding_setup();cfg.early_bank=(int)bank;bound_reset_case(-EIO,1,0);
        binding_setup();cfg.final_mask_bank=(int)bank;bound_reset_case(-EIO,1,1);
        binding_setup();cfg.late_bank=(int)bank;cfg.late_via_isr=true;bound_reset_case(-EIO,1,1);
        binding_setup();cfg.pending[bank/2]=511U<<(16*(bank%2));bound_reset_case(-EBUSY,1,1);
    }
    for(n=0;n<4;n++){
        binding_setup();cfg.ack_count=n;bound_reset_case(-ETIMEDOUT,1,1);
    }
    binding_setup();
    {
        struct camss_cdm21 *cdm=bind_ok();
        regs[0]=cfg.version;cdm->reset.epoch=UINT64_MAX;
        CHECK(camss_cdm21_reset_paused(cdm)==-EOVERFLOW);
        CHECK(enables==0 && disables==0 && irq_depth==1 && cdm->irq_disabled && cdm->quarantined);
        modeled_detach();
    }
}
int main(void)
{
    CHECK(reset_main()==0);
    binding_main();
    printf("{\"reset_cases\":%u,\"binding_cases\":%u,\"total_assertions\":%u}\n",cases,binding_cases,assertions);
    return 0;
}
"""

def load_candidate(root):
    result={}
    for name,pin in PINS.items():
        path=root/"drivers/media/platform/qcom/camss"/name
        if not path.is_file() or path.is_symlink():raise ValueError("candidate missing/symlink: "+name)
        data=path.read_bytes()
        if hashlib.sha256(data).hexdigest()!=pin:raise ValueError("candidate pin mismatch: "+name)
        result[name]=data.decode()
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--candidate",type=Path,required=True)
    p.add_argument("--reference",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    path=Path(__file__).with_name("test-upstream-cdm21-backend.py")
    if hashlib.sha256(path.read_bytes()).hexdigest()!=MODEL_PIN:raise ValueError("reset model changed")
    spec=importlib.util.spec_from_file_location("cdm21_reset_model",path)
    model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
    ref=model.load_reference(args.reference)
    own=load_candidate(args.candidate)
    model.validate_descriptors(ref,own["camss-cdm-2-1.c"])
    kernel_irq=(args.candidate/"include/linux/interrupt.h").read_text()
    if not re.search(r"#define IRQF_NO_AUTOEN\s+0x00080000",kernel_irq):raise ValueError("kernel IRQ flag mismatch")
    adapter=model.ADAPTER.replace("int main(void)","static int reset_main(void)")
    adapter=adapter.replace("    CHECK(irq == live->irq && !live->irq_lock.held);\n    disables++;",
                            "    CHECK(irq == live->irq && !live->irq_lock.held);\n    CHECK(irq_depth == 0); irq_depth = 1;\n    disables++;")
    adapter=adapter.replace("    regs[(0x44 + bank * 0x100) / 4] |= status;",
                            "    CHECK(irq_depth == 0);\n    regs[(0x44 + bank * 0x100) / 4] |= status;")
    adapter=adapter.replace("    reads=writes=syncs=disables=commands=reinitializations=0;",
                            "    reads=writes=syncs=disables=commands=reinitializations=enables=irq_depth=0;")
    adapter=adapter.replace('    printf("{\\"cases\\":%u,\\"assertions\\":%u}\\n",cases,assertions);',"")
    stale_old = """            CHECK(camss_cdm21_isr(live->irq, live) == IRQ_NONE);"""
    stale_new = """            CHECK(camss_cdm21_isr(live->irq, live) == IRQ_HANDLED);
            CHECK(live->reset.fault && live->reset.seen == 0 && live->reset_complete.done == 0);
            CHECK(regs[(0x44 + mask_bank * 0x100) / 4] == 0);
            CHECK(camss_cdm21_isr(live->irq, live) == IRQ_NONE);"""
    if adapter.count(stale_old) != 1:raise ValueError("stale IRQ fixture selector")
    adapter=adapter.replace(stale_old,stale_new)
    header=re.sub(r"^#include <linux/[^\n]*\n","",own["camss-cdm-2-1.h"],flags=re.M)
    body=re.sub(r"^#include [^\n]*\n","",own["camss-cdm-2-1.c"],flags=re.M)
    runs=[]
    with tempfile.TemporaryDirectory(prefix="sp11-cdm21-bind-") as tmp:
        tmp=Path(tmp)
        for name in ("sp11-cdm.h","sp11-cdm21-state.h"):(tmp/name).write_text(own[name])
        (tmp/"test.c").write_text(model.PREFIX+EXTRA_PREFIX+header+adapter+BIND_ADAPTER+body)
        for cc in ("gcc","clang"):
            exe=tmp/cc
            argv=[cc,"-std=gnu11","-O1","-g","-Wall","-Wextra","-Werror","-fsanitize=address,undefined",
                  "-fno-omit-frame-pointer","-I",str(tmp),str(tmp/"test.c"),"-o",str(exe)]
            c=subprocess.run(argv,capture_output=True,text=True)
            if c.returncode:raise RuntimeError(c.stdout+c.stderr)
            r=subprocess.run([str(exe)],capture_output=True,text=True)
            if r.returncode:raise RuntimeError(cc+" "+r.stdout+r.stderr)
            runs.append({"compiler":cc,"sanitizers":["address","undefined"],"counts":json.loads(r.stdout),"stderr":r.stderr})
        rejected=[]
        for name in PINS:
            for mode in ("changed","missing","symlink"):
                root=tmp/(name+"-"+mode)
                fixture=root/"drivers/media/platform/qcom/camss";fixture.mkdir(parents=True)
                for other in PINS:(fixture/other).write_text(own[other])
                load_candidate(root)
                target=fixture/name
                if mode=="changed":target.write_text(target.read_text()+"\n")
                else:
                    target.unlink()
                    if mode=="symlink":target.symlink_to(args.candidate/"drivers/media/platform/qcom/camss"/name)
                try:load_candidate(root)
                except ValueError as error:
                    if name not in str(error):raise AssertionError("wrong rejection reason")
                    rejected.append({"file":name,"mode":mode,"positive_control_passed":True})
                else:raise AssertionError("invalid fixture accepted")
    result={"schema":"sp11-cdm21-binding-host-v1","status":"PASS_SOURCE_ONLY","candidate_pins":PINS,
            "reset_model_pin":MODEL_PIN,"runs":runs,"candidate_rejections":rejected,
            "executed":"Complete unchanged own binding/reset/IRQ backend with hosted device-resource, MMIO, IRQ-depth and lock models",
            "framework_cleanup_is_modeled":True,"installed":False,"hardware_qualified":False,"dma_retirement_proven":False}
    with args.output.open("x") as out:json.dump(result,out,indent=2);out.write("\n")
    print(json.dumps(result))
if __name__=="__main__":main()
