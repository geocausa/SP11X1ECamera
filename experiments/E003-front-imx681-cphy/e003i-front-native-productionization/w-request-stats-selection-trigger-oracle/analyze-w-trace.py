#!/usr/bin/env python3
import argparse, json, re, struct, hashlib
from pathlib import Path
P_RE=re.compile(r'^E003IW PARSER n=(\d+).* raw=([0-9A-Fa-f]+) parsed=([0-9A-Fa-f]+) ')
L_RE=re.compile(r'^E003IW LSC n=(\d+).* frame=([0-9A-Fa-f]+) statsptr=([0-9A-Fa-f]+) ')
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('log',type=Path); a=ap.parse_args()
 data=a.log.read_bytes(); text=data.decode('utf-8',errors='replace').splitlines(); ev=[]; order=0
 for line in text:
  m=P_RE.match(line)
  if m: order+=1; ev.append(('P',order,int(m.group(1)),m.group(3).lower())); continue
  m=L_RE.match(line)
  if m: order+=1; ev.append(('L',order,int(m.group(1)),int(m.group(2),16),m.group(3).lower()))
 ps=[x for x in ev if x[0]=='P']; ls=[x for x in ev if x[0]=='L']; mapped=[]
 for l in ls:
  if int(l[4],16)==0: continue
  c=[p for p in ps if p[1]<l[1] and p[3]==l[4]]
  if not c: raise SystemExit(f'FAIL unmatched non-null LSC frame {l[3]} ptr {l[4]}')
  p=c[-1]; mapped.append((l[3],p[2],l[3]-p[2]))
 if len(mapped)!=104 or {x[2] for x in mapped}!={3}: raise SystemExit('FAIL mapping law drift')
 out={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'parser_hits':len(ps),'lsc_hits':len(ls),'mapped_nonnull':len(mapped),'delay_unique':sorted({x[2] for x in mapped}),'first_12':[{'request':r,'source_generation':g,'delta':d} for r,g,d in mapped[:12]]}
 print(json.dumps(out,indent=2))
if __name__=='__main__': main()
