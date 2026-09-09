#!/usr/bin/env python3
import ctypes
import importlib.util
import json
import os
import random
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
REPO = HERE.parents[3]
CT = BASE / 'ct-native-aec-bhist-bank4-replay'
CR = BASE / 'cr-native-aec-effective-analyzer-producer'
CP = BASE / 'cp-native-aec-self-contained-cold-init'
CF = BASE / 'cf-native-aec-final-exposure-si'
CE = BASE / 'ce-native-aec-final-target-producer'
CC = BASE / 'cc-native-aec-adrc-darkboost-tail'
BY = BASE / 'by-native-aec-method11-point-aggregation'
CG = BASE / 'cg-native-aec-qword-convergence-input'
CH = BASE / 'ch-native-aec-t681-preview-arbitration'
BK = BASE / 'bk-native-aec-history-state'
BJ = BASE / 'bj-native-aec-log103-coordinate'
AB = BASE / 'ab-clean-lux-reconstruction'
PARENT = '9a3b9fa'

STATS_BYTES = 64 + 0x51000
AEC_BYTES = 0x14000
BHIST_OFF = 64 + AEC_BYTES
BHIST_BYTES = 0x1000
PIXELS = 2_073_600


def fresh(rel, script, marker):
    p = BASE / rel / script
    cp = subprocess.run([sys.executable, str(p)], cwd=p.parent, text=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if cp.returncode:
        raise AssertionError(f'{rel} failed\n{cp.stdout}\n{cp.stderr}')
    assert marker in cp.stdout, (rel, marker, cp.stdout[-4000:])


def fbits(x):
    return struct.unpack('<I', struct.pack('<f', float(x)))[0]


def bytesof(x):
    return ctypes.string_at(ctypes.byref(x), ctypes.sizeof(x))


def make_aec_uniform(sum_value):
    raw = bytearray(AEC_BYTES)
    for i in range(1024):
        o = i * 0x50
        for qoff in (0x00, 0x08, 0x10, 0x18):
            struct.pack_into('<Q', raw, o + qoff, int(sum_value))
        for coff in (0x06, 0x1e, 0x0e, 0x16):
            struct.pack_into('<H', raw, o + coff, 1980)
    return raw


def make_aec_random(seed):
    rng = random.Random(seed)
    raw = bytearray(AEC_BYTES)
    max_sum = 1980 * ((1 << 18) - 1)
    for i in range(1024):
        o = i * 0x50
        values = [rng.randrange(1_000_000, max_sum) for _ in range(4)]
        for qoff, value in zip((0x00, 0x08, 0x10, 0x18), values):
            struct.pack_into('<Q', raw, o + qoff, value)
        for coff in (0x06, 0x1e, 0x0e, 0x16):
            struct.pack_into('<H', raw, o + coff, 1980)
    return raw


def make_stats(generation, source_seq, slot, sum_value, peak=700):
    data = bytearray(STATS_BYTES)
    struct.pack_into('<IHHQIII', data, 0, 0x54534133, 1, 64,
                     generation, source_seq, slot, 0)
    struct.pack_into('<IIIIII', data, 28, 0x14000, 0x14000, 0x1000,
                     0x15000, 0x3c000, 1)
    data[64:64 + AEC_BYTES] = make_aec_uniform(sum_value)
    if peak is not None:
        assert 0 <= peak < 1024
        struct.pack_into('<I', data, BHIST_OFF + peak * 4, PIXELS)
    return data


# CU is a child of the accepted CT checkpoint. Parent fresh runs deliberately
# happen before local compilation so stale inherited evidence cannot be hidden.
assert subprocess.run(['git', 'merge-base', '--is-ancestor', PARENT, 'HEAD'],
                      cwd=REPO).returncode == 0
fresh('ct-native-aec-bhist-bank4-replay', 'verify-ct.py', 'CT_VERIFY=PASS')
fresh('cp-native-aec-self-contained-cold-init', 'verify-cp.py', 'CP_VERIFY=PASS')

# AB is the accepted Windows-backed FrameLuma reference. Use deterministic
# generated inputs rather than local-only raw fixture files.
spec = importlib.util.spec_from_file_location('e003i_ab_luma_cu', AB / 'replay-measured-luma.py')
ab = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = ab
spec.loader.exec_module(ab)
abr = json.loads((AB / 'RESULT.json').read_text())
assert abr['measured_luma']['status'] == 'PASS_LIVE_BIT_EXACT'
assert abr['measured_luma']['frame_luma_descriptor_mask'] == '0x00000010'
assert abr['measured_luma']['selected_cells_per_output_bin'] == 2

# Source-level seams added for CU: CR accepts exact startup zero B7/B8 and CP
# publishes a non-mutating copy accessor around its existing selector.
crc = (CR / 'native-effective-analyzers.c').read_text()
assert 'in->sat_prev_high_pctl_luma < 0.0f' in crc
assert 'in->dark_prev_low_pctl_luma < 0.0f' in crc
cph = (CP / 'native-aec-request-loop.h').read_text()
cpc = (CP / 'native-aec-request-loop.c').read_text()
assert 'e003i_request_loop_get_history_offset' in cph
assert '*out = *selected;' in cpc

with tempfile.TemporaryDirectory(prefix='e003i-cu-') as tds:
    td = Path(tds)
    libp = td / 'libe003i-cu.so'
    incs = [HERE, CR, CT, CP, CF, CE, CC, BY, CG, CH, BK, BJ]
    srcs = [
        HERE / 'native-raw-aec-loop.c', HERE / 'native-stats3a.c',
        CR / 'native-effective-analyzers.c', CT / 'native-bhist-bank4.c',
        CP / 'native-aec-request-loop.c', CF / 'native-final-exposure.c',
        CE / 'native-final-target.c', CC / 'native-aec-tail.c',
        BY / 'native-target-aggregate.c', CG / 'native-convergence.c',
        CH / 'native-t681.c', BK / 'native-aec-state.c', BJ / 'native-log103.c',
    ]
    cmd = ['cc', '-shared', '-fPIC', '-O2', '-std=c11', '-Wall', '-Wextra',
           '-Werror', '-fno-fast-math', '-ffp-contract=off']
    for x in incs:
        cmd += ['-I', str(x)]
    cmd += [str(x) for x in srcs] + ['-lm', '-o', str(libp)]
    subprocess.run(cmd, check=True)
    lib = ctypes.CDLL(str(libp))

    class Cand(ctypes.Structure):
        _fields_ = [('value', ctypes.c_float), ('confidence', ctypes.c_float)]

    class TargetIn(ctypes.Structure):
        _fields_ = [
            ('lux_index', ctypes.c_float), ('frame', Cand), ('sat_prev', Cand),
            ('dark_prev', Cand), ('brighten', Cand), ('extreme_color', Cand),
            ('illuminance', Cand), ('short_sat_prev', Cand), ('long_dark_prev', Cand)]

    class Tail(ctypes.Structure):
        _fields_ = [
            ('adrc_lux_face_cap', ctypes.c_float), ('adj_ratio_short', ctypes.c_float),
            ('adrc_gain', ctypes.c_float), ('short_adj_ratio', ctypes.c_float),
            ('drc_gain_remainder', ctypes.c_float), ('adj_ratio_long', ctypes.c_float),
            ('dark_boost_gain', ctypes.c_float), ('long_adj_ratio', ctypes.c_float)]

    class TargetOut(ctypes.Structure):
        _fields_ = [
            ('safe_target', ctypes.c_float), ('safe_adj_ratio', ctypes.c_float),
            ('short_target', ctypes.c_float), ('long_target', ctypes.c_float), ('tail', Tail)]

    class FinalOut(ctypes.Structure):
        _fields_ = [('targets', TargetOut), ('short_exposure', ctypes.c_uint64),
                    ('long_exposure', ctypes.c_uint64), ('safe_exposure', ctypes.c_uint64)]

    class ConvOut(ctypes.Structure):
        _fields_ = [
            ('basic_safe_log', ctypes.c_double), ('post_stretch_log', ctypes.c_double * 7),
            ('final_log', ctypes.c_double * 7), ('linear', ctypes.c_uint64 * 7),
            ('pred_gain', ctypes.c_float), ('short_stretch', ctypes.c_float),
            ('safe_stretch', ctypes.c_float), ('stretch_ratio', ctypes.c_float),
            ('drc_ratio', ctypes.c_float), ('basic_direction_ok', ctypes.c_uint32),
            ('drc_branch', ctypes.c_uint32)]

    class ArbOut(ctypes.Structure):
        _fields_ = [('gain', ctypes.c_float), ('exposure_time_ns', ctypes.c_uint64),
                    ('correction', ctypes.c_float), ('retained_exposure', ctypes.c_uint64),
                    ('upper_knee', ctypes.c_uint32)]

    class HistEntry(ctypes.Structure):
        _fields_ = [('frame_id', ctypes.c_uint64), ('short_exposure', ctypes.c_uint64),
                    ('long_exposure', ctypes.c_uint64), ('safe_exposure', ctypes.c_uint64),
                    ('s1_exposure', ctypes.c_uint64), ('pred_gain', ctypes.c_float),
                    ('valid', ctypes.c_uint8)]

    class State(ctypes.Structure):
        _fields_ = [('lux_trigger', ctypes.c_float), ('algorithm001_alpha', ctypes.c_float),
                    ('next_frame_id', ctypes.c_uint64), ('start_history', HistEntry),
                    ('history', HistEntry * 16)]

    class Remaining(ctypes.Structure):
        _fields_ = [('sat_prev', Cand), ('dark_prev', Cand), ('brighten', Cand),
                    ('extreme_color', Cand), ('illuminance', Cand),
                    ('short_sat_prev', Cand), ('long_dark_prev', Cand)]

    class RequestIn(ctypes.Structure):
        _fields_ = [('frame_id', ctypes.c_uint64), ('measured_luma', ctypes.c_float),
                    ('analyzers', Remaining)]

    class RequestOut(ctypes.Structure):
        _fields_ = [
            ('lux_trigger_in', ctypes.c_float), ('frame_target', ctypes.c_float),
            ('frame_candidate', Cand), ('history_reference_log103', ctypes.c_float),
            ('next_lux_trigger', ctypes.c_float), ('target_publication', FinalOut),
            ('convergence', ConvOut), ('short_arbitration', ArbOut),
            ('long_arbitration', ArbOut), ('safe_arbitration', ArbOut),
            ('s1_arbitration', ArbOut)]

    class BHistHistory(ctypes.Structure):
        _fields_ = [('safe_exposure', ctypes.c_uint64), ('s1_exposure', ctypes.c_uint64),
                    ('pred_gain', ctypes.c_float)]

    class BHistOut(ctypes.Structure):
        _fields_ = [('b6', ctypes.c_float), ('b7', ctypes.c_float),
                    ('b8', ctypes.c_float), ('b19', ctypes.c_float)]

    class AnalyzerRaw(ctypes.Structure):
        _fields_ = [
            ('lux_index', ctypes.c_float), ('frame_luma', ctypes.c_float),
            ('frame_target', ctypes.c_float), ('delayed_short_exposure', ctypes.c_uint64),
            ('saturate_stats_ratio', ctypes.c_float),
            ('sat_prev_high_pctl_luma', ctypes.c_float),
            ('dark_prev_low_pctl_luma', ctypes.c_float),
            ('short_sat_prev_high_pctl_luma', ctypes.c_float)]

    class StatsView(ctypes.Structure):
        _fields_ = [('generation', ctypes.c_uint64), ('source_seq', ctypes.c_uint32),
                    ('slot', ctypes.c_uint32), ('aec_raw', ctypes.c_void_p),
                    ('bhist_raw', ctypes.POINTER(ctypes.c_uint32)),
                    ('awb_raw', ctypes.c_void_p)]

    class RawIn(ctypes.Structure):
        _fields_ = [('frame_id', ctypes.c_uint64), ('stats3a', ctypes.c_void_p),
                    ('stats3a_bytes', ctypes.c_size_t)]

    class RawOut(ctypes.Structure):
        _fields_ = [('stats_generation', ctypes.c_uint64),
                    ('stats_source_seq', ctypes.c_uint32), ('stats_slot', ctypes.c_uint32),
                    ('measured_luma', ctypes.c_float), ('bank4', BHistOut),
                    ('effective_target', TargetIn), ('request', RequestOut)]

    lib.e003i_stats3a_open.argtypes = [ctypes.c_void_p, ctypes.c_size_t,
                                       ctypes.POINTER(StatsView)]
    lib.e003i_stats3a_open.restype = ctypes.c_int
    lib.e003i_aecbe_frame_luma.argtypes = [ctypes.c_void_p,
                                           ctypes.POINTER(ctypes.c_float)]
    lib.e003i_aecbe_frame_luma.restype = ctypes.c_int
    lib.e003i_request_loop_init.argtypes = [ctypes.POINTER(State)]
    lib.e003i_request_loop_init.restype = ctypes.c_int
    lib.e003i_request_loop_get_history_offset.argtypes = [
        ctypes.POINTER(State), ctypes.c_uint64, ctypes.c_uint,
        ctypes.POINTER(HistEntry)]
    lib.e003i_request_loop_get_history_offset.restype = ctypes.c_int
    lib.e003i_bhist_replay_bank4.argtypes = [
        ctypes.POINTER(ctypes.c_uint32), ctypes.c_float,
        ctypes.POINTER(BHistHistory), ctypes.POINTER(BHistOut)]
    lib.e003i_bhist_replay_bank4.restype = ctypes.c_int
    lib.e003i_framesa_target_low.argtypes = [ctypes.c_float]
    lib.e003i_framesa_target_low.restype = ctypes.c_float
    lib.e003i_aec_default_effective_analyzers.argtypes = [
        ctypes.POINTER(AnalyzerRaw), ctypes.POINTER(TargetIn)]
    lib.e003i_aec_default_effective_analyzers.restype = ctypes.c_int
    lib.e003i_request_loop_process.argtypes = [
        ctypes.POINTER(State), ctypes.POINTER(RequestIn), ctypes.POINTER(RequestOut)]
    lib.e003i_request_loop_process.restype = ctypes.c_int
    lib.e003i_raw_request_loop_process.argtypes = [
        ctypes.POINTER(State), ctypes.POINTER(RawIn), ctypes.POINTER(RawOut)]
    lib.e003i_raw_request_loop_process.restype = ctypes.c_int

    # Native AEC_BE implementation must match the already-Windows-proven AB
    # Python reference for generated inputs, including nonuniform grids.
    luma_cases = [make_aec_uniform(x) for x in
                  (1_000_000, 81_100_796, 101_375_995, 400_000_000)]
    luma_cases += [make_aec_random(0xC000 + i) for i in range(8)]
    for raw in luma_cases:
        expected = ab.replay(bytes(raw))
        buf = ctypes.create_string_buffer(bytes(raw))
        got = ctypes.c_float()
        assert lib.e003i_aecbe_frame_luma(buf, ctypes.byref(got)) == 0
        assert fbits(got.value) == fbits(expected), (hex(fbits(got.value)), hex(fbits(expected)))

    # STATS3A producer envelope/parser guards are exact and independent of AEC.
    good = make_stats(1, 1, 0, 101_375_995, 700)
    gb = ctypes.create_string_buffer(bytes(good)); view = StatsView()
    assert lib.e003i_stats3a_open(gb, len(good), ctypes.byref(view)) == 0
    assert (view.generation, view.source_seq, view.slot) == (1, 1, 0)
    assert lib.e003i_stats3a_open(gb, len(good) - 1, ctypes.byref(view)) == -1
    bad = bytearray(good); struct.pack_into('<I', bad, 0, 0)
    bb = ctypes.create_string_buffer(bytes(bad))
    assert lib.e003i_stats3a_open(bb, len(bad), ctypes.byref(view)) == -2
    bad = bytearray(good); struct.pack_into('<I', bad, 48, 0)
    bb = ctypes.create_string_buffer(bytes(bad))
    assert lib.e003i_stats3a_open(bb, len(bad), ctypes.byref(view)) == -3
    bad = bytearray(good); struct.pack_into('<Q', bad, 8, 0)
    bb = ctypes.create_string_buffer(bytes(bad))
    assert lib.e003i_stats3a_open(bb, len(bad), ctypes.byref(view)) == -4

    # Wrapper-vs-independent composition over four deterministic generated
    # frames. The histogram peak at axis bin 700 keeps this synthetic sequence
    # inside T681; it is not claimed to be a Windows captured scene.
    sums = [101_375_995, 93_265_916, 91_200_000, 90_000_000]
    expected = [
        (0x42480000, (0x00000000,0x00000000,0x00000000,0x423c8081),
         0x4365b24a,0x4365b24a,0x3f800000,(197890639,211553009,197890639)),
        (0x42380000, (0x00000000,0x423c807f,0x423c8080,0x423c8081),
         0x4365b24a,0x43926342,0x3f800000,(315897325,347299339,315897325)),
        (0x4233ecaa, (0x00000000,0x423c807f,0x423c8080,0x423c8080),
         0x43926342,0x4392c441,0x3f800000,(504230670,563178231,504230670)),
        (0x42318ea5, (0x00000000,0x423c807f,0x423c8080,0x423c8080),
         0x4392c441,0x4392fd9b,0x3f800000,(723655354,820289070,723655354)),
    ]
    wrapped_state = State(); step_state = State()
    assert lib.e003i_request_loop_init(ctypes.byref(wrapped_state)) == 0
    assert lib.e003i_request_loop_init(ctypes.byref(step_state)) == 0

    composed = []
    for frame_id, sum_value in enumerate(sums):
        data = make_stats(frame_id + 1, frame_id + 1, frame_id & 1,
                          sum_value, 700)
        buf = ctypes.create_string_buffer(bytes(data))
        rin = RawIn(frame_id, ctypes.cast(buf, ctypes.c_void_p), len(data))
        wout = RawOut()
        assert lib.e003i_raw_request_loop_process(
            ctypes.byref(wrapped_state), ctypes.byref(rin), ctypes.byref(wout)) == 0

        # Independent same-library steps, deliberately outside the wrapper.
        sv = StatsView()
        assert lib.e003i_stats3a_open(buf, len(data), ctypes.byref(sv)) == 0
        luma = ctypes.c_float()
        assert lib.e003i_aecbe_frame_luma(sv.aec_raw, ctypes.byref(luma)) == 0
        delayed = HistEntry()
        before = bytesof(step_state)
        assert lib.e003i_request_loop_get_history_offset(
            ctypes.byref(step_state), frame_id, 3, ctypes.byref(delayed)) == 0
        assert bytesof(step_state) == before
        bh = BHistHistory(delayed.safe_exposure, delayed.s1_exposure,
                          delayed.pred_gain)
        bout = BHistOut()
        assert lib.e003i_bhist_replay_bank4(
            sv.bhist_raw, step_state.lux_trigger, ctypes.byref(bh),
            ctypes.byref(bout)) == 0
        frame_target = lib.e003i_framesa_target_low(step_state.lux_trigger)
        ai = AnalyzerRaw(step_state.lux_trigger, luma.value, frame_target,
                         delayed.short_exposure, bout.b6, bout.b7, bout.b8, bout.b19)
        eff = TargetIn()
        assert lib.e003i_aec_default_effective_analyzers(
            ctypes.byref(ai), ctypes.byref(eff)) == 0
        step_in = RequestIn(); step_in.frame_id = frame_id
        step_in.measured_luma = luma.value
        for name in ('sat_prev','dark_prev','brighten','extreme_color','illuminance',
                     'short_sat_prev','long_dark_prev'):
            setattr(step_in.analyzers, name, getattr(eff, name))
        step_out = RequestOut()
        assert lib.e003i_request_loop_process(
            ctypes.byref(step_state), ctypes.byref(step_in), ctypes.byref(step_out)) == 0

        assert fbits(wout.measured_luma) == fbits(luma.value)
        assert bytesof(wout.bank4) == bytesof(bout)
        assert bytesof(wout.effective_target) == bytesof(eff)
        assert bytesof(wout.request) == bytesof(step_out)
        assert bytesof(wrapped_state) == bytesof(step_state)
        assert bytesof(wout.request.frame_candidate) == bytesof(wout.effective_target.frame)
        assert (wout.stats_generation, wout.stats_source_seq, wout.stats_slot) == (
            frame_id + 1, frame_id + 1, frame_id & 1)

        exp = expected[frame_id]
        got_b = tuple(fbits(getattr(wout.bank4, n)) for n in ('b6','b7','b8','b19'))
        got_ret = (wout.request.short_arbitration.retained_exposure,
                   wout.request.safe_arbitration.retained_exposure,
                   wout.request.s1_arbitration.retained_exposure)
        assert fbits(wout.measured_luma) == exp[0]
        assert got_b == exp[1]
        assert fbits(wout.request.lux_trigger_in) == exp[2]
        assert fbits(wout.request.next_lux_trigger) == exp[3]
        assert fbits(wout.request.convergence.pred_gain) == exp[4]
        assert got_ret == exp[5]
        composed.append({
            'frame': frame_id, 'generation': frame_id + 1,
            'luma_bits': f'0x{exp[0]:08x}',
            'bank4_bits': [f'0x{x:08x}' for x in exp[1]],
            'lux_in_bits': f'0x{exp[2]:08x}',
            'next_lux_bits': f'0x{exp[3]:08x}',
            'pred_gain_bits': f'0x{exp[4]:08x}',
            'retained_short_safe_s1': list(exp[5]),
        })

    # Error paths before CP must not mutate AEC state.
    def assert_reject(data, frame_id, expected_rc, size=None):
        state = State(); assert lib.e003i_request_loop_init(ctypes.byref(state)) == 0
        before = bytesof(state)
        buf = ctypes.create_string_buffer(bytes(data))
        ri = RawIn(frame_id, ctypes.cast(buf, ctypes.c_void_p),
                   len(data) if size is None else size)
        ro = RawOut()
        assert lib.e003i_raw_request_loop_process(
            ctypes.byref(state), ctypes.byref(ri), ctypes.byref(ro)) == expected_rc
        assert bytesof(state) == before

    assert_reject(good, 1, -2)
    assert_reject(good, 0, -11, len(good) - 1)
    wrong_generation = make_stats(2, 1, 0, 101_375_995, 700)
    assert_reject(wrong_generation, 0, -14)
    bad_counts = bytearray(good); struct.pack_into('<H', bad_counts, 64 + 0x06, 1979)
    assert_reject(bad_counts, 0, -22)
    empty_hist = make_stats(1, 1, 0, 101_375_995, None)
    assert_reject(empty_hist, 0, -51)

result = {
    'schema': 'sp11-e003i-cu-native-aec-raw-stats-request-loop-v1',
    'status': 'PASS',
    'parent_ct_commit': PARENT,
    'pipeline': [
        'generation-tagged STATS3A envelope',
        'AEC_BE -> FrameLumaBE16x16 -> FrameSA measured luma',
        'BHist -> CT Bank4 {6,7,8,19}',
        'CR effective analyzers',
        'CP self-contained request recurrence',
    ],
    'stats3a': {
        'bytes': STATS_BYTES, 'header_bytes': 64, 'aec_bytes': AEC_BYTES,
        'bhist_bytes': BHIST_BYTES, 'awb_bytes': 0x3c000,
        'cold_generation_law': 'generation == source_seq == frame_id + 1',
        'slot_range': [0,1],
    },
    'frame_luma': {
        'reference': 'AB Windows-backed replay-measured-luma.py',
        'generated_differential_cases': len(luma_cases),
        'bit_exact': True,
    },
    'cold_start': {
        'ct_bank4_7_8_exact_zero_supported_by_cr': True,
        'cp_history_accessor_non_mutating': True,
    },
    'composition': {
        'generated_frames': len(composed),
        'wrapper_matches_independent_steps_byte_exact': True,
        'frames': composed,
    },
    'failure_atomicity': {
        'state_unchanged_on_wrong_frame': True,
        'state_unchanged_on_bad_size': True,
        'state_unchanged_on_generation_mismatch': True,
        'state_unchanged_on_bad_aec_counts': True,
        'state_unchanged_on_empty_bhist_cr_rejection': True,
    },
    'safety': {
        'linux_camera_runtime': False,
        'sensor_control_writes': False,
        'cq_invoked': False,
        'fixture_type': 'deterministic generated STATS3A only',
    },
    'scope_limit': 'offline raw-stat to CP request recurrence; no CQ/IMX681 programming',
}
(HERE / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
print('PARENT_CT_COMMIT='+PARENT)
print(f'STATS3A_BYTES={STATS_BYTES}')
print(f'FRAME_LUMA_DIFFERENTIAL={len(luma_cases)} bit-exact-to-AB-reference')
print('COLD_START_BANK4_7_8_ZERO=CR_ACCEPTED')
print('CP_HISTORY_ACCESSOR=READ_ONLY')
print(f'COMPOSED_FRAMES={len(composed)} wrapper-vs-independent-byte-exact')
print('FAILURE_ATOMICITY=PASS')
print('SENSOR_CONTROL_WRITES=0')
print('CU_VERIFY=PASS')
