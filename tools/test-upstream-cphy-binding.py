#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
import pathlib,copy,json,traceback,datetime,os,pwd
from dtschema import DTValidator
SELF=pathlib.Path(__file__).read_text()
import argparse,hashlib
ap=argparse.ArgumentParser(description='Validate C-PHY and D-PHY endpoint controls against the actual processed binding.')
ap.add_argument('--source',type=pathlib.Path,required=True)
ap.add_argument('--build',type=pathlib.Path,required=True)
ap.add_argument('--output',type=pathlib.Path,required=True)
a=ap.parse_args();S=a.source.resolve();B=a.build.resolve();T=a.output.absolute()
m=json.loads((pathlib.Path(__file__).resolve().parents[1]/'src/upstream/receiver/cphy-x1e-20261012/manifest.json').read_text())
name='Documentation/devicetree/bindings/phy/qcom,x1e80100-csi2-phy.yaml'
assert hashlib.sha256((S/name).read_bytes()).hexdigest()==m['output_source_sha256'][name]
assert not T.exists() and not T.is_symlink() and not T.resolve().is_relative_to(S) and not T.resolve().is_relative_to(B)
T.mkdir();(T/'runner.py').write_text(SELF)
result={'ok':False,'cases':[],'scope':'Actual processed kernel binding on decoded D-PHY example; transformed endpoint instances, not live firmware.'}
try:
 D=B/'Documentation/devicetree/bindings'
 validator=DTValidator([str(D/'processed-schema.json')])
 decoded=validator.decode_dtb((D/'phy/qcom,x1e80100-csi2-phy.example.dtb').read_bytes())
 def find(n):
  if not isinstance(n,dict):return None
  if 'compatible' in n and 'qcom,x1e80100-csi2-phy' in n['compatible']:return n
  for val in n.values():
   found=find(val)
   if found:return found
 node=next(found for root in decoded if (found:=find(root)))
 def test(name,ep,valid):
  instance=copy.deepcopy(node);instance['ports']['port@0']['endpoint']=ep
  errors=list(validator.iter_errors(instance,filter=['qcom,x1e80100-csi2-phy']))
  case={'name':name,'expected_valid':valid,'error_count':len(errors),'errors':[e.message for e in errors]}
  result['cases'].append(case);assert (len(errors)==0)==valid,name
 ep=node['ports']['port@0']['endpoint'];test('original-dphy-four-lanes',ep,True)
 cp=copy.deepcopy(ep);cp['bus-type']=1;cp['data-lanes']=[0];del cp['clock-lanes']
 test('cphy-one-trio-zero',cp,True)
 abc=copy.deepcopy(cp);abc['line-orders']=[0];test('cphy-one-trio-abc',abc,True)
 three=copy.deepcopy(cp);three['data-lanes']=[0,1,2];test('binding-cphy-three-trios-not-driver-admission',three,True)
 for name,prop,value in [('clock','clock-lanes',0),('polarity','lane-polarities',[0]),('empty','data-lanes',[]),('trio-three','data-lanes',[3]),('four-trios','data-lanes',[0,1,2,3]),('bad-bus','bus-type',3)]:
  bad=copy.deepcopy(cp);bad[prop]=value;test('reject-'+name,bad,False)
 bad=copy.deepcopy(ep);bad['data-lanes']=[0];test('reject-dphy-zero',bad,False)
 del bad['bus-type'];test('reject-default-dphy-zero',bad,False)
 result['ok']=True
except Exception as e:result['error']=repr(e);(T/'exception.log').write_text(traceback.format_exc())
result['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
(T/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'ok':result['ok'],'cases':len(result['cases']),'error':result.get('error')}))
