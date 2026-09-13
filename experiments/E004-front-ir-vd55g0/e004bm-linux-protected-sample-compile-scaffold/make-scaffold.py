#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, shutil, sys

BASE_VIDEO_SHA = "2eb92e872b4bc4f0aaa2e17197707ca270e3f5f8b8d8460952599631c9b76df4"
BASE_HEADER_SHA = "69fdbb6364a772d5b9fe50114878bbc7a1a1ffc61e62af1e71c79fd16e94c982"

HEADER = r'''/* SPDX-License-Identifier: GPL-2.0 */
/*
 * Compile-only protected-sample contract for CAMSS.
 *
 * This file intentionally contains no backend, no runtime selector and no
 * protected-memory operation.  It only fixes the object/lifetime interface
 * that a future platform backend must satisfy.
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

struct camss_protected_sample {
	u8 id[CAMSS_PROTECTED_SAMPLE_ID_BYTES];
	dma_addr_t addr[CAMSS_PROTECTED_SAMPLE_MAX_PLANES];
	size_t size[CAMSS_PROTECTED_SAMPLE_MAX_PLANES];
	unsigned int num_planes;
	void *backend_handle;
	bool prepared;
};

struct camss_protected_sample_ops {
	int (*prepare)(struct device *dev, struct vb2_buffer *vb,
		       struct camss_protected_sample *sample);
	void (*release)(struct device *dev,
			struct camss_protected_sample *sample);
};

/*
 * Compile-time only: there is deliberately no ops instance, feature switch,
 * queue selector or call to prepare/release in this checkpoint.
 */
static inline void camss_protected_sample_compile_contract(void)
{
	BUILD_BUG_ON(CAMSS_PROTECTED_SAMPLE_ID_BYTES != 16);
	BUILD_BUG_ON(CAMSS_PROTECTED_SAMPLE_MAX_PLANES != 3);
}

#endif /* QC_MSM_CAMSS_PROTECTED_SAMPLE_H */
'''

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("output")
    ns=ap.parse_args()
    src=Path(ns.source)
    out=Path(ns.output)
    vc=src/"camss-video.c"
    vh=src/"camss-video.h"
    if sha(vc)!=BASE_VIDEO_SHA or sha(vh)!=BASE_HEADER_SHA:
        raise SystemExit("base source hash mismatch")
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(src,out)

    c=out/"camss-video.c"
    text=c.read_text()
    marker='#include "camss-video.h"\n'
    replacement=marker+'#include "camss-protected-sample.h"\n'
    if text.count(marker)!=1:
        raise SystemExit("camss-video include marker mismatch")
    text=text.replace(marker,replacement,1)

    hook='\tstruct vb2_queue *q;\n\tint ret;\n\n\tvdev = &video->vdev;\n'
    hooked='\tstruct vb2_queue *q;\n\tint ret;\n\n\tcamss_protected_sample_compile_contract();\n\tvdev = &video->vdev;\n'
    if text.count(hook)!=1:
        raise SystemExit("msm_video_register hook marker mismatch")
    text=text.replace(hook,hooked,1)
    c.write_text(text)

    (out/"camss-protected-sample.h").write_text(HEADER)
    print("E004bm scaffold generation: PASS")
    print("base_video_sha="+sha(vc))
    print("base_header_sha="+sha(vh))
    print("scaffold_video_sha="+sha(c))
    print("scaffold_contract_sha="+sha(out/"camss-protected-sample.h"))

if __name__=="__main__":
    main()
