#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, shutil

BASE_VIDEO_SHA = "2eb92e872b4bc4f0aaa2e17197707ca270e3f5f8b8d8460952599631c9b76df4"
BASE_HEADER_SHA = "69fdbb6364a772d5b9fe50114878bbc7a1a1ffc61e62af1e71c79fd16e94c982"

HEADER = r'''/* SPDX-License-Identifier: GPL-2.0 */
/*
 * Compile-only protected camera lifetime contract.
 *
 * No backend, selector, control, ioctl or secure-memory operation exists here.
 * The three ownership domains are intentionally represented separately:
 * queue policy, per-sample protected backing, and secure-lane ownership.
 */
#ifndef QC_MSM_CAMSS_PROTECTED_SAMPLE_H
#define QC_MSM_CAMSS_PROTECTED_SAMPLE_H

#include <linux/build_bug.h>
#include <linux/types.h>

struct device;
struct vb2_buffer;

#define CAMSS_PROTECTED_SAMPLE_ID_BYTES 16
#define CAMSS_PROTECTED_SAMPLE_MAX_PLANES 3

enum camss_sample_backing {
	CAMSS_SAMPLE_BACKING_STANDARD = 0,
	CAMSS_SAMPLE_BACKING_PROTECTED = 1,
};

/*
 * Queue policy is not a memory allocator.  A future protected queue must
 * explicitly prohibit CPU-visible fallback and ordinary SG fallback.
 */
struct camss_protected_queue_contract {
	bool cpu_mappable;
	bool ordinary_sg_fallback;
	bool read_io_allowed;
	bool mmap_io_allowed;
	bool dmabuf_import_requires_protected_proof;
};

struct camss_protected_sample {
	u8 id[CAMSS_PROTECTED_SAMPLE_ID_BYTES];
	dma_addr_t addr[CAMSS_PROTECTED_SAMPLE_MAX_PLANES];
	size_t size[CAMSS_PROTECTED_SAMPLE_MAX_PLANES];
	unsigned int num_planes;
	void *backend_handle;
	bool prepared;
};

/* One protected allocation/object lifetime. */
struct camss_protected_sample_ops {
	int (*prepare)(struct device *dev, struct vb2_buffer *vb,
		       struct camss_protected_sample *sample);
	void (*release)(struct device *dev,
			struct camss_protected_sample *sample);
};

/*
 * Secure lane ownership is deliberately not part of sample_ops.
 * It brackets streaming/hardware ownership rather than VB2 buffer lifetime.
 */
struct camss_secure_lane_ops {
	int (*acquire)(struct device *dev);
	void (*release)(struct device *dev);
};

struct camss_protected_lifecycle_contract {
	struct camss_protected_queue_contract queue;
	const struct camss_protected_sample_ops *sample_ops;
	const struct camss_secure_lane_ops *lane_ops;
};

/*
 * Compile-time only.  No lifecycle contract instance exists in E004bn and no
 * runtime code calls any operation above.
 */
static inline void camss_protected_lifecycle_compile_contract(void)
{
	BUILD_BUG_ON(CAMSS_PROTECTED_SAMPLE_ID_BYTES != 16);
	BUILD_BUG_ON(CAMSS_PROTECTED_SAMPLE_MAX_PLANES != 3);
}

#endif /* QC_MSM_CAMSS_PROTECTED_SAMPLE_H */
'''

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("output")
    ns=ap.parse_args()
    src=Path(ns.source); out=Path(ns.output)
    if sha(src/"camss-video.c") != BASE_VIDEO_SHA:
        raise SystemExit("camss-video.c base hash mismatch")
    if sha(src/"camss-video.h") != BASE_HEADER_SHA:
        raise SystemExit("camss-video.h base hash mismatch")
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(src,out)

    c=out/"camss-video.c"
    text=c.read_text()
    marker='#include "camss-video.h"\n'
    if text.count(marker)!=1:
        raise SystemExit("include marker mismatch")
    text=text.replace(marker,marker+'#include "camss-protected-sample.h"\n',1)

    hook='\tstruct vb2_queue *q;\n\tint ret;\n\n\tvdev = &video->vdev;\n'
    hooked='\tstruct vb2_queue *q;\n\tint ret;\n\n\tcamss_protected_lifecycle_compile_contract();\n\tvdev = &video->vdev;\n'
    if text.count(hook)!=1:
        raise SystemExit("register hook marker mismatch")
    c.write_text(text.replace(hook,hooked,1))
    (out/"camss-protected-sample.h").write_text(HEADER)

    print("E004bn lifecycle scaffold generation: PASS")
    print("base_video_sha="+sha(src/"camss-video.c"))
    print("scaffold_video_sha="+sha(c))
    print("contract_sha="+sha(out/"camss-protected-sample.h"))

if __name__=="__main__":
    main()
