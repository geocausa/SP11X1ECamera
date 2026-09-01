#!/usr/bin/env python3
import argparse, hashlib, json, pathlib, struct

MAGIC=b'QTI Chromatix Header'
MODE_NAMES={0:'Default',1:'Sensor',2:'Usecase',3:'Feature1',4:'Feature2',5:'Scene',6:'Effect'}
USECASE_NAMES={0:'Preview',1:'Snapshot',2:'Video',3:'ZSL',4:'Liveshot'}
WANTED_MODULES=(
    'bpcabf41_ife_v2','demuxblklevel14_ife_v2','gamma15_ife_v2','gic31_ife_v2',
    'gtm13_ife_v2','lsc41_ife_v2','pdpc31_ife_v2','wb20_ife_v2',
    'dsx10_ife_video_full_dc4_v2')


def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha(p): return sha_bytes(p.read_bytes())
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]

def parse_header(b):
    if not b.startswith(MAGIC): raise ValueError('not QTI Chromatix')
    file_len=u32(b,0x1c)
    version=[u16(b,0x20),u16(b,0x22),u16(b,0x24)]
    parser=b[0x28:0x50].split(b'\0')[0].decode('ascii','replace')
    module=b[0x58:0x98].split(b'\0')[0].decode('ascii','replace')
    root_count=u32(b,0x98)
    header_bytes=u32(b,0xa0)
    nsec=u32(b,0xa4)
    if header_bytes != 0xa8: raise ValueError(f'unexpected header size {header_bytes:#x}')
    if nsec != 3: raise ValueError(f'unexpected section count {nsec}')
    sections=[]
    p=header_bytes
    for i in range(nsec):
        tag,off,size=struct.unpack_from('<3I',b,p+i*12)
        if tag != i: raise ValueError(f'section tag drift {tag} != {i}')
        sections.append({'index':i,'tag':tag,'offset':off,'size':size,'end':off+size})
    if file_len != len(b)-4: raise ValueError('file length field mismatch')
    for i,s in enumerate(sections):
        if s['end'] > file_len: raise ValueError('section outside file')
        if i and s['offset'] != sections[i-1]['end']: raise ValueError('sections not contiguous')
    return {'bytes':len(b),'len_field':file_len,'version':version,'parser_signature':parser,
            'module_name':module,'root_count':root_count,'header_bytes':header_bytes,
            'section_count':nsec,'sections':sections}

def parse_selector_index(b,sec):
    raw=b[sec['offset']:sec['end']]
    if len(raw)%20: raise ValueError('selector index is not 20-byte records')
    recs=[struct.unpack_from('<5I',raw,i) for i in range(0,len(raw),20)]
    if len(recs)%17: raise ValueError('selector record count is not groups of 17')
    groups=[]
    for gi in range(0,len(recs),17):
        g=recs[gi:gi+17]
        if [r[2] for r in g] != list(range(17)): raise ValueError(f'group {gi//17}: slot sequence')
        sels={r[1] for r in g}
        if len(sels)!=1: raise ValueError(f'group {gi//17}: selector drift')
        if any(r[4]!=0xffffffff for r in g): raise ValueError(f'group {gi//17}: sentinel drift')
        sel=next(iter(sels)); mode=sel&0xffff; sub=sel>>16
        parent=g[0][3]
        groups.append({'group':gi//17,'first_symbol_id':g[0][0], 'last_symbol_id':g[-1][0],
                       'selector_raw':sel,'mode':mode,'mode_name':MODE_NAMES.get(mode,'Unknown'),
                       'submode':sub,'submode_name':USECASE_NAMES.get(sub) if mode==2 else None,
                       'parent_symbol_id':parent,'slot_parent_ids':[r[3] for r in g]})
    roots={g['first_symbol_id']:g['group'] for g in groups}
    for g in groups: g['parent_group']=roots.get(g['parent_symbol_id'])
    return {'record_bytes':20,'records':len(recs),'slots_per_group':17,'groups':groups}

