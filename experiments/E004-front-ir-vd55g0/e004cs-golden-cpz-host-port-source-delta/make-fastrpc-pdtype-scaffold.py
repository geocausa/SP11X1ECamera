#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, shutil
BASE_SHA='e2410813bdab7ca71d972749bd3da8040a53e0fc35bf472983b5254220d5dcb2'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def one(s, old, new, label):
 if s.count(old)!=1: raise SystemExit(f'{label} marker count={s.count(old)}')
 return s.replace(old,new,1)
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('source'); ap.add_argument('output'); ns=ap.parse_args()
 src=Path(ns.source); out=Path(ns.output)
 if sha(src)!=BASE_SHA: raise SystemExit('Golden fastrpc.c hash mismatch')
 out.parent.mkdir(parents=True,exist_ok=True)
 s=src.read_text()
 old='''#define ROOT_PD\t\t(0)\n#define USER_PD\t\t(1)\n#define SENSORS_PD\t(2)\n'''
 new=old+'''\n/* E004cs staged PD-type vocabulary. No user ABI or DT binding yet. */\nenum fastrpc_remote_pd_type {\n\tFASTRPC_PD_TYPE_DEFAULT_UNUSED = 0,\n\tFASTRPC_PD_TYPE_ROOT = 1,\n\tFASTRPC_PD_TYPE_AUDIO_STATIC = 2,\n\tFASTRPC_PD_TYPE_SENSORS_STATIC = 3,\n\tFASTRPC_PD_TYPE_SECURE_STATIC = 4,\n\tFASTRPC_PD_TYPE_OIS_STATIC = 5,\n\tFASTRPC_PD_TYPE_CPZ_USER = 6,\n\tFASTRPC_PD_TYPE_USER = 7,\n\tFASTRPC_PD_TYPE_GUEST_OS_SHARED = 8,\n\tFASTRPC_PD_TYPE_MAX,\n};\n'''
 s=one(s,old,new,'pd enum')
 old='''struct fastrpc_session_ctx {\n\tstruct device *dev;\n\tint sid;\n\tbool used;\n\tbool valid;\n};\n'''
 new='''struct fastrpc_session_ctx {\n\tstruct device *dev;\n\tint sid;\n\tint pd_type;\n\tbool used;\n\tbool valid;\n};\n'''
 s=one(s,old,new,'session field')
 old='''\tint client_id;\n\tint pd;\n\tbool is_secure_dev;\n'''
 new='''\tint client_id;\n\tint pd;\n\tint pd_type;\n\tbool is_secure_dev;\n'''
 s=one(s,old,new,'user field')
 old='''static struct fastrpc_session_ctx *fastrpc_session_alloc(\n\t\t\t\t\tstruct fastrpc_user *fl)\n'''
 new='''static struct fastrpc_session_ctx *fastrpc_session_alloc(\n\t\t\t\t\tstruct fastrpc_user *fl, int pd_type)\n'''
 s=one(s,old,new,'allocator signature')
 old='''\tfor (i = 0; i < cctx->sesscount; i++) {\n\t\tif (!cctx->session[i].used && cctx->session[i].valid) {\n'''
 new='''\tfor (i = 0; i < cctx->sesscount; i++) {\n\t\tif (!cctx->session[i].used && cctx->session[i].valid &&\n\t\t    (pd_type == FASTRPC_PD_TYPE_DEFAULT_UNUSED ||\n\t\t     cctx->session[i].pd_type == pd_type)) {\n'''
 s=one(s,old,new,'allocator match')
 old='''\tfl->cctx = cctx;\n\tfl->is_secure_dev = fdevice->secure;\n\n\tfl->sctx = fastrpc_session_alloc(fl);\n'''
 new='''\tfl->cctx = cctx;\n\tfl->is_secure_dev = fdevice->secure;\n\t/* E004cs: staged only. No ioctl/DT path can select a nonzero type. */\n\tfl->pd_type = FASTRPC_PD_TYPE_DEFAULT_UNUSED;\n\n\tfl->sctx = fastrpc_session_alloc(fl, fl->pd_type);\n'''
 s=one(s,old,new,'device open')
 old='''\tsess->used = false;\n\tsess->valid = true;\n\tsess->dev = dev;\n'''
 new='''\tsess->used = false;\n\tsess->valid = true;\n\tsess->pd_type = FASTRPC_PD_TYPE_DEFAULT_UNUSED;\n\tsess->dev = dev;\n'''
 s=one(s,old,new,'cb default')
 out.write_text(s)
 print('E004cs FastRPC PD-type scaffold generation: PASS')
 print('base_sha='+sha(src)); print('scaffold_sha='+sha(out))
if __name__=='__main__': main()
