#!/usr/bin/env python3
import hashlib,json,pathlib,re,subprocess
D=pathlib.Path(__file__).resolve().parent
R=D.parents[2]
EXPECTED={
'RUNTIME-CAMNOC300-0056-RUN.txt':'1b185e5b12cd505d09d6820c34d4f5d0e08145cb0ef389d76f7598e12565bf99',
'RUNTIME-CAMNOC300-0056-POST.txt':'758fd6fb8ef625ca28adf4159826560c938eae43497b0be22164f0beb434ac15',
'RUNTIME-CAMNOC300-0056-DMESG.txt':'fbe5bcb49a2be46b364a4615490fa0a282b056212c253c3277f6488bf4c271a9',
'RUNTIME-CAMNOC300-0056-CLOCK.txt':'234fb707871309b6d0145bd148b52bbdeeaeeff64fb024dec940e10974c47cf5',
'RUNTIME-CAMNOC300-0056-RTCDM-STAGES.txt':'2d25141a60289ed071e78ae24cfa1f3e07d67011284fe0985ce158a1274c32b9',
'AUTHORIZATION.json':'1dfdd8e25f65c797409cfd566d83cc751e42140d2d3d80eebf3aed82274fcb26',
'runtime-0056-analysis.json':'6a1d58bb38a6855c06b8d6d06f7ba3fc9acc89790914f75ec5159dd8a507848d',
'AUTHORIZATION-CONSUMED.json':'774bd8e8aaf3415bc395a401629e8dde474c449369416ac1d49a79d6c1383909',
'RUNTIME-CAMNOC300-0056-GOLDEN-RETURN.txt':'d16dda05593059d16c1865f0119bc08b7f30b5e44e200a1ca984dda03021a603',
}
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def need(c,m):
    if not c: raise SystemExit('FAIL: '+m)
for n,h in EXPECTED.items(): need((D/n).is_file() and sha(D/n)==h,'hash '+n)
run=(D/'RUNTIME-CAMNOC300-0056-RUN.txt').read_text(); post=(D/'RUNTIME-CAMNOC300-0056-POST.txt').read_text(); clock=(D/'RUNTIME-CAMNOC300-0056-CLOCK.txt').read_text(); dm=(D/'RUNTIME-CAMNOC300-0056-DMESG.txt').read_text(); a=json.load(open(D/'runtime-0056-analysis.json'))
need(run.count('HELPER_INVOCATION_COUNT=1')==1 and 'CAMERA_PROGRAMMING_DELTA=CAMNOC_RT_CCF_300MHZ_ONLY' in run,'execution contract')
need('LINUX_CAMNOC_MATCH_WINDOWS=yes' in post,'CAMNOC match')
need('SUMMARY samples=1375 changes=6 seen_any_live=1 seen_live_300=1' in clock,'clock summary')
need(any('cfg=0x00000203 branch=0x00000001 rate_hz=300000000' in x for x in clock.splitlines()),'physical 300 MHz state')
need('VFE1 epoch0-timeout top=00000000/00030003 mask=0007f051/00000000 bus=00000000/00000000 bmask=d0000000/00000000' in dm,'VFE timeout')
need('line-error=00000000/00000000/00000000' in dm and 'measure=0000001f/08700f00' in dm,'healthy CSID')
need('QC10C_OUTPUT=absent' in post and 'fifo_seq=25' in post and 'faulted=0' in post,'downstream result')
need(a['accepted'] and a['authorization_consumed'] and a['camnoc']['physical_parity_reached'],'analysis acceptance')
need(a['classification']['camnoc_underclock_was_real_parity_bug'] and not a['classification']['camnoc_underclock_causal_for_vfe1_stall'],'causal classification')
g=(D/'RUNTIME-CAMNOC300-0056-GOLDEN-RETURN.txt').read_text(); need('sp11_entry=7.1.5-sp11-fullio-v19c' in g and 'saved_entry=sp11-audio-fullio-v19c' in g and 'CAMERA_MODULES=none' in g,'Golden return')
print('PASS: 0056 one helper; physical CAMNOC Windows parity 300 MHz reached; CSID healthy 3840x2160; RT-CDM fifo25/no fault; VFE1 raw Epoch0 and QC10C still absent; CAMNOC underclock real but noncausal; Golden return verified.')
