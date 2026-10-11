#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Replay this pinned source series and exercise real C bodies with fake MMIO.

Only reads public kernel source and compiles a temporary userspace harness.
Never accesses camera devices, firmware, boot files or private tuning.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

PREFIX = 'drivers/media/platform/qcom/camss/'
PINS = {
    'camss-vfe.c': ('8efb77a4571a7a9b31201d24280ee566df4106aa1cf31ba0121701ed50cd5957',
                    '278c8f6fa942836f4cea08a6ca3643d5efea7045e5d4e68c2e6498770c929f1b'),
    'camss-vfe-680.c': ('ac316835ce1af153e1fc9fe778bb896faa457bbb4b7056b1b5ab42237c335dc2',
                        '78f78ee24343a929fda2b95cf06b5c604904fbf4bc37aa86af5d4410321575cd'),
    'camss-vfe-17x.c': ('9990956960254ae29d6e6e060bc8ca3b7de5c1a2785a647bdcca90c7fbce05b5',
                        'f81a3d464f12c27e31fa5a4a5ab8e0bac25abbdf25c2c2bbc73ce435703e1ca3'),
    'camss-vfe.h': ('e156d808d1cf98db9c0a561d38adefe3e02353dd6d334360efc63d031b12dfe3',
                    'e7f4a827d67605166dd61dcad30aa7f64e946c47a97ca204b0a8f3a795d19980'),
    'camss-vfe-340.c': ('e1e2e212f9180fa16b139545ac11539e43513c7955df50ace9bdc444f8b157c7',
                        'c103246f09d796bd34528d3dae1565752370d7b663ab852003b0c7508c518056'),
    'camss-vfe-480.c': ('e63a2bf7fd0a6cc6bcabe95f606a6d5ccb990647a2540bfe185d8fe0186842e2',
                        'a7149811a3e9fee3c288d70c6b8f83061494038329b289c0fc18c219c6f79664'),
    'camss-vfe-690.c': ('092324f3a384c35a642c9848a03fe0bdf303726a973274cf1acecc27a17edcf9',
                        '4d1521365a1928277413c733120842d4fbea258304511336fc95fa347d3a233b'),
    'camss-vfe-780.c': ('f98e612c46998b653b2aea2afbf4340f85d85def75e433eafd785f95656b1fd0',
                        '93fa79579ac485faa13164e19dec5bc89a214642d9e533b701174cb09ab70fd4'),
}
PATCHES = {
    '0001-camss-drop-unused-rfc-format-helper.patch': '7c57d76f70d41563b61c8913024f0ccb195bac077925fe555d68b87d96784b6b',
    '0002-camss-release-gen2-completion-port.patch': 'd01697d8e4e47af86081315e41a7b323c02f1a439e7f258f420e4538d49e8878',
    '0003-camss-vfe680-use-rdi-output-descriptors.patch': 'e74e9f877bcf6a0a1e8fecb7a15496f5ad33f8c00792d31e1e89598e8a391f90',
    '0004-camss-vfe17x-use-output-array-and-descriptors.patch': '267807334c002a2831078a33ce525ce99d680efd39fd3af563bb4895096db3ee',
}


def pinned(path, digest):
    if path.is_symlink() or not path.is_file():
        raise ValueError(f'missing or symlink source: {path}')
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != digest:
        raise ValueError(f'changed pinned source: {path}')
    return data.decode()


def body(source, name):
    match = re.search(r'^(?:static )?(?:inline )?(?:int|void) ' + name + r'\([^;]*?\)\n\{', source, re.M)
    if not match:
        raise ValueError(f'function absent: {name}')
    end = match.end()
    depth = 1
    while depth:
        if end >= len(source):
            raise ValueError('unbalanced function')
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[match.start():end] + '\n'


