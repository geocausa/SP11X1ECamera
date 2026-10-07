# Frame-associated front statistics

The optional metadata overlay requires the qualified native NV12 queue and its
consumed-owner checks. Its module flag defaults false. It registers msm_vfe1_stats
as a standard V4L2 META_CAPTURE node linked to VFE1 PIX, with four-byte format
QXS1. This is an experimental platform format; no upstream FourCC registration
or complete public product ABI is claimed.

Each metadata buffer contains a 64-byte little-endian header followed by the
owned AEC_BE, BHist, AWB_BG and TL_BG active prefixes. Its sequence and timestamp
match the processed video buffer. A new video STREAMON gets a fresh stream ID.
The source sequence is the hardware completion counter, not an app request ID.
Statistics are copied to vb2-backed metadata memory only after all five
consumed-owner groups have retired, before the corresponding video completion.
No metadata buffer becomes a new hardware DMA target.

Video and metadata queues are independent. Missing metadata buffers do not stall
pixel DMA; cumulative drops and discontinuity are reported, and this development
consumer rejects gaps. A delivery mutex serializes copy and STREAMOFF. Unregister
removes the owner pointer under a mutex; video-device references keep CAMSS alive
while FDs or mappings survive removal. Metadata stop returns pending buffers
without changing camera hardware.

The shared envelope validator is used by the real libcamera libipa helper.
It rejects malformed sizes, stale stream/frame IDs, timestamp mismatch and
discontinuity, preserving caller outputs on error. Existing source-qualified AEC
interpretation is reused. This is still helper integration, not the completed
CAMSS pipeline/IPA runtime. Raw capsules remain diagnostic until typed parameter
submission replaces them.

Consumed and retired metadata02 passed80 video/metadata pairs, including reversed vb2
pixel order, matching hardware sequence, timestamps, stream ID, exact payload
bounds and valid AEC luma reduction. Test input and raw statistics stay private
on SP11; derived counts may be committed. It must stop both queues, reach standby
and neutral topology, return Golden unchanged and retire its one-use identity.
Never rearm after an attempt.


Metadata01 is consumed and retired. It reached the complete120-link graph,
but the old runner selected msm_vfe1_stats as the first VFE source-pad remote and
rejected the actual pixel endpoint before hardware startup. All sensors remained
suspended; zero ownership/fault markers and unchanged Golden assets. The corrected
metadata overlay looks up the exact pixel link in metadata mode, preserving the
old upstream route checks. See docs/NATIVE-RGB-FRONT-META-01-20261007.json.
Never rearm metadata01.


Metadata02 physically passed all80 paired frames, exact video timestamps/sequence,
stable stream ID, no metadata gaps, and80 valid AEC luma reductions. All405
consumed-owner checks passed. Both queues stopped; neutral topology, standby,
zero critical faults and unchanged Golden. No live3A or optical claim.
See docs/NATIVE-RGB-FRONT-META-02-20261007.json. Never rearm metadata02.
