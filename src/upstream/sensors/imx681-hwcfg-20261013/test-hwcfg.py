#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Exercise actual IMX681 endpoint admission and power-on failure paths."""
import argparse, hashlib, json, subprocess, sys
from pathlib import Path

def function(text,name):
    start=text.index('static int '+name+'(')
    end=text.index('{',start)+1
    level=1
    while level:
        level+=(text[end]=='{')-(text[end]=='}')
        end+=1
    return text[start:end]



def main():
    if sys.flags.optimize: raise ValueError('Python -O is not supported')
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--manifest',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--compiler',choices=['gcc','clang'],required=True)
    a=ap.parse_args()
    if a.source.is_symlink() or not a.source.is_file(): raise ValueError('source must be a regular file')
    data=a.source.read_bytes();m=json.loads(a.manifest.read_text())
    if hashlib.sha256(data).hexdigest()!=m['sensor_sha256']:raise ValueError('sensor source changed')
    out=a.output.absolute()
    if out.exists() or out.is_symlink():raise ValueError('output already exists')
    if out.resolve().is_relative_to(a.source.resolve().parent):raise ValueError('output inside source')
    text=data.decode()
    selected='\n'.join(function(text,n) for n in ['imx681_validate_endpoint','imx681_check_hwcfg','imx681_power_on'])
    # Admission must precede reset acquisition, rail/clock enable and identify.
    probe=function(text,'imx681_probe')
    assert probe.index('imx681_check_hwcfg(sensor)')<probe.index('devm_gpiod_get(dev, "reset"')<probe.index('imx681_power_on(dev)')<probe.index('imx681_identify(sensor)')
    assert 'devm_gpiod_get_optional' not in probe
    fixtures={}
    for name,key in [('hwcfg-stub.c','host_stub_sha256'),('hwcfg-harness.c','host_harness_sha256')]:
        path=a.manifest.parent/name
        if path.is_symlink() or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=m[key]:raise ValueError('host fixture changed')
        fixtures[name]=path.read_text()
    STUB=fixtures['hwcfg-stub.c'];HARNESS=fixtures['hwcfg-harness.c']
    import re
    for name in ['IMX681_LINK_FREQ','IMX681_XCLK_FREQ','IMX681_XCLR_MIN_DELAY_US','IMX681_XCLR_DELAY_RANGE_US']:
        line=re.search(r'^#define\s+'+name+r'\s+[^\n]+',text,re.M)
        if not line:raise ValueError('missing actual driver constant: '+name)
        STUB=re.sub(r'^#define\s+'+name+r'\s+[^\n]+',lambda _:line.group(0),STUB,flags=re.M)
    start=text.index('static const char * const imx681_supply_name[] =')
    supplies=text[start:text.index('};',start)+2]
    STUB=re.sub(r'static const char \*const imx681_supply_name\[\]=\{[^;]+;',lambda _:supplies,STUB)
    out.mkdir(parents=True,exist_ok=False)
    c=out/'hwcfg.c';c.write_text(STUB+'\n'+selected+'\n'+HARNESS)
    exe=out/'hwcfg'
    cmd=[a.compiler,'-std=c11','-Wall','-Wextra','-Werror','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(c),'-o',str(exe)]
    r=subprocess.run(cmd,capture_output=True,text=True)
    (out/'compile.log').write_text(r.stdout+r.stderr)
    if r.returncode:raise RuntimeError(r.stdout+r.stderr)
    r=subprocess.run([str(exe)],capture_output=True,text=True)
    (out/'run.log').write_text(r.stdout+r.stderr)
    if r.returncode:raise RuntimeError(r.stdout+r.stderr)
    result=json.loads(r.stdout)
    result.update(compiler=a.compiler,sanitizers=['address','undefined'],scope='actual sensor functions; modeled fwnode/parser/clock/regulator/GPIO helpers; no hardware',sensor_sha256=m['sensor_sha256'],installed=False,hardware_qualified=False)
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
if __name__=='__main__':
    try:main()
    except (ValueError,RuntimeError,AssertionError,OSError) as e:sys.exit(str(e))
