#!/usr/bin/env python3
"""Run original and adapted IMX681 control code with PM/I2C fault injection."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path

def function(text, name):
    a=text.index('static int '+name+'(')
    b=text.index('{',a); level=1;c=b+1
    while level:
        level += (text[c]=='{')-(text[c]=='}');c+=1
    return text[a:c]
def pin(path, sha):
    if path.is_symlink() or not path.is_file():raise ValueError('not regular reference: '+str(path))
    data=path.read_bytes()
    if hashlib.sha256(data).hexdigest()!=sha:raise ValueError('reference changed: '+str(path))
    return data.decode()
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--reference-root',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    p.add_argument('--compiler',choices=['gcc','clang'],required=True)
    a=p.parse_args()
    root=Path(__file__).resolve().parents[1]
    src=root/'src/upstream/sensors/imx681-ooaklee'
    ref=json.loads((src/'reference.json').read_text())
    original=pin(a.reference_root/'drivers/media/i2c/imx681.c',ref['sensor_sha256'])
    pin(a.reference_root/'drivers/media/i2c/imx681-tables.h',ref['tables_sha256'])
    adapted=pin(src/'imx681.c',ref['adapted_sha256'])
    pin(src/'imx681-tables.h',ref['tables_sha256'])
    a.output.mkdir(exist_ok=False,parents=True)
    stub=r'''
#include <assert.h>
#include <errno.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#define container_of(p,t,m) ((t *)((char *)(p)-offsetof(t,m)))
#define min_t(t,a,b) ((t)(a)<(t)(b)?(t)(a):(t)(b))
#define IMX681_HEIGHT 2640
#define IMX681_EXPOSURE_MARGIN 48
#define IMX681_EXPOSURE_DEF 1600
#define V4L2_CID_VBLANK 1
#define V4L2_CID_EXPOSURE 2
#define V4L2_CID_ANALOGUE_GAIN 3
#define V4L2_CID_DIGITAL_GAIN 4
#define IMX681_REG_GROUP_HOLD 0x0104
#define IMX681_REG_FRAME_LENGTH 0x0340
#define IMX681_REG_EXPOSURE 0x0229
#define IMX681_REG_ANALOG_GAIN 0x0204
#define IMX681_REG_DIGITAL_GAIN 0x020e
struct v4l2_ctrl_handler { int unused; };
struct v4l2_ctrl { int id,val,minimum; struct v4l2_ctrl_handler *handler; };
struct imx681 { void *dev,*regmap; struct v4l2_ctrl_handler ctrl_handler; struct v4l2_ctrl *expo_ctrl; };
static int pm_result,range_result,pm_gets,pm_puts;
static int hold_error,payload_error,release_error,writes,release_attempts;
static int __v4l2_ctrl_modify_range(struct v4l2_ctrl *c,int min,int max,int step,int def)
{ (void)c;(void)min;(void)max;(void)step;(void)def; return range_result; }
static int pm_runtime_get_if_in_use(void *dev)
{ (void)dev;pm_gets++;return pm_result; }
static void pm_runtime_put_autosuspend(void *dev) { (void)dev;pm_puts++; }
static int cci_write(void *map, unsigned int reg, unsigned long long value,int *err)
{
 int ret;
 (void)map;
 if(err && *err)return *err;
 writes++;
 if(reg==IMX681_REG_GROUP_HOLD && !value) { release_attempts++;ret=release_error; }
 else if(reg==IMX681_REG_GROUP_HOLD)ret=hold_error;
 else ret=payload_error;
 if(err && ret)*err=ret;
 return ret;
}
'''
    baseline=function(original,'imx681_s_ctrl').replace('imx681_s_ctrl','baseline_s_ctrl',1)
    fixed=function(adapted,'imx681_s_ctrl')
    harness=r'''
static void reset_case(int pm,int range,int hold,int payload,int release)
{
 pm_result=pm;range_result=range;hold_error=hold;payload_error=payload;release_error=release;
 pm_gets=pm_puts=writes=release_attempts=0;
}
int main(void)
{
 struct v4l2_ctrl exposure={.minimum=8};
 struct imx681 sensor={.expo_ctrl=&exposure};
 struct v4l2_ctrl ctrl={.id=V4L2_CID_EXPOSURE,.val=1600,.handler=&sensor.ctrl_handler};
 const int pm_values[]={-EAGAIN,0,1,2};
 const int errors[]={0,-EIO,-EREMOTEIO};
 unsigned int cases=0;
 int expected,ret;
 reset_case(-EAGAIN,0,0,0,0);
 ret=baseline_s_ctrl(&ctrl);
 assert(ret==0 && writes==3 && pm_puts==1);
 reset_case(1,0,0,-EIO,0);
 ret=baseline_s_ctrl(&ctrl);
 assert(ret==-EIO && release_attempts==0);
 reset_case(1,0,-EREMOTEIO,0,0);
 ret=baseline_s_ctrl(&ctrl);
 assert(ret==-EREMOTEIO && release_attempts==0);
 for(unsigned int id=1;id<=5;id++)
 for(unsigned int p=0;p<4;p++)
 for(unsigned int rg=0;rg<2;rg++)
 for(unsigned int h=0;h<3;h++)
 for(unsigned int w=0;w<3;w++)
 for(unsigned int r=0;r<3;r++) {
  ctrl.id=(int)id;
  reset_case(pm_values[p],rg?-EINVAL:0,errors[h],errors[w],errors[r]);
  ret=imx681_s_ctrl(&ctrl);
  if(id==V4L2_CID_VBLANK && rg) {
   expected=-EINVAL;
   assert(pm_gets==0 && pm_puts==0 && writes==0);
  } else if(pm_values[p]<=0) {
   expected=pm_values[p];
   assert(pm_gets==1 && pm_puts==0 && writes==0);
  } else {
   expected=errors[h]?errors[h]:(id<=4 && errors[w]?errors[w]:errors[r]);
   assert(pm_gets==1 && pm_puts==1 && release_attempts==1);
   assert(writes==(id<=4 && !errors[h]?3:2));
  }
  assert(ret==expected);
  cases++;
 }
 printf("{\"baseline_counterexamples\":3,\"adapted_cases\":%u}\n",cases);
 return 0;
}
'''
    c=a.output/'control.c';c.write_text(stub+'\n'+baseline+'\n'+fixed+'\n'+harness)
    exe=a.output/'control'
    cmd=[a.compiler,'-std=c11','-Wall','-Wextra','-Werror','-O1','-g',
         '-fsanitize=address,undefined','-fno-omit-frame-pointer',str(c),'-o',str(exe)]
    r=subprocess.run(cmd,capture_output=True,text=True)
    (a.output/'compile.log').write_text(r.stdout+r.stderr)
    if r.returncode:raise RuntimeError(r.stderr)
    r=subprocess.run([str(exe)],capture_output=True,text=True)
    (a.output/'run.log').write_text(r.stdout+r.stderr)
    if r.returncode:raise RuntimeError(r.stdout+r.stderr)
    result=json.loads(r.stdout)
    result.update({'compiler':a.compiler,'sanitizers':['address','undefined'],'scope':'actual extracted s_ctrl; modeled PM, I2C and control-range helpers','ok':True})
    (a.output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
if __name__=='__main__':
    try:main()
    except (ValueError,RuntimeError) as e:sys.exit(str(e))
