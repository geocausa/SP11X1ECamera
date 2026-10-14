#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""One-use sensor genpd ownership/removal test; no buffers or streaming."""
from pathlib import Path
import fcntl, hashlib, json, os, re, subprocess, time

KREL = '7.2.0-sp11-upstream-front26'
ID = 'sp11-camera-upstream-front-20261014-07'
TOKEN = 'sp11_camera_upstream_front_20261014_07=1'
ENTRY = 'sp11_entry=' + ID
D = Path('/var/lib') / ID
R = Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-upstream')
DTROOT = Path('/sys/firmware/devicetree/base')
MODULE_ROOT = D / 'module-root'

def need(v, why):
    if not v:
        raise RuntimeError(why)

def run(args, timeout=15):
    p = subprocess.run(args, text=True, capture_output=True, timeout=timeout)
    need(p.returncode == 0, str(args[0]) + ': ' + p.stderr[-500:])
    return p.stdout

def regulators():
    result = {}
    for p in Path('/sys/class/regulator').glob('regulator.*'):
        if (p / 'name').exists():
            name = (p / 'name').read_text().strip()
            need(name not in result, 'duplicate regulator')
            result[name] = p
    return result

def no_modules():
    for name in ['qcom_camss', 'imx681', 'phy_qcom_mipi_csi2', 'i2c_qcom_cci', 'sp11_phy_owned_cycle']:
        need(not (Path('/sys/module') / name).exists(), 'camera module already loaded')
    need(not list(Path('/dev').glob('video*')) and not list(Path('/dev').glob('media*')) and not list(Path('/dev').glob('v4l-subdev*')), 'camera node already present')

def reset237_low(gpio):
    headers = list(re.finditer(r'^gpiochip\d+: (\d+) GPIOs, parent: platform/f100000\.pinctrl, f100000\.pinctrl:$', gpio, re.M))
    need(len(headers) == 1 and int(headers[0][1]) == 239, 'unique TLMM239 heading required')
    block = gpio[headers[0].end():].split('\ngpiochip', 1)[0]
    lines = re.findall(r'^\s*gpio237\s*:\s*(.*)$', block, re.M)
    need(len(lines) == 1 and re.fullmatch(r'out\s+low\s+func0\s+2mA\s+no pull\s*', lines[0]) is not None, 'reset237 output-low function0 required')
    return True


def check_entities(metadata):
    blocks = metadata.split('\n- entity')
    found = {}
    sensors = []
    for block in blocks:
        header = block.split('\n', 1)[0]
        m = re.search(r'\b(msm_tpg[0-2]) \(1 pad,', header)
        if m:
            need(m[1] not in found, 'duplicate TPG entity')
            need('subtype Sensor' in block and 'pad0: SOURCE' in block, 'one-pad synthetic source classification')
            need('[ENABLED' not in block, 'synthetic generator unexpectedly linked')
            found[m[1]] = 'Sensor'
        if re.search(r'\bimx681 \d+-0010 \(1 pad,', header):
            need('subtype Sensor' in block, 'physical sensor classification')
            need('-> "msm_csiphy2":0 [ENABLED,IMMUTABLE]' in block, 'physical front source link changed')
            sensors.append(True)
    need(set(found) == {'msm_tpg0', 'msm_tpg1', 'msm_tpg2'} and len(sensors) == 1,
         'unique physical/synthetic source identities')
    return dict(tpg_functions=found, synthetic_links_enabled=0, physical_front_source='imx681', physical_phy=2)


def check_top_membership(summary, device_name):
    lines = summary.splitlines()
    indices = [i for i, line in enumerate(lines) if line.startswith('cam_cc_titan_top_gdsc ')]
    need(len(indices) == 1, 'unique TOP domain summary')
    start = indices[0]
    end = next((i for i in range(start + 1, len(lines)) if lines[i] and not lines[i][0].isspace()), len(lines))
    records = [line.split() for line in lines[start + 1:end] if line.split() and line.split()[0] == device_name]
    need(len(records) == 1 and len(records[0]) >= 2, 'unique sensor dev_name in TOP genpd')
    need(records[0][1] == 'suspended', 'TOP sensor device must be suspended')
    return {'domain': 'cam_cc_titan_top_gdsc', 'device_name': device_name, 'runtime_status': records[0][1]}

