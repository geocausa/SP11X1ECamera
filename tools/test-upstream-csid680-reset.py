#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Compare actual CSID680 reset source with public reset code and fault adapters."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

PREFIX=Path("drivers/media/platform/qcom/camss")
PARENT_SHA="e546e09dd13f1e0be0fb63f164519ec43a119a54a64049daa97c5ed25325d9d6"
CANDIDATE_SHA="84aea2239ea7d8db62d82721fe5fcd6d25f0c0f26a84e29f184391e6f67ad255"
PATCH_SHA="6a9216b549e2aece4af85c816eba051d792b69b57a71e4d35c562b0a7a0e3dcc"

def pinned(path, expected):
    if not path.is_file() or any(p.is_symlink() for p in [path,*path.parents]):
        raise ValueError("missing or symlink source")
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=expected:
        raise ValueError("changed pinned source")
    return raw.decode()

def balanced(text,start):
    begin=text.index("{",start)
    pos,depth=begin+1,1
    while depth:
        if pos>=len(text):
            raise ValueError("unbalanced public source")
        depth+=(text[pos]=="{")-(text[pos]=="}")
        pos+=1
    return text[start:pos]

def function(text,name):
    m=re.search(r"^(?:static\s+)?int\s+"+name+r"\s*\(",text,re.M)
    if not m:
        raise ValueError("function missing")
    return balanced(text,m.start())+"\n"

def verify_reference(root,manifest):
    sources={}
    for pin in manifest["files"]:
        rel=Path(pin["path"])
        if rel.is_absolute() or ".." in rel.parts or rel.name in sources:
            raise ValueError("invalid reference path")
        text=pinned(root/rel,pin["sha256"])
        raw=text.encode()
        if len(raw)!=pin["bytes"] or hashlib.sha1(("blob "+str(len(raw))+"\0").encode()+raw).hexdigest()!=pin["git_blob_sha1"]:
            raise ValueError("reference Git identity differs")
        sources[rel.name]=text
    if len(sources)!=9:
        raise ValueError("incomplete reset reference")
    return sources

def enum_for(sources,token):
    for text in sources.values():
        for m in re.finditer(r"enum\s+\w+\s*\{",text):
            block=balanced(text,m.start())
            if re.search(r"\b"+token+r"\b",block):
                return block+";\n"
    raise ValueError("enum missing: "+token)

def reference_code(sources):
    hw=sources["cam_ife_csid680.h"]
    driver=sources["cam_ife_csid_hw_ver2.c"]
    body=function(driver,"cam_ife_csid_ver2_internal_reset")
    common_name=re.search(r"\.cmn_reg\s*=\s*&(\w+)",hw).group(1)
    rx_name=re.search(r"\.csi2_reg\s*=\s*&(\w+)",hw).group(1)
    result=""
    initializers={}
    for key,name,typename,variable in [
        ("cmn_reg",common_name,"cam_ife_csid_ver2_common_reg_info","public_common"),
        ("csi2_reg",rx_name,"cam_ife_csid_ver2_csi2_rx_reg_info","public_rx")]:
        block=balanced(hw,re.search(r"\b"+name+r"\s*=\s*\{",hw).start())
        pattern=r"csid_reg->cmn_reg->(\w+)" if key=="cmn_reg" else r"csi2_reg->(\w+)"
        fields=sorted(set(re.findall(pattern,body)))
        values={}
        for field in fields:
            match=re.search(r"\."+field+r"\s*=\s*([^,\n]+)",block)
            if not match:
                raise ValueError("required scalar not explicit: "+field)
            values[field]=match.group(1).strip()
        result+="struct "+typename+" { "+"; ".join("u32 "+f for f in fields)+"; };\n"
        result+="static struct "+typename+" "+variable+" = {\n"+",\n".join("."+f+"="+values[f] for f in fields)+"\n};\n"
        initializers[key]=values
    common_block=balanced(hw,re.search(r"\b"+common_name+r"\s*=\s*\{",hw).start())
    metadata={}
    for macro,field in {
        "CSID_TOP_IRQ_STATUS":"top_irq_status_addr",
        "CSID_TOP_IRQ_MASK":"top_irq_mask_addr",
        "CSID_TOP_IRQ_CLEAR":"top_irq_clear_addr",
        "CSID_IRQ_CMD":"irq_cmd_addr",
        "CSID_TOP_IRQ_RESET":"top_reset_irq_mask",
    }.items():
        match=re.search(r"\."+field+r"\s*=\s*(?:\{\s*)?(0x[0-9a-fA-F]+|[0-9]+)",common_block)
        if not match:
            raise ValueError("required IRQ descriptor missing: "+field)
        metadata[macro]=match.group(1)
        result+='_Static_assert('+macro+' == '+match.group(1)+', "public IRQ descriptor");\n'
    result+='_Static_assert(CSID_CSI2_RX_CFG0 == '+initializers["csi2_reg"]["cfg0_addr"]+', "RX cfg0");\n'
    result+='_Static_assert(CSID_CSI2_RX_CFG1 == '+initializers["csi2_reg"]["cfg1_addr"]+', "RX cfg1");\n'
    initializers["IRQ"] = metadata
    for token in ["CAM_IFE_CSID_RESET_CMD_SW_RST","CAM_IFE_CSID_RESET_LOC_COMPLETE","CAM_CSID_HALT_IMMEDIATELY","CAM_HW_STATE_POWER_UP"]:
        result+=enum_for(sources,token)
    # Logical context role is a test-only token; it is never a hardware field.
    result+="#define CAM_ISP_HW_SYNC_SLAVE 2\n#define CAM_IFE_CSID_CLC_MEM_BASE_ID 0\n#define __iomem\n"
    result+=r"""
struct cam_hw_soc_info { struct { void *mem_base; } reg_map[1]; };
struct public_hw_info { int hw_state, hw_complete; struct cam_hw_soc_info soc_info; };
struct public_core_info { void *csid_reg; };
struct cam_ife_csid_ver2_reg_info {
    struct cam_ife_csid_ver2_common_reg_info *cmn_reg;
    struct cam_ife_csid_ver2_csi2_rx_reg_info *csi2_reg;
};
struct cam_ife_csid_ver2_hw { struct public_hw_info *hw_info; struct public_core_info *core_info; int sync_mode; };
static int public_wait_result;
static int cam_ife_csid_ver2_wait_for_reset(struct cam_ife_csid_ver2_hw *hw) { (void)hw; return public_wait_result; }
"""
    # Preserve the public GPL header with the unchanged actual function.
    result+=driver[:driver.index("#include")]
    result+=body
    return result,initializers

