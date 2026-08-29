#!/usr/bin/env python3
import argparse, hashlib, json, re
from pathlib import Path

RAW_SHA = 'b6777baf442eab4cfea0985ad3a1274e80e3545505483935e506e2d9e086dd41'
RAW_BYTES = 291780
KMD_SHA = '64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c'
CONFIG_EXPECTED = [
    (0x3000, 0), (0x3000, 1),
    (0x3001, 0), (0x3002, 0),
    (0x301c, 0), (0x3010, 0), (0x300f, 0), (0x300e, 0), (0x300c, 0),
]
PORTS_EXPECTED = [0x3000, 0x3001, 0x3002, 0x301c, 0x3010, 0x300f, 0x300e, 0x300c]
PORT_NAMES = {
    0x3000: 'FULL',
    0x3001: 'DS4',
    0x3002: 'DS16',
    0x301c: 'STATS_AEC_BE',
    0x3010: 'STATS_RS',
    0x300f: 'STATS_BHIST',
    0x300e: 'STATS_AWB_BG',
    0x300c: 'STATS_TL_BG',
}
BP_ANCHORS = {
    'isp_start_done': ('0x16220', '===E003H_ISP_START_DONE==='),
    'bus_enable': ('0x1d830', '===E003H_BUS_ENABLE==='),
    'bus_config': ('0x1df40', '===E003H_BUS_CONFIG==='),
    'wm_update_builder': ('0x27920', '===E003H_WM_UPDATE_BUILDER==='),
    'video_done': ('0x1f438', '===E003H_VIDEO_DONE==='),
}
REJECTED_BP = ('0x15ee0', '===E003H_DEVICE_START===')


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_config(lines, i):
    if i + 2 >= len(lines):
        raise ValueError(f'truncated BUS_CONFIG at line {i+1}')
    m_w = re.fullmatch(r'w2=([0-9a-fA-F]{8})', lines[i+1].strip())
    m_p = re.search(r'\b([0-9a-fA-F]{8})$', lines[i+2].strip())
    if not m_w or not m_p:
        raise ValueError(f'malformed BUS_CONFIG at line {i+1}')
    return int(m_p.group(1), 16), int(m_w.group(1), 16)


