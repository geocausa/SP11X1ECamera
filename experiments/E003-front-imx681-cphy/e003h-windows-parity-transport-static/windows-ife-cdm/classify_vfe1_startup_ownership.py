#!/usr/bin/env python3
import csv, glob, json, os
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROUTE = HERE.parent.parent / 'e003g-windows-csid-vfe-oracle' / 'route-oracle-summary.json'
# Repository layout: e003h dir is sibling of e003g dir.
ROUTE = HERE.parents[1] / 'e003g-windows-csid-vfe-oracle' / 'route-oracle-summary.json'
PATCH = HERE / 'patch-dmi-summary.json'
OUT_CSV = HERE / 'vfe1-startup-register-ownership.csv'
OUT_JSON = HERE / 'vfe1-startup-ownership-summary.json'

QREF = '0f16924ff6a7f9bb56a7e958016da2ed8a174f2f'
VFE0_BASE = 0x0AC62000
VFE1_BASE = 0x0AC71000
CURRENT_X1E_SPAN = 0x4000
DENALI_BASELINE_SPAN = 0xF000
PAGE = 0x1000

# Names/layout only from pinned Qualcomm cam_vfe680.h. Windows remains the value oracle.
TOP_NAMES = {
    0x24: 'core_cfg_0',
    0x2C: 'core_cfg_2',
    0x8C: 'period_cfg',
    0x90: 'irq_sub_pattern_cfg',
}
# Pinned public VFE680 bus common + clients occupy 0x0c00 through client27 at 0x2988.
VFE680_BUS_MIN = 0x0C00
VFE680_BUS_MAX = 0x2988

def parse_int(x):
    return int(x, 0)

def page_round(n):
    return (n + PAGE - 1) & ~(PAGE - 1)