SHIM=r"""
#include <assert.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
typedef uint32_t u32;
#define BIT(n) (1U<<(n))
#define GENMASK(h,l) ((~0U>>(31U-(h)))&(~0U<<(l)))
#define CAM_DBG(...) ((void)0)
#define CAM_ERR(...) ((void)0)
#define dev_err(...) ((void)0)
#define MSM_CSID_MAX_SRC_STREAMS 4
#define CSID_RESET_TIMEOUT_MS 500
struct csid_device { void *base; unsigned int irq; int reset_complete; struct { void *dev; } *camss; };
struct event { unsigned int kind,offset; u32 value; };
static u32 bank[1024];
static struct event events[128];
static unsigned int count,syncs,waits,commands;
static bool reference_mode,stuck_clear,inflight_old,late_after_timeout;
static unsigned int phase;
static u32 pending_clear;
static int *kernel_completion;
static void event(unsigned int kind,unsigned int offset,u32 value) {
    assert(count<128); events[count++]=(struct event){kind,offset,value};
}
static unsigned int offset(const void *address) {
    uintptr_t n=(uintptr_t)address-(uintptr_t)bank;
    assert(n<sizeof(bank) && !(n&3)); return n;
}
static u32 readl(const void *address) {
    unsigned int off=offset(address);event(2,off,bank[off/4]);return bank[off/4];
}
static void writel(u32 value,void *address) {
    unsigned int off=offset(address);event(1,off,value);
    if(reference_mode) { bank[off/4]=value; return; }
    if(off==0x84) { pending_clear|=value; return; }
    if(off==0x14 && value==1) {
        if(!stuck_clear) bank[0x7c/4]&=~pending_clear;
        pending_clear=0; return;
    }
    bank[off/4]=value;
    if(off==0x10) {
        assert(value==2 && bank[0xc/4]==0x11);
        assert(bank[0x200/4]==0 && bank[0x204/4]==0);
        assert(bank[0x80/4]==1 && *kernel_completion==0);
        commands++;
        if(phase==0) *kernel_completion=1;
    }
}
static void cam_io_w_mb(u32 value,void *address) { writel(value,address); }
static void synchronize_irq(unsigned int irq) {
    assert(!reference_mode && irq==44 && bank[0x80/4]==0);
    event(3,irq,0);syncs++;
    if(inflight_old) { *kernel_completion=1; inflight_old=false; }
    if(late_after_timeout) { *kernel_completion=1; late_after_timeout=false; }
}
static void reinit_completion(int *completion) {
    event(4,0,0); *completion=0;
    if(!reference_mode) assert(!inflight_old && !(bank[0x7c/4]&1));
}
static unsigned long msecs_to_jiffies(unsigned long milliseconds) { return milliseconds; }
static unsigned long wait_for_completion_timeout(int *completion,unsigned long timeout) {
    assert(timeout==500 && commands==1);waits++;event(5,0,0);
    if(phase==1) *completion=1;
    if(*completion) { *completion=0;return 1; }
    if(phase==3) late_after_timeout=true;
    return 0;
}
"""

