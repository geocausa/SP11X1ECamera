# E003i DP — bounded native AEC cap sensor loop

Status: FAIL_CLOSED_IQ_AWB_ZERO_WEIGHT; GOLDEN_RETURNED; CANDIDATE_RETIRED.

DP is a fresh disposable live candidate after DO/DN closed the missing Windows CapExposure branch inputs. It does not reuse the consumed DB candidate identity or runtime directory.

Attempt 1 reached G1-G3 native AEC successfully and proved the DN cap integration live through G3. The run then failed closed because the live IQ producer encountered a legitimate G1 AWB sample with zero aggregate AGW weight (all eight P01 survivors were rejected by P04). With no R5 queued, the kernel six-frame worker safely unwound and returned the fourth V4L2 buffer as an error buffer with sequence 0; the userspace ordering guard then pinned. See LIVE-FAILURE-ATTEMPT1.txt. Do not repeat this consumed candidate. The next gate is the exact Windows zero-weight AWB fallback.

Single variable under test: the live six-frame helper, three-write fail-closed schedule, and atomic IMX681 bootstrap are byte-identical copies of DB attempt4's proven machinery. The compile graph changes only the request recurrence from DJ to DN and adds DN's native internal-cap implementation.

DN is offline-proven against 18 Windows cap pairs, 423 ARM64 arithmetic comparisons, unchanged G1-G3 controls, and the saved G4 failure pair. DO proves ordinary bank9:data10 lookup absence implies w12=0, compact+0x98=0, snap step=0.5, and static history selector offset 1 maps to native H1.

Safety boundary:
- exactly six ordinary front generations;
- at most three sensor writes behind inherited exact DQBUF release gates;
- any AEC, ownership, schedule, geometry, ioctl, or timing failure permanently prevents later writes;
- atomic four-control IMX681 extended-control transport unchanged;
- one candidate boot, one helper invocation, no same-boot retry;
- post-STREAM failure may pin the helper, so invoke through a persistent PiMaster job and recover only by whole-machine Golden reboot;
- Golden remains persistent GRUB default and camera modules stay blacklisted until explicit load.

The inherited EFFECT=G4,G5,G6 messages are scheduling labels from earlier CY/DB evidence, not a promoted final write-to-statistics claim. DP captures six STATS3A/TLBG generations plus exact write timing so that association can be checked after the run.

Residual ISP gain is still not applied, so even a six-generation sensor-side pass is not yet full continuous automatic-exposure parity.