def parse_symbol_table(b,sec,objsec):
    # Parameter Parser V3.4 section 0 is fixed-width ParameterFileSymbolTableEntry data:
    #   u32 ID; char Type[32]; u32 Version; u32 ModeId; u32 Mode;
    #   u32 DataOffset(relative to section 1); u32 DataBytes.
    recsz=56
    if sec['size']%recsz: raise ValueError('symbol table is not 56-byte records')
    records={}
    for p in range(sec['offset'],sec['end'],recsz):
        sid=u32(b,p)
        name=b[p+4:p+36].split(b'\0',1)[0].decode('ascii','replace')
        version,mode_id,mode_symbol_id,data_offset,data_bytes=struct.unpack_from('<5I',b,p+36)
        if sid in records: raise ValueError(f'duplicate SymbolTableID {sid:#x}')
        if data_offset+data_bytes>objsec['size']:
            raise ValueError(f'SymbolTableID {sid:#x} data outside section1')
        records[sid]={'symbol_id':sid,'type':name,'record_offset':p,'version_raw':version,
                      'version_major':version&0xffff,'version_minor':version>>16,
                      'mode_id':mode_id,'mode_symbol_id':mode_symbol_id,
                      'data_offset':data_offset,'data_bytes':data_bytes,
                      'data_abs_offset':objsec['offset']+data_offset}
    ids=sorted(records)
    return records,{'record_bytes':recsz,'records':len(records),'first_symbol_id':ids[0],
                    'last_symbol_id':ids[-1]}

def module_records(records,index):
    groups=index['groups']
    sym2group={s:g['group'] for g in groups for s in range(g['first_symbol_id'],g['last_symbol_id']+1)}
    out=[]
    for r in records.values():
        if r['type'] not in WANTED_MODULES: continue
        x=dict(r); x['selector_group']=sym2group.get(r['mode_symbol_id'])
        if x['selector_group'] is not None:
            g=groups[x['selector_group']]
            x['selector']={'mode':g['mode'],'mode_name':g['mode_name'],'submode':g['submode'],
                           'submode_name':g.get('submode_name')}
        else: x['selector']=None
        out.append(x)
    return sorted(out,key=lambda x:(x['type'],x['symbol_id']))

def ancestry(index,target_group):
    by={g['group']:g for g in index['groups']}; out=[]; seen=set(); cur=target_group
    while cur is not None and cur not in seen:
        seen.add(cur); g=by[cur]; out.append(g)
        nxt=g.get('parent_group'); cur=None if nxt==cur else nxt
    out.reverse(); return out

def effective_modules_for_group(index,mods,target_group):
    chain=ancestry(index,target_group)
    allowed={g['group']:depth for depth,g in enumerate(chain)}
    best={}
    for r in mods:
        g=r.get('selector_group')
        if g not in allowed: continue
        depth=allowed[g]
        if r['type'] not in best or depth>best[r['type']][0]: best[r['type']]=(depth,r)
    return {name:r for name,(depth,r) in sorted(best.items())}

def data_bytes(b,objsec,r):
    s=objsec['offset']+r['data_offset']; return b[s:s+r['data_bytes']]

def child_refs(b,objsec,records,r):
    # For module/trigger records, pointer entries are serialized as SymbolTableIDs.
    # Do not recursively scan region payloads: large numeric LUTs can coincide with IDs.
    if r['type'] in ('region','revision','control_var_type') or r['data_bytes']==0: return []
    raw=data_bytes(b,objsec,r); refs=[]
    for o in range(0,len(raw)-3,4):
        sid=struct.unpack_from('<I',raw,o)[0]
        c=records.get(sid)
        if sid>=0x400 and c is not None and c['data_bytes']>=0:
            refs.append({'at':o,'symbol_id':sid,'type':c['type']})
    # Keep order but remove duplicate same-offset/ID only (duplicates across offsets are meaningful).
    return refs

