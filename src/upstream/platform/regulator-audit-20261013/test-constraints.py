#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Reproduce camera voltage-constraint admission using pinned kernel bodies."""
import argparse,hashlib,json,re,subprocess,sys
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p,value):
    if p.is_symlink() or not p.is_file() or sha(p)!=value:raise ValueError('input changed or not regular: '+str(p))
    return p.read_text()
def function(t,name,static=True):
    a=t.index(('static int ' if static else 'int ')+name+'(');b=t.index('{',a);c=b+1;level=1
    while level:level+=(t[c]=='{')-(t[c]=='}');c+=1
    return t[a:c]
def ranges(t,name):
    a=t.index('static const struct rpmh_vreg_hw_data '+name+' = {');b=t.index('\n};',a)
    return [tuple(map(int,x)) for x in re.findall(r'REGULATOR_LINEAR_RANGE\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)',t[a:b])]
STUB=r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <limits.h>
#include <errno.h>
#define EPROBE_DEFER 517
#define ERR_PTR(x) ((void *)(intptr_t)(x))
#define rdev_err(d,...) ((void)(d))
#define rdev_info(d,...) ((void)(d))
#define rdev_dbg(d,...) ((void)(d))
#define DIV_ROUND_UP(n,d) (((n)+(d)-1)/(d))
#define RPMH_REGULATOR_REG_VRM_VOLTAGE 0
struct regulation_constraints { int min_uV,max_uV;bool apply_uV; };
struct regulator_dev;
struct regulator_ops { int (*list_voltage)(struct regulator_dev *,unsigned int); };
struct regulator_desc { const struct regulator_ops *ops;int n_voltages;bool continuous_voltage_range; };
struct rpmh_vreg { int enabled,voltage_selector;unsigned int addr; };
struct regulator_dev { struct regulator_desc *desc;struct regulation_constraints *constraints;struct rpmh_vreg *driver_data;const int *values; };
struct tcs_cmd { unsigned int addr,data;bool wait; };
static int requests,map_attempts;
static struct rpmh_vreg *rdev_get_drvdata(struct regulator_dev *d) { return d->driver_data; }
static int regulator_list_voltage_linear_range(struct regulator_dev *d,unsigned int s)
{ return s<(unsigned int)d->desc->n_voltages?d->values[s]:-EINVAL; }
static int rpmh_regulator_send_request(struct rpmh_vreg *v,struct tcs_cmd *c,bool wait)
{ (void)v;(void)c;(void)wait;requests++;return 0; }
'''
HELPERS=r'''
static int regulator_get_voltage_rdev(struct regulator_dev *d)
{
 int s=rpmh_regulator_vrm_get_voltage_sel(d);
 return s<0?s:regulator_list_voltage_linear_range(d,(unsigned int)s);
}
static int _regulator_do_set_voltage(struct regulator_dev *d,int lo,int hi)
{
 map_attempts++;
 for(unsigned int s=0;s<(unsigned int)d->desc->n_voltages;s++) {
  int v=regulator_list_voltage_linear_range(d,s);
  if(v>=lo && v<=hi)return rpmh_regulator_vrm_set_voltage_sel(d,s);
 }
 return -EINVAL;
}
'''
HARNESS=r'''
int main(void)
{
 const int *tables[]={values_pmic5_pldo,values_pmic5_pldo502ln,values_pmic5_pldo502,values_pmic5_nldo502};
 const int counts[]={256,32,256,128};
 const int targets[]={2900000,1800000,2800000,1200000};
 unsigned int cases=0;
 assert(values_pmic5_pldo[174]==2896000 && values_pmic5_pldo[175]==2904000);
 assert(values_pmic5_pldo[162]==2800000 && values_pmic5_pldo502ln[0]==1800000);
 for(int rail=0;rail<4;rail++)for(int old=0;old<2;old++)for(int scenario=0;scenario<6;scenario++) {
  int target=targets[rail];
  struct regulator_ops ops={.list_voltage=regulator_list_voltage_linear_range};
  struct regulator_desc desc={.ops=&ops,.n_voltages=counts[rail]};
  struct rpmh_vreg vreg={.enabled=-EINVAL,.voltage_selector=-ENOTRECOVERABLE};
  struct regulation_constraints c={.min_uV=target,.max_uV=target,.apply_uV=true};
  struct regulator_dev d={.desc=&desc,.constraints=&c,.driver_data=&vreg,.values=tables[rail]};
  if(scenario==1)c=(struct regulation_constraints){0};
  if(scenario==2)c=(struct regulation_constraints){.max_uV=target};
  if(scenario==3)c=(struct regulation_constraints){.min_uV=target};
  if(scenario==4)c=(struct regulation_constraints){.min_uV=target+8000,.max_uV=target,.apply_uV=true};
  /* Numerical range illustration only, not approved electrical tolerance. */
  if(scenario==5)c=(struct regulation_constraints){.min_uV=target-4000,.max_uV=target+4000,.apply_uV=true};
  requests=map_attempts=0;
  int ret=old?baseline_constraints(&d,&c):candidate_constraints(&d,&c);
  int expected=(scenario==1 || scenario==5 || (scenario==0 && rail!=0))?0:-EINVAL;
  if(old && ((scenario==0 && rail==0) || scenario==4))expected=-ENOTRECOVERABLE;
  assert(ret==expected && requests==0);
  if(scenario==0 && rail==0)assert(vreg.voltage_selector==-ENOTRECOVERABLE);
  if(scenario==0 && rail!=0)assert(regulator_get_voltage_rdev(&d)==target);
  if(scenario==5 && rail==0)assert(regulator_get_voltage_rdev(&d)==2896000 && c.min_uV==2896000 && c.max_uV==2904000);
  cases++;
 }
 printf("{\"constraint_cases\":%u,\"ldo16_exact_2900000_rejected\":true,\"front_1800000_2800000_selectors_supported\":true,\"voltage_stage_rpmh_requests\":0}\n",cases);
 return 0;
}
'''
def main():
    if sys.flags.optimize:raise ValueError('Python -O is not supported')
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline-source',required=True,type=Path)
    p.add_argument('--candidate-source',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    p.add_argument('--compiler',required=True,choices=['gcc','clang'])
    a=p.parse_args();q=Path(__file__).resolve().parent;m=json.loads((q/'reference.json').read_text())
    trees={}
    for label,root in [('baseline',a.baseline_source),('candidate',a.candidate_source)]:
        trees[label]={n:pin(root/n,h) for n,h in m['source_sha256'][label].items()}
    out=a.output.absolute()
    if any(x.is_symlink() for x in [out,*out.parents]):raise ValueError('symlink output path')
    out=out.resolve()
    if out.exists():raise ValueError('occupied output')
    for x in [q,a.baseline_source,a.candidate_source]:
        if out==x.resolve() or x.resolve() in out.parents:raise ValueError('output nested in input')
    core=trees['candidate']['drivers/regulator/core.c'];old=trees['baseline']['drivers/regulator/core.c'];driver=trees['candidate']['drivers/regulator/qcom-rpmh-regulator.c']
    mappings={'pm8550_vreg_data':{'ldo7':'pmic5_pldo','ldo16':'pmic5_pldo'},'pm8010_vreg_data':{'ldo1':'pmic5_nldo502','ldo3':'pmic5_pldo502ln','ldo5':'pmic5_pldo502','ldo6':'pmic5_pldo502ln'}}
    for label in ['baseline','candidate']:
        t=trees[label]['drivers/regulator/qcom-rpmh-regulator.c']
        for name,expected in mappings.items():
            start=t.index('static const struct rpmh_vreg_init_data '+name+'[]');end=t.index('\n};',start)
            actual=dict(re.findall(r'RPMH_VREG\("(ldo\d+)",\s*LDO,\s*\d+,\s*&([a-zA-Z0-9_]+)',t[start:end]))
            if any(actual.get(k)!=v for k,v in expected.items()):raise ValueError('PMIC rail mapping changed')
    arrays=[]
    for name in ['pmic5_pldo','pmic5_pldo502ln','pmic5_pldo502','pmic5_nldo502']:
        rr=ranges(driver,name)
        if rr!=ranges(trees['baseline']['drivers/regulator/qcom-rpmh-regulator.c'],name):raise ValueError('range differs between trees')
        values=[0]*(max(x[2] for x in rr)+1)
        for uv,lo,hi,step in rr:
            for s in range(lo,hi+1):values[s]=uv+(s-lo)*step
        arrays.append('static const int values_'+name+'[]={'+','.join(map(str,values))+'};')
    c='\n'.join([STUB,*arrays,*[function(driver,n) for n in ['_rpmh_regulator_vrm_set_voltage_sel','rpmh_regulator_vrm_set_voltage_sel','rpmh_regulator_vrm_get_voltage_sel']],HELPERS,function(old,'machine_constraints_voltage').replace('machine_constraints_voltage','baseline_constraints',1),function(core,'machine_constraints_voltage').replace('machine_constraints_voltage','candidate_constraints',1),HARNESS])
    out.mkdir(parents=True,exist_ok=False);(out/'audit.c').write_text(c)
    for name,cmd in [('compile',[a.compiler,'-std=c11','-Wall','-Wextra','-Werror','-Wno-sign-compare','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(out/'audit.c'),'-o',str(out/'audit')]),('run',[str(out/'audit')])]:
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=60);(out/(name+'.log')).write_text(r.stdout+r.stderr)
        if r.returncode:raise RuntimeError(name+' failed; see '+str(out/(name+'.log')))
    result=json.loads(r.stdout);result.update(ok=True,compiler=a.compiler,sanitizers=['address','undefined'],hardware_qualified=False,installed=False,scope='actual old/current core voltage-admission and current RPMh cache/set/get bodies; parsed actual rail mappings/ranges; modeled selector lookup, RPMh transport and registration surrounding stages',reference=m)
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':
    try:main()
    except (ValueError,OSError,RuntimeError,subprocess.SubprocessError) as e:sys.exit(str(e))
