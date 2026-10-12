#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Execute pinned dormant power/reset/binding code and real kernel bulk helpers.
Host PM/clock/IRQ models are not hardware retirement or provider-route proof.
"""
import argparse, hashlib, importlib.util, json, re, subprocess, tempfile
from pathlib import Path
PINS={
"camss-cdm-2-1.c":"cfe0f22c817b5dd553755c3a182d20174ad9ef36a0c5c69502f55826dcc68f31",
"camss-cdm-2-1.h":"42c762b6e83fdfe828efb4806b357ab54602ee3429c819f138d6bd88df0f9733",
"camss-cdm-power.c":"4e8b48815922a0954d18227dd5456e7d65feada31f9ab5b792963594f6f83e76",
"camss-cdm-power.h":"26626dfbfac68214e87edba2dced73205501179cb427b89320e13106c773c41d",
"sp11-cdm.h":"2d13187fdb4170779bbd811400ed4b0a6b2649377fc72ecbac9d5dc2cda8f53c",
"sp11-cdm21-state.h":"64f0b9551bd080a656bc716a8d4d87f675d89247fa9bbd630c2711b3c8cb8fff"}
MODEL_PINS={"test-upstream-cdm21-backend.py":"7ad3f6aad2f658066a58d0cc878e3df59d88b27a227d30900a323aa5d13e7729","test-upstream-cdm21-binding.py":"114117cbab2f0d85f6e2fca6459e55cc80c30d91be9c6f284ae86cce954909e8"}
KERNEL_PINS={"drivers/clk/clk-bulk.c":"47968c0bf3de985075f86bc4f12fae1d611312862d28391fb3f5d1f39d344236","include/linux/clk.h":"470df6235438d6b05e4f22f36627b7bb74c919ef3ca9a82654f6a982caecaee1"}
EXTRA=r"""
#define __must_check
#define pr_err(...) ((void)0)
struct clk { int tag, prepared, enabled; };
struct clk_bulk_data { const char *id; struct clk *clk; };
static int clk_prepare(struct clk *);
static void clk_unprepare(struct clk *);
static int clk_enable(struct clk *);
static void clk_disable(struct clk *);
static int pm_runtime_resume_and_get(struct device *);
static int pm_runtime_put_sync(struct device *);
static void check_power_mmio(void);
"""
POWER=r"""
static struct camss_cdm21 power_cdm;
static struct camss_cdm21_power lease;
static struct device pm_device;
static struct clk leaves[4];
static struct clk_bulk_data bundle[4];
static unsigned int power_cases, pm_gets, pm_puts;
static int pm_refs, get_error, put_error, prep_fail, enable_fail, count;
static bool power_checks;
static void check_power_mmio(void)
{
    if (!power_checks) return;
    CHECK(live == &power_cdm && live->power_owner == &lease);
    CHECK(lease.initialized && lease.held && lease.touched && !lease.fault);
    CHECK(lease.lock.held && pm_refs == 4);
    for (int i=0;i<count;i++) CHECK(leaves[i].prepared==3 && leaves[i].enabled==3);
}
static int pm_runtime_resume_and_get(struct device *dev)
{
    CHECK(dev==&pm_device && lease.lock.held && !lease.held);
    pm_gets++;
    if (get_error<0) return get_error;
    CHECK(pm_refs==3);pm_refs++;return 0;
}
static int pm_runtime_put_sync(struct device *dev)
{
    CHECK(dev==&pm_device && lease.lock.held && pm_refs==4);
    for (int i=0;i<count;i++) CHECK(leaves[i].prepared==2 && leaves[i].enabled==2);
    pm_puts++;pm_refs--;return put_error;
}
static int clk_prepare(struct clk *clk)
{
    CHECK(lease.lock.held && pm_refs==4 && clk->prepared==2);
    if (clk->tag==prep_fail) return -ENOMEM;
    clk->prepared++;return 0;
}
static void clk_unprepare(struct clk *clk)
{
    CHECK(lease.lock.held && pm_refs==4 && clk->prepared==3 && clk->enabled==2);
    clk->prepared--;
}
static int clk_enable(struct clk *clk)
{
    CHECK(lease.lock.held && pm_refs==4 && clk->prepared==3 && clk->enabled==2);
    if (clk->tag==enable_fail) return -EIO;
    clk->enabled++;return 0;
}
static void clk_disable(struct clk *clk)
{
    CHECK(lease.lock.held && pm_refs==4 && clk->prepared==3 && clk->enabled==3);
    clk->enabled--;
}
static void fresh(int n)
{
    power_checks=false;default_scenario();setup(&power_cdm);
    power_cdm.irq_disabled=true;irq_depth=1;
    memset(&lease,0,sizeof(lease));count=n;
    pm_refs=3;pm_gets=pm_puts=0;get_error=put_error=0;prep_fail=enable_fail=-1;
    for(int i=0;i<4;i++){
        leaves[i]=(struct clk){i,2,2};bundle[i]=(struct clk_bulk_data){"synthetic",&leaves[i]};
    }
    power_cases++;
}
static void attach(void)
{
    CHECK(camss_cdm21_power_init(&lease,&power_cdm,&pm_device,bundle,count)==0);
    CHECK(power_cdm.power_owner==&lease && lease.initialized && !lease.held);
    CHECK(!reads && !writes && !pm_gets && !pm_puts);
    power_checks=true;
}
static void balanced(void)
{
    CHECK(pm_refs==3 && !lease.held && !reads && !writes && !lease.touched);
    for(int i=0;i<count;i++) CHECK(leaves[i].prepared==2 && leaves[i].enabled==2);
}
static void reset_case(int expected)
{
    unsigned int before_reads,before_writes;
    /* Synchronize the modeled registers after selecting the scenario. */
    regs[0]=cfg.version;regs[0x6c/4]=cfg.pending[0];regs[0x70/4]=cfg.pending[1];
    attach();
    CHECK(camss_cdm21_reset_paused(&power_cdm)==-EPERM && !reads && !writes);
    CHECK(camss_cdm21_reset_paused_owned(&power_cdm,&lease)==-EPERM && !reads && !writes);
    CHECK(camss_cdm21_power_reset(&lease)==expected);
    CHECK(lease.held && lease.touched && pm_refs==4 && pm_gets==1 && !pm_puts);
    CHECK(!lease.lock.held && !power_cdm.lock.held && !power_cdm.active);
    for(int i=0;i<count;i++) CHECK(leaves[i].prepared==3 && leaves[i].enabled==3);
    before_reads=reads;before_writes=writes;
    CHECK(camss_cdm21_power_release_unused(&lease)==-EBUSY);
    CHECK(reads==before_reads && writes==before_writes && !pm_puts);
    if(expected){
        CHECK(power_cdm.quarantined);
        CHECK(camss_cdm21_power_reset(&lease)==-EIO);
        CHECK(reads==before_reads && writes==before_writes && pm_gets==1 && !pm_puts);
    }
    /* End a synthetic world with held refs; do not model a forbidden release. */
}
static void power_main(void)
{
    struct camss_cdm21_power other={0};
    int errors[]={-EIO,-EAGAIN,-ENOMEM,-ETIMEDOUT};
    fresh(1);
    CHECK(camss_cdm21_power_hold(NULL)==-EINVAL);
    CHECK(camss_cdm21_power_reset(&lease)==-EINVAL);
    CHECK(camss_cdm21_power_release_unused(&lease)==-EINVAL);
    CHECK(camss_cdm21_power_init(NULL,&power_cdm,&pm_device,bundle,1)==-EINVAL);
    CHECK(camss_cdm21_power_init(&lease,NULL,&pm_device,bundle,1)==-EINVAL);
    CHECK(camss_cdm21_power_init(&lease,&power_cdm,NULL,bundle,1)==-EINVAL);
    CHECK(camss_cdm21_power_init(&lease,&power_cdm,(void *)(intptr_t)-EINVAL,bundle,1)==-EINVAL);
    CHECK(camss_cdm21_power_init(&lease,&power_cdm,&pm_device,NULL,1)==-EINVAL);
    CHECK(camss_cdm21_power_init(&lease,&power_cdm,&pm_device,bundle,0)==-EINVAL);
    CHECK(camss_cdm21_power_init(&lease,&power_cdm,&pm_device,bundle,-1)==-EINVAL);
    for(int k=0;k<3;k++){
        fresh(2);
        bundle[1].clk=k==0?NULL:k==1?(void *)(intptr_t)-EINVAL:bundle[0].clk;
        CHECK(camss_cdm21_power_init(&lease,&power_cdm,&pm_device,bundle,2)==-EINVAL);
        CHECK(!power_cdm.power_owner && !lease.initialized);balanced();
    }
    for(int k=0;k<5;k++){
        fresh(1);
        if(k==0)power_cdm.initialized=false;
        if(k==1)power_cdm.irq_disabled=false;
        if(k==2)power_cdm.reset.epoch=1;
        if(k==3)power_cdm.active=true;
        if(k==4)power_cdm.quarantined=true;
        CHECK(camss_cdm21_power_init(&lease,&power_cdm,&pm_device,bundle,1)==(k==0?-EINVAL:-EBUSY));
        balanced();
    }
    for(int n=1;n<=4;n++){
        fresh(n);attach();
        CHECK(camss_cdm21_power_init(&lease,&power_cdm,&pm_device,bundle,n)==-EBUSY);
        CHECK(camss_cdm21_power_init(&other,&power_cdm,&pm_device,bundle,n)==-EBUSY);
        CHECK(camss_cdm21_power_hold(&lease)==0);
        CHECK(camss_cdm21_power_hold(&lease)==0 && pm_gets==1);
        CHECK(camss_cdm21_power_release_unused(&lease)==0);balanced();
        CHECK(camss_cdm21_power_release_unused(&lease)==0 && pm_puts==1);
        CHECK(camss_cdm21_power_hold(&lease)==0 && pm_gets==2);
        CHECK(camss_cdm21_power_release_unused(&lease)==0 && pm_puts==2);balanced();
        for(int k=0;k<4;k++){
            fresh(n);attach();get_error=errors[k];
            CHECK(camss_cdm21_power_reset(&lease)==errors[k]);
            CHECK(pm_gets==1 && !pm_puts && !lease.fault);balanced();
            get_error=0;CHECK(camss_cdm21_power_hold(&lease)==0);
            CHECK(camss_cdm21_power_release_unused(&lease)==0);balanced();
        }
        for(int phase=0;phase<2;phase++)for(int fail=0;fail<n;fail++)for(int p=0;p<2;p++){
            fresh(n);attach();if(phase)enable_fail=fail;else prep_fail=fail;
            put_error=p?-EIO:0;
            CHECK(camss_cdm21_power_reset(&lease)==(phase?-EIO:-ENOMEM));
            CHECK(pm_gets==1 && pm_puts==1 && lease.fault==(p!=0));balanced();
            prep_fail=enable_fail=-1;put_error=0;
            if(p){CHECK(camss_cdm21_power_hold(&lease)==-EIO && pm_gets==1);balanced();}
            else {CHECK(camss_cdm21_power_hold(&lease)==0);
                  CHECK(camss_cdm21_power_release_unused(&lease)==0);balanced();}
        }
        fresh(n);attach();CHECK(camss_cdm21_power_hold(&lease)==0);put_error=-EIO;
        CHECK(camss_cdm21_power_release_unused(&lease)==-EIO && lease.fault);balanced();
        CHECK(camss_cdm21_power_hold(&lease)==-EIO && pm_gets==1);
        for(unsigned int a=0;a<4;a++)for(unsigned int b=0;b<4;b++)
        for(unsigned int c=0;c<4;c++)for(unsigned int d=0;d<4;d++){
            if(a==b||a==c||a==d||b==c||b==d||c==d)continue;
            fresh(n);cfg.order[0]=a;cfg.order[1]=b;cfg.order[2]=c;cfg.order[3]=d;
            reset_case(0);
        }
        for(int k=0;k<7;k++){
            fresh(n);
            if(k==0)cfg.ack_count=3;
            if(k==1)cfg.error=8;
            if(k==2)cfg.early_bank=0;
            if(k==3)cfg.pending[0]=1;
            if(k==4)cfg.version=0x30010000;
            if(k==5){cfg.late_bank=0;cfg.late_via_isr=true;}
            if(k==6)cfg.immediate=true;
            reset_case(k==0?-ETIMEDOUT:k==3?-EBUSY:k==4?-ENODEV:k==6?0:-EIO);
        }
    }
    for(int k=0;k<4;k++){
        fresh(1);attach();
        if(k==0)power_cdm.power_owner=&other;
        if(k==1)lease.fault=true;
        if(k==2)power_cdm.quarantined=true;
        if(k==3){lease.held=true;lease.touched=true;lease.cdm=NULL;
                 CHECK(camss_cdm21_reset_paused_owned(&power_cdm,&lease)==-EPERM);
                 CHECK(!reads && !writes);continue;}
        CHECK(camss_cdm21_power_hold(&lease)==(k==0?-EPERM:-EIO));
        CHECK(!pm_gets && !reads && !writes);
    }
    power_checks=false;
}
int main(void)
{
    CHECK(legacy_main()==0);power_main();
    printf("{\"reset_cases\":%u,\"binding_cases\":%u,\"power_cases\":%u,\"total_assertions\":%u}\n",
           cases,binding_cases,power_cases,assertions);
    return 0;
}
"""
def digest(data):return hashlib.sha256(data).hexdigest()
def load_model(name):
    path=Path(__file__).with_name(name)
    if digest(path.read_bytes())!=MODEL_PINS[name]:raise ValueError("model pin: "+name)
    spec=importlib.util.spec_from_file_location(name.replace("-","_"),path)
    model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model);return model
def load_candidate(root):
    own={}
    for name,pin in PINS.items():
        p=root/"drivers/media/platform/qcom/camss"/name
        if p.is_symlink() or not p.is_file():raise ValueError("missing/symlink: "+name)
        data=p.read_bytes()
        if digest(data)!=pin:raise ValueError("pin mismatch: "+name)
        own[name]=data.decode()
    return own
def extract(text,name):
    match=re.search(r"(?:static inline\s+)?(?:int|void)\s+(?:__must_check\s+)?"+name+r"\s*\([^;{]*\)\s*\{",text)
    if not match:raise ValueError("kernel definition: "+name)
    start=match.start();pos=match.end();depth=1
    while depth:
        if text[pos]=="{":depth+=1
        if text[pos]=="}":depth-=1
        pos+=1
    return text[start:pos]+"\n"
def strip(text):return re.sub(r"^#include [^\n]*\n","",text,flags=re.M)
def main():
    p=argparse.ArgumentParser()
    for key in ("candidate","reference","output"):p.add_argument("--"+key,type=Path,required=True)
    args=p.parse_args();own=load_candidate(args.candidate)
    model=load_model("test-upstream-cdm21-backend.py");bind=load_model("test-upstream-cdm21-binding.py")
    ref=model.load_reference(args.reference);model.validate_descriptors(ref,own["camss-cdm-2-1.c"])
    kernels={}
    for name,pin in KERNEL_PINS.items():
        data=(args.candidate/name).read_bytes()
        if digest(data)!=pin:raise ValueError("kernel pin: "+name)
        kernels[name]=data.decode()
    bulk="".join(extract(kernels["drivers/clk/clk-bulk.c"],n) for n in ("clk_bulk_unprepare","clk_bulk_prepare","clk_bulk_disable","clk_bulk_enable"))
    bulk+="".join(extract(kernels["include/linux/clk.h"],n) for n in ("clk_bulk_prepare_enable","clk_bulk_disable_unprepare"))
    adapter=model.ADAPTER.replace("int main(void)","static int reset_main(void)")
    adapter=adapter.replace("    CHECK(irq == live->irq && !live->irq_lock.held);\n    disables++;","    CHECK(irq == live->irq && !live->irq_lock.held);\n    CHECK(irq_depth == 0); irq_depth = 1;\n    disables++;")
    adapter=adapter.replace("    regs[(0x44 + bank * 0x100) / 4] |= status;","    CHECK(irq_depth == 0);\n    regs[(0x44 + bank * 0x100) / 4] |= status;")
    adapter=adapter.replace("    reads=writes=syncs=disables=commands=reinitializations=0;","    reads=writes=syncs=disables=commands=reinitializations=enables=irq_depth=0;")
    old="            CHECK(camss_cdm21_isr(live->irq, live) == IRQ_NONE);"
    if adapter.count(old)!=1:raise ValueError("stale IRQ selector")
    adapter=adapter.replace(old,"""            CHECK(camss_cdm21_isr(live->irq, live) == IRQ_HANDLED);
            CHECK(live->reset.fault && live->reset.seen == 0 && live->reset_complete.done == 0);
            CHECK(regs[(0x44 + mask_bank * 0x100) / 4] == 0);
            CHECK(camss_cdm21_isr(live->irq, live) == IRQ_NONE);""")
    adapter=adapter.replace("    unsigned int off = offset(ptr);","    check_power_mmio();\n    unsigned int off = offset(ptr);")
    adapter=adapter.replace("    unsigned int off = offset(ptr), bank;","    check_power_mmio();\n    unsigned int off = offset(ptr), bank;")
    adapter=re.sub(r"^    printf\([^\n]*\n","",adapter,flags=re.M)
    binding=bind.BIND_ADAPTER.replace("int main(void)","static int legacy_main(void)")
    binding=re.sub(r"^    printf\([^\n]*\n","",binding,flags=re.M)
    runs=[];rejected=[]
    with tempfile.TemporaryDirectory(prefix="sp11-cdm21-power-") as tmp:
        tmp=Path(tmp)
        for name in ("sp11-cdm.h","sp11-cdm21-state.h"):(tmp/name).write_text(own[name])
        unit=model.PREFIX+bind.EXTRA_PREFIX+EXTRA+strip(own["camss-cdm-2-1.h"])+strip(own["camss-cdm-power.h"])+adapter+binding+POWER+bulk+strip(own["camss-cdm-2-1.c"])+strip(own["camss-cdm-power.c"])
        (tmp/"test.c").write_text("// SPDX-License-Identifier: GPL-2.0-only\n"+unit)
        for cc in ("gcc","clang"):
            exe=tmp/cc
            cmd=[cc,"-std=gnu11","-O1","-g","-Wall","-Wextra","-Werror","-fsanitize=address,undefined","-fno-omit-frame-pointer","-I",str(tmp),str(tmp/"test.c"),"-o",str(exe)]
            c=subprocess.run(cmd,capture_output=True,text=True)
            if c.returncode:raise RuntimeError(c.stdout+c.stderr)
            r=subprocess.run([str(exe)],capture_output=True,text=True)
            if r.returncode:raise RuntimeError(cc+" "+r.stdout+r.stderr)
            counts=json.loads(r.stdout)
            if counts["reset_cases"]!=659 or counts["binding_cases"]!=899:raise AssertionError(counts)
            runs.append({"compiler":cc,"sanitizers":["address","undefined"],"counts":counts,"stderr":r.stderr})
        for name in PINS:
            for mode in ("changed","missing","symlink"):
                root=tmp/(name+"-"+mode);fixture=root/"drivers/media/platform/qcom/camss";fixture.mkdir(parents=True)
                for other in PINS:(fixture/other).write_text(own[other])
                load_candidate(root);target=fixture/name
                if mode=="changed":target.write_text(target.read_text()+"\n")
                else:
                    target.unlink()
                    if mode=="symlink":target.symlink_to(args.candidate/"drivers/media/platform/qcom/camss"/name)
                try:load_candidate(root)
                except ValueError as error:
                    if name not in str(error):raise AssertionError("wrong rejection")
                    rejected.append({"file":name,"mode":mode,"positive_control_passed":True})
                else:raise AssertionError("invalid fixture admitted")
    result={"schema":"sp11-cdm21-power-host-v1","status":"PASS_SOURCE_ONLY","candidate_pins":PINS,"model_pins":MODEL_PINS,"kernel_pins":KERNEL_PINS,"runs":runs,"candidate_rejections":rejected,"kernel_bulk_functions_executed":6,"framework_pm_irq_mmio_and_leaf_clocks_modeled":True,"installed":False,"hardware_qualified":False,"provider_routing_proven":False,"physical_retirement_proven":False}
    with args.output.open("x") as out:json.dump(result,out,indent=2);out.write("\n")
    print(json.dumps({"status":result["status"],"runs":runs,"pin_rejections":len(rejected)}))
if __name__=="__main__":main()
