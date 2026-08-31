#!/usr/bin/env python3
import hashlib, json, pathlib, re, sys

D = pathlib.Path(__file__).resolve().parent
EXPECTED = {
    'AUTHORIZATION.json': '2527d991fca75c3cdf52f372f2da31308bf1ce8332dffb69b3062bedd4c58fb7',
    'RUNTIME-CAMNOC-0055-RUN.txt': '2a921758f3afe6222efb3d02986113cdeba7c799427533ea1ef96f9fda69c9b2',
    'RUNTIME-CAMNOC-0055-POST.txt': '8c40368d18c0c7283b3150b3596902bd5facae74e552c27ba290304478cd51b6',
    'RUNTIME-CAMNOC-0055-DMESG.txt': '47270ab6a5f37835063f162ac71ce7cbdcb1546d5518e2c60604a8fa0983b361',
    'RUNTIME-CAMNOC-0055-CLOCK.txt': '7ce645069ac06eb5f74b04686cfd9c81d9017f12748720da1897bba064a2351a',
    'RUNTIME-CAMNOC-0055-RTCDM-STAGES.txt': 'c1391d6a797b36d59eb9cfa4a3095969dd93b2a18d881a6d9f519f135327e616',
    'WINDOWS-E003H-CAMNOC-RATE-20260831.log': '237e5c7ba0eeef73e0b7452a61778003d3364471ec1560e2649fdd35ac2e15f3',
    'runtime-0055-analysis.json': '9fdba6fad49d493d8eafb4a97a658323e70e09b20f2a110a06457bb9496d96b0',
    'AUTHORIZATION-CONSUMED.json': 'f17427ac59e5fb07683a3a819ec0df640c7585ba821a3424d0b16d4e4d5c0a19',
    'RUNTIME-CAMNOC-0055-GOLDEN-RETURN.txt': '6f6cadf75f9782068c2b28a3190ec72fd03c83ccd0ed2483d9aee604261b3eac',
}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def need(cond, msg):
    if not cond:
        raise SystemExit('FAIL: ' + msg)

for name, expected in EXPECTED.items():
    p = D / name
    need(p.is_file(), f'missing {name}')
    need(sha(p) == expected, f'hash mismatch {name}')

run = (D/'RUNTIME-CAMNOC-0055-RUN.txt').read_text()
need(run.count('HELPER_INVOCATION_COUNT=1') == 1, 'helper count')
need('CAMERA_PROGRAMMING_DELTA=0' in run, 'camera programming delta')
need('RUN_RC=1' in run, 'run rc')

clock = (D/'RUNTIME-CAMNOC-0055-CLOCK.txt').read_text()
need('SUMMARY samples=1285 changes=4 seen_any_live=1 seen_live_300=0' in clock, 'clock summary')
live = [ln for ln in clock.splitlines() if 'branch=0x00000001' in ln]
need(live, 'no Linux live CAMNOC branch')
need(all('cfg=0x00000000' in ln for ln in live), 'Linux live CFG drift')
need(not any('cfg=0x00000203' in ln and 'branch=0x00000001' in ln for ln in clock.splitlines()), 'unexpected Linux 300 MHz state')

win = (D/'WINDOWS-E003H-CAMNOC-RATE-20260831.log').read_text(encoding='utf-16')
wlines = win.splitlines()
need(sum(ln == '===E003H_CAMNOC_LIVE===' for ln in wlines) == 1, 'Windows live marker count')
need(sum(ln == '===E003H_CAMNOC_LIVE_REPEAT===' for ln in wlines) == 1, 'Windows repeat marker count')
need(sum(ln.startswith('# adf38f8 00000000 00000203') for ln in wlines) == 2, 'Windows CFG 0x203 repeat count')
need(sum(ln.startswith('# adf3910 00000001') for ln in wlines) == 2, 'Windows branch-enable repeat count')

post = (D/'RUNTIME-CAMNOC-0055-POST.txt').read_text()
need('LINUX_CAMNOC_MATCH_WINDOWS=no' in post, 'post comparison')
need('fifo_seq=25' in post and 'faulted=0' in post, 'RT-CDM final state')
need('QC10C_OUTPUT=absent' in post, 'QC10C state')

gold = (D/'RUNTIME-CAMNOC-0055-GOLDEN-RETURN.txt').read_text()
need('sp11_entry=7.1.5-sp11-fullio-v19c' in gold, 'not Golden return')
need('saved_entry=sp11-audio-fullio-v19c' in gold, 'saved entry')
need('next_entry=\n' in gold, 'next entry not empty')
need('CAMERA_MODULES=none' in gold, 'camera modules remain loaded')

analysis = json.loads((D/'runtime-0055-analysis.json').read_text())
need(analysis['accepted'] is True and analysis['authorization_consumed'] is True, 'analysis acceptance')
need(analysis['camera_programming_delta'] == 0, 'analysis programming delta')
need(analysis['windows'] == {'live_branch':'0x00000001','live_cfg':'0x00000203','rate_hz':300000000,'repeat_identical':True}, 'Windows analysis')
need(analysis['linux']['live_branch'] == '0x00000001' and analysis['linux']['live_cfg'] == '0x00000000', 'Linux live analysis')
need(analysis['linux']['derived_parent'] == 'P_BI_TCXO' and analysis['linux']['derived_rate_hz'] == 19200000, 'Linux rate decode')
need(analysis['linux']['clock_samples'] == 1285 and analysis['linux']['seen_live_300'] is False, 'Linux sampling')
need(analysis['rtcdm'] == {'error':0,'faulted':False,'fifo_seq_final':25}, 'RT-CDM analysis')
need(analysis['qc10c_output'] == 'absent', 'QC10C analysis')

print('PASS: 0055 hashes; one helper; zero camera programming delta; Linux live branch=1 with CFG=0 (19.2 MHz); Windows live branch=1 with CFG=0x203 (300 MHz) repeated; RT-CDM seq25/faulted0; QC10C absent; Golden return verified.')
