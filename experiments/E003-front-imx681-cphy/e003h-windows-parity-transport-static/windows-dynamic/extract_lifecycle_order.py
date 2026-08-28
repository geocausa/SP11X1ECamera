#!/usr/bin/env python3
import argparse, hashlib, json, pathlib, re

RUNTIME_RE = re.compile(r'^===E003H_(ISP_START_ENTER|ISP_START_DONE|ISP_STOP_ENTER|ISP_STOP_DONE|SENSOR_STREAM_ON_APPLY|SENSOR_STREAM_OFF_APPLY)===$')
KEY = {
    'ISP_START_DONE': 'isp_start_done',
    'SENSOR_STREAM_ON_APPLY': 'sensor_stream_on_apply',
    'ISP_STOP_DONE': 'isp_stop_done',
    'SENSOR_STREAM_OFF_APPLY': 'sensor_stream_off_apply',
}
EXPECTED = ['ISP_START_DONE', 'SENSOR_STREAM_ON_APPLY', 'ISP_STOP_DONE', 'SENSOR_STREAM_OFF_APPLY']

DRIVERS = {
    'qccamisp8380.sys': {
        'sha256': '64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c',
        'base': '0xfffff802eed70000',
        'entry_rva': '0x2c730',
    },
    'qccammipicsi8380.sys': {
        'sha256': '033f5b1431ad4c76a12ac3b7f0a5be42e460a03bcff40d249511b3034786d407',
        'base': '0xfffff802eb340000',
        'entry_rva': '0x7f70',
    },
    'surfacecamfrontsensor8380.sys': {
        'sha256': '80a8e4a1ef8f0dacfbc2e8c6919cb269993057ffd3133c2ef7016ff742e46f03',
        'base': '0xfffff802ef200000',
        'entry_rva': '0xb980',
    },
}

BREAKPOINTS = {
    'isp_start_enter': '0xfffff802eed85ee0',
    'isp_start_done': '0xfffff802eed86220',
    'isp_stop_enter': '0xfffff802eed86300',
    'isp_stop_done': '0xfffff802eed86500',
    'sensor_stream_on_apply': '0xfffff802ef207e94',
    'sensor_stream_off_apply': '0xfffff802ef207c6c',
}

def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('log', type=pathlib.Path)
    ap.add_argument('--kd-script', type=pathlib.Path)
    ap.add_argument('--holder', type=pathlib.Path)
    ap.add_argument('--out', type=pathlib.Path)
    args = ap.parse_args()

    raw = args.log.read_bytes()
    text = raw.decode('utf-16')
    events = []
    noisy_counts = {k: 0 for k in ['ISP_START_ENTER','ISP_STOP_ENTER']}
    for lineno, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        m = RUNTIME_RE.fullmatch(s)
        if not m:
            continue
        marker = m.group(1)
        if marker in noisy_counts:
            noisy_counts[marker] += 1
        if marker in KEY:
            events.append({'line': lineno, 'marker': marker, 'event': KEY[marker]})

    markers = [e['marker'] for e in events]
    expected_all = EXPECTED * 2
    if markers != expected_all:
        raise SystemExit(f'FAIL: lifecycle marker sequence {markers!r} != {expected_all!r}')

    cycles = []
    for i in range(2):
        chunk = events[i*4:(i+1)*4]
        cycles.append({
            'cycle': i + 1,
            'order': [x['event'] for x in chunk],
            'lines': {x['event']: x['line'] for x in chunk},
        })

    out = {
        'status': 'PASS',
        'policy': 'Same-machine Windows on this exact SP11 is the behavioral oracle.',
        'raw_log': {
            'path': args.log.name,
            'bytes': len(raw),
            'sha256': hashlib.sha256(raw).hexdigest(),
            'encoding': 'UTF-16LE via KD .logopen /u',
        },
        'driver_oracle': DRIVERS,
        'breakpoints': BREAKPOINTS,
        'runtime_enter_marker_counts': noisy_counts,
        'runtime_enter_marker_policy': 'ISP START/STOP ENTER addresses are internal command-path sites and are intentionally not used to define top-level lifecycle order.',
        'cycles': cycles,
        'proven_cross_driver_start': 'ISP_START_DONE -> SENSOR_STREAM_ON_APPLY',
        'proven_cross_driver_stop': 'ISP_STOP_DONE -> SENSOR_STREAM_OFF_APPLY',
        'combined_windows_start': 'IFE start -> initial IFE/CSID configuration -> CSID start -> sensor 0x0100=0x01',
        'combined_windows_stop': 'CSID stop -> IFE stop -> CDM/remaining core stop -> sensor 0x0100=0x00',
    }
    if args.kd_script:
        out['kd_script'] = {'path': args.kd_script.name, 'bytes': args.kd_script.stat().st_size, 'sha256': sha256(args.kd_script)}
    if args.holder:
        out['winrt_holder'] = {'path': args.holder.name, 'bytes': args.holder.stat().st_size, 'sha256': sha256(args.holder), 'required_device': 'Surface Camera Front'}

    payload = json.dumps(out, indent=2) + '\n'
    if args.out:
        args.out.write_text(payload, encoding='utf-8')
    print(payload, end='')

if __name__ == '__main__':
    main()