def main():
    need(os.geteuid() == 0, 'root required')
    cmd = Path('/proc/cmdline').read_text().split()
    need(TOKEN in cmd and ENTRY in cmd and run(['uname', '-r']).strip() == KREL,
         'dedicated new-kernel boot required')
    with (D / 'ATTEMPT-CONSUMED').open('x') as f:
        f.write(Path('/proc/sys/kernel/random/boot_id').read_text())
    lock = (D / 'observer.lock').open('w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    result = dict(status='FAILED_SENSOR_DOMAIN_RUNTIME_PM_UNLOAD', kernel_release=KREL,
                  boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                  streaming=False, capture=False, same_boot_retry=False)
    loaded = []
    try:
        run(['sha256sum', '-c', str(D / 'ASSETS.sha256')], 30)
        for path, pin in json.loads((D / 'GOLDEN-HASHES.json').read_text()).items():
            need(hashlib.sha256(Path(path).read_bytes()).hexdigest() == pin, 'Golden asset drift')
        env = os.environ.copy()
        env.update(GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='safe.directory', GIT_CONFIG_VALUE_0=str(R))
        head = subprocess.check_output(['git', '-C', str(R), 'rev-parse', 'HEAD'], env=env, text=True).strip()
        need(head == (D / 'EXPECTED-HEAD').read_text().strip(), 'source head changed')
        grub = run(['grub-editenv', '/boot/grub/grubenv', 'list'])
        need('saved_entry=sp11-audio-fullio-v19c' in grub and not re.search(r'^next_entry=.+', grub, re.M), 'Golden default or next entry')
        result['network_interfaces'] = [p.name for p in Path('/sys/class/net').iterdir() if p.name != 'lo']
        need(result['network_interfaces'], 'network absent')
        result['wifi_driver'] = Path('/sys/bus/pci/devices/0004:01:00.0/driver').resolve().name
        need(result['wifi_driver'] == 'ath12k_wifi7_pci', 'WiFi binding absent')
        no_modules()
        (D / 'PRIVATE-PRE-DMESG.txt').write_text(run(['dmesg']))
        result['candidate_module_root'] = str(MODULE_ROOT)
        for name in ['camcc_x1e80100', 'i2c_qcom_cci', 'phy_qcom_mipi_csi2', 'imx681', 'qcom_camss']:
            run(['modprobe', '-d', str(MODULE_ROOT), '--set-version', KREL, '-C', str(D / 'empty-modprobe.conf'), '--ignore-install', name], 20)
            loaded.append(name)
            need((Path('/sys/module') / name).exists(), 'requested module absent: ' + name)
        sensor_node = DTROOT / 'soc@0/cci@ac16000/i2c-bus@1/camera@10'
        devices = [p for p in Path('/sys/bus/i2c/devices').iterdir()
                   if (p / 'of_node').is_symlink() and (p / 'of_node').resolve() == sensor_node]
        need(len(devices) == 1, 'sensor client identity')
        device = devices[0]
        need((device / 'driver').is_symlink() and (device / 'driver').resolve().name == 'imx681', 'sensor did not bind')
        need(list(Path('/dev').glob('media*')) and list(Path('/dev').glob('v4l-subdev*')), 'media graph missing')
        deadline = time.monotonic() + 12
        while time.monotonic() < deadline and (device / 'power/runtime_status').read_text().strip() != 'suspended':
            time.sleep(0.25)
        result['sensor_runtime_status'] = (device / 'power/runtime_status').read_text().strip()
        need(result['sensor_runtime_status'] == 'suspended', 'sensor runtime power-off not completed')
        reg = regulators()
        result['sensor_rails'] = {}
        for name in ['vreg_l3m_1p8', 'vreg_l7b_2p8']:
            need(name in reg, 'sensor rail absent')
            users = int((reg[name] / 'num_users').read_text())
            need(users == 0, 'sensor rail references remain')
            result['sensor_rails'][name] = dict(num_users=users, microvolts_cache=int((reg[name] / 'microvolts').read_text()))
        clock = Path('/sys/kernel/debug/clk/clk_summary').read_text()
        (D / 'PRIVATE-CLOCK.txt').write_text(clock)
        lines = [x.split() for x in clock.splitlines() if x.split() and x.split()[0] == 'cam_cc_mclk4_clk']
        need(len(lines) == 1, 'MCLK4 summary absent')
        result['mclk4'] = dict(enable_count=int(lines[0][1]), prepare_count=int(lines[0][2]), rate=int(lines[0][4]))
        need(result['mclk4']['enable_count'] == 0 and result['mclk4']['prepare_count'] == 0 and result['mclk4']['rate'] == 19200000, 'MCLK references remain')
        gpio = Path('/sys/kernel/debug/gpio').read_text()
        (D / 'PRIVATE-GPIO.txt').write_text(gpio)
        result['reset237_output_low'] = reset237_low(gpio)
        log = run(['dmesg'])
        (D / 'PRIVATE-DMESG.txt').write_text(log)
        need('detected model id 0x0681 (IMX681)' in log, 'sensor identity not observed')
        need(not any(x in log for x in ['power-on cleanup failed', 'failed to disable avdd', 'failed to disable dovdd']), 'power cleanup failure')
        result['model_id'] = '0x0681'
        result['tpg_entity_function_warnings'] = sum('Entity type for entity msm_tpg' in x for x in log.splitlines())
        result['media_nodes'] = [p.name for p in Path('/dev').glob('media*')]
        result['video_nodes'] = [p.name for p in Path('/dev').glob('video*')]
        need(result['tpg_entity_function_warnings'] == 0, 'TPG classification warning remains')
        media_tool = __import__('shutil').which('media-ctl')
        need(media_tool, 'media-ctl required for entity classification')
        metadata = run([media_tool, '-p', '-d', str(Path('/dev') / result['media_nodes'][0])])
        (D / 'PRIVATE-MEDIA.txt').write_text(metadata)
        result['entity_classification'] = check_entities(metadata)
        pd = (sensor_node / 'power-domains').read_bytes()
        cci_pd = (sensor_node.parent.parent / 'power-domains').read_bytes()
        need(len(pd) == 8 and pd == cci_pd and int.from_bytes(pd[4:], 'big') == 5, 'sensor TOP domain absent/mismatched')
        result['sensor_domain_matches_cci1_top'] = True
        summary = Path('/sys/kernel/debug/pm_genpd/pm_genpd_summary').read_text()
        (D / 'PRIVATE-GENPD.txt').write_text(summary)
        result['sensor_domain_observation'] = check_top_membership(summary, device.name)
        result['sensor_top_domain_membership'] = True
        phy_device = Path('/sys/bus/platform/devices/ace8000.phy')
        need((phy_device / 'driver').resolve().name == 'qcom-mipi-csi2-phy', 'PHY2 driver')
        before_users = {n: int((reg[n] / 'num_users').read_text()) for n in ['vreg_l2c_0p8', 'vreg_l1c_1p2']}
        clock_names = ['cam_cc_csiphy2_clk', 'cam_cc_csi2phytimer_clk', 'cam_cc_core_ahb_clk']
        def clock_counts():
            summary = Path('/sys/kernel/debug/clk/clk_summary').read_text()
            counts = {}
            for name in clock_names:
                records = [x.split() for x in summary.splitlines() if x.split() and x.split()[0] == name]
                need(len(records) == 1, 'PHY clock summary ' + name)
                counts[name] = [int(records[0][1]), int(records[0][2])]
            return counts
        before_clocks = clock_counts()
        run(['modprobe', '-d', str(MODULE_ROOT), '--set-version', KREL,
             '-C', str(D / 'empty-modprobe.conf'), '--ignore-install',
             'sp11_phy_owned_cycle', 'execute=1'], 30)
        loaded.append('sp11_phy_owned_cycle')
        params = Path('/sys/module/sp11_phy_owned_cycle/parameters')
        cycle = {n: int((params / n).read_text()) for n in ['result', 'completed', 'stage', 'pinned']}
        result['phy_cycles'] = cycle
        need(cycle == {'result': 1, 'completed': 3, 'stage': 9, 'pinned': 0}, 'PHY cycle diagnostic: ' + str(cycle))
        deadline = time.monotonic() + 12
        while time.monotonic() < deadline and (phy_device / 'power/runtime_status').read_text().strip() != 'suspended':
            time.sleep(0.25)
        result['phy_runtime_after_cycles'] = (phy_device / 'power/runtime_status').read_text().strip()
        need(result['phy_runtime_after_cycles'] == 'suspended', 'PHY runtime references remain')
        after_users = {n: int((reg[n] / 'num_users').read_text()) for n in before_users}
        result['phy_rail_users'] = {'before': before_users, 'after': after_users}
        need(before_users == after_users, 'PHY supply references changed')
        after_clocks = clock_counts()
        result['phy_clock_counts'] = {'before': before_clocks, 'after': after_clocks}
        need(before_clocks == after_clocks, 'PHY clock references changed')
        need((device / 'power/runtime_status').read_text().strip() == 'suspended', 'sensor powered during PHY test')
        need(reset237_low(Path('/sys/kernel/debug/gpio').read_text()), 'sensor reset released')
        sensor_clock = Path('/sys/kernel/debug/clk/clk_summary').read_text()
        mclk = [x.split() for x in sensor_clock.splitlines() if x.split() and x.split()[0] == 'cam_cc_mclk4_clk']
        need(len(mclk) == 1 and int(mclk[0][1]) == 0 and int(mclk[0][2]) == 0, 'sensor MCLK enabled during PHY test')
        run(['modprobe', '-d', str(MODULE_ROOT), '--set-version', KREL,
             '-C', str(D / 'empty-modprobe.conf'), '-r', 'sp11_phy_owned_cycle'], 20)
        need(not Path('/sys/module/sp11_phy_owned_cycle').exists(), 'diagnostic references remain')
        for name in ['qcom_camss', 'imx681', 'phy_qcom_mipi_csi2', 'i2c_qcom_cci']:
            run(['modprobe', '-d', str(MODULE_ROOT), '--set-version', KREL, '-C', str(D / 'empty-modprobe.conf'), '-r', name], 20)
            need(not (Path('/sys/module') / name).exists(), 'module unload failed')
        no_modules()
        reg = regulators()
        need(all(int((reg[n] / 'num_users').read_text()) == 0 for n in ['vreg_l3m_1p8', 'vreg_l7b_2p8']), 'rail users after unload')
        result['camera_modules_unloaded'] = True
        final_log = run(['dmesg'])
        (D / 'PRIVATE-POST-UNLOAD-DMESG.txt').write_text(final_log)
        current_boot = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
        guard = subprocess.run(['python3', str(D / 'camera_final_log_guard.py'),
                                '--before', str(D / 'PRIVATE-PRE-DMESG.txt'),
                                '--after', str(D / 'PRIVATE-POST-UNLOAD-DMESG.txt'),
                                '--before-boot-id', result['boot_id'], '--after-boot-id', current_boot],
                               capture_output=True, text=True, timeout=10)
        result['final_kernel_log'] = json.loads(guard.stdout)
        need(guard.returncode == 0, 'final kernel log diagnostics: ' + guard.stdout)
        result['status'] = 'PASS_PHY_OWNED_POWER_CYCLES_AND_WARNING_FREE_UNLOAD'
    except Exception as e:
        result['error'] = str(e)
        raise
    finally:
        result['loaded_requests'] = loaded
        (D / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')

if __name__ == '__main__':
    main()
