# E006i — source-lock rear 0x49B8/0x49BC to BPC/ABF411 calculated state

Parent Git: ca755b20 (E006h rear steady symbolic compose PASS).

Status: **STATIC/OFFLINE PASS**. No camera runtime, reboot, module load, MMIO mutation or new Windows oracle run was performed.

## Question

E006h left exactly two request-varying IFE register offsets with unnamed producer ownership:

- 0x49B8
- 0x49BC

They remained symbolic and therefore could not be accidentally frozen, but the steady rear materializer cannot be considered producer-complete until their source is identified.

## False-friend correction

A first literal-scalar search of QcDeviceMFT8380.dll also found the numbers 0x49B8 and 0x49BC as **byte offsets inside the CamX global settings object**:

- settings +0x49B8 = vsrFactor
- settings +0x49BC = dualIFESplitPointOffset

Those are unrelated structure offsets and are **not** IFE hardware register ownership evidence. They are explicitly rejected as a numerical coincidence.

The hardware-register trace below instead follows the Titan680 IQ command writer that emits register address ranges into the RT-CDM packet.

## Exact hardware owner

Pinned same-SP11 binary:

- QcDeviceMFT8380.dll
- SHA-256 c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35

Surviving source strings identify:

- CamX::IFEBPCABF411Titan680::CreateCmdList
- camx/src/hwl/isphwsetting/titan680/camxifebpcabf411titan680.cpp

The exact CreateCmdList decompilation writes the BPC/ABF411 register structure in these ranges:

- 0x4958, count 3
- 0x4968, count 2
- 0x4980, count 4
- **0x49A0, count 8**
- 0x49C8, count 9
- DMI 0x4908 selector 1, 0x100 bytes

Therefore 0x49B8 and 0x49BC are words 6 and 7 of the eight-register **0x49A0..0x49BC BPC/ABF411 range**. They are definitively part of IFEBPCABF411Titan680.

## Exact packing

Surviving source strings identify the packer:

CamX::IFEBPCABF411Titan680::PackIQRegisterSetting

The packed register array maps:

- puVar4[0x0F] -> hardware 0x49B8
- puVar4[0x10] -> hardware 0x49BC

For 0x49B8 the exact decompilation packs:

- bits 0..9 from signed/calculated field puVar5[0x28] masked to 10 bits
- bits 16..24 from puVar5[0x26] masked to 9 bits
- bits 28..31 from puVar5[0x2A] masked to 4 bits

For 0x49BC it packs:

- bits 0..9 from signed/calculated field puVar5[0x29] masked to 10 bits
- bits 16..24 from puVar5[0x27] masked to 9 bits
- bits 28..31 from puVar5[0x2B] masked to 4 bits

These are calculated BPC/ABF411 setting fields, not ping-pong-bank bits.

## Request-time producer chain

Surviving source strings and decompilation source-lock:

CamX::IFEBPCABF411::CheckDependenceChange
-> CamX::IFEBPCABF411::RunCalculation
-> CamX::IQInterface::BPCABF411CalculateSetting
-> BPCABF41 interpolation/common-library hardware setting
-> CamX::IFEBPCABF411Titan680::PackIQRegisterSetting
-> CamX::IFEBPCABF411Titan680::CreateCmdList

The IQInterface calculation performs BPCABF41 interpolation and then the Titan680 hardware-setting pack. Therefore 0x49B8/0x49BC belong to the existing **BPC_ABF** producer family, but their actual request-time values require the BPCABF411 calculated setting, not the front-only bank toggle model.

## Private-corpus scalar reduction

The retained private E006a record set was temporarily relayed to SP11 cache and reduced only to the two register values. The temporary copy was then deleted.

22 selected/complete MAIN records contained the pair.

Observed pair values:

- 18 records: 0x49B8 = 0xA09A0000 and 0x49BC = 0xA09A0000
- 4 records: 0x49B8 = 0xA0CD0000 and 0x49BC = 0xA0CD0000

They were equal in every observed record.

Sequence highlights:

- startup n0: A09A
- startup n1/n2: A0CD
- early steady AC8 n4/n5: A0CD
- AC8 n6 onward: A09A
- A98 n25/n26: A09A

Under the exact pack:

- low 10-bit field = 0 in both observed states
- top 4-bit field = 0xA in both observed states
- the 9-bit middle field changes 0xCD -> 0x9A

This is consistent with a request-time BPC/ABF411 calculated-setting transition, not a simple 0/1 bank toggle.

## Linux consequence

The existing front Linux BPC_ABF contract modeled only:

- 0x4958 / 0x495C bank fields
- 0x4908 selector1 0x100-byte DMI

because those were sufficient for the accepted front steady evidence.

Rear requires the BPC_ABF producer interface to be widened so it can also supply the calculated scalar words:

- 0x49B8
- 0x49BC

This does **not** imply a new IQ module. It is the same BPC/ABF411 producer family.

The complete BPCABF411 algorithm is not claimed ported by this experiment. The owner and exact Titan680 packing contract are closed; request-time algorithm integration remains a Linux implementation task.

## Decision

E006h's two unnamed dynamic register owners are closed:

- 0x49B8 -> BPC_ABF
- 0x49BC -> BPC_ABF

No additional Windows/KD experiment is needed for ownership.

Next: widen the compile-only rear producer binding so BPC_ABF explicitly owns those two scalar words, then verify the steady materializer contract remains unreachable and W=1 clean.

Native rear Linux processed ISP remains **DENIED**.