def summarize_node(b,objsec,records,sid,depth=0,seen=None,maxdepth=16):
    if seen is None: seen=set()
    r=records[sid]; raw=data_bytes(b,objsec,r)
    out={'symbol_id':sid,'type':r['type'],'data_offset':r['data_offset'],
         'data_abs_offset':r['data_abs_offset'],'data_bytes':r['data_bytes'],
         'data_sha256':sha_bytes(raw)}
    if r['type']=='region':
        vals=[]
        for o in range(0,len(raw)-3,4): vals.append(struct.unpack_from('<f',raw,o)[0])
        finite=[x for x in vals if x==x and abs(x)!=float('inf')]
        out['region_summary']={'float_words':len(vals),'first_floats':vals[:12],
                               'last_floats':vals[-12:] if vals else [],
                               'min_float':min(finite) if finite else None,
                               'max_float':max(finite) if finite else None}
        return out
    refs=child_refs(b,objsec,records,r); out['pointer_refs']=refs
    if depth>=maxdepth or sid in seen: return out
    nseen=set(seen); nseen.add(sid); children=[]
    for ref in refs:
        cid=ref['symbol_id']
        if cid not in nseen: children.append(summarize_node(b,objsec,records,cid,depth+1,nseen,maxdepth))
    if children: out['children']=children
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('tuning'); ap.add_argument('--sensor-module'); ap.add_argument('--out')
    a=ap.parse_args(); p=pathlib.Path(a.tuning); b=p.read_bytes(); h=parse_header(b)
    idx=parse_selector_index(b,h['sections'][2])
    records,sym_summary=parse_symbol_table(b,h['sections'][0],h['sections'][1])
    mods=module_records(records,idx)
    sensor2=[g for g in idx['groups'] if g['mode']==1 and g['submode']==2]
    if len(sensor2)!=1: raise ValueError('Sensor2 branch not unique')
    s2=sensor2[0]
    by={g['group']:g for g in idx['groups']}
    descendants=[]
    for g in idx['groups']:
        q=g; seen=set()
        while q.get('parent_group') is not None and q['group'] not in seen:
            seen.add(q['group'])
            if q['parent_group']==s2['group']:
                descendants.append(g); break
            q=by[q['parent_group']]
    usecases={g['submode']:g for g in descendants if g['mode']==2}
    required=(0,1,2)
    if any(x not in usecases for x in required): raise ValueError('Sensor2 Preview/Snapshot/Video branches incomplete')
    effective={}
    for uc in required:
        effective[USECASE_NAMES[uc]]=effective_modules_for_group(idx,mods,usecases[uc]['group'])
    sigs={uc:{n:(r['symbol_id'],r['data_offset'],r['data_bytes']) for n,r in m.items()} for uc,m in effective.items()}
    invariant=(sigs['Preview']==sigs['Snapshot']==sigs['Video'])
    if not invariant: raise ValueError('required Sensor2 IFE modules differ by usecase; active usecase must be resolved')
    video=effective['Video']
    if set(video)!=set(WANTED_MODULES):
        raise ValueError(f'effective module set mismatch: {sorted(video)}')
    # Exact root-pointer invariants observed in the Surface V3.4 blob.
    expected_refs={
        'bpcabf41_ife_v2':(0x44d,0x44e,0x44f),
        'gtm13_ife_v2':(0x497,0x498,0x499),
        'lsc41_ife_v2':(0x4b0,0x4b1,0x4b2),
    }
    for name,expect in expected_refs.items():
        got=tuple(x['symbol_id'] for x in child_refs(b,h['sections'][1],records,video[name]))
        if got!=expect: raise ValueError(f'{name}: root pointer drift {got} != {expect}')
    pointer_graph={name:summarize_node(b,h['sections'][1],records,r['symbol_id']) for name,r in video.items()}
    result={'accepted':True,'schema':'sp11-e003h-imx681-chromatix-container-v2',
            'tuning':{'path':str(p),'sha256':sha(p),**h},'sensor_module':None,
            'symbol_table':sym_summary,'selector_index':idx,'required_module_records':mods,
            'front_branch':{'proven_sensor_mode':2,'sensor_group':s2,'descendant_groups':descendants,
                            'active_usecase':'UNRESOLVED_BUT_REQUIRED_IFE_MODULES_USECASE_INVARIANT',
                            'required_ife_modules_usecase_invariant':invariant,
                            'effective_required_ife_modules':video,
                            'runtime_request6_authorized':False},
            'pointer_graph':pointer_graph,
            'policy':{'offline_only':True,'request6_generated':False,'request6_executed':False}}
    if a.sensor_module:
        sp=pathlib.Path(a.sensor_module); sb=sp.read_bytes(); result['sensor_module']={'path':str(sp),'sha256':sha(sp),**parse_header(sb)}
    text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if a.out: pathlib.Path(a.out).write_text(text)
    else: print(text,end='')
if __name__=='__main__': main()
