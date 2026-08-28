#!/usr/bin/env python3
import argparse, csv, hashlib, json, re
from pathlib import Path

REGIONS = {
    "wrapper": (0x0ACB6000, 0x1000),
    "csid0": (0x0ACB7000, 0x2000),
    "csid1": (0x0ACB9000, 0x2000),
    "csid2": (0x0ACBB000, 0x2000),
    "vfe0": (0x0AC62000, 0x4000),
    "vfe1": (0x0AC71000, 0x4000),
    "csiphy2": (0x0ACE8000, 0x2000),
}
PHASES = ("IDLE", "LIVE1", "POST", "LIVE2", "POST2")
LINE = re.compile(
    r"^([0-9a-f]{8})`([0-9a-f]{8})\s+"
    r"([0-9a-f]{8})\s+([0-9a-f]{8})\s+([0-9a-f]{8})\s+([0-9a-f]{8})\s*$",
    re.I | re.M,
)

def parse_dump(text, phase, region):
    begin=f"===E003G3_{phase}_{region.upper()}_BEGIN==="
    end=f"===E003G3_{phase}_{region.upper()}_END==="
    if begin not in text or end not in text:
        raise RuntimeError(f"missing marker pair: {begin} / {end}")
    body=text.rsplit(begin,1)[1].split(end,1)[0]
    out={}
    for m in LINE.finditer(body):
        addr=int(m.group(1)+m.group(2),16)
        for i in range(4): out[addr+4*i]=int(m.group(3+i),16)
    return out

def write_nonzero(path, base, l1, l2):
    with path.open('w',newline='') as f:
        w=csv.writer(f,lineterminator='\n')
        w.writerow(['offset','address','live1','live2','stable'])
        for a in sorted(l1):
            if l1[a] not in (0,0x80000000) or l2[a] not in (0,0x80000000):
                w.writerow([f'0x{a-base:04x}',f'0x{a:08x}',f'0x{l1[a]:08x}',f'0x{l2[a]:08x}',int(l1[a]==l2[a])])

def decode_csid_cfg0(v):
    return {
        'enabled': bool(v & (1<<31)),
        'dt_id': (v>>27)&0x3,
        'vc': (v>>22)&0x1f,
        'data_type': (v>>16)&0x3f,
        'decode_format': (v>>12)&0xf,
    }

