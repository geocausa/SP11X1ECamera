#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, shutil
C_SHA='9937c99567878507e03e213a0b89b2f2c1b31dec1ac89c0342deb387de467c33'
H_SHA='7c946d7e6509af94b9902f17e572153db88956a815d5897f3730a3abbe647d04'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def one(s,old,new,label):
 n=s.count(old)
 if n!=1: raise SystemExit(f'{label}: marker count {n}')
 return s.replace(old,new,1)
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('source_root'); ap.add_argument('out_root'); ns=ap.parse_args()
 src=Path(ns.source_root); out=Path(ns.out_root)
 csrc=src/'drivers/firmware/qcom/qcom_scm.c'; hsrc=src/'include/linux/firmware/qcom/qcom_scm.h'
 if sha(csrc)!=C_SHA: raise SystemExit('qcom_scm.c hash mismatch')
 if sha(hsrc)!=H_SHA: raise SystemExit('qcom_scm.h public hash mismatch')
 (out/'include/linux/firmware/qcom').mkdir(parents=True,exist_ok=True)
 c=csrc.read_text(); h=hsrc.read_text()
 structs='''struct qcom_scm_current_perm_info {\n\t__le32 vmid;\n\t__le32 perm;\n\t__le64 ctx;\n\t__le32 ctx_size;\n\t__le32 unused;\n};\n\nstruct qcom_scm_mem_map_info {\n\t__le64 mem_addr;\n\t__le64 mem_size;\n};\n\n'''
 if c.count(structs)!=1: raise SystemExit('private struct block mismatch')
 c=c.replace(structs,'',1)
 marker='''struct qcom_scm_vmperm {\n\tint vmid;\n\tint perm;\n};\n'''
 add=marker+'''\n/* Multi-region ownership descriptors used by Qualcomm MP/HYP_ASSIGN. */\nstruct qcom_scm_current_perm_info {\n\t__le32 vmid;\n\t__le32 perm;\n\t__le64 ctx;\n\t__le32 ctx_size;\n\t__le32 unused;\n};\n\nstruct qcom_scm_mem_map_info {\n\t__le64 mem_addr;\n\t__le64 mem_size;\n};\n\nstatic inline void qcom_scm_populate_vmperm_info(\n\t\tstruct qcom_scm_current_perm_info *destvm, int vmid, int perm)\n{\n\tif (!destvm)\n\t\treturn;\n\tdestvm->vmid = cpu_to_le32(vmid);\n\tdestvm->perm = cpu_to_le32(perm);\n\tdestvm->ctx = 0;\n\tdestvm->ctx_size = 0;\n\tdestvm->unused = 0;\n}\n\nstatic inline void qcom_scm_populate_mem_map_info(\n\t\tstruct qcom_scm_mem_map_info *mem, phys_addr_t addr, size_t size)\n{\n\tif (!mem)\n\t\treturn;\n\tmem->mem_addr = cpu_to_le64(addr);\n\tmem->mem_size = cpu_to_le64(size);\n}\n'''
 h=one(h,marker,add,'public structs')
 proto='''int qcom_scm_assign_mem(phys_addr_t mem_addr, size_t mem_sz, u64 *src,\n\t\t\tconst struct qcom_scm_vmperm *newvm,\n\t\t\tunsigned int dest_cnt);\n'''
 newproto=proto+'''int qcom_scm_assign_mem_regions(const struct qcom_scm_mem_map_info *mem_regions,\n\t\t\t\tsize_t mem_regions_sz, const u32 *srcvms, size_t src_sz,\n\t\t\t\tconst struct qcom_scm_current_perm_info *newvms,\n\t\t\t\tsize_t newvms_sz);\n'''
 h=one(h,proto,newproto,'public prototype')
 anchor='''EXPORT_SYMBOL_GPL(qcom_scm_assign_mem);\n\n/**\n * qcom_scm_ocmem_lock_available() - is OCMEM lock/unlock interface available\n'''
 fn='''EXPORT_SYMBOL_GPL(qcom_scm_assign_mem);\n\n/**\n * qcom_scm_assign_mem_regions() - reassign several physical memory regions.\n *\n * The public descriptors are copied into the same SCM TZ-memory pool used by\n * qcom_scm_assign_mem(), so the secure call never consumes caller kmalloc or\n * vmalloc addresses directly. This is the multi-region form required by\n * secure_buffer-style SG batching.\n */\nint qcom_scm_assign_mem_regions(const struct qcom_scm_mem_map_info *mem_regions,\n\t\t\t\tsize_t mem_regions_sz, const u32 *srcvms, size_t src_sz,\n\t\t\t\tconst struct qcom_scm_current_perm_info *newvms,\n\t\t\t\tsize_t newvms_sz)\n{\n\tphys_addr_t ptr_phys, mem_phys, src_phys, dest_phys;\n\tsize_t mem_off = 0;\n\tsize_t src_off, dest_off, ptr_sz;\n\t__le32 *src;\n\tunsigned int i, nr_src;\n\n\tif (!__scm)\n\t\treturn -EPROBE_DEFER;\n\tif (!mem_regions || !mem_regions_sz || !srcvms || !src_sz ||\n\t    !newvms || !newvms_sz ||\n\t    mem_regions_sz % sizeof(*mem_regions) ||\n\t    src_sz % sizeof(*srcvms) || newvms_sz % sizeof(*newvms))\n\t\treturn -EINVAL;\n\n\tsrc_off = ALIGN(mem_regions_sz, SZ_64);\n\tdest_off = src_off + ALIGN(src_sz, SZ_64);\n\tptr_sz = dest_off + ALIGN(newvms_sz, SZ_64);\n\n\tvoid *ptr __free(qcom_tzmem) = qcom_tzmem_alloc(__scm->mempool,\n\t\t\t\t\t\t\tptr_sz, GFP_KERNEL);\n\tif (!ptr)\n\t\treturn -ENOMEM;\n\n\tptr_phys = qcom_tzmem_to_phys(ptr);\n\tmem_phys = ptr_phys + mem_off;\n\tsrc_phys = ptr_phys + src_off;\n\tdest_phys = ptr_phys + dest_off;\n\n\tmemcpy(ptr + mem_off, mem_regions, mem_regions_sz);\n\tsrc = ptr + src_off;\n\tnr_src = src_sz / sizeof(*srcvms);\n\tfor (i = 0; i < nr_src; i++)\n\t\tsrc[i] = cpu_to_le32(srcvms[i]);\n\tmemcpy(ptr + dest_off, newvms, newvms_sz);\n\n\treturn __qcom_scm_assign_mem(__scm->dev, mem_phys, mem_regions_sz,\n\t\t\t\t     src_phys, src_sz, dest_phys, newvms_sz);\n}\nEXPORT_SYMBOL_GPL(qcom_scm_assign_mem_regions);\n\n/**\n * qcom_scm_ocmem_lock_available() - is OCMEM lock/unlock interface available\n'''
 c=one(c,anchor,fn,'regions function')
 (out/'qcom_scm-e004ct.c').write_text(c)
 (out/'include/linux/firmware/qcom/qcom_scm.h').write_text(h)
 print('E004ct qcom_scm multi-region scaffold generation: PASS')
 print('base_c_sha='+sha(csrc)); print('scaffold_c_sha='+sha(out/'qcom_scm-e004ct.c'))
 print('base_h_sha='+sha(hsrc)); print('scaffold_h_sha='+sha(out/'include/linux/firmware/qcom/qcom_scm.h'))
if __name__=='__main__': main()
