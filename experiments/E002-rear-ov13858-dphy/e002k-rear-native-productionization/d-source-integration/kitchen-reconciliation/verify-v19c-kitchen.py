#!/usr/bin/env python3
import argparse
import re
import subprocess
import tempfile
from pathlib import Path


def sh(*args, check=True):
    p = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and p.returncode:
        raise RuntimeError(f"command failed ({p.returncode}): {' '.join(args)}\n{p.stderr}")
    return p.stdout


def decompile(dtb):
    fd, name = tempfile.mkstemp(prefix='sp11-kitchen-', suffix='.dts')
    Path(name).unlink(missing_ok=True)
    try:
        p = subprocess.run(['dtc', '-I', 'dtb', '-O', 'dts', '-s', '-o', name, dtb],
                           text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode:
            raise RuntimeError(f'dtc failed for {dtb}: {p.stderr}')
        return Path(name).read_text()
    finally:
        Path(name).unlink(missing_ok=True)


def parse_dts(text):
    # dtc's decompiled DTS is regular enough to parse structurally without
    # guessing phandle semantics.  Keep property values textual: this stage
    # only compares a before/after pair built from the same camera source.
    nodes = {'/'}
    props = {}
    stack = []
    pending = []

    def path_now():
        return '/' + '/'.join(stack) if stack else '/'

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith('/dts-v1/') or line.startswith('/memreserve/'):
            continue
        if pending:
            pending.append(line)
            if ';' not in line:
                continue
            stmt = ' '.join(pending)
            pending = []
            key = stmt.split('=', 1)[0].strip().rstrip(';')
            props[(path_now(), key)] = stmt
            continue
        if line == '};':
            if stack:
                stack.pop()
            continue
        if line.endswith('{'):
            name = line[:-1].strip()
            if name == '/':
                stack = []
                nodes.add('/')
                continue
            # Be tolerant if a decompiler ever emits labels.
            if ':' in name:
                name = name.split(':', 1)[1].strip()
            stack.append(name)
            nodes.add(path_now())
            continue
        if ';' in line:
            stmt = line
            key = stmt.split('=', 1)[0].strip().rstrip(';')
            props[(path_now(), key)] = stmt
        else:
            pending = [line]
    if pending:
        raise RuntimeError('unterminated DTS property while parsing')
    return nodes, props


SPI = '/soc@0/geniqup@ac0000/spi@a88000'
GPI = '/soc@0/dma-controller@a00000'
TLMM = '/soc@0/pinctrl@f100000'
G6TS = TLMM + '/g6ts-qspi-data23-state'
TOUCH = SPI + '/touchscreen@0'
SOUND = '/sound'
TX = SOUND + '/tx-dmic-dai-link'


def allowed_change(path, prop=None):
    if path == '/__symbols__' and prop == 'g6ts_qspi_data23':
        return True
    if path == GPI and prop == 'status':
        return True
    if path == SPI and prop in {'dmas', 'pinctrl-0', 'qcom,biosref-qspi',
                                'qcom,enable-gsi-dma', 'status'}:
        return True
    if path == SOUND and prop in {'model', 'audio-routing'}:
        return True
    if path == G6TS or path.startswith(G6TS + '/'):
        return True
    if path == TOUCH or path.startswith(TOUCH + '/'):
        return True
    if path == TX or path.startswith(TX + '/'):
        return True
    return False


HEX = re.compile(r'0x[0-9a-fA-F]+')


def phandle_map(props):
    out = {}
    for (path, prop), stmt in props.items():
        if prop != 'phandle':
            continue
        vals = HEX.findall(stmt)
        if len(vals) == 1:
            out[int(vals[0], 16)] = path
    return out


def phandle_renumber_only(old, new, old_ph, new_ph):
    """Return True when textual change is only an FDT phandle renumber.

    Adding one labelled node can cause dtc to renumber hundreds of later
    handles.  Compare changed numeric cells positionally: every changed cell
    must resolve to the same target node in the old and new DTB.  Unchanged
    numeric cells are deliberately ignored so ordinary constants that happen
    to equal a phandle value cannot become false positives.
    """
    if old is None or new is None:
        return False
    oparts = HEX.split(old); nparts = HEX.split(new)
    ovals = HEX.findall(old); nvals = HEX.findall(new)
    if oparts != nparts or len(ovals) != len(nvals):
        return False
    saw = False
    for ov, nv in zip(ovals, nvals):
        oi = int(ov, 16); ni = int(nv, 16)
        if oi == ni:
            continue
        saw = True
        if old_ph.get(oi) != new_ph.get(ni) or old_ph.get(oi) is None:
            return False
    return saw


def compare_scoped(a_text, b_text, label):
    an, ap = parse_dts(a_text)
    bn, bp = parse_dts(b_text)
    old_ph = phandle_map(ap); new_ph = phandle_map(bp)
    node_changes = sorted((an ^ bn))
    prop_changes = []
    renumber_only = []
    for k in sorted(set(ap) | set(bp)):
        if ap.get(k) != bp.get(k):
            x = (k[0], k[1], ap.get(k), bp.get(k))
            prop_changes.append(x)
            if phandle_renumber_only(x[2], x[3], old_ph, new_ph):
                renumber_only.append(x)
    bad_nodes = [p for p in node_changes if not allowed_change(p)]
    bad_props = [x for x in prop_changes
                 if not allowed_change(x[0], x[1]) and x not in renumber_only]
    print(f'{label}_node_changes={len(node_changes)}')
    print(f'{label}_property_changes={len(prop_changes)}')
    print(f'{label}_phandle_renumber_only={len(renumber_only)}')
    print(f'{label}_unexpected_nodes={len(bad_nodes)}')
    print(f'{label}_unexpected_properties={len(bad_props)}')
    if bad_nodes:
        print('UNEXPECTED_NODES:')
        for x in bad_nodes: print(' ', x)
    if bad_props:
        print('UNEXPECTED_PROPERTIES:')
        for path, prop, old, new in bad_props:
            print(f'  {path}:{prop}\n    OLD {old}\n    NEW {new}')
    if bad_nodes or bad_props:
        raise SystemExit(20)
    return node_changes, prop_changes


def fdt_s(dtb, path, prop):
    return sh('fdtget', '-t', 's', dtb, path, prop).strip()


def fdt_x(dtb, path, prop):
    out = sh('fdtget', '-t', 'x', dtb, path, prop).strip()
    return [int(x, 16) for x in out.split()] if out else []


def props_at(dtb, path):
    return set(sh('fdtget', '-p', dtb, path).split())


def sym(dtb, name):
    return fdt_s(dtb, '/__symbols__', name)


def ph(dtb, name):
    return fdt_x(dtb, sym(dtb, name), 'phandle')[0]


def req(cond, msg):
    if not cond:
        raise SystemExit('VERIFY_FAIL: ' + msg)


def verify_post(post, live):
    # Exact human-facing strings must equal deployed FullIO v19c.
    req(fdt_s(post, SOUND, 'model') == fdt_s(live, SOUND, 'model') ==
        'X1E80100-Microsoft-Surface-Pro-11-FullIO-v19c0', 'sound model')
    req(fdt_s(post, SOUND, 'audio-routing') == fdt_s(live, SOUND, 'audio-routing'),
        'audio-routing string list')

    # GPI and QSPI transport. Resolve phandles from symbols in the POST DTB;
    # camera additions are allowed to renumber them.
    gpi = sym(post, 'gpi_dma1'); spi = sym(post, 'spi10')
    req(fdt_s(post, gpi, 'status') == 'okay', 'gpi_dma1 status')
    sp = props_at(post, spi)
    req({'qcom,enable-gsi-dma', 'qcom,biosref-qspi'} <= sp, 'QSPI GSI/BIOSREF booleans')
    req(fdt_s(post, spi, 'status') == 'okay', 'spi10 status')
    gp = ph(post, 'gpi_dma1')
    req(fdt_x(post, spi, 'dmas') == [gp, 0, 2, 4, gp, 1, 2, 4], 'spi10 QSPI DMA specifiers')
    req(fdt_x(post, spi, 'pinctrl-0') ==
        [ph(post, 'qup_spi10_data_clk'), ph(post, 'qup_spi10_cs'), ph(post, 'g6ts_qspi_data23')],
        'spi10 pinctrl tuple')

    g6 = sym(post, 'g6ts_qspi_data23')
    req(g6 == G6TS, 'g6ts symbol path')
    req(fdt_s(post, g6, 'pins') == 'gpio49 gpio50', 'g6ts GPIO49/50')
    req(fdt_s(post, g6, 'function') == 'qup1_se2', 'g6ts qup1_se2 function')
    req(fdt_x(post, g6, 'drive-strength') == [6], 'g6ts drive strength')
    req('bias-disable' in props_at(post, g6), 'g6ts bias-disable')

    touch = spi + '/touchscreen@0'
    req(fdt_s(post, touch, 'compatible') == 'microsoft,mshw0485', 'touch compatible')
    req(fdt_x(post, touch, 'reg') == [0], 'touch chip select')
    req(fdt_x(post, touch, 'spi-max-frequency') == [40000000], 'touch SPI frequency')
    tl = ph(post, 'tlmm')
    req(fdt_x(post, touch, 'interrupt-parent') == [tl], 'touch interrupt parent')
    req(fdt_x(post, touch, 'interrupts') == [51, 8], 'touch IRQ tuple')
    req(fdt_x(post, touch, 'interrupt-gpios') == [tl, 51, 1], 'touch IRQ GPIO')
    req(fdt_x(post, touch, 'power-gpios') == [tl, 64, 0], 'touch power GPIO')
    req(fdt_x(post, touch, 'reset-gpios') == [tl, 48, 0], 'touch reset GPIO')

    tx = SOUND + '/tx-dmic-dai-link'
    req(fdt_s(post, tx, 'link-name') == 'TX DMIC Capture', 'TX DMIC link name')
    req(fdt_x(post, tx + '/codec', 'sound-dai') == [ph(post, 'lpass_txmacro'), 0],
        'TX codec DAI')
    req(fdt_x(post, tx + '/cpu', 'sound-dai') == [ph(post, 'q6apmbedai'), 0x78],
        'TX CPU DAI')
    req(fdt_x(post, tx + '/platform', 'sound-dai') == [ph(post, 'q6apm')],
        'TX platform DAI')

    # Cross-check the literal non-phandle semantics against the deployed DTB.
    req(fdt_s(post, touch, 'compatible') == fdt_s(live, TOUCH, 'compatible'), 'touch/live compatible')
    req(fdt_x(post, touch, 'interrupts') == fdt_x(live, TOUCH, 'interrupts'), 'touch/live IRQ')
    print('post_v19c_kitchen_semantics=PASS')


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--baseline', required=True, help='maintained Golden source DTB before Kitchen')
    a.add_argument('--live', required=True, help='deployed FullIO v19c DTB')
    a.add_argument('--pre', help='camera-integrated DTB before Kitchen')
    a.add_argument('--post', help='camera-integrated DTB after Kitchen')
    args = a.parse_args()

    base_text = decompile(args.baseline)
    live_text = decompile(args.live)
    compare_scoped(base_text, live_text, 'baseline_to_live')
    # Preserve the historical exact line-count oracle too.
    with tempfile.TemporaryDirectory() as td:
        p1=Path(td)/'a'; p2=Path(td)/'b'; p1.write_text(live_text); p2.write_text(base_text)
        d = subprocess.run(['diff','-u',str(p1),str(p2)], text=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        changed = [x for x in d.stdout.splitlines() if re.match(r'^[+-][^-+]', x)]
        print(f'baseline_live_changed_dts_lines={len(changed)}')
        req(len(changed) == 44, 'historical source/live delta is no longer exactly 44 changed DTS lines')

    if bool(args.pre) != bool(args.post):
        raise SystemExit('--pre and --post must be supplied together')
    if args.pre:
        compare_scoped(decompile(args.pre), decompile(args.post), 'camera_pre_to_post')
        verify_post(args.post, args.live)
        print('NONCAMERA_V19C_RECONCILIATION=PASS')
    else:
        print('BASELINE_V19C_SCOPE=PASS')

if __name__ == '__main__':
    main()