TEST=r"""
static void reset_fixture(void) {
    memset(bank,0,sizeof(bank));memset(events,0,sizeof(events));
    count=syncs=waits=commands=0;pending_clear=0;
    reference_mode=stuck_clear=inflight_old=late_after_timeout=false;
}
static void check_fresh_prefix(void) {
    assert(count>=13);
    const struct event expected[]={
        {1,0x80,0},{2,0x80,0},{3,44,0},{1,0x84,1},
        {1,0x14,1},{2,0x7c,0},{4,0,0},{1,0x80,1},
        {1,0x200,0},{1,0x204,0},{1,0xc,0x11},{1,0x10,2},{5,0,0}
    };
    for(unsigned int i=0;i<13;i++) {
        assert(events[i].kind==expected[i].kind && events[i].offset==expected[i].offset);
        if(i!=5) assert(events[i].value==expected[i].value);
        else assert(!(events[i].value&1));
    }
}
int main(void) {
    unsigned int cases=0,public_cases=0;
    const u32 statuses[]={0,1,0xffff0001U,0x80000000U};
    const int old_completions[]={0,1,17};
    struct { void *dev; } device={0};
    for(unsigned int s=0;s<4;s++) for(unsigned int old=0;old<3;old++)
    for(unsigned int pending=0;pending<2;pending++) for(unsigned int p=0;p<4;p++) {
        reset_fixture(); phase=p;
        struct csid_device csid={bank,44,old_completions[old],(void *)&device};
        kernel_completion=&csid.reset_complete;inflight_old=pending;
        bank[0x7c/4]=statuses[s];bank[0x200/4]=0xa5;bank[0x204/4]=0x5a;
        int ret=csid_reset(&csid);check_fresh_prefix();
        assert(commands==1 && waits==1);
        if(p<2) {
            assert(ret==0 && syncs==1 && bank[0x80/4]==~0U);
            for(unsigned int i=0;i<4;i++) assert(bank[(0xf0+i*0x10)/4]==BIT(23));
            assert(count==20);
        } else {
            assert(ret==-ETIMEDOUT && syncs==2 && bank[0x80/4]==0);
            assert(count==16 && bank[0x90/4]==0);
            assert(events[13].kind==1 && events[13].offset==0x80 && events[13].value==0);
            assert(events[14].kind==2 && events[15].kind==3);
        }
        cases++;
    }
    for(unsigned int old=0;old<3;old++) for(unsigned int pending=0;pending<2;pending++) {
        reset_fixture();stuck_clear=true;inflight_old=pending;
        struct csid_device csid={bank,44,old_completions[old],(void *)&device};
        kernel_completion=&csid.reset_complete;bank[0x7c/4]=1;
        assert(csid_reset(&csid)==-EIO);
        assert(commands==0 && waits==0 && syncs==1 && count==6 && bank[0x80/4]==0);
        cases++;
    }
    /* Actual public reset function encodes each supported command/location/mode. */
    struct cam_ife_csid_ver2_reg_info reg={&public_common,&public_rx};
    struct public_core_info core={&reg};
    for(unsigned int cmd=0;cmd<3;cmd++) for(unsigned int loc=0;loc<2;loc++)
    for(unsigned int mode=0;mode<2;mode++) for(unsigned int fail=0;fail<2;fail++) {
        reset_fixture();reference_mode=true;public_wait_result=fail ? -ETIMEDOUT : 0;
        struct public_hw_info info={.hw_state=CAM_HW_STATE_POWER_UP,.soc_info={.reg_map={{bank}}}};
        struct cam_ife_csid_ver2_hw hw={&info,&core,0};
        u32 halt=mode ? CAM_CSID_HALT_IMMEDIATELY : CAM_CSID_HALT_AT_FRAME_BOUNDARY;
        int ret=cam_ife_csid_ver2_internal_reset(&hw,cmd,loc,halt);
        assert(ret==public_wait_result);
        u32 reset=cmd==CAM_IFE_CSID_RESET_CMD_SW_RST ? 2 : cmd==CAM_IFE_CSID_RESET_CMD_HW_RST ? 1 : 4;
        assert(bank[0x10/4]==reset && bank[0xc/4]==((loc ? 16U : 0U)|mode));
        unsigned int write_count=0;
        for(unsigned int i=0;i<count;i++) if(events[i].kind==1) write_count++;
        assert(write_count==(cmd==CAM_IFE_CSID_RESET_CMD_SW_RST ? 4U : 2U));
        public_cases++;
    }
    reset_fixture();reference_mode=true;
    struct public_hw_info info={.hw_state=CAM_HW_STATE_POWER_DOWN,.soc_info={.reg_map={{bank}}}};
    struct cam_ife_csid_ver2_hw hw={&info,&core,0};
    assert(cam_ife_csid_ver2_internal_reset(&hw,CAM_IFE_CSID_RESET_CMD_SW_RST,CAM_IFE_CSID_RESET_LOC_COMPLETE,CAM_CSID_HALT_IMMEDIATELY)==-EINVAL);
    assert(count==0); public_cases++;
    /* Exact published complete software reset: same four programming writes. */
    reset_fixture();reference_mode=true;public_wait_result=0;info.hw_state=CAM_HW_STATE_POWER_UP;
    assert(!cam_ife_csid_ver2_internal_reset(&hw,CAM_IFE_CSID_RESET_CMD_SW_RST,CAM_IFE_CSID_RESET_LOC_COMPLETE,CAM_CSID_HALT_IMMEDIATELY));
    const struct event public_expected[]={{1,0x200,0},{1,0x204,0},{1,0xc,0x11},{1,0x10,2}};
    unsigned int n=0;
    for(unsigned int i=0;i<count;i++) if(events[i].kind==1) {
        assert(n<4 && !memcmp(&events[i],&public_expected[n],sizeof(struct event)));n++;
    }
    assert(n==4);public_cases++;
    printf("PASS reset freshness=%u public_reset_cases=%u exact_SW_command=2 RX_cutoff=2 timeout_top_masked=1\n",cases,public_cases);
    return 0;
}
"""

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent",required=True,type=Path)
    parser.add_argument("--candidate",required=True,type=Path)
    parser.add_argument("--reference-dir",required=True,type=Path)
    parser.add_argument("--cc",choices=["gcc","clang"],default="gcc")
    args=parser.parse_args()
    repo=Path(__file__).resolve().parents[1]
    parent=pinned(args.parent/PREFIX/"camss-csid-680.c",PARENT_SHA)
    candidate=pinned(args.candidate/PREFIX/"camss-csid-680.c",CANDIDATE_SHA)
    patch=repo/"src/upstream/camss/patches/0006-camss-csid680-use-fresh-software-reset.patch"
    pinned(patch,PATCH_SHA)
    manifest=json.loads((repo/"src/upstream/camss/csid680-reset-reference-20261012.json").read_text())
    sources=verify_reference(args.reference_dir,manifest)
    public,initializers=reference_code(sources)
    definitions="\n".join(line for line in candidate.splitlines() if line.startswith("#define"))
    with tempfile.TemporaryDirectory(prefix="csid680-reset-test-") as temp:
        work=Path(temp);target=work/PREFIX/"camss-csid-680.c";target.parent.mkdir(parents=True);target.write_text(parent)
        result=subprocess.run(["patch","-p1","--batch","--forward","-i",str(patch)],cwd=work,capture_output=True,text=True)
        if result.returncode or target.read_text()!=candidate:
            raise ValueError("patch replay does not match")
        source=work/"test.c";source.write_text(SHIM+definitions+"\n"+public+function(candidate,"csid_reset")+TEST)
        executable=work/"test"
        subprocess.run([args.cc,"-std=gnu11","-O1","-g","-Wall","-Wextra","-Werror","-Wno-unused-parameter","-fsanitize=address,undefined","-fno-omit-frame-pointer",str(source),"-o",str(executable)],check=True)
        result=subprocess.run([str(executable)],capture_output=True,text=True)
        if result.returncode:
            raise RuntimeError(result.stderr+result.stdout)
        print(json.dumps({"status":"PASS","compiler":args.cc,"detail":result.stdout.strip(),"asan":True,"ubsan":True,
            "unchanged_actual_public_function_compiled":True,"actual_candidate_reset_compiled":True,"reference_source_files":9,
            "public_scalar_definitions":initializers,"kernel_primitives_IRQ_MMIO_and_waits_are_test_adapters":True,
            "hardware_qualified":False,"streaming_stop_or_DMA_retirement_proven":False},indent=2))
if __name__=="__main__":
    main()
