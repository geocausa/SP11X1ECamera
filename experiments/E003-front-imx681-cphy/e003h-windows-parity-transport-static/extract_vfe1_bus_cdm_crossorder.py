#!/usr/bin/env python3
import argparse, hashlib, json, re
from pathlib import Path

RAW_SHA = 'c32acebd61e0b2364450035c2b9e383a86e0ad355387760c149fb0e113342963'
RAW_BYTES = 47032
BUS_SHA = '89ddee9746d54927f8624a5267f5726d38ee8b02190ae60b9525a4b783206363'
RTCDM_SHA = '489f47f45465603260a06f8aa2083cc417fff816478be9b6c8f68233bb0be927'
LIFECYCLE_SHA = '0414879944824585eb3d4e6a8ce6384a0396bb37571c9aaa68d5de9074fd6301'


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha_path(path):
    return sha_bytes(Path(path).read_bytes())


def die(msg):
    raise SystemExit('FAIL: ' + msg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--raw', type=Path, required=True)
    ap.add_argument('--bus-order', type=Path, required=True)
    ap.add_argument('--rtcdm-order', type=Path, required=True)
    ap.add_argument('--lifecycle', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path)
    a = ap.parse_args()

    raw = a.raw.read_bytes()
    if len(raw) != RAW_BYTES or sha_bytes(raw) != RAW_SHA:
        die('raw cross-order log identity drift')
    for path, expected, label in (
        (a.bus_order, BUS_SHA, 'BUS order'),
        (a.rtcdm_order, RTCDM_SHA, 'RT-CDM order'),
        (a.lifecycle, LIFECYCLE_SHA, 'lifecycle'),
    ):
        if sha_path(path) != expected:
            die(label + ' oracle identity drift')

    bus = json.loads(a.bus_order.read_text())
    rt = json.loads(a.rtcdm_order.read_text())
    life = json.loads(a.lifecycle.read_text())
    if not bus.get('accepted') or not rt.get('accepted') or life.get('status') != 'PASS':
        die('upstream oracle not accepted')

    text = raw.decode('utf-16')
    events = [line.strip() for line in text.splitlines() if line.startswith('EV ')]
    try:
        end = events.index('EV ISP_START_DONE') + 1
    except ValueError:
        die('ISP_START_DONE missing')
    pre = events[:end]

    expected = (
        ['EV IFE803 p=0', 'EV IFE803 p=1'] +
        ['EV BUS_CONFIG'] * 9 +
        ['EV BUS_SET'] * 8 +
        ['EV ADDR'] * 9 +
        ['EV IFE803 p=2', 'EV IFE803 p=3', 'EV ISP_START_DONE']
    )
    if pre != expected:
        die('pre-start cross-order drift: ' + repr(pre))

    if rt['device_start']['manager_order'] != [
        'CDM start command 0x804',
        'IFE start command 0x804',
        'initial packet command 0x803 to IFE/SFE/CSID resources',
        'CSID start command 0x804',
    ]:
        die('manager start-order drift')
    if bus['session_order'] != 'BUS static config -> BUS enable -> ISP_START_DONE -> BUS disable':
        die('BUS session-order drift')
    if life['proven_cross_driver_start'] != 'ISP_START_DONE -> SENSOR_STREAM_ON_APPLY':
        die('sensor start placement drift')

    out = {
        'schema': 'sp11-e003h-vfe1-bus-cdm-crossorder-v1',
        'accepted': True,
        'raw': {'bytes': len(raw), 'sha256': sha_bytes(raw)},
        'upstream_oracles': {
            'bus_order_sha256': BUS_SHA,
            'rtcdm_order_sha256': RTCDM_SHA,
            'lifecycle_sha256': LIFECYCLE_SHA,
        },
        'pre_start_events': pre,
        'counts': {
            'ife_803_before_bus': 2,
            'bus_static_config': 9,
            'bus_enable': 8,
            'initial_dynamic_address_writes': 9,
            'ife_803_after_bus': 2,
        },
        'cross_layer_order': [
            'CDM_START',
            'IFE_START',
            'IFE803_PACKET0',
            'IFE803_PACKET1',
            'VFE1_BUS_STATIC_CONFIG',
            'VFE1_BUS_ENABLE',
            'VFE1_INITIAL_DYNAMIC_ADDRESSES',
            'IFE803_PACKET2',
            'IFE803_PACKET3',
            'CSID_START',
            'ISP_START_DONE',
        ],
        'outside_orchestrator_after_start_done': [
            'MIPI/CSIPHY start',
            'IMX681 stream-on 0x0100=1',
        ],
        'linux_consequence': {
            'packet_split': 'the four startup IFE 0x803 packets are not one uninterrupted block; VFE1 BUS prepare lands between packets 1 and 2',
            'bus_prepare': 'static config -> enable -> initial address set remains one ordered phase between packet1 and packet2',
            'sensor_gate': 'front sensor/MIPI start remains outside the static host orchestrator and after ISP_START_DONE',
            'runtime': 'no Linux runtime authorization follows from this oracle',
        },
    }
    txt = json.dumps(out, indent=2, sort_keys=True) + '\n'
    if a.output:
        a.output.write_text(txt)
    else:
        print(txt, end='')
    print('PASS: packet0/1 -> BUS config/enable/initial addresses -> packet2/3 is exact before ISP_START_DONE')


if __name__ == '__main__':
    main()
