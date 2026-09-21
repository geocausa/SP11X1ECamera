#!/usr/bin/env python3
"""E004kg fail-closed read-only media-graph state classifier; front RDI != PIX."""
import argparse
import re
from pathlib import Path

LINKS={
 'rear_phy': ('msm_csiphy1','msm_csid0',0),
 'rear_rdi': ('msm_csid0','msm_vfe0_rdi0',0),
 'front_phy': ('msm_csiphy2','msm_csid1',0),
 'front_pix': ('msm_csid1','msm_vfe1_pix',0),
 'front_rdi': ('msm_csid1','msm_vfe1_rdi0',0),
 'front_cross_rdi': ('msm_csid1','msm_vfe0_rdi0',0),
}
def media_block(text,name):
    match=re.search(rf'^- entity \d+: {re.escape(name)} \(.*?\)(.*?)(?=^- entity |\Z)',text,re.M|re.S)
    if not match:
        raise ValueError("MISSING_GRAPH_ENTITY_"+name)
    return match.group(1)
def classify(text):
    state={}
    for label,(src,dst,pad) in LINKS.items():
        source=media_block(text,src)
        match=re.search(rf'^\s*-> "{re.escape(dst)}":{pad} \[([^\]]*)\]\s*$',source,re.M)
        if not match:
            raise ValueError("MISSING_MUTABLE_LINK_"+label)
        state[label]='ENABLED' in {t.strip() for t in match.group(1).split(',')}
    rear=state['rear_phy'] or state['rear_rdi']
    front=state['front_phy'] or state['front_pix'] or state['front_rdi'] or state['front_cross_rdi']
    if state['front_cross_rdi']:
        name='invalid-cross-route'
    elif rear and front:
        name='invalid-mixed'
    elif state['rear_phy'] and state['rear_rdi']:
        name='rear-only'
    elif rear:
        name='invalid-partial'
    elif state['front_phy'] and state['front_rdi'] and not state['front_pix']:
        name='front-rdi-only'
    elif state['front_phy'] and state['front_pix'] and not state['front_rdi']:
        name='front-pix-only'
    elif front:
        name='invalid-partial'
    else:
        name='neutral'
    return name,state
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('topology',type=Path)
    parser.add_argument('--expect',choices=('neutral','rear-only','front-rdi-only','front-pix-only',
                                              'invalid-partial','invalid-mixed','invalid-cross-route'))
    a=parser.parse_args()
    name,values=classify(a.topology.read_text(errors='replace'))
    if a.expect and a.expect!=name:
        raise SystemExit(f'E004KG_GRAPH_STATE_MISMATCH expected={a.expect} actual={name} flags={values}')
    print('E004KG_MEDIA_ROUTE='+name+' '+' '.join(f'{k}={int(v)}' for k,v in values.items()))
if __name__=='__main__':
    main()