def parse_enable(lines, i):
    if i + 1 >= len(lines):
        raise ValueError(f'truncated BUS_ENABLE at line {i+1}')
    m = re.fullmatch(r'w1=([0-9a-fA-F]{8}) w2=([0-9a-fA-F]{8})', lines[i+1].strip())
    if not m:
        raise ValueError(f'malformed BUS_ENABLE at line {i+1}')
    return int(m.group(1), 16), int(m.group(2), 16)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('raw', type=Path)
    ap.add_argument('--driver', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()

    raw_bytes = args.raw.read_bytes()
    if len(raw_bytes) != RAW_BYTES:
        raise SystemExit(f'raw byte count mismatch: {len(raw_bytes)} != {RAW_BYTES}')
    raw_sha = hashlib.sha256(raw_bytes).hexdigest()
    if raw_sha != RAW_SHA:
        raise SystemExit(f'raw sha256 mismatch: {raw_sha}')
    kmd_sha = sha256(args.driver)
    if kmd_sha != KMD_SHA:
        raise SystemExit(f'KMD sha256 mismatch: {kmd_sha}')

    lines = raw_bytes.decode('utf-16').splitlines()
    text = '\n'.join(lines)
    for name, (off, marker) in BP_ANCHORS.items():
        if f'qccamisp8380+{off}' not in text or marker not in text:
            raise SystemExit(f'missing breakpoint anchor {name}: {off} {marker}')
    if f'qccamisp8380+{REJECTED_BP[0]}' not in text or REJECTED_BP[1] not in text:
        raise SystemExit('missing rejected/noisy breakpoint anchor')

    configs, enables, start_done, wm, video, rejected, request_update = [], [], [], [], [], [], []
    for i, line in enumerate(lines):
        marker = line.strip()
        if marker == '===E003H_BUS_CONFIG===':
            port, index = parse_config(lines, i)
            configs.append({'line': i+1, 'port': port, 'index': index})
        elif marker == '===E003H_BUS_ENABLE===':
            port, enable = parse_enable(lines, i)
            enables.append({'line': i+1, 'port': port, 'enable': enable})
        elif marker == '===E003H_ISP_START_DONE===':
            start_done.append(i+1)
        elif marker == '===E003H_WM_UPDATE_BUILDER===':
            wm.append(i+1)
        elif marker == '===E003H_VIDEO_DONE===':
            video.append(i+1)
        elif marker == '===E003H_DEVICE_START===':
            rejected.append(i+1)
        elif marker == '===E003H_REQUEST_UPDATE===':
            request_update.append(i+1)

    starts = [c['line'] for c in configs if c['port'] == 0x3000 and c['index'] == 0]
    cycles = []
    for n, start in enumerate(starts):
        end = starts[n+1] if n+1 < len(starts) else len(lines) + 1
        c_cfg = [c for c in configs if start <= c['line'] < end]
        c_en = [e for e in enables if start <= e['line'] < end]
        c_sd = [x for x in start_done if start <= x < end]
        c_wm = [x for x in wm if start <= x < end]
        c_vid = [x for x in video if start <= x < end]
        c_rej = [x for x in rejected if start <= x < end]

        cfg_pairs = [(x['port'], x['index']) for x in c_cfg]
        if cfg_pairs != CONFIG_EXPECTED:
            raise SystemExit(f'cycle {n+1}: config sequence mismatch: {cfg_pairs!r}')
        if len(c_sd) != 1:
            raise SystemExit(f'cycle {n+1}: expected one ISP_START_DONE, got {len(c_sd)}')
        sd = c_sd[0]
        en_on = [x for x in c_en if x['enable'] == 1]
        en_off = [x for x in c_en if x['enable'] == 0]
        if [x['port'] for x in en_on] != PORTS_EXPECTED:
            raise SystemExit(f'cycle {n+1}: enable sequence mismatch')
        if [x['port'] for x in en_off] != PORTS_EXPECTED:
            raise SystemExit(f'cycle {n+1}: disable sequence mismatch')
        if not (c_cfg[-1]['line'] < en_on[0]['line'] < en_on[-1]['line'] < sd < en_off[0]['line']):
            raise SystemExit(f'cycle {n+1}: phase ordering mismatch')
        if any(c['line'] > sd for c in c_cfg):
            raise SystemExit(f'cycle {n+1}: BUS_CONFIG after ISP_START_DONE')
        if any(x['line'] > sd for x in en_on):
            raise SystemExit(f'cycle {n+1}: BUS enable-on after ISP_START_DONE')

        cycles.append({
            'cycle': n + 1,
            'line_range': [start, end - 1],
            'config': [{'port': f'0x{x[0]:04x}', 'name': PORT_NAMES[x[0]], 'index': x[1]} for x in cfg_pairs],
            'enable_order': [f'0x{x:04x}' for x in PORTS_EXPECTED],
            'isp_start_done_line': sd,
            'disable_order': [f'0x{x:04x}' for x in PORTS_EXPECTED],
            'wm_update_builder_hits': len(c_wm),
            'video_done_hits': len(c_vid),
            'rejected_0x15ee0_hits': len(c_rej),
        })

    if len(cycles) != 3:
        raise SystemExit(f'expected 3 complete BUS sessions, got {len(cycles)}')
    if len(wm) <= 1 or len(video) <= 1:
        raise SystemExit('dynamic WM/VIDEO repetition evidence missing')
    if request_update:
        raise SystemExit(f'unexpected REQUEST_UPDATE hits: {len(request_update)}')

    out = {
        'schema': 'sp11-e003h-windows-vfe1-bus-order-v1',
        'accepted': True,
        'raw': {'bytes': len(raw_bytes), 'sha256': raw_sha},
        'driver': {'sha256': kmd_sha},
        'breakpoint_offsets': {k: v[0] for k, v in BP_ANCHORS.items()},
        'rejected_breakpoint': {
            'offset': REJECTED_BP[0],
            'marker': REJECTED_BP[1],
            'reason': 'fires repeatedly inside resource processing; not an acceptance lifecycle anchor',
            'standalone_hits': len(rejected),
        },
        'public_port_names_reference_only': {f'0x{k:04x}': v for k, v in PORT_NAMES.items()},
        'windows_port_literals_authoritative': [f'0x{x:04x}' for x in PORTS_EXPECTED],
        'static_config_sequence': [
            {'port': f'0x{p:04x}', 'name': PORT_NAMES[p], 'index': idx} for p, idx in CONFIG_EXPECTED
        ],
        'session_order': 'BUS static config -> BUS enable -> ISP_START_DONE -> BUS disable',
        'complete_sessions': len(cycles),
        'cycles': cycles,
        'dynamic_evidence': {
            'wm_update_builder_hits_total': len(wm),
            'video_done_hits_total': len(video),
            'request_update_breakpoint_hits': len(request_update),
            'interpretation': 'WM update builder and VIDEO done are repeated dynamic/request/completion layers; hit counts are observational only because noisy breakpoints were disabled during later capture phases',
        },
        'linux_consequence': {
            'bus_static_state': 'session-static and established before ISP_START_DONE',
            'full_resource': '0x3000 has two static config indices (0 and 1), matching the Windows FULL Y/C two-WM topology',
            'dynamic_addresses': 'must remain per-request/per-buffer and must not be frozen into static BUS configuration',
            'streaming_status': 'Linux PIX remains blocked; no runtime authorization follows from this oracle alone',
        },
    }
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    print(f"PASS: {len(cycles)} complete Windows VFE1 BUS sessions; config/enable/disable order identical")
    print(json.dumps(out, indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