SHIM = r'''
#include <assert.h>
#include <errno.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef uint8_t u8;
typedef uint32_t u32;
#define BIT(n) (1U << (n))
#define VFE_LINE_NONE (-1)
#define VFE_OUTPUT_OFF 0
#define ARRAY_SIZE(a) (sizeof(a) / sizeof((a)[0]))
#define dev_dbg(...) ((void)0)
struct vfe_device;
struct vfe_line;
struct device { int unused; };
struct camss_video_ops { int unused; };
struct v4l2_pix_format_mplane {
    u32 width, height;
    struct { u32 bytesperline; } plane_fmt[2];
};
struct vfe_output {
    struct vfe_line *line;
    struct { struct { struct { struct v4l2_pix_format_mplane pix_mp; } fmt; } active_fmt; } video_out;
    struct { u8 bus_client, plane; } wm[2];
    int state;
    unsigned int wm_num;
};
struct vfe_line { int id; unsigned int num_outputs; struct vfe_device *vfe; struct vfe_output output[5]; };
struct vfe_device {
    bool lite; char *base; int output_lock; int wm_output_map[7];
    int stream_lock, stream_count, mutex_calls;
    struct { unsigned int line_num; } *res;
    struct { struct device *dev; } *camss;
    struct camss_video_ops video_ops;
    struct vfe_line line[4];
};
struct camss_buffer { u32 addr[2]; };
static const struct camss_video_ops vfe_video_ops_680 = {0};
static bool vfe_is_lite(struct vfe_device *vfe) { return vfe->lite; }
static struct vfe_device *to_vfe(struct vfe_line *line) { return line->vfe; }
#define spin_lock_irqsave(lock, flags) do { (flags) = 0; assert(*(lock) == 0); ++*(lock); } while (0)
#define spin_unlock_irqrestore(lock, flags) do { assert((flags) == 0); assert(*(lock) == 1); --*(lock); } while (0)
static int stop_result;
static int vfe_disable_output(struct vfe_line *line) { (void)line; return stop_result; }
static void mutex_lock(int *lock) { assert(*lock == 0); ++*lock; }
static void mutex_unlock(int *lock) { assert(*lock == 1); --*lock; }
static char bank[65536];
struct write { u32 value; unsigned int offset; };
static struct write writes[64];
static unsigned int count;
static void writel(u32 value, char *addr) {
    assert(addr >= bank && addr <= bank + sizeof(bank) - 4);
    assert(count < 64);
    writes[count++] = (struct write){value, (unsigned int)(addr - bank)};
}
'''

