#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / 'E003H_MIPI_ORDER_20260828.log'
OUT = ROOT / 'mipi-order-summary.json'

EXPECTED_SHA256 = '09a9b0aa11c677563dee521b14157d76eaecebe9971491a8156b82020bbef224'
EXPECTED_BYTES = 8600
EXPECTED_CYCLES = 4

M = {
    'isp_start_done': '===E003H_ISP_START_DONE===',
    'mipi_start_enter': '===E003H_MIPI_START_ENTER===',
    'mipi_start_done': '===E003H_MIPI_START_DONE===',
    'sensor_on': '===E003H_SENSOR_STREAM_ON_APPLY===',
    'isp_stop_done': '===E003H_ISP_STOP_DONE===',
    'mipi_stop_enter': '===E003H_MIPI_STOP_ENTER===',
    'mipi_stop_done': '===E003H_MIPI_STOP_DONE===',
    'sensor_off': '===E003H_SENSOR_STREAM_OFF_APPLY===',
}
REVERSE = {v: k for k, v in M.items()}

raw = RAW.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
if len(raw) != EXPECTED_BYTES:
    raise SystemExit(f'raw byte count mismatch: {len(raw)} != {EXPECTED_BYTES}')
if sha != EXPECTED_SHA256:
    raise SystemExit(f'raw sha256 mismatch: {sha} != {EXPECTED_SHA256}')

text = raw.decode('utf-16')
runtime = []
for line_no, line in enumerate(text.splitlines(), 1):
    key = REVERSE.get(line.strip())
    if key:
        runtime.append((line_no, key))

if len(runtime) != EXPECTED_CYCLES * 8:
    raise SystemExit(f'expected {EXPECTED_CYCLES * 8} runtime markers, got {len(runtime)}')

cycles = []
for n in range(EXPECTED_CYCLES):
    chunk = runtime[n * 8:(n + 1) * 8]
    keys = [k for _, k in chunk]
    lines = {k: ln for ln, k in chunk}
    if len(lines) != 8:
        raise SystemExit(f'cycle {n + 1}: duplicate/missing markers: {keys}')

    required_start = [
        'isp_start_done',
        'mipi_start_enter',
        'mipi_start_done',
        'sensor_on',
        'isp_stop_done',
    ]
    if keys[:5] != required_start:
        raise SystemExit(f'cycle {n + 1}: start/ISP boundary mismatch: {keys[:5]}')

    # Windows demonstrates no stable total order between SENSOR_OFF and the
    # MIPI stop interval. Enforce only the dependencies reproduced in all runs.
    if not (lines['isp_stop_done'] < lines['sensor_off']):
        raise SystemExit(f'cycle {n + 1}: sensor-off preceded ISP stop completion')
    if not (lines['isp_stop_done'] < lines['mipi_stop_enter'] < lines['mipi_stop_done']):
        raise SystemExit(f'cycle {n + 1}: invalid MIPI stop dependency')

    cycles.append({
        'cycle': n + 1,
        'order': keys,
        'lines': lines,
        'stop_tail': keys[5:],
    })

stop_tails = [c['stop_tail'] for c in cycles]
observed_tail_forms = []
for tail in stop_tails:
    if tail not in observed_tail_forms:
        observed_tail_forms.append(tail)

summary = {
    'status': 'PASS',
    'policy': 'Same-machine Windows on this exact SP11 is the behavioral oracle.',
    'raw_log': {
        'path': RAW.name,
        'bytes': len(raw),
        'sha256': sha,
        'encoding': 'UTF-16LE via KD .logopen /u',
    },
    'driver_oracle': {
        'qccamisp8380.sys': {
            'sha256': '64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c',
            'base': '0xfffff8034aaa0000',
        },
        'qccammipicsi8380.sys': {
            'sha256': '033f5b1431ad4c76a12ac3b7f0a5be42e460a03bcff40d249511b3034786d407',
            'base': '0xfffff803488e0000',
        },
        'surfacecamfrontsensor8380.sys': {
            'sha256': '80a8e4a1ef8f0dacfbc2e8c6919cb269993057ffd3133c2ef7016ff742e46f03',
            'base': '0xfffff8034af30000',
        },
    },
    'mipi_static_rvas': {
        'start_enter': '0x2068',
        'start_done': '0x2398',
        'stop_enter': '0x1e70',
        'stop_done': '0x2024',
    },
    'cycles': cycles,
    'proven_start_total_order': [
        'isp_start_done',
        'mipi_start_enter',
        'mipi_start_done',
        'sensor_on',
    ],
    'proven_stop_partial_order': {
        'isp_stop_done_before_sensor_off': True,
        'isp_stop_done_before_mipi_stop_enter': True,
        'mipi_stop_enter_before_mipi_stop_done': True,
        'sensor_off_vs_mipi_stop': 'unordered by Windows; observed before enter, between enter/done, and after done',
    },
    'observed_stop_tail_forms': observed_tail_forms,
    'linux_0010_consequence': 'CSID -> VFE -> CSIPHY -> sensor is an observed-valid serialization of the Windows stop partial order; do not claim Windows requires CSIPHY before sensor.',
}
OUT.write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary, indent=2))
