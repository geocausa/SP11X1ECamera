#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Exercise actual sensor/CCI bodies against a modeled byte-addressed regmap."""
import argparse,hashlib,json,re,subprocess,sys
from pathlib import Path

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p,value):
    if p.is_symlink() or not p.is_file() or sha(p)!=value:
        raise ValueError('input changed or not regular: '+str(p))
    return p.read_text()
def function(text,name,prefix='static int '):
    a=text.index(prefix+name+'(');b=text.index('{',a);c=b+1;level=1
    while level:
        level+=(text[c]=='{')-(text[c]=='}');c+=1
    return text[a:c]
def main():
    if sys.flags.optimize: raise ValueError('Python -O is not supported')
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',required=True,type=Path)
    ap.add_argument('--parent-source',required=True,type=Path)
    ap.add_argument('--kernel-source',required=True,type=Path)
    ap.add_argument('--output',required=True,type=Path)
    ap.add_argument('--compiler',required=True,choices=['gcc','clang'])
    a=ap.parse_args();q=Path(__file__).resolve().parent;m=json.loads((q/'manifest.json').read_text())
    text=pin(a.source,m['sensor_sha256']);parent=pin(a.parent_source,m['parent_sensor_sha256'])
    tables=pin(a.source.with_name('imx681-tables.h'),m['tables_sha256'])
    cci=pin(a.kernel_source/'drivers/media/v4l2-core/v4l2-cci.c',m['cci_sha256'])
    header=pin(a.kernel_source/'include/media/v4l2-cci.h',m['cci_header_sha256'])
    stub=pin(q/'fll-stub.c',m['stub_sha256']);harness=pin(q/'fll-harness.c',m['harness_sha256'])
    out=a.output.absolute()
    if any(p.is_symlink() for p in [out,*out.parents]):raise ValueError('symlink output path')
    out=out.resolve()
    if out.exists() or out.is_symlink():raise ValueError('output already exists')
    for source in [a.source,a.parent_source,a.kernel_source,q]:
        if out==source.resolve() or source.resolve() in out.parents:raise ValueError('output nested in input')
    constants='\n'.join(re.findall(r'^#define IMX681_.*$',text,re.M))
    macros=header[header.index('#define CCI_REG_ADDR_MASK'):header.index('/**\n * cci_read()')]
    tables=re.sub(r'^#include .*$', '',tables,flags=re.M)
    original=function(parent,'imx681_s_ctrl').replace('imx681_s_ctrl','baseline_s_ctrl',1).replace('IMX681_REG_FRAME_LENGTH','LEGACY_FRAME_LENGTH')
    legacy=re.search(r'^#define IMX681_REG_FRAME_LENGTH\s+(.*)$',parent,re.M).group(1)
    setup='''
static int __v4l2_ctrl_handler_setup(struct v4l2_ctrl_handler *h)
{
 struct v4l2_ctrl c={.handler=h};
 for(int id=1;id<=4;id++) {
  c.id=id;c.val=id==1?setup_sensor->vblank_ctrl->val:(id==2?IMX681_EXPOSURE_DEF:(id==3?0:IMX681_DGAIN_DEF));
  int ret=imx681_s_ctrl(&c);if(ret)return ret;
 }
 return 0;
}
'''
    c='\n'.join([stub,macros,constants,tables,function(cci,'cci_write','int '),function(cci,'cci_multi_reg_write','int '),'#define LEGACY_FRAME_LENGTH '+legacy,original,function(text,'imx681_s_ctrl'),setup,function(text,'imx681_start_streaming'),harness])
    out.mkdir(parents=True,exist_ok=False);(out/'test.c').write_text(c)
    for k,cmd in [('compile',[a.compiler,'-std=c11','-Wall','-Wextra','-Werror','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(out/'test.c'),'-o',str(out/'test')]),('run',[str(out/'test')])]:
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=60);(out/(k+'.log')).write_text(p.stdout+p.stderr)
        if p.returncode:raise RuntimeError(k+' failed: '+p.stdout+p.stderr)
    result=json.loads(p.stdout);result.update(ok=True,compiler=a.compiler,sanitizers=['address','undefined'],sensor_sha256=m['sensor_sha256'],tables_sha256=m['tables_sha256'],scope='actual sensor constants, control/start and CCI write/multi-write bodies; modeled regmap/PM/control setup/unaligned helpers',installed=False,hardware_qualified=False)
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':
    try:main()
    except (ValueError,OSError,RuntimeError,subprocess.SubprocessError) as e:sys.exit(str(e))
