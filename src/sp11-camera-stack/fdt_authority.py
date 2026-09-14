#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,re,shutil,struct,subprocess
from pathlib import Path
MAGIC=0xd00dfeed; BEGIN=1; END_NODE=2; PROP=3; NOP=4; END=9
GOLDEN_SHA='2fcfa738c229b32764ff2722847cf4056b3153c64a12f8490429309f29df6d00'
CAND_SHA='019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f'
SAFE_NUMERIC={'reg','interrupts','#address-cells','#size-cells','clock-frequency','bus-type','data-lanes','drive-strength','regulator-min-microvolt','regulator-max-microvolt','regulator-initial-mode','#clock-cells','#reset-cells','#power-domain-cells'}
SEQ_REFS={'clocks':'#clock-cells','power-domains':'#power-domain-cells','interconnects':'#interconnect-cells','iommus':'#iommu-cells','dmas':'#dma-cells','phys':'#phy-cells','resets':'#reset-cells','mboxes':'#mbox-cells','interrupts-extended':'#interrupt-cells'}
LIST_REFS={'remote-endpoint','required-opps','interrupt-parent','memory-region','msi-parent'}

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def align4(n:int)->int:return (n+3)&~3
def u32s(b:bytes)->list[int]:
    if len(b)%4: raise ValueError('cell property length not multiple of 4')
    return list(struct.unpack('>'+('I'*(len(b)//4)),b)) if b else []
def cells(v:list[int])->bytes:return struct.pack('>'+('I'*len(v)),*v) if v else b''
def cstr(block:bytes,off:int)->str:return block[off:block.index(b'\0',off)].decode()

def parse_fdt(path:Path)->dict[str,dict[str,bytes]]:
    b=path.read_bytes(); hdr=struct.unpack('>10I',b[:40]);
    if hdr[0]!=MAGIC: raise ValueError('bad fdt magic '+str(path))
    _,_,so,stro,_,_,_,_,strsz,structsz=hdr; st=b[so:so+structsz]; ss=b[stro:stro+strsz]
    out={}; stack=[]; i=0
    while i<len(st):
        tok=struct.unpack('>I',st[i:i+4])[0]; i+=4
        if tok==BEGIN:
            z=st.index(b'\0',i); name=st[i:z].decode(); i=align4(z+1)
            if not stack: pathn='/'
            else: pathn=(stack[-1].rstrip('/')+'/'+name) if stack[-1]!='/' else '/'+name
            stack.append(pathn); out.setdefault(pathn,{})
        elif tok==END_NODE: stack.pop()
        elif tok==PROP:
            ln,no=struct.unpack('>II',st[i:i+8]); i+=8; data=st[i:i+ln]; i=align4(i+ln)
            out[stack[-1]][cstr(ss,no)]=data
        elif tok==NOP: pass
        elif tok==END: break
        else: raise ValueError(f'unknown token {tok:#x} at {i-4:#x}')
    return out

def phandle_map(tree):
    bynum={}; bypath={}
    for p,pr in tree.items():
        v=pr.get('phandle',pr.get('linux,phandle'))
        if v is not None:
            n=u32s(v)[0]; bynum[n]=p; bypath[p]=n
    return bynum,bypath

def prop_list(path:Path,node:str)->list[str]:
    cp=subprocess.run(['fdtget','-p',str(path),node],text=True,capture_output=True,check=True)
    return [x for x in cp.stdout.splitlines() if x]
def set_raw(dt:Path,node:str,prop:str,data:bytes):
    args=['fdtput','-t','bx',str(dt),node,prop,*[f'{x:x}' for x in data]]
    subprocess.run(args,check=True)
def create_node(dt:Path,node:str): subprocess.run(['fdtput','-p','-c',str(dt),node],check=True)

def provider_arg_cells(ctree,cph,provider:int,cellprop:str)->int:
    path=cph.get(provider)
    if path is None: raise ValueError(f'unknown provider phandle {provider:#x}')
    raw=ctree[path].get(cellprop)
    if raw is None: raise ValueError(f'{path} missing {cellprop}')
    vals=u32s(raw)
    if len(vals)!=1: raise ValueError(f'{path} malformed {cellprop}')
    return vals[0]

def is_list_ref(prop:str)->bool:
    return prop in LIST_REFS or re.fullmatch(r'pinctrl-[0-9]+',prop) is not None or prop.endswith('-supply')
def seq_cellprop(prop:str)->str|None:
    if prop in SEQ_REFS:return SEQ_REFS[prop]
    if prop=='gpios' or prop.endswith('-gpios'):return '#gpio-cells'
    return None

def remap_ref_property(prop:str,data:bytes,ctree,cph,remap)->bytes:
    vals=u32s(data)
    if is_list_ref(prop):
        out=[]
        for x in vals:
            if x not in remap: raise ValueError(f'{prop}: unmapped phandle {x:#x}')
            out.append(remap[x])
        return cells(out)
    cp=seq_cellprop(prop)
    if cp:
        out=[];i=0
        while i<len(vals):
            provider=vals[i]
            if provider not in remap: raise ValueError(f'{prop}: unmapped provider {provider:#x}')
            n=provider_arg_cells(ctree,cph,provider,cp)
            if i+1+n>len(vals): raise ValueError(f'{prop}: truncated specifier')
            out.append(remap[provider]); out.extend(vals[i+1:i+1+n]); i+=1+n
        return cells(out)
    return data

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--golden',type=Path,required=True);ap.add_argument('--candidate',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    if sha(a.golden)!=GOLDEN_SHA:raise SystemExit('Golden DTB identity drift: '+sha(a.golden))
    if sha(a.candidate)!=CAND_SHA:raise SystemExit('candidate DTB identity drift: '+sha(a.candidate))
    g=parse_fdt(a.golden); c=parse_fdt(a.candidate); gs=set(g); cs=set(c); added=sorted(cs-gs,key=lambda p:(p.count('/'),p))
    if len(added)!=31 or gs-cs:raise SystemExit(f'node-set authority drift added={len(added)} golden_only={len(gs-cs)}')
    # Existing common-node property names must match except camera symbol aliases.
    common_extra={}
    for p in sorted(gs&cs):
        ge=set(g[p]);ce=set(c[p]);
        if ge!=ce:common_extra[p]=(sorted(ge-ce),sorted(ce-ge))
    if set(common_extra)!={'/__symbols__'} or common_extra['/__symbols__'][0]:raise SystemExit('unexpected common property-set delta '+repr(common_extra))
    symbol_add=common_extra['/__symbols__'][1]
    cph,cpath=phandle_map(c); gph,gpath=phandle_map(g)
    # Every common phandle-bearing path maps by path; added phandles get collision-free numbers above Golden max.
    remap={}
    for p in sorted(gs&cs):
        if p in cpath:
            if p not in gpath:raise SystemExit('common phandle path absent in Golden '+p)
            remap[cpath[p]]=gpath[p]
    nextph=max(gph)+1
    added_ph={}
    for p in added:
        if p in cpath:
            added_ph[p]=nextph;remap[cpath[p]]=nextph;nextph+=1
    # Audit numeric properties so no unclassified phandle-bearing property silently slips through.
    for p in added:
        for prop,data in c[p].items():
            if prop in ('phandle','linux,phandle') or is_list_ref(prop) or seq_cellprop(prop):continue
            if len(data)%4==0 and data and b'\0' not in data and prop not in SAFE_NUMERIC:
                vals=u32s(data)
                hits=[x for x in vals if x in cph]
                if hits:raise SystemExit(f'unclassified possible phandle property {p}:{prop} hits={hits}')
    shutil.copyfile(a.golden,a.out)
    for p in added:create_node(a.out,p)
    for p in added:
        for prop,data in c[p].items():
            if prop=='phandle' or prop=='linux,phandle':
                if p not in added_ph:raise SystemExit('missing new phandle '+p)
                set_raw(a.out,p,prop,cells([added_ph[p]]))
            elif is_list_ref(prop) or seq_cellprop(prop):
                set_raw(a.out,p,prop,remap_ref_property(prop,data,c,cph,remap))
            else:set_raw(a.out,p,prop,data)
    # Preserve camera-only symbols as path strings; all pre-existing Golden symbol bytes stay untouched.
    for prop in symbol_add:set_raw(a.out,'/__symbols__',prop,c['/__symbols__'][prop])
    out=parse_fdt(a.out); oph,opath=phandle_map(out)
    if len(oph)!=len(set(oph)):raise SystemExit('duplicate phandle')
    print('HV_BUILD=PASS')
    print('GOLDEN_SHA256='+sha(a.golden));print('SOURCE_FRONT_SHA256='+sha(a.candidate));print('OUTPUT_SHA256='+sha(a.out))
    print('GOLDEN_NODES='+str(len(g))+' OUTPUT_NODES='+str(len(out))+' ADDED='+str(len(set(out)-set(g))))
    print('GOLDEN_MAX_PHANDLE='+hex(max(gph))+' ADDED_PHANDLE_RANGE='+hex(min(added_ph.values()))+'..'+hex(max(added_ph.values())))
    print('SYMBOL_ALIASES_ADDED='+str(len(symbol_add)))
if __name__=='__main__':main()
