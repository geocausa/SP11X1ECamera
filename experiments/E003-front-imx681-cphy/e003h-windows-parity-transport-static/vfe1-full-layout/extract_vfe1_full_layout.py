#!/usr/bin/env python3
import csv, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CSV = HERE.parents[1] / 'e003g-windows-csid-vfe-oracle' / 'vfe1-route-live-nonzero.csv'
OUT = HERE / 'vfe1-full-layout-summary.json'

def iv(x): return int(x, 16)
def align(x, a): return (x + a - 1) // a * a

def find(rows, off):
    key=f'0x{off:04x}'
    row=next((r for r in rows if r['offset'].lower()==key), None)
    if not row: raise SystemExit(f'missing {key}')
    return row

rows=list(csv.DictReader(CSV.open()))
# VFE680 BUS client 0 FULL_Y and client 1 FULL_C offsets from Qualcomm layout.
y={k:find(rows,o) for k,o in {
    'cfg':0x0e00,'image':0x0e04,'frame_incr':0x0e08,'image_cfg0':0x0e0c,
    'stride':0x0e14,'packer':0x0e18,'meta':0x0e40,'meta_cfg':0x0e44,
    'mode_cfg':0x0e48,'ctrl2':0x0e50,'lossy0':0x0e54,'lossy1':0x0e58}.items()}
c={k:find(rows,o) for k,o in {
    'cfg':0x0f00,'image':0x0f04,'frame_incr':0x0f08,'image_cfg0':0x0f0c,
    'stride':0x0f14,'packer':0x0f18,'meta':0x0f40,'meta_cfg':0x0f44,
    'mode_cfg':0x0f48,'ctrl2':0x0f50,'lossy0':0x0f54,'lossy1':0x0f58}.items()}

for group in (y,c):
    for r in group.values():
        if r['stable'] != '1' and r not in (group['image'], group['meta']):
            raise SystemExit(f'unexpected unstable config {r}')

width = iv(y['image_cfg0']['live1']) & 0xffff
height_y = iv(y['image_cfg0']['live1']) >> 16
width_c = iv(c['image_cfg0']['live1']) & 0xffff
height_c = iv(c['image_cfg0']['live1']) >> 16
stride = iv(y['stride']['live1'])
assert width == width_c == 2560
assert height_y == 1440 and height_c == 720
assert stride == iv(c['stride']['live1']) == 0xe00
assert iv(y['packer']['live1']) == iv(c['packer']['live1']) == 0xb  # PACKER_FMT_VER3_TP_10

# Standard TP10 UBWC geometry used by Qualcomm multimedia blocks.
y_meta_stride = align((width + 48 - 1)//48, 64)
y_meta_scan = align((height_y + 4 - 1)//4, 16)
y_meta_size = align(y_meta_stride * y_meta_scan, 4096)
c_meta_stride = align((((width + 1)//2) + 24 - 1)//24, 64)
c_meta_scan = align((((height_y + 1)//2) + 4 - 1)//4, 16)
c_meta_size = align(c_meta_stride * c_meta_scan, 4096)
data_stride = align((width * 4)//3, 256)
y_data_size = data_stride * height_y
c_data_size = data_stride * height_c
assert data_stride == stride
assert y_meta_size == 0x6000
assert c_meta_size == 0x3000
assert y_data_size == 0x4ec000
assert c_data_size == 0x276000
assert iv(y['frame_incr']['live1']) == y_meta_size + y_data_size == 0x4f2000
assert iv(c['frame_incr']['live1']) == c_meta_size + c_data_size == 0x279000

runs=[]
for live in ('live1','live2'):
    ym=iv(y['meta'][live]); yi=iv(y['image'][live]); cm=iv(c['meta'][live]); ci=iv(c['image'][live])
    assert yi-ym == y_meta_size
    assert cm-ym == y_meta_size+y_data_size
    assert ci-cm == c_meta_size
    runs.append({
        'phase': live,
        'base_y_meta': f'0x{ym:08x}',
        'y_image': f'0x{yi:08x}',
        'c_meta': f'0x{cm:08x}',
        'c_image': f'0x{ci:08x}',
        'y_image_minus_y_meta': f'0x{yi-ym:x}',
        'c_meta_minus_y_meta': f'0x{cm-ym:x}',
        'c_image_minus_c_meta': f'0x{ci-cm:x}',
    })

summary={
    'status':'PASS',
    'policy':'Same-machine Windows is behavioral oracle; Qualcomm source is register/format-layout reference only.',
    'windows_vfe1_full': {
        'width': width, 'height': height_y, 'chroma_height': height_c,
        'packer_cfg': '0x0000000b',
        'packer_decode': 'PACKER_FMT_VER3_TP_10',
        'v4l2_opaque_format_family': 'V4L2_PIX_FMT_QC10C (Qualcomm compressed 10-bit YUV420 / TP10 UBWC)',
        'stride_bytes': stride,
        'y_meta_size': y_meta_size,
        'y_data_size': y_data_size,
        'c_meta_size': c_meta_size,
        'c_data_size': c_data_size,
        'y_slice_size': y_meta_size+y_data_size,
        'c_slice_size': c_meta_size+c_data_size,
        'total_surface_size': y_meta_size+y_data_size+c_meta_size+c_data_size,
        'layout': ['Y_META','Y_TP10_UBWC','C_META','C_TP10_UBWC'],
    },
    'windows_address_runs': runs,
    'stable_client_config': {
        'full_y': {k:r['live1'] for k,r in y.items() if k not in ('image','meta')},
        'full_c': {k:r['live1'] for k,r in c.items() if k not in ('image','meta')},
    },
    'linux_consequence': 'One contiguous vb2 DMA buffer is sufficient in principle; CAMSS must derive internal Y/C meta+data addresses and implement QC10C/TP10 UBWC plus the Windows VFE1 ISP/scaler programming. Linear NV12 is not parity.'
}
OUT.write_text(json.dumps(summary, indent=2)+'\n')
print(json.dumps(summary, indent=2))
