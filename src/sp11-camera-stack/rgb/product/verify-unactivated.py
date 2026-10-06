#!/usr/bin/env python3
from pathlib import Path
import os,subprocess

def need(v,m):
    if not v: raise AssertionError(m)
need(os.geteuid()==0,'root verifier required')
need('sp11_camera_rgb_product=1' not in Path('/proc/cmdline').read_text().split(),'product boot token unexpectedly active')
for p in ('/usr/local/libexec/sp11-camera-stack/rgb/product/product_daemon.py','/usr/local/libexec/sp11-camera-stack/rgb/product/product_owner.py','/usr/local/libexec/sp11-camera-stack/rgb/service/session.py','/usr/local/libexec/sp11-camera-stack/routing/route_policy.py','/usr/local/bin/sp11-rgbctl','/var/lib/sp11-camera-rgb/PRODUCT-ASSETS.sha256'):
    need(Path(p).is_file(),p)
need(not Path('/var/lib/sp11-camera-rgb/ENABLE').exists(),'ENABLE must not exist')
for unit in ('sp11-camera-rgb.service','sp11-camera-rgb-publisher@front.service','sp11-camera-rgb-publisher@rear.service'):
    cp=subprocess.run(['systemctl','is-active','--quiet',unit]); need(cp.returncode!=0,'active '+unit)
cp=subprocess.run(['systemctl','is-enabled','--quiet','sp11-camera-rgb.service']); need(cp.returncode!=0,'enabled product service')
for m in ('qcom_camss','imx681','ov13858','sp11_vd55g0','v4l2loopback'): need(not Path('/sys/module',m).exists(),'loaded '+m)
need(not any(Path('/dev').glob('media*')),'media node present')
print('SP11 RGB PRODUCT VERIFY: PASS INSTALLED=YES ACTIVATED=NO')
