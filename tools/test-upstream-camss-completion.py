#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Exercise actual CAMSS completion functions with test-only MMIO/lock/buffer adapters."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

PREFIX = Path("drivers/media/platform/qcom/camss")
PINS = {
    "camss-csid-680.c": ("804001536fee3123536edfa1f1476c83b12872dff993d9e70645d80ee0a6be16", "e546e09dd13f1e0be0fb63f164519ec43a119a54a64049daa97c5ed25325d9d6"),
    "camss.c": ("32404c0f137a2c7a0da791cfbfc9051c2b3451f7ad4d41d1255a73ea90dd1fe0", "1fb1bf12382f5e687903ced5707486eb08ed43095358de179220369884d404c2"),
    "camss-vfe.c": ("278c8f6fa942836f4cea08a6ca3643d5efea7045e5d4e68c2e6498770c929f1b", "42155f444290c82494278f6016e5916158196ae39ee30d0cfffea5519b93c81d"),
}
HEADER_PINS = {
    "camss.h": "52cc0bc056bde6637f5ed539ebed310456f71776a39a42ac89af94d236d265cf",
    "camss-vfe.h": "e7f4a827d67605166dd61dcad30aa7f64e946c47a97ca204b0a8f3a795d19980",
    "camss-csid.h": "170c9314e633f2978ebecd0a346e300cb0b267695761caab551502e17beac7b0",
}
PATCH = "0005-camss-validate-completion-routing.patch"
PATCH_SHA = "41c4add40c2b1bcb296d1fc5433426b0bfee5e11eac1597bd7f7f3ae0aed7375"

def pinned(path, expected):
    if not path.is_file() or any(p.is_symlink() for p in [path, *path.parents]):
        raise ValueError("missing or symlink source")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("changed pinned source")
    return raw.decode()

def body(source, name):
    match = re.search(r"^(?:static )?(?:void|irqreturn_t) " + name + r"\([^;]*?\)\n\{", source, re.M)
    if not match:
        raise ValueError("function missing: " + name)
    pos, depth = match.end(), 1
    while depth:
        if pos >= len(source):
            raise ValueError("unbalanced function")
        depth += (source[pos] == "{") - (source[pos] == "}")
        pos += 1
    return source[match.start():pos] + "\n"

