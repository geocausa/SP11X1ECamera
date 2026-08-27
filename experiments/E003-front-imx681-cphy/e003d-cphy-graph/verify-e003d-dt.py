#!/usr/bin/env python3
import hashlib,re,subprocess,sys,tempfile
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
CAMPORT='/soc@0/isp@acb7000/ports/port@2'
CAMEND=CAMPORT+'/endpoint'
SENSOR='/soc@0/cci@ac16000/i2c-bus@1/camera@10'
SENPORT=SENSOR+'/port'
SENEND=SENPORT+'/endpoint'
ALLOWED_NODES={CAMPORT,CAMEND,SENPORT,SENEND}
SYMS={'camss_csiphy2_ep','imx681_ep'}
def allowed_prop(p,k): return (p=='/__symbols__' and k in SYMS) or p in ALLOWED_NODES
an,ap=parse(decomp(BASE));bn,bp=parse(decomp(CAND)); aph=phmap(ap);bph=phmap(bp)
nc=sorted(an^bn); pc=[]; rr=[]
for k in sorted(set(ap)|set(bp)):
 if ap.get(k)!=bp.get(k):
  z=(k[0],k[1],ap.get(k),bp.get(k));pc.append(z)
  if renum(z[2],z[3],aph,bph):rr.append(z)
bad_nodes=[x for x in nc if x not in ALLOWED_NODES]
bad_props=[x for x in pc if not allowed_prop(x[0],x[1]) and x not in rr]
print('baseline_sha256='+hashlib.sha256(Path(BASE).read_bytes()).hexdigest())
print('candidate_sha256='+hashlib.sha256(Path(CAND).read_bytes()).hexdigest())
print('node_changes='+str(len(nc)))
print('property_changes='+str(len(pc)))
print('phandle_renumber_only='+str(len(rr)))
print('unexpected_nodes='+str(len(bad_nodes)))
print('unexpected_properties='+str(len(bad_props)))
if bad_nodes:
 print('BAD_NODES'); print('\n'.join(bad_nodes))
if bad_props:
 print('BAD_PROPS'); [print(x) for x in bad_props]
if bad_nodes or bad_props: raise SystemExit(20)
def sx(path,prop):return run('fdtget','-t','x',CAND,path,prop).split()
def si(path,prop):return [int(x,16) for x in sx(path,prop)]
def ss(path,prop):return run('fdtget','-t','s',CAND,path,prop)
def sym(n):return ss('/__symbols__',n)
def ph(path):return si(path,'phandle')[0]
def children(path):return run('fdtget','-l',CAND,path,check=False).split()
def req(c,m):
 if not c:raise SystemExit('VERIFY_FAIL: '+m)
req(set(nc)==ALLOWED_NODES,'node delta is not exactly the four intended graph nodes')
req(sym('camss_csiphy2_ep')==CAMEND,'camss_csiphy2_ep symbol path')
req(sym('imx681_ep')==SENEND,'imx681_ep symbol path')
req(si(CAMPORT,'reg')==[2],'CAMSS port@2 reg')
for p in (CAMEND,SENEND):
 req(si(p,'bus-type')==[1],p+' C-PHY bus-type')
 req(si(p,'data-lanes')==[0],p+' one zero-based trio')
req(si(CAMEND,'remote-endpoint')==[ph(SENEND)],'CAMSS remote endpoint reciprocal')
req(si(SENEND,'remote-endpoint')==[ph(CAMEND)],'sensor remote endpoint reciprocal')
req(set(children('/soc@0/isp@acb7000/ports'))=={'port@1','port@2'},'CAMSS ports must be rear port@1 + front port@2 only')
req(children(SENSOR)==['port'],'front sensor must gain only one port child')
# E003d is topology-only: no link frequency metadata is introduced yet.
for p in (CAMEND,SENEND):
 req(run('fdtget','-p',CAND,p).find('link-frequencies')<0,p+' unexpectedly has link-frequencies')
print('E003D_DT_SCOPE=PASS')
