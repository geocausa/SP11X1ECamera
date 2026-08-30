#!/usr/bin/env python3
import argparse, hashlib, json, sys
from pathlib import Path

ALLOWED={'WINDOWS_OBSERVED','WINDOWS_REVERSED','LINUX_IMPLEMENTATION','UNVERIFIED'}

def sha256(path: Path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser(description='Fail-closed provenance gate for SP11 front Windows-parity work')
    ap.add_argument('--manifest',default='provenance/front-parity.json')
    ap.add_argument('--target',choices=['bounded_first_pix','production_parity'],default='bounded_first_pix')
    ap.add_argument('--repo',default='.')
    a=ap.parse_args()
    root=Path(a.repo).resolve(); mf=root/a.manifest
    try: data=json.loads(mf.read_text(encoding='utf-8'))
    except Exception as e: print(f'FAIL manifest read: {e}',file=sys.stderr); return 2
    errors=[]; blockers=[]; counts={k:0 for k in ALLOWED}
    if data.get('schema')!='sp11-front-parity-provenance-v1': errors.append('unexpected manifest schema')
    for f in data.get('facts',[]):
        fid=f.get('id','<missing-id>'); c=f.get('classification')
        if c not in ALLOWED: errors.append(f'{fid}: invalid classification {c!r}'); continue
        counts[c]+=1
        ev=f.get('evidence') or []
        if c in {'WINDOWS_OBSERVED','WINDOWS_REVERSED'} and not ev:
            errors.append(f'{fid}: Windows fact has no evidence')
        if c=='LINUX_IMPLEMENTATION':
            if f.get('parity_claim') is not False: errors.append(f'{fid}: Linux implementation must set parity_claim=false')
            if not f.get('equivalence_basis'): errors.append(f'{fid}: Linux implementation missing equivalence_basis')
        for e in ev:
            rel=e.get('path'); exp=e.get('sha256')
            if not rel or not exp: errors.append(f'{fid}: incomplete evidence record'); continue
            ep=root/rel
            if not ep.is_file(): errors.append(f'{fid}: missing evidence {rel}'); continue
            got=sha256(ep)
            if got.lower()!=exp.lower(): errors.append(f'{fid}: evidence drift {rel}: {got} != {exp}')
        crit='runtime_critical' if a.target=='bounded_first_pix' else 'production_critical'
        if f.get(crit) and c=='UNVERIFIED': blockers.append(fid)
    # A rejected upstream/reference candidate may never be treated as accepted proof in this manifest.
    for r in data.get('rejected_unproven_candidates',[]):
        if r.get('status')!='REJECTED_AS_PROOF': errors.append(f"rejected candidate state drift: {r}")
    print('PROVENANCE_COUNTS ' + ' '.join(f'{k}={counts[k]}' for k in sorted(counts)))
    if errors:
        for e in errors: print('FAIL '+e,file=sys.stderr)
        return 2
    if blockers:
        print(f'BLOCK target={a.target}: ' + ', '.join(blockers),file=sys.stderr)
        return 3
    print(f'PASS target={a.target}: no critical UNVERIFIED facts')
    return 0
if __name__=='__main__': raise SystemExit(main())
