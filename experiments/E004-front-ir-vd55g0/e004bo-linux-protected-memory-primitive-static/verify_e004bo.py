#!/usr/bin/env python3
from pathlib import Path
import json,sys

d=Path(__file__).resolve().parent
def need(v,m):
    if not v:
        print("E004bo VERIFY: FAIL - "+m); sys.exit(1)

r=json.loads((d/"RESULT.json").read_text())
need(r["status"]=="PASS_STATIC_PRIMITIVE_INVENTORY_LOW_LEVEL_ASSIGN_PRESENT_NO_PROTECTED_HEAP","status")

scm=(d/"evidence/QCOM-SCM-ASSIGN-MEM.txt").read_text(errors="replace")
for x in (
    "qcom_scm_assign_mem() - Make a secure call to reassign memory ownership",
    "int qcom_scm_assign_mem(phys_addr_t mem_addr, size_t mem_sz",
    "QCOM_SCM_VMID_CP_CAMERA",
    "QCOM_SCM_VMID_CP_CAMERA_PREVIEW",
    "QCOM_SCM_PERM_READ",
    "QCOM_SCM_PERM_WRITE",
):
    need(x in scm,"SCM evidence missing "+x)

rb=(d/"evidence/ASSIGN-ROLLBACK-PRECEDENTS.txt").read_text(errors="replace")
for x in (
    "FASTRPC secure-map assign + free-path reclaim",
    "dst_perms[1].vmid",
    "perm.vmid = QCOM_SCM_VMID_HLOS",
    "RMTFS known physical reserved region + remove-time reclaim",
    "rmtfs_mem->addr = rmem->base",
    "remoteproc PAS known physical resource + unassign",
    "pas->region_assign_phys[offset] = res.start",
):
    need(x in rb,"rollback precedent missing "+x)

heap=(d/"evidence/DMA-HEAP-INVENTORY.txt").read_text(errors="replace")
for x in (
    "cma_heap.c",
    "system_heap.c",
    "RESTRICTED_OR_SECURE_HEAP_SOURCE_PRESENT=0",
    ".mmap = cma_heap_mmap",
    ".vmap = cma_heap_vmap",
    "struct sg_table sg_table",
    ".mmap = system_heap_mmap",
    ".vmap = system_heap_vmap",
):
    need(x in heap,"heap evidence missing "+x)

gap=(d/"evidence/CAMSS-DMA-VS-PHYS-GAP.txt").read_text(errors="replace")
for x in (
    "buffer->addr[i] = sg_dma_address(sgt->sgl);",
    "These macros should be used after a dma_map_sg call has been done",
    "to get bus addresses",
    'compatible = "qcom,x1e80100-camss";',
    "iommus = <0x3d",
    'compatible = "qcom,x1e80100-smmu-500"',
    "platform acb7000.isp: Adding to iommu group 8",
    "iommu: Default domain type: Translated",
    "dma_set_mask_and_coherent(dev, 0xffffffff)",
):
    need(x in gap,"CAMSS address evidence missing "+x)

cfg=(d/"evidence/KERNEL-CONFIG.txt").read_text(errors="replace")
for x in (
    "CONFIG_DMABUF_HEAPS=y",
    "CONFIG_DMABUF_HEAPS_CMA=y",
    "CONFIG_DMABUF_HEAPS_SYSTEM=y",
    "CONFIG_QCOM_SCM=y",
    "CONFIG_QCOM_TZMEM=y",
    "CONFIG_ARM_SMMU=y",
    "CONFIG_IOMMU_SUPPORT=y",
    "CAMSS_DIRECT_ASSIGN_MEM_USER=0",
):
    need(x in cfg,"config evidence missing "+x)

need(r["kernel_facilities"]["qcom_scm_assign_mem_present"] is True,"SCM primitive")
need(r["kernel_facilities"]["restricted_dma_heap_present"] is False,"restricted heap")
need(r["allocator_assessment"]["cma_current_exporter_is_protected_backend"] is False,"CMA overclaim")
need(r["allocator_assessment"]["qcom_tzmem_is_bulk_camera_sample_allocator"] is False,"TZMEM overclaim")
need(r["camss_address_model"]["camss_attached_to_apps_smmu"] is True,"CAMSS SMMU")
need(r["camss_address_model"]["physical_and_camera_iova_must_be_separate_fields"] is True,"physical/IOVA split")
need(r["unresolved"]["external_sample_vmid"] is False,"VMID overclaim")
need(r["unresolved"]["protected_camss_smmu_context"] is False,"SMMU overclaim")
for k,v in r["safety"].items():
    need(v is False,"safety state "+k)

print("E004bo VERIFY: PASS")
print(" - qcom_scm_assign_mem exists as a physical-range ownership primitive")
print(" - existing Qualcomm users demonstrate explicit assign/reclaim transaction patterns")
print(" - current kernel has ordinary system/CMA heaps but no restricted/secure DMA heap")
print(" - qcom_tzmem is SCM plumbing, not the bulk camera-sample allocator")
print(" - SP11 CAMSS is SMMU-attached; its sg_dma_address is a DMA/bus address, not proof of physical identity")
print(" - future backend must track physical backing separately from CAMSS IOVA")
print(" - external camera VMID and protected SMMU context remain deliberately unresolved")
print(" - no secure runtime operation occurred")