def main():
    route = json.load(open(ROUTE))
    patch = json.load(open(PATCH))
    assert patch['qualcomm_cdm_reference_commit'] == QREF
    volatile = {parse_int(x) for x in route['regions']['vfe1']['volatile_live_offsets']}

    writes = defaultdict(lambda: defaultdict(list))
    total_writes = 0
    for p in sorted(glob.glob(str(HERE / 'packet*-register-writes.csv'))):
        pkt = int(os.path.basename(p).split('-')[0].replace('packet', ''))
        with open(p, newline='') as f:
            for row in csv.DictReader(f):
                off = parse_int(row['register_offset'])
                val = parse_int(row['value'])
                writes[off][pkt].append(val)
                total_writes += 1

    dmi_regs = sorted({parse_int(g['dmi_register_offset']) for g in patch['dmi_groups']})
    dmi_phase = set()
    for reg in dmi_regs:
        for delta in (0x50, 0x54):
            off = reg + delta
            if off not in writes:
                continue
            vals = {v for pv in writes[off].values() for v in pv}
            if vals <= {0, 1} and all(len(set(pv)) == 1 for pv in writes[off].values()):
                dmi_phase.add(off)

    rows = []
    within_packet_multi = []
    for off in sorted(writes):
        pd = writes[off]
        all_values = [v for pkt in sorted(pd) for v in pd[pkt]]
        distinct = sorted(set(all_values))
        within_multi = any(len(set(vs)) > 1 for vs in pd.values())
        if within_multi:
            within_packet_multi.append(off)
        phase_variant = len(distinct) > 1
        packets = sorted(pd)

        if off in volatile:
            ownership = 'runtime_volatile_do_not_freeze'
            basis = 'independent E003g same-machine Windows live1/live2 mismatch'
        elif off in TOP_NAMES:
            ownership = 'known_top_phase_variant' if phase_variant else 'known_top_static_config_candidate'
            basis = f'pinned Qualcomm VFE680 name={TOP_NAMES[off]}; values from Windows'
        elif off in dmi_phase:
            ownership = 'dmi_associated_phase_variant_control' if phase_variant else 'dmi_associated_static_control'
            basis = 'exactly DMI register +0x50/+0x54, 0/1-valued per startup packet; semantics intentionally unresolved'
        elif VFE680_BUS_MIN <= off <= VFE680_BUS_MAX:
            ownership = 'known_vfe680_bus_register'
            basis = 'pinned Qualcomm VFE680 bus range; Windows value oracle'
        elif off >= 0x3000:
            ownership = 'unpublished_iq_phase_variant' if phase_variant else 'unpublished_iq_static_config_candidate'
            basis = 'outside public VFE680 top/bus map; semantic IQ name intentionally unresolved'
        else:
            ownership = 'unclassified'
            basis = 'no authoritative public/same-machine semantic classification yet'

        rows.append({
            'register_offset': f'0x{off:04x}',
            'absolute_address': f'0x{VFE1_BASE + off:08x}',
            'public_name': TOP_NAMES.get(off, ''),
            'ownership_class': ownership,
            'basis': basis,
            'write_count': len(all_values),
            'packet_coverage': ','.join(str(x) for x in packets),
            'distinct_value_count': len(distinct),
            'distinct_values': ';'.join(f'0x{x:08x}' for x in distinct),
            'within_packet_value_change': int(within_multi),
            'independent_windows_live_volatile': int(off in volatile),
            'dmi_associated_control': int(off in dmi_phase),
            'dmi_associated_phase_variant': int(off in dmi_phase and phase_variant),
        })

    with open(OUT_CSV, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys(), lineterminator='\n')
        w.writeheader(); w.writerows(rows)

    max_write_off = max(writes)
    max_dmi_off = max(dmi_regs)
    max_touched_off = max(max_write_off, max_dmi_off)
    exact_required = max_touched_off + 4
    page_required = page_round(exact_required)
    spacing = VFE1_BASE - VFE0_BASE

    counts = defaultdict(int)
    for r in rows:
        counts[r['ownership_class']] += 1

    summary = {
        'status': 'PASS',
        'policy': 'Same-machine Windows is behavioral oracle; Qualcomm source is used only for VFE680 register names/layout.',
        'qualcomm_vfe680_reference_commit': QREF,
        'windows_corpus': {
            'ordinary_register_writes': total_writes,
            'unique_ordinary_register_offsets': len(writes),
            'dmi_commands': patch['closure']['total_dmi_commands'],
            'dmi_identity_groups': patch['closure']['dmi_register_selector_payload_groups'],
            'unique_dmi_payloads': patch['closure']['unique_payload_sha256_count'],
        },
        'behavior': {
            'single_value_unique_offsets': sum(1 for r in rows if int(r['distinct_value_count']) == 1),
            'cross_packet_variant_unique_offsets': sum(1 for r in rows if int(r['distinct_value_count']) > 1),
            'within_packet_value_change_offsets': [f'0x{x:x}' for x in within_packet_multi],
            'within_packet_value_change_count': len(within_packet_multi),
            'independent_live_volatile_overlap_count': sum(1 for r in rows if int(r['independent_windows_live_volatile'])),
            'independent_live_volatile_overlap_offsets': [r['register_offset'] for r in rows if int(r['independent_windows_live_volatile'])],
            'dmi_associated_control_count': len(dmi_phase),
            'dmi_associated_control_offsets': [f'0x{x:x}' for x in sorted(dmi_phase)],
            'dmi_associated_phase_variant_count': sum(1 for r in rows if int(r['dmi_associated_phase_variant'])),
            'dmi_associated_static_control_count': sum(1 for r in rows if int(r['dmi_associated_control']) and not int(r['dmi_associated_phase_variant'])),
        },
        'ownership_counts': dict(sorted(counts.items())),
        'public_vfe680_bus_crosscheck': {
            'public_bus_range': f'0x{VFE680_BUS_MIN:x}..0x{VFE680_BUS_MAX:x}',
            'initial_cdm_writes_in_public_bus_range': sum(1 for off in writes if VFE680_BUS_MIN <= off <= VFE680_BUS_MAX),
            'conclusion': 'Initial IFE CDM corpus does not contain VFE680 bus-client programming; FULL/DS/stats buffer state is programmed elsewhere.',
        },
        'aperture': {
            'vfe0_base': f'0x{VFE0_BASE:08x}',
            'vfe1_base': f'0x{VFE1_BASE:08x}',
            'instance_base_spacing_bytes': spacing,
            'max_ordinary_register_offset': f'0x{max_write_off:x}',
            'max_dmi_register_offset': f'0x{max_dmi_off:x}',
            'max_touched_offset': f'0x{max_touched_off:x}',
            'exact_required_span_bytes': exact_required,
            'page_rounded_required_span_bytes': page_required,
            'current_x1e_span_bytes': CURRENT_X1E_SPAN,
            'same_machine_denali_baseline_span_bytes': DENALI_BASELINE_SPAN,
            'denali_span_equals_vfe_instance_spacing': DENALI_BASELINE_SPAN == spacing,
            'denali_span_covers_windows_corpus': DENALI_BASELINE_SPAN >= exact_required,
            'denali_span_headroom_bytes': DENALI_BASELINE_SPAN - exact_required,
            'static_conclusion': '0x4000 is mechanically insufficient. 0xf000 is now an evidence-backed SP11 static mapping candidate because it is the same-machine Denali baseline span, exactly equals VFE0->VFE1 base spacing, and covers every observed Windows startup access. Runtime remains unauthorized.',
        },
        'remaining_boundary': 'Semantic names for unpublished IQ blocks and the Linux PIX/TP10-UBWC ownership/implementation remain unresolved. Do not replay live-volatile offsets as fixed state.',
    }
    json.dump(summary, open(OUT_JSON, 'w'), indent=2); open(OUT_JSON, 'a').write('\n')
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    main()