def main():
    here=Path(__file__).resolve().parent
    ap=argparse.ArgumentParser()
    ap.add_argument('raw',nargs='?',type=Path,default=here/'raw'/'E003G_ROUTE_ORACLE_20260828.log')
    ap.add_argument('--out',type=Path,default=here)
    args=ap.parse_args()
    raw=args.raw.read_bytes(); text=raw.decode('utf-16',errors='replace')
    args.out.mkdir(parents=True,exist_ok=True)
    d={p:{r:parse_dump(text,p,r) for r in REGIONS} for p in PHASES}
    summary={
        'date':'2026-08-28',
        'device':'Surface Camera Front / Sony IMX681',
        'acquisition':'same-machine Windows 11; WinRT MediaCapture/MediaFrameReader; two StartAsync=Success passes with clean StopAsync; SP7 KDNET physical MMIO',
        'raw_file':args.raw.name,
        'raw_bytes':len(raw),
        'raw_sha256':hashlib.sha256(raw).hexdigest(),
        'qualcomm_register_map_reference':{
            'repo':'https://github.com/qualcomm-linux/camera-driver',
            'branch':'camera-kernel.qclinux.0.0',
            'commit':'0f16924ff6a7f9bb56a7e958016da2ed8a174f2f',
            'policy':'register names/layout only; Windows values remain the behavioral oracle',
        },
        'regions':{},
    }
    for r,(base,size) in REGIONS.items():
        exp=size//4
        for p in PHASES:
            if len(d[p][r])!=exp: raise RuntimeError(f'{p}/{r}: {len(d[p][r])} dwords expected {exp}')
        idle,l1,post,l2,post2=(d[p][r] for p in PHASES)
        diff=[a for a in l1 if l1[a]!=l2[a]]
        stablechg=[a for a in l1 if l1[a]==l2[a] and l1[a]!=idle[a]]
        nz=[a for a in l1 if l1[a] not in (0,0x80000000)]
        summary['regions'][r]={
            'base':f'0x{base:08x}','size_bytes':size,'dwords':exp,
            'live1_live2_mismatches':len(diff),
            'stable_changed_vs_idle_dwords':len(stablechg),
            'live1_nonzero_nonsentinel_dwords':len(nz),
            'idle_post1_mismatches':sum(idle[a]!=post[a] for a in idle),
            'idle_post2_mismatches':sum(idle[a]!=post2[a] for a in idle),
            'volatile_live_offsets':[f'0x{a-base:04x}' for a in diff],
        }
        write_nonzero(args.out/f'{r}-route-live-nonzero.csv',base,l1,l2)
    wb=REGIONS['wrapper'][0]; c1=REGIONS['csid1'][0]; v1=REGIONS['vfe1'][0]
    w=d['LIVE1']['wrapper']; cs=d['LIVE1']['csid1']; vf=d['LIVE1']['vfe1']
    rx0=cs[c1+0x200]; rx1=cs[c1+0x204]
    ipp=cs[c1+0x300]
    hc=cs[c1+0x35c]; vc=cs[c1+0x360]
    fm=cs[c1+0x388]
    summary['route_decode']={
        'wrapper_io_path_cfg0':{
            'csid0':f'0x{w[wb+0]:08x}','csid1':f'0x{w[wb+4]:08x}','csid2':f'0x{w[wb+8]:08x}',
            'active_output_ife':'CSID1 (bit8 OUTPUT_IFE_EN set only at wrapper +0x004)',
        },
        'csid1_rx':{
            'cfg0':f'0x{rx0:08x}',
            'num_active_lanes_field':rx0 & 0xf,
            'active_lanes_or_trios':(rx0 & 0xf)+1,
            'lane_cfg':(rx0 >> 4) & 0xffff,
            'phy_num_sel':(rx0 >> 20) & 0xf,
            'phy_type_sel':(rx0 >> 24) & 0x1,
            'tpg_mux_en':(rx0 >> 27) & 0x1,
            'tpg_num_sel':(rx0 >> 28) & 0xf,
            'cfg1':f'0x{rx1:08x}',
            'packet_ecc_correction_en':bool(rx1 & 1),
            'misr_enable':bool(rx1 & (1 << 6)),
        },
        'csid1_ipp':{
            'cfg0':f'0x{ipp:08x}',**decode_csid_cfg0(ipp),
            'cfg1':f'0x{cs[c1+0x310]:08x}',
            'cfg1_named_bits':{
                'crop_h_en':bool(cs[c1+0x310] & (1 << 12)),
                'crop_v_en':bool(cs[c1+0x310] & (1 << 13)),
                'pix_store_en':bool(cs[c1+0x310] & (1 << 14)),
                'timestamp_en':bool(cs[c1+0x310] & (1 << 9)),
                'early_eof_en':bool(cs[c1+0x310] & (1 << 16)),
                'drop_h_en':bool(cs[c1+0x310] & (1 << 10)),
                'drop_v_en':bool(cs[c1+0x310] & (1 << 11)),
                'format_measure_en_bit4':bool(cs[c1+0x310] & (1 << 4)),
                'unresolved_set_bits':[bit for bit in range(32) if (cs[c1+0x310] & (1 << bit)) and bit not in (4,9,10,11,12,13,14,16)],
            },
            'hcrop':f'0x{hc:08x}','crop_x_start':hc&0x3fff,'crop_x_end':(hc>>16)&0xffff,
            'vcrop':f'0x{vc:08x}','crop_y_start':vc&0x3fff,'crop_y_end':(vc>>16)&0xffff,
            'format_measure_cfg1':f'0x{fm:08x}','measured_width':fm&0xffff,'measured_height':(fm>>16)&0xffff,
        },
        'vfe':{
            'vfe0_live_nonzero':summary['regions']['vfe0']['live1_nonzero_nonsentinel_dwords'],
            'vfe1_live_nonzero':summary['regions']['vfe1']['live1_nonzero_nonsentinel_dwords'],
            'vfe1_bus_hw_version':f'0x{vf[v1+0xc00]:08x}',
        },
    }
    wm_names = {
        0:'FULL_Y', 1:'FULL_C', 2:'DS4', 3:'DS16', 4:'DISP_Y', 5:'DISP_C',
        6:'DISP_DS4', 7:'DISP_DS16', 8:'FD_Y', 9:'FD_C', 10:'PIXEL_RAW',
        11:'STATS_BE0', 12:'STATS_BHIST0', 13:'STATS_TINTLESS_BG', 14:'STATS_AWB_BG',
        15:'STATS_AWB_BFW', 16:'STATS_BAF', 17:'STATS_BHIST', 18:'STATS_RS',
        19:'STATS_IHIST', 20:'SPARSE_PD', 21:'PDAF_PD_DATA', 22:'PDAF_SAD', 23:'LCR',
        24:'RDI0', 25:'RDI1', 26:'RDI2', 27:'LTM_STATS',
    }
    clients=[]
    for i in range(28):
        off=0xe00+i*0x100
        cfg=vf[v1+off]
        clients.append({
            'client':i, 'name':wm_names[i], 'cfg':f'0x{cfg:08x}',
            'enabled':bool(cfg & 1),
            'image_addr':f'0x{vf[v1+off+0x04]:08x}',
            'frame_incr':f'0x{vf[v1+off+0x08]:08x}',
            'image_cfg0':f'0x{vf[v1+off+0x0c]:08x}',
            'image_cfg2':f'0x{vf[v1+off+0x14]:08x}',
            'packer_cfg':f'0x{vf[v1+off+0x18]:08x}',
            'width':vf[v1+off+0x0c] & 0xffff,
            'height':(vf[v1+off+0x0c] >> 16) & 0xffff,
            'stride':vf[v1+off+0x14],
        })
    summary['route_decode']['vfe']['clients']=clients
    summary['route_decode']['vfe']['enabled_clients']=[
        {k:c[k] for k in ('client','name','cfg','width','height','stride','frame_incr','packer_cfg')} for c in clients if c['enabled']
    ]
    summary['route_decode']['vfe']['windows_full_output']={'width':clients[0]['width'],'height':clients[0]['height'],'chroma_height':clients[1]['height']}
    (args.out/'route-oracle-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