SHIM = r"""
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <limits.h>
typedef uint8_t u8;
typedef uint32_t u32;
typedef uint64_t u64;
typedef int irqreturn_t;
#define BIT(n) (1U << (n))
#define READ_ONCE(x) mapping_snapshot(&(x))
#define GENMASK(h,l) ((~0U >> (31U-(h))) & (~0U << (l)))
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
#define MSM_CSID_MAX_SRC_STREAMS 4
#define MSM_VFE_NUM_OUTPUTS 5
#define VFE_OUTPUT_ON 6
#define VFE_LINE_NONE (-1)
#define VB2_BUF_STATE_DONE 0
#define IRQ_HANDLED 1
#define dev_err_ratelimited(...) ((void)0)
struct vfe_device;
struct vfe_line;
struct camss_buf_done_info { int hw_id, port_id; u32 status; };
struct vb2_buffer { unsigned int id; };
struct camss_buffer { struct { struct vb2_buffer vb2_buf; } vb; };
struct vfe_output {
    u8 comp_group, wm_num;
    int state;
    unsigned int sequence;
};
struct vfe_line {
    int id;
    bool is_pix;
    unsigned int num_outputs;
    struct vfe_output output[MSM_VFE_NUM_OUTPUTS];
};
struct vfe_hw_ops {
    void (*vfe_buf_done)(struct vfe_device *, int, struct camss_buf_done_info *);
    void (*reg_update)(struct vfe_device *, int);
};
struct vfe_resource { unsigned int line_num; struct vfe_hw_ops *hw_ops; };
struct camss_resource { unsigned int vfe_num; };
struct camss { struct camss_resource *res; struct vfe_device *vfe; void *dev; };
struct vfe_device {
    int output_lock, wm_output_map[7];
    struct vfe_line line[4];
    struct vfe_resource *res;
    struct camss *camss;
    struct { void (*wm_done)(struct vfe_device *, u8); } isr_ops;
};
struct csid_device { char *base; int id, reset_complete; bool lite; struct camss *camss; };
static unsigned int completed[6], selected[5], params_calls, updates, dispatches;
static unsigned int rup_calls[4], composite_calls, composite_port, mmio_writes;
static struct camss_buf_done_info last_info;
static struct camss_buffer buffers[6];
static struct vfe_device *current;
static bool return_ready, return_params;
static u32 registers[4096];
static bool replace_mapping;
static int replacement_mapping;
static unsigned int snapshot_reads;
static int mapping_snapshot(int *mapping) {
    int saved=*mapping;
    snapshot_reads++;
    if(replace_mapping) { *mapping=replacement_mapping; replace_mapping=false; }
    return saved;
}
static u64 ktime_get_ns(void) { return 123456; }
#define spin_lock_irqsave(lock, flags) do { (flags)=0; assert(*(lock)==0); ++*(lock); } while (0)
#define spin_unlock_irqrestore(lock, flags) do { assert((flags)==0 && *(lock)==1); --*(lock); } while (0)
static struct camss_buffer *vfe_output_done(struct vfe_device *vfe, struct vfe_line *line, struct vfe_output *out, u64 ts) {
    assert(vfe->output_lock==1 && ts==123456);
    unsigned int index = out - line->output;
    assert(index < 5); selected[index]++; out->sequence++;
    return return_ready ? &buffers[index] : NULL;
}
static struct camss_buffer *vfe_params_apply_next(struct vfe_device *vfe, struct vfe_line *line, u32 sequence) {
    assert(vfe->output_lock==1 && sequence==line->output[0].sequence);
    params_calls++;
    return return_params ? &buffers[5] : NULL;
}
static void vb2_buffer_done(struct vb2_buffer *buf, int state) {
    assert(current->output_lock==0 && state==VB2_BUF_STATE_DONE && buf->id<6);
    completed[buf->id]++;
}
static void reg_update(struct vfe_device *vfe, int id) { assert(vfe->output_lock==1 && id==0); updates++; }
static void record_dispatch(struct vfe_device *vfe, int port, struct camss_buf_done_info *info) {
    (void)vfe; assert(port==info->port_id); dispatches++; last_info=*info;
}
static void wm_done(struct vfe_device *vfe, u8 port) { (void)vfe; composite_calls++; composite_port=port; }
static bool csid_is_lite(struct csid_device *csid) { return csid->lite; }
static u32 readl(char *address) { uintptr_t offset=address-(char *)registers; assert(offset<sizeof(registers) && !(offset&3)); return registers[offset/4]; }
static void writel(u32 value, char *address) { uintptr_t offset=address-(char *)registers; assert(offset<sizeof(registers) && !(offset&3)); (void)value; mmio_writes++; }
static void csid_rup_complete(struct csid_device *csid, int port) { (void)csid; assert(port>=0 && port<4); rup_calls[port]++; }
static void complete(int *completion) { (*completion)++; }
"""