MAIN = r'''
int main(void) {
    static const u32 dimensions[8][3] = {
        {16, 1, 16}, {64, 48, 128}, {640, 480, 1280}, {1280, 720, 2560},
        {1920, 1080, 3840}, {2560, 1440, 5120}, {3840, 2160, 7680}, {4096, 4096, 8192}
    };
    static const u32 addresses[8] = {0, 16, 4096, 65536, 0x100000, 0x80000000U, 0xffff0000U, 0xfffffff0U};
    unsigned int cases = 0, planes = 0, mappings = 0, stops = 0;
    for (unsigned int lite = 0; lite < 2; lite++) {
        struct vfe_device vfe = {0};
        __typeof__(*vfe.res) res = {lite ? 4U : 3U};
        vfe.lite = lite; vfe.base = bank; vfe.res = &res;
        for (unsigned int i = 0; i < res.line_num; i++) {
            vfe.line[i].id = (int)i; vfe.line[i].vfe = &vfe;
            vfe.line[i].num_outputs = 1;
            vfe.line[i].output[0].line = &vfe.line[i];
            vfe.line[i].output[0].wm[0].bus_client = (u8)i;
        }
        candidate_vfe_subdev_init(NULL, &vfe);
        for (unsigned int i = 0; i < res.line_num; i++) {
            struct vfe_line *line = &vfe.line[i];
            struct vfe_output *out = &line->output[0];
            assert(out->wm[0].bus_client == (lite ? i : 24 + i));
            for (unsigned int d = 0; d < 8; d++) for (unsigned int a = 0; a < 8; a++) {
                struct v4l2_pix_format_mplane *pix = &out->video_out.active_fmt.fmt.pix_mp;
                pix->width = dimensions[d][0]; pix->height = dimensions[d][1];
                pix->plane_fmt[0].bytesperline = dimensions[d][2];
                struct camss_buffer buf = {{addresses[a], addresses[7 - a]}};
                struct write expected[64]; unsigned int n;
                count = 0;
                reference_vfe_wm_start(&vfe, (u8)i, line);
                reference_vfe_wm_update(&vfe, (u8)i, buf.addr[0], line);
                reference_vfe_wm_stop(&vfe, (u8)i, line);
                n = count; memcpy(expected, writes, sizeof(writes));
                count = 0;
                candidate_vfe_output_start(&vfe, out);
                candidate_vfe_output_update(&vfe, out, &buf);
                candidate_vfe_output_stop(&vfe, out);
                assert(count == n && count == 18);
                assert(memcmp(expected, writes, n * sizeof(writes[0])) == 0);
                cases++;
            }
            for (unsigned int p = 0; p < 2; p++) for (unsigned int a = 0; a < 8; a++) {
                struct camss_buffer buf = {{addresses[a], addresses[7 - a]}};
                out->wm[0].plane = (u8)p; count = 0;
                candidate_vfe_output_update(&vfe, out, &buf);
                assert(count == 1 && writes[0].value == buf.addr[p]);
                assert(writes[0].offset == (lite ? 0x404U : 0xe04U) + out->wm[0].bus_client * 0x100U);
                planes++;
            }
        }
    }
    for (unsigned int id = 0; id < 4; id++) for (unsigned int wm = 0; wm < 4; wm++)
        for (unsigned int outputs = 1; outputs <= 5; outputs++) {
            static const u8 clients[4] = {0, 1, 24, 26};
            struct vfe_device vfe = {0}; struct vfe_line *line = &vfe.line[id];
            line->id = (int)id; line->vfe = &vfe; line->num_outputs = outputs;
            for (unsigned int j = 0; j < 7; j++) vfe.wm_output_map[j] = (int)j;
            for (unsigned int j = 0; j < 5; j++) {
                line->output[j].state = 2;
                line->output[j].wm[0].bus_client = clients[wm];
            }
            vfe_put_output_v2(line);
            assert(vfe.output_lock == 0);
            for (unsigned int j = 0; j < 7; j++)
                assert(vfe.wm_output_map[j] == (j == id ? VFE_LINE_NONE : (int)j));
            for (unsigned int j = 0; j < 5; j++)
                assert(line->output[j].state == (j < outputs ? VFE_OUTPUT_OFF : 2));
            mappings++;
        }
    for (unsigned int mode = 0; mode < 2; mode++) for (unsigned int id = 0; id < 4; id++)
        for (unsigned int slot = 0; slot < 3; slot++) for (unsigned int fail = 0; fail < 2; fail++) {
            static const u8 legacy_clients[3] = {0, 1, 6};
            static const u8 port_clients[3] = {0, 24, 26};
            struct vfe_device vfe = {0}; struct vfe_line *line = &vfe.line[id];
            int expected[7]; unsigned int reserved = mode ? id : legacy_clients[slot];
            vfe.stream_count = 3; line->id = (int)id; line->vfe = &vfe; line->num_outputs = 2;
            line->output[0].wm_num = 1;
            line->output[0].wm[0].bus_client = mode ? port_clients[slot] : legacy_clients[slot];
            for (unsigned int j = 0; j < 7; j++) vfe.wm_output_map[j] = (int)j;
            vfe.wm_output_map[reserved] = (int)id;
            memcpy(expected, vfe.wm_output_map, sizeof(expected));
            if (!fail) expected[reserved] = VFE_LINE_NONE;
            for (unsigned int j = 0; j < 5; j++) line->output[j].state = 2;
            stop_result = fail ? -EINVAL : 0;
            int result = mode ? vfe_disable_v2(line) : vfe_disable(line);
            assert(result == stop_result);
            assert(memcmp(expected, vfe.wm_output_map, sizeof(expected)) == 0);
            assert(vfe.stream_count == (fail ? 3 : 2));
            assert(vfe.stream_lock == 0 && vfe.output_lock == 0);
            for (unsigned int j = 0; j < 5; j++)
                assert(line->output[j].state == (!fail && j < 2 ? VFE_OUTPUT_OFF : 2));
            stops++;
        }
    printf("PASS register cases=%u plane cases=%u mapping cases=%u stop cases=%u\n", cases, planes, mappings, stops);
    return 0;
}
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--cc', default='gcc')
    args = parser.parse_args()
    before = {n: pinned(args.reference / PREFIX / n, p[0]) for n, p in PINS.items()}
    after = {n: pinned(args.candidate / PREFIX / n, p[1]) for n, p in PINS.items()}
    patches = Path(__file__).resolve().parents[1] / 'src/upstream/camss/patches'
    for name, digest in PATCHES.items():
        pinned(patches / name, digest)
    # This series must leave Gen1's common release body unchanged.
    assert body(before['camss-vfe.c'], 'vfe_put_output') == body(after['camss-vfe.c'], 'vfe_put_output')
    # It must fix exactly the three obsolete VFE17x references.
    expected17x = before['camss-vfe-17x.c'].replace('output = &line->output;', 'output = &line->output[0];').replace('output->wm_idx[0]', 'output->wm[0].bus_client')
    assert expected17x == after['camss-vfe-17x.c']
    assert '.vfe_disable = vfe_disable,' in after['camss-vfe-17x.c']
    for backend in ['340', '480', '680', '690', '780']:
        assert '.vfe_disable = vfe_disable_v2,' in after[f'camss-vfe-{backend}.c']
        assert '.vfe_enable = vfe_enable_v2,' in after[f'camss-vfe-{backend}.c']
    with tempfile.TemporaryDirectory(prefix='camss-descriptor-test-') as directory:
        work = Path(directory)
        for n, data in before.items():
            path = work / PREFIX / n
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(data)
        for name in PATCHES:
            subprocess.run(['git', 'apply', '--whitespace=error', str(patches / name)], cwd=work, check=True)
        for n, data in after.items():
            assert (work / PREFIX / n).read_text() == data
        source = before['camss-vfe-680.c']
        macros = source[source.index('#define VFE_TOP_IRQn_STATUS'):source.index('static void vfe_global_reset')]
        functions = []
        for prefix, data, names in [
            ('reference_', source, ['vfe_disable_irq', 'vfe_wm_start', 'vfe_wm_update', 'vfe_wm_stop']),
            ('candidate_', after['camss-vfe-680.c'], ['vfe_disable_irq', 'vfe_output_start', 'vfe_output_update', 'vfe_output_stop', 'vfe_subdev_init'])
        ]:
            text = '\n'.join(body(data, name) for name in names)
            for name in names:
                text = re.sub(r'\b' + name + r'\b', prefix + name, text)
            functions.append(text)
        generic = '\n'.join(body(after['camss-vfe.c'], name) for name in
                            ['vfe_release_wm', 'vfe_put_output', 'vfe_put_output_v2',
                             'vfe_disable_common', 'vfe_disable', 'vfe_disable_v2'])
        harness = SHIM + macros + '\n#define VFE_680_WM_RDI0 24\n#define VFE_680_LITE_WM_RDI0 0\n' + '\n'.join(functions) + generic + MAIN
        path = work / 'test.c'; path.write_text(harness)
        subprocess.run([args.cc, '-std=gnu11', '-O1', '-g', '-Wall', '-Wextra', '-Werror', '-Wno-unused-parameter', '-fsanitize=address,undefined', '-fno-omit-frame-pointer', str(path), '-o', str(work / 'test')], check=True)
        subprocess.run([str(work / 'test')], check=True)
    print(json.dumps({'status': 'PASS_SOURCE_ONLY', 'compiler': args.cc, 'patch_replay': 4,
                      'register_cases': 448, 'plane_cases': 112, 'mapping_cases': 80,
                      'stop_cases': 48, 'reference_and_candidate_pins': 16, 'patch_pins': 4,
                      'kernel_locking_or_physical_dma_proven': False, 'hardware_qualified': False}))


if __name__ == '__main__':
    main()
