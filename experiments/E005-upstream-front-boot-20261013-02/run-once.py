#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""One-use new-kernel front registration/runtime-PM test, without streaming."""
from pathlib import Path
import fcntl, hashlib, json, os, re, subprocess, time

KREL = '7.2.0-sp11-upstream-front26'
ID = 'sp11-camera-upstream-front-20261013-02'
TOKEN = 'sp11_camera_upstream_front_20261013_02=1'
ENTRY = 'sp11_entry=' + ID
D = Path('/var/lib') / ID
R = Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-upstream')
DTROOT = Path('/sys/firmware/devicetree/base')

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
    for name in ['qcom_camss', 'imx681', 'phy_qcom_mipi_csi2', 'i2c_qcom_cci']:
        need(not (Path('/sys/module') / name).exists(), 'camera module already loaded')
    need(not list(Path('/dev').glob('video*')) and not list(Path('/dev').glob('media*')) and not list(Path('/dev').glob('v4l-subdev*')), 'camera node already present')

def reset237_low(gpio):
    headers = list(re.finditer(r'^gpiochip\d+: (\d+) GPIOs, parent: platform/f100000\.pinctrl, f100000\.pinctrl:$', gpio, re.M))
    need(len(headers) == 1 and int(headers[0][1]) == 239, 'unique TLMM239 heading required')
    block = gpio[headers[0].end():].split('\ngpiochip', 1)[0]
    lines = re.findall(r'^\s*gpio237\s*:\s*(.*)$', block, re.M)
    need(len(lines) == 1 and re.fullmatch(r'out\s+low\s+func0\s+2mA\s+no pull\s*', lines[0]) is not None, 'reset237 output-low function0 required')
    return True


def main():
    need(os.geteuid() == 0, 'root required')
    cmd = Path('/proc/cmdline').read_text().split()
    need(TOKEN in cmd and ENTRY in cmd and run(['uname', '-r']).strip() == KREL,
         'dedicated new-kernel boot required')
    with (D / 'ATTEMPT-CONSUMED').open('x') as f:
        f.write(Path('/proc/sys/kernel/random/boot_id').read_text())
    lock = (D / 'observer.lock').open('w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    result = dict(status='FAILED_UPSTREAM_FRONT_PROBE', kernel_release=KREL,
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
        for name in ['camcc_x1e80100', 'i2c_qcom_cci', 'phy_qcom_mipi_csi2', 'imx681', 'qcom_camss']:
            run(['modprobe', '-C', str(D / 'empty-modprobe.conf'), '--ignore-install', name], 20)
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
        if shutil_which := __import__('shutil').which('media-ctl'):
            (D / 'PRIVATE-MEDIA.txt').write_text(run([shutil_which, '-p', '-d', str(Path('/dev') / result['media_nodes'][0])]))
        for name in ['qcom_camss', 'imx681', 'phy_qcom_mipi_csi2', 'i2c_qcom_cci']:
            run(['modprobe', '-C', str(D / 'empty-modprobe.conf'), '-r', name], 20)
            need(not (Path('/sys/module') / name).exists(), 'module unload failed')
        no_modules()
        reg = regulators()
        need(all(int((reg[n] / 'num_users').read_text()) == 0 for n in ['vreg_l3m_1p8', 'vreg_l7b_2p8']), 'rail users after unload')
        result['camera_modules_unloaded'] = True
        result['status'] = 'PASS_UPSTREAM_FRONT_PROBE_AND_RUNTIME_PM'
    except Exception as e:
        result['error'] = str(e)
        raise
    finally:
        result['loaded_requests'] = loaded
        (D / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')

if __name__ == '__main__':
    main()