TEST = r"""
static struct vfe_hw_ops ops;
static struct vfe_resource resource;
static struct camss_resource resources;
static struct camss camss;
static struct vfe_device devices[2];
static unsigned int cases;

static void reset_fixture(void) {
    memset(devices,0,sizeof(devices)); memset(completed,0,sizeof(completed));
    memset(selected,0,sizeof(selected)); memset(registers,0,sizeof(registers));
    memset(rup_calls,0,sizeof(rup_calls));
    params_calls=updates=dispatches=composite_calls=mmio_writes=0;
    replace_mapping=false; snapshot_reads=0;
    return_ready=return_params=true;
    resource=(struct vfe_resource){4,&ops}; resources=(struct camss_resource){2};
    camss=(struct camss){&resources,devices,NULL}; current=&devices[0];
    for(unsigned int d=0;d<2;d++) {
        devices[d].res=&resource; devices[d].camss=&camss;
        devices[d].isr_ops.wm_done=wm_done;
        for(unsigned int p=0;p<7;p++) devices[d].wm_output_map[p]=VFE_LINE_NONE;
        devices[d].wm_output_map[0]=0;
        devices[d].line[0].num_outputs=5; devices[d].line[0].is_pix=true;
        for(unsigned int o=0;o<5;o++) devices[d].line[0].output[o]=(struct vfe_output){o,1,VFE_OUTPUT_ON,0};
    }
    for(unsigned int b=0;b<6;b++) buffers[b].vb.vb2_buf.id=b;
    ops=(struct vfe_hw_ops){vfe_buf_done,reg_update};
}
static void empty(void) {
    for(unsigned int i=0;i<5;i++) assert(!selected[i]);
    for(unsigned int i=0;i<6;i++) assert(!completed[i]);
    assert(!params_calls && !updates && !current->output_lock); cases++;
}
int main(void) {
    /* RDI/TFE fallback and per-group image/statistics completion are kept. */
    for(unsigned int pix=0;pix<2;pix++) for(unsigned int n=1;n<=5;n++)
    for(u32 mask=0;mask<32;mask++) for(unsigned int ready=0;ready<2;ready++)
    for(unsigned int has_params=0;has_params<2;has_params++) {
        reset_fixture(); current->line[0].is_pix=pix;
        current->line[0].num_outputs=n; return_ready=ready; return_params=has_params;
        struct camss_buf_done_info info={0,0,mask};
        vfe_buf_done(current,0,&info);
        bool grouped=pix && mask;
        for(unsigned int o=0;o<5;o++) {
            bool expected=grouped ? (o<n && (mask&BIT(o))) : o==0;
            assert(selected[o]==expected && completed[o]==(expected && ready));
        }
        bool image=grouped && (mask&1U) && ready;
        assert(params_calls==image && updates==(image && has_params));
        assert(completed[5]==(image && has_params)); assert(!current->output_lock);
        cases++;
    }
    reset_fixture(); vfe_buf_done(current,0,NULL);
    assert(selected[0]==1 && !params_calls); cases++;
    const int ports[]={INT_MIN,-2,-1,7,8,INT_MAX};
    for(unsigned int i=0;i<ARRAY_SIZE(ports);i++) {
        reset_fixture(); vfe_buf_done(current,ports[i],NULL); empty();
    }
    const int mappings[]={INT_MIN,-2,-1,4,5,INT_MAX};
    for(unsigned int i=0;i<ARRAY_SIZE(mappings);i++) {
        reset_fixture(); current->wm_output_map[0]=mappings[i];
        vfe_buf_done(current,0,NULL); empty();
    }
    reset_fixture(); resource.line_num=0; vfe_buf_done(current,0,NULL); empty();
    reset_fixture(); resource.line_num=99; current->wm_output_map[0]=4;
    vfe_buf_done(current,0,NULL); empty();
    const unsigned int counts[]={0,6,UINT_MAX};
    for(unsigned int i=0;i<ARRAY_SIZE(counts);i++) {
        reset_fixture(); current->line[0].num_outputs=counts[i];
        vfe_buf_done(current,0,NULL); empty();
    }
    /* Invalid groups never shift; every legal u32 status bit remains usable. */
    for(unsigned int group=0;group<256;group++) {
        reset_fixture(); current->line[0].num_outputs=1;
        current->line[0].output[0].comp_group=group;
        struct camss_buf_done_info info={0,0,UINT_MAX};
        vfe_buf_done(current,0,&info);
        assert(selected[0]==(group<32)); assert(completed[0]==(group<32));
        assert(params_calls==(group<32)); assert(!current->output_lock); cases++;
    }
    for(unsigned int o=0;o<5;o++) for(unsigned int kind=0;kind<2;kind++) {
        reset_fixture();
        if(kind) current->line[0].output[o].wm_num=0;
        else current->line[0].output[o].state=0;
        struct camss_buf_done_info info={0,0,31}; vfe_buf_done(current,0,&info);
        assert(!selected[o] && !completed[o]); cases++;
    }
    /* Dispatcher's hardware index is checked before any array access. */
    const int ids[]={INT_MIN,-1,0,1,2,INT_MAX};
    const int dispatch_ports[]={-1,0,6,7,INT_MAX};
    for(unsigned int h=0;h<ARRAY_SIZE(ids);h++) for(unsigned int p=0;p<ARRAY_SIZE(dispatch_ports);p++) {
        reset_fixture(); ops.vfe_buf_done=record_dispatch;
        struct camss_buf_done_info info={ids[h],dispatch_ports[p],0x12345678};
        camss_buf_done(&camss,&info);
        bool expected=ids[h]>=0 && ids[h]<2 && dispatch_ports[p]>=0;
        assert(dispatches==expected);
        if(expected) assert(last_info.status==info.status);
        cases++;
    }
    reset_fixture(); camss_buf_done(&camss,NULL); assert(!dispatches); cases++;
    /* Composite scans reject bad mappings and preserve first PIX selection. */
    for(unsigned int p=0;p<7;p++) {
        reset_fixture(); for(unsigned int i=0;i<7;i++) current->wm_output_map[i]=i&1 ? -2 : 4;
        current->wm_output_map[p]=0; vfe_isr_comp_done(current,1);
        assert(composite_calls==1 && composite_port==p); cases++;
    }
    reset_fixture(); for(unsigned int i=0;i<7;i++) current->wm_output_map[i]=4;
    vfe_isr_comp_done(current,1); assert(!composite_calls); cases++;
    /* A changed mapping after READ_ONCE cannot change the checked line index. */
    const int replacements[]={-1,4,INT_MAX};
    for(unsigned int i=0;i<ARRAY_SIZE(replacements);i++) {
        reset_fixture(); replace_mapping=true; replacement_mapping=replacements[i];
        vfe_isr_comp_done(current,1);
        assert(composite_calls==1 && composite_port==0 && snapshot_reads==1);
        assert(current->wm_output_map[0]==replacements[i]); cases++;
    }
    /* Actual CSID ISR: mixed RDI/RUP/reset bits, full and lite devices. */
    for(unsigned int lite=0;lite<2;lite++) for(unsigned int reset=0;reset<2;reset++)
    for(unsigned int done=0;done<16;done++) for(unsigned int rup=0;rup<16;rup++) {
        reset_fixture(); ops.vfe_buf_done=record_dispatch;
        struct csid_device device={(char *)registers,1,0,lite,&camss};
        struct csid_device *csid=&device;
        registers[CSID_TOP_IRQ_STATUS/4]=reset ? CSID_TOP_IRQ_RESET : 0;
        registers[CSID_BUF_DONE_IRQ_STATUS/4]=done << BUF_DONE_IRQ_STATUS_RDI_OFFSET;
        for(unsigned int p=0;p<4;p++)
            registers[CSID_CSI2_RDIN_IRQ_STATUS(p)/4]=rup&BIT(p) ? CSID_CSI2_RDIN_RUP_DONE : 0;
        assert(csid_isr(0,csid)==IRQ_HANDLED);
        assert(dispatches==(unsigned int)__builtin_popcount(done));
        if(done) assert(last_info.hw_id==1 && last_info.status==0);
        for(unsigned int p=0;p<4;p++) assert(rup_calls[p]==!!(rup&BIT(p)));
        assert(csid->reset_complete==(int)reset && mmio_writes==4+(unsigned int)__builtin_popcount(rup));
        cases++;
    }
    printf("PASS completion routing cases=%u actual CSID/VFE/dispatcher functions; no hardware\n",cases);
    return 0;
}
"""

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--cc", choices=["gcc", "clang"], default="gcc")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    parent, candidate = {}, {}
    for name, pair in PINS.items():
        parent[name] = pinned(args.parent / PREFIX / name, pair[0])
        candidate[name] = pinned(args.candidate / PREFIX / name, pair[1])
    patch = repo / "src/upstream/camss/patches" / PATCH
    pinned(patch, PATCH_SHA)
    with tempfile.TemporaryDirectory(prefix="camss-completion-tests-") as temp:
        work = Path(temp)
        for name, text in parent.items():
            path = work / PREFIX / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        result = subprocess.run(["patch", "-p1", "--batch", "--forward", "-i", str(patch)], cwd=work, capture_output=True, text=True)
        if result.returncode:
            raise ValueError("patch replay failed: " + result.stderr)
        for name, text in candidate.items():
            if (work / PREFIX / name).read_text() != text:
                raise ValueError("candidate not reproduced by patch")
        definitions = "\n".join(line for line in candidate["camss-csid-680.c"].splitlines() if line.startswith("#define"))
        # test-only structure sizes are checked against pinned public declarations.
        headers = {name: pinned(args.candidate / PREFIX / name, digest)
                   for name, digest in HEADER_PINS.items()}
        csid_header = headers["camss-csid.h"]
        vfe_header = headers["camss-vfe.h"]
        if not re.search(r"#define MSM_CSID_MAX_SRC_STREAMS\s+4\b", csid_header) or not re.search(r"#define MSM_VFE_IMAGE_MASTERS_NUM\s+7\b", vfe_header):
            raise ValueError("test adapter sizes differ")
        if not re.search(r"#define MSM_VFE_PAD_NUM_PIX\s+6\b", vfe_header):
            raise ValueError("test output adapter size differs")
        functions = body(candidate["camss-vfe.c"], "vfe_buf_done")
        functions += body(candidate["camss-vfe.c"], "vfe_isr_comp_done")
        functions += body(candidate["camss.c"], "camss_buf_done")
        functions += body(candidate["camss-csid-680.c"], "csid_isr")
        code = work / "test.c"
        code.write_text(SHIM + definitions + "\n" + functions + TEST)
        executable = work / "test"
        cmd = [args.cc, "-std=gnu11", "-O1", "-g", "-Wall", "-Wextra", "-Werror", "-Wno-unused-parameter", "-fsanitize=address,undefined", "-fno-omit-frame-pointer", str(code), "-o", str(executable)]
        subprocess.run(cmd, check=True)
        result = subprocess.run([str(executable)], capture_output=True, text=True, check=True)
        print(json.dumps({"status":"PASS", "compiler":args.cc, "sanitizers":["address","undefined"],
              "detail":result.stdout.strip(), "actual_production_functions":4, "patch_replay_files":3,
              "source_pins":9, "patch_pins":1, "kernel_primitives_mmio_and_buffers_are_test_adapters":True,
              "hardware_qualified":False}, indent=2))

if __name__ == "__main__":
    main()
