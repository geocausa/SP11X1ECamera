#!/usr/bin/env python3
import re, subprocess, sys, tempfile
from pathlib import Path
BASE=sys.argv[1]; CAND=sys.argv[2]
HEX=re.compile(r'0x[0-9a-fA-F]+')

def run(*a,check=True):
 p=subprocess.run(a,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 if check and p.returncode: raise SystemExit(f'cmd fail {a}: {p.stderr}')
 return p.stdout.strip()
def decomp(p):
 with tempfile.NamedTemporaryFile(suffix='.dts') as f:
  run('dtc','-I','dtb','-O','dts','-s','-o',f.name,p)
  return Path(f.name).read_text()
def parse(t):
 nodes={'/'}; props={}; stack=[]; pending=[]
 def path(): return '/'+'/'.join(stack) if stack else '/'
 for raw in t.splitlines():
  x=raw.strip()
  if not x or x.startswith('/dts-v1/') or x.startswith('/memreserve/'): continue
  if pending:
   pending.append(x)
   if ';' not in x: continue
   st=' '.join(pending); pending=[]; key=st.split('=',1)[0].strip().rstrip(';'); props[(path(),key)]=st; continue
  if x==' };': pass
  if x=='};':
   if stack: stack.pop()
  elif x.endswith('{'):
   n=x[:-1].strip()
   if n=='/': stack=[]; nodes.add('/')
   else:
    if ':' in n:n=n.split(':',1)[1].strip()
    stack.append(n); nodes.add(path())
  elif ';' in x:
   key=x.split('=',1)[0].strip().rstrip(';'); props[(path(),key)]=x
  else: pending=[x]
 return nodes,props
def phmap(props):
 o={}
 for (p,k),v in props.items():
  if k=='phandle':
   z=HEX.findall(v)
   if len(z)==1:o[int(z[0],16)]=p
 return o
def renum(a,b,ap,bp):
 if a is None or b is None:return False
 if HEX.split(a)!=HEX.split(b):return False
 av=HEX.findall(a);bv=HEX.findall(b)
 if len(av)!=len(bv):return False
 saw=False
 for x,y in zip(av,bv):
  xi=int(x,16);yi=int(y,16)
  if xi==yi:continue
  saw=True
  if ap.get(xi) is None or ap.get(xi)!=bp.get(yi):return False
 return saw
CCI='/soc@0/cci@ac16000'
L7='/soc@0/rsc@17500000/regulators-0/ldo7'
L3='/soc@0/rsc@17500000/regulators-8/ldo3'
TL='/soc@0/pinctrl@f100000'
ALLOWED_NODES=(CCI,L7,L3,TL+'/cci1-master1-default-state',TL+'/cci1-master1-sleep-state',TL+'/front-imx681-default-state')
SYMS={'cci1','cci1_i2c0','cci1_i2c1','vreg_l7b_2p8','vreg_l3m_camera','cci1_master1_default','cci1_master1_sleep','front_imx681_default'}
def allowed_node(p): return any(p==x or p.startswith(x+'/') for x in ALLOWED_NODES)
def allowed_prop(p,k): return (p=='/__symbols__' and k in SYMS) or allowed_node(p)
an,ap=parse(decomp(BASE));bn,bp=parse(decomp(CAND)); aph=phmap(ap);bph=phmap(bp)
nc=sorted(an^bn); pc=[]; rr=[]
for k in sorted(set(ap)|set(bp)):
 if ap.get(k)!=bp.get(k):
  z=(k[0],k[1],ap.get(k),bp.get(k));pc.append(z)
  if renum(z[2],z[3],aph,bph):rr.append(z)
bn_bad=[x for x in nc if not allowed_node(x)]
bp_bad=[x for x in pc if not allowed_prop(x[0],x[1]) and x not in rr]
print('node_changes=',len(nc));print('property_changes=',len(pc));print('phandle_renumber_only=',len(rr));print('unexpected_nodes=',len(bn_bad));print('unexpected_properties=',len(bp_bad))
if bn_bad:
 print('BAD_NODES');print('\n'.join(bn_bad))
if bp_bad:
 print('BAD_PROPS')
 for x in bp_bad:print(x)
if bn_bad or bp_bad:raise SystemExit(20)

def sx(path,prop):return run('fdtget','-t','x',CAND,path,prop).split()
def si(path,prop):return [int(x,16) for x in sx(path,prop)]
def ss(path,prop):return run('fdtget','-t','s',CAND,path,prop)
def sym(n):return ss('/__symbols__',n)
def ph(n):return si(sym(n),'phandle')[0]
def props(path):return set(run('fdtget','-p',CAND,path).split())
def children(path):return run('fdtget','-l',CAND,path,check=False).split()
def req(c,m):
 if not c:raise SystemExit('VERIFY_FAIL: '+m)
req(sym('cci1')==CCI,'cci1 path')
req(ss(CCI,'compatible')=='qcom,x1e80100-cci qcom,msm8996-cci','cci1 compatible')
req(si(CCI,'reg')==[0,0x0ac16000,0,0x1000],'cci1 reg')
# GIC_SPI expands to 0, IRQ 271, edge rising 1.
req(si(CCI,'interrupts')==[0,271,1],'cci1 IRQ')
req(ss(CCI,'status')=='okay','cci1 enabled')
req(si(CCI+'/i2c-bus@1','clock-frequency')==[400000],'cci1 master1 400k')
front=CCI+'/i2c-bus@1/front-probe@10'
req(ss(front,'compatible')=='microsoft,sp11-imx681-probe','front compatible')
req(si(front,'reg')==[0x10],'front address')
req(children(front)==[],'front probe has no endpoint/port children')
req(si(front,'clocks')==[ph('camcc'),79],'MCLK4 phandle/id')
req(si(front,'reset-gpios')==[ph('tlmm'),237,1],'GPIO237 active-low')
req(si(front,'ldo3m-supply')==[ph('vreg_l3m_camera')],'LDO3M supply')
req(si(front,'ldo7b-supply')==[ph('vreg_l7b_2p8')],'LDO7B supply')
req(si(L3,'regulator-min-microvolt')==[1800000] and si(L3,'regulator-max-microvolt')==[1800000],'LDO3M voltage')
req(si(L7,'regulator-min-microvolt')==[2800000] and si(L7,'regulator-max-microvolt')==[2800000],'LDO7B voltage')
for n,bias in [('cci1_master1_default','bias-pull-up'),('cci1_master1_sleep','bias-pull-down')]:
 p=sym(n);req(ss(p,'pins')=='gpio235 gpio236',n+' pins');req(ss(p,'function')=='aon_cci',n+' function');req(si(p,'drive-strength')==[2],n+' drive');req(bias in props(p),n+' bias')
p=sym('front_imx681_default');m=p+'/mclk-pins';r=p+'/reset-pins'
req(ss(m,'pins')=='gpio100' and ss(m,'function')=='cam_aon','GPIO100 cam_aon')
req(si(m,'drive-strength')==[4] and 'bias-disable' in props(m) and 'output-enable' in props(m),'GPIO100 electrical')
req(ss(r,'pins')=='gpio237' and ss(r,'function')=='gpio','GPIO237 reset pinctrl')
# Explicit absence of a new front CAMSS graph: only existing R3 port@1 may be present.
camports='/soc@0/isp@acb7000/ports'
req(children(camports)==['port@1'],'CAMSS ports changed / front endpoint exists')
print('E003B_DT_SCOPE=PASS')
