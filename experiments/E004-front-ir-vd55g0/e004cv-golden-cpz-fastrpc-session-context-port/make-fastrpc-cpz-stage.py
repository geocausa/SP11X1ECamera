#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib

SRC_SHA='b487ae3a9f58504cf969d296db662913b797cad98eb31c87e5e393860c558181'
UAPI_SHA='1b75dd9e95a2cda193cff7b9ba4a306642c9f6e1454bf99771b3a1e5862b1132'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def one(s,a,b,label):
    n=s.count(a)
    if n!=1: raise SystemExit(f'{label}: marker count {n}')
    return s.replace(a,b,1)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('stage1_source')
    ap.add_argument('golden_uapi')
    ap.add_argument('out_source')
    ap.add_argument('out_uapi')
    ns=ap.parse_args()
    src,uapi,out,outu=map(Path,(ns.stage1_source,ns.golden_uapi,ns.out_source,ns.out_uapi))
    if sha(src)!=SRC_SHA: raise SystemExit('E004cs FastRPC preimage hash mismatch')
    if sha(uapi)!=UAPI_SHA: raise SystemExit('Golden FastRPC UAPI preimage hash mismatch')

    h=uapi.read_text()
    marker='#endif /* __QCOM_FASTRPC_H__ */\n'
    add='''/* E004cv: Qualcomm downstream session-info ABI, compile-only stage. */
#define FASTRPC_IOCTL_INVOKE2_E004CV _IOWR('R', 18, struct fastrpc_ioctl_invoke2_e004cv)
#define FASTRPC_INVOKE2_SESS_INFO_E004CV 6
#define FASTRPC_REMOTE_PD_DEFAULT_UNUSED 0
#define FASTRPC_REMOTE_PD_CPZ_USER 6
#define FASTRPC_REMOTE_PD_USER 7
#define FASTRPC_REMOTE_PD_MAX 9

struct fastrpc_proc_sess_info_e004cv {
\t__u32 domain_id;
\t__u32 session_id;
\t__u32 pd_type;
\t__u32 sharedcb;
};

struct fastrpc_ioctl_invoke2_e004cv {
\t__u32 req;
\t__u32 reserved0;
\t__u64 invparam;
\t__u32 size;
\t__s32 err;
};

'''
    h=one(h,marker,add+marker,'uapi append')
    outu.write_text(h)

    s=src.read_text()
    s=one(s,'#include <linux/completion.h>\n','#include <linux/capability.h>\n#include <linux/completion.h>\n','capability include')
    s=one(s,'#include <uapi/misc/fastrpc.h>\n','#include "fastrpc-e004cv-uapi.h"\n#include "sp11-cpz-dmabuf-query.h"\n','local staged uapi')

    old='''\tu64 raddr;\n\tu32 attr;\n\tstruct kref refcount;\n};\n'''
    new='''\tu64 raddr;\n\tu32 attr;\n\tbool protected;\n\tstruct kref refcount;\n};\n'''
    s=one(s,old,new,'map protected flag')

    old='''\tint client_id;\n\tint pd;\n\tint pd_type;\n\tbool is_secure_dev;\n'''
    new='''\tint client_id;\n\tint pd;\n\tint pd_type;\n\tpid_t opener_tgid;\n\tbool session_config_locked;\n\tbool is_secure_dev;\n'''
    s=one(s,old,new,'user authority state')

    old='''\tfl->cctx = cctx;\n\tfl->is_secure_dev = fdevice->secure;\n\t/* E004cs: staged only. No ioctl/DT path can select a nonzero type. */\n\tfl->pd_type = FASTRPC_PD_TYPE_DEFAULT_UNUSED;\n'''
    new='''\tfl->cctx = cctx;\n\tfl->is_secure_dev = fdevice->secure;\n\tfl->opener_tgid = current->tgid;\n\tfl->session_config_locked = false;\n\t/* E004cv still has no DT path that can create a typed context bank. */\n\tfl->pd_type = FASTRPC_PD_TYPE_DEFAULT_UNUSED;\n'''
    s=one(s,old,new,'open authority state')

    # Exact protected dma-buf classification comes from the E004cu provider, not SECUREMAP.
    old='''\tmap->buf = dma_buf_get(fd);\n\tif (IS_ERR(map->buf)) {\n\t\terr = PTR_ERR(map->buf);\n\t\tgoto get_err;\n\t}\n\n\tmap->attach = dma_buf_attach(map->buf, sess->dev);\n'''
    new='''\tmap->buf = dma_buf_get(fd);\n\tif (IS_ERR(map->buf)) {\n\t\terr = PTR_ERR(map->buf);\n\t\tgoto get_err;\n\t}\n\n\tmap->protected = sp11_cpz_dma_buf_is_protected(map->buf);\n\tif (map->protected) {\n\t\t/* Protected ownership is provider-authoritative; legacy SECUREMAP is forbidden. */\n\t\tif ((attr & FASTRPC_ATTR_SECUREMAP) || !fl->is_secure_dev ||\n\t\t    fl->pd_type != FASTRPC_PD_TYPE_CPZ_USER || !fl->sctx ||\n\t\t    fl->sctx->pd_type != FASTRPC_PD_TYPE_CPZ_USER) {\n\t\t\terr = -EACCES;\n\t\t\tgoto attach_err;\n\t\t}\n\t}\n\n\tmap->attach = dma_buf_attach(map->buf, sess->dev);\n'''
    s=one(s,old,new,'protected import classification')

    old='''\tif (attr & FASTRPC_ATTR_SECUREMAP)\n\t\tmap->dma_addr = sg_phys(map->table->sgl);\n\telse\n\t\tmap->dma_addr = fastrpc_compute_dma_addr(fl, sg_dma_address(map->table->sgl));\n'''
    new='''\tif (map->protected)\n\t\tmap->dma_addr = fastrpc_compute_dma_addr(fl, sg_dma_address(map->table->sgl));\n\telse if (attr & FASTRPC_ATTR_SECUREMAP)\n\t\tmap->dma_addr = sg_phys(map->table->sgl);\n\telse\n\t\tmap->dma_addr = fastrpc_compute_dma_addr(fl, sg_dma_address(map->table->sgl));\n'''
    s=one(s,old,new,'protected dma address')
    s=one(s,'\tmap->va = sg_virt(map->table->sgl);\n','\tmap->va = map->protected ? NULL : sg_virt(map->table->sgl);\n','no HLOS va for protected map')

    # Atomic context-bank rebinding before a process is created.
    marker='''static void fastrpc_session_free(struct fastrpc_channel_ctx *cctx,\n\t\t\t\t struct fastrpc_session_ctx *session)\n{\n\tunsigned long flags;\n\n\tspin_lock_irqsave(&cctx->lock, flags);\n\tsession->used = false;\n\tspin_unlock_irqrestore(&cctx->lock, flags);\n}\n'''
    helper=marker+'''\nstatic int fastrpc_session_rebind_pd_type(struct fastrpc_user *fl, int pd_type)\n{\n\tstruct fastrpc_channel_ctx *cctx = fl->cctx;\n\tstruct fastrpc_session_ctx *old = fl->sctx, *target = NULL;\n\tunsigned long flags;\n\tint i;\n\n\tspin_lock_irqsave(&cctx->lock, flags);\n\tif (old && old->valid && old->pd_type == pd_type) {\n\t\ttarget = old;\n\t\tgoto out;\n\t}\n\tfor (i = 0; i < cctx->sesscount; i++) {\n\t\tif (!cctx->session[i].used && cctx->session[i].valid &&\n\t\t    cctx->session[i].pd_type == pd_type) {\n\t\t\ttarget = &cctx->session[i];\n\t\t\tbreak;\n\t\t}\n\t}\n\tif (!target) {\n\t\tspin_unlock_irqrestore(&cctx->lock, flags);\n\t\treturn -ENODEV;\n\t}\n\ttarget->used = true;\n\tif (old)\n\t\told->used = false;\n\tfl->sctx = target;\n\tfl->client_id = (int)(target - cctx->session) + 1;\nout:\n\tspin_unlock_irqrestore(&cctx->lock, flags);\n\treturn 0;\n}\n'''
    s=one(s,marker,helper,'session rebind helper')

    # Session-info control: exact downstream shape, but stronger CPZ authority gate.
    marker='''static long fastrpc_device_ioctl(struct file *file, unsigned int cmd,\n\t\t\t\t unsigned long arg)\n'''
    handler='''static int fastrpc_set_session_info_e004cv(struct fastrpc_user *fl,\n\t\t\t\t\t struct fastrpc_proc_sess_info_e004cv *info)\n{\n\tbool delegated;\n\tint ret;\n\n\tif (info->domain_id != fl->cctx->domain_id || info->sharedcb)\n\t\treturn -EINVAL;\n\tif (info->pd_type <= FASTRPC_REMOTE_PD_DEFAULT_UNUSED ||\n\t    info->pd_type >= FASTRPC_REMOTE_PD_MAX)\n\t\treturn -EINVAL;\n\n\tdelegated = current->tgid != fl->opener_tgid;\n\tif (delegated && info->pd_type != FASTRPC_REMOTE_PD_USER)\n\t\treturn -EACCES;\n\n\t/* E004cv only authorizes ordinary USERPD or the camera CPZ candidate. */\n\tif (info->pd_type != FASTRPC_REMOTE_PD_USER &&\n\t    info->pd_type != FASTRPC_REMOTE_PD_CPZ_USER)\n\t\treturn -EOPNOTSUPP;\n\n\tif (info->pd_type == FASTRPC_REMOTE_PD_CPZ_USER &&\n\t    (delegated || !capable(CAP_SYS_ADMIN) || !fl->is_secure_dev ||\n\t     fl->cctx->domain_id != CDSP_DOMAIN_ID))\n\t\treturn -EACCES;\n\n\tmutex_lock(&fl->mutex);\n\tif (fl->session_config_locked) {\n\t\tmutex_unlock(&fl->mutex);\n\t\treturn -EBUSY;\n\t}\n\n\tret = fastrpc_session_rebind_pd_type(fl, info->pd_type);\n\tif (!ret) {\n\t\tfl->pd_type = info->pd_type;\n\t\tfl->session_config_locked = true;\n\t\tinfo->session_id = fl->sctx->sid;\n\t}\n\tmutex_unlock(&fl->mutex);\n\treturn ret;\n}\n\nstatic int fastrpc_invoke2_session_info_e004cv(struct fastrpc_user *fl, char __user *argp)\n{\n\tstruct fastrpc_ioctl_invoke2_e004cv inv2;\n\tstruct fastrpc_proc_sess_info_e004cv info;\n\tvoid __user *param;\n\tint ret;\n\n\tif (copy_from_user(&inv2, argp, sizeof(inv2)))\n\t\treturn -EFAULT;\n\tif (inv2.req != FASTRPC_INVOKE2_SESS_INFO_E004CV ||\n\t    inv2.size != sizeof(info) || inv2.err)\n\t\treturn -EINVAL;\n\tparam = u64_to_user_ptr(inv2.invparam);\n\tif (copy_from_user(&info, param, sizeof(info)))\n\t\treturn -EFAULT;\n\tret = fastrpc_set_session_info_e004cv(fl, &info);\n\tif (ret)\n\t\treturn ret;\n\tif (copy_to_user(param, &info, sizeof(info)))\n\t\treturn -EFAULT;\n\treturn 0;\n}\n\nstatic void fastrpc_lock_session_config_e004cv(struct fastrpc_user *fl)\n{\n\tmutex_lock(&fl->mutex);\n\tfl->session_config_locked = true;\n\tmutex_unlock(&fl->mutex);\n}\n\n'''+marker
    s=one(s,marker,handler,'session-info handlers')

    # Lock session selection before every process init/attach attempt.
    for case in ('FASTRPC_IOCTL_INIT_ATTACH','FASTRPC_IOCTL_INIT_ATTACH_SNS','FASTRPC_IOCTL_INIT_CREATE_STATIC','FASTRPC_IOCTL_INIT_CREATE'):
        old=f'\tcase {case}:\n'
        new=old+'\t\tfastrpc_lock_session_config_e004cv(fl);\n'
        s=one(s,old,new,f'lock {case}')

    old='''\tcase FASTRPC_IOCTL_GET_DSP_INFO:\n\t\terr = fastrpc_get_dsp_info(fl, argp);\n\t\tbreak;\n'''
    new=old+'''\tcase FASTRPC_IOCTL_INVOKE2_E004CV:\n\t\terr = fastrpc_invoke2_session_info_e004cv(fl, argp);\n\t\tbreak;\n'''
    s=one(s,old,new,'invoke2 session ioctl')

    # Preserve the compile-proof roots even though driver registration is disabled.
    # This emits the authority/import code into the object without creating any runtime entrypoint.
    s=one(s,'static int fastrpc_map_attach(struct fastrpc_user *fl, int fd,\n',
          'static __used int fastrpc_map_attach(struct fastrpc_user *fl, int fd,\n',
          'emit protected import proof')
    s=one(s,'static int fastrpc_set_session_info_e004cv(struct fastrpc_user *fl,\n',
          'static __used int fastrpc_set_session_info_e004cv(struct fastrpc_user *fl,\n',
          'emit session authority proof')
    s=one(s,'static int fastrpc_invoke2_session_info_e004cv(struct fastrpc_user *fl, char __user *argp)\n',
          'static __used int fastrpc_invoke2_session_info_e004cv(struct fastrpc_user *fl, char __user *argp)\n',
          'emit session ioctl proof')

    # Build-only: no driver registration if the object is accidentally linked.
    s=one(s,'module_init(fastrpc_init);\n','/* E004cv compile-only: FastRPC driver registration disabled. */\n','disable module init')
    s=one(s,'module_exit(fastrpc_exit);\n','/* E004cv compile-only: FastRPC driver unregister hook disabled. */\n','disable module exit')
    s=s.replace('static int fastrpc_init(void)','static int __maybe_unused fastrpc_init(void)',1)
    s=s.replace('static void fastrpc_exit(void)','static void __maybe_unused fastrpc_exit(void)',1)

    out.write_text(s)
    print('E004cv FastRPC CPZ session/context scaffold: PASS')
    print('stage1_sha='+sha(src))
    print('golden_uapi_sha='+sha(uapi))
    print('out_source_sha='+sha(out))
    print('out_uapi_sha='+sha(outu))

if __name__=='__main__': main()
