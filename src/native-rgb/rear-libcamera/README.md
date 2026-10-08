## 2026-10-08 rear35 source-locked output commit qualified, hardware pending

34 hardware fixed the QBUF waitqueue fault and delivered1 VB2 buffer while live.
Generation3 address writes alone produced no consumed receipts: timeout-110,
IPP33epochs/12events, no overflow/errors/hazards; mappings conservatively held
until automatic Golden8be04a9a-5760-416c-9f4e-25c2a16ad619.34 consumed/retired,
units disabled, no watchdog, protected hashes unchanged. Never retry34.
Source startup packets end with CSID RUP/AUP0x01f501f5 at named register0x18.
Fresh35/build46 applies that exact commit after all10 address readbacks under
exclusive rear-owner/epoch/live-path guards; no command-DMA resubmission.
22 checks PASS,3 ARM64 W1/Werror modules0 diagnostics; actual fixed MMIO helper
GCC/Clang537 assertions,15 negatives each; queue26529 assertions/211 negatives/
80 model frames each. Runtime103 negatives. All hardware APIs are models.
35 unconsumed/uninstalled/unarmed; libcamera04 unchanged. NEXT35 real80 Requests.
Hardware32 remains latest clean success; no persistent rear proof yet.
Native56/66IDs132boots/prestream10/failed-after-start21; combined73IDs146boots.
No adaptive IPA, SensorTimestamp, full-rate/soak or optical parity claim.
Evidence docs/NATIVE-RGB-REAR-GENERATION-34-20261008.json and
docs/NATIVE-RGB-REAR-GENERATION-35-PREP-20261008.json.
Earlier entries are historical.

## 2026-10-08 rear34 queue initialization repaired, source qualified, hardware pending

33 consumed/retired after a pre-sensor kernel Oops in QBUF3: rear worker started
without initializing the shared buffer waitqueue. No packets or frames; mandatory
return to Golden6a092b27-5fae-40d7-8ffd-5900bd57a007 succeeded, protected hashes
unchanged; units disabled, no watchdog. Never retry33.
Fresh34/build45 initializes the queue at video registration before any callback.
21 checks PASS,3 ARM64 W1/Werror modules0 diagnostics; actual QBUF/start/join
GCC/Clang271 assertions each plus omitted-initializer negative control rejected.
Rolling queue28030 assertions/211 negatives/80 simulated frames each retained.
libcamera04 unchanged. NEXT one-use34 hardware80 reused4K NV12 requests.
34 unconsumed/uninstalled/unarmed; hardware32 remains latest success.
Native55/65IDs130boots/prestream10/failed-after-start20; combined72IDs144boots.
No continuous rear/adaptive IPA/SensorTimestamp/full-rate/optical parity claim.
Evidence docs/NATIVE-RGB-REAR-GENERATION-33-20261008.json and
docs/NATIVE-RGB-REAR-GENERATION-34-PREP-20261008.json.
Earlier entries are historical.

## 2026-10-08 rear33 continuous Request queue source qualified, hardware pending

Fresh33/build44 + libcamera04 passed20 pre-install checks; all3 ARM64 modules
W1/Werror with zero diagnostics. Actual rolling queue/ledger/address writes/live
output retirement: GCC and Clang ASAN/UBSAN each28030 assertions,80 model
completions,211 negative cases. Runtime/graph admission102 negatives.
Hardware APIs are models; no rear continuous hardware proof yet.
Four application DMA-BUF Requests reuse buffers until80 real completions;
all10 replacement consumed addresses and stable owner observation precede live
FULL/8aux retirement and VB2 delivery. Startup commands retired once, no command
resubmission; fixed startup ISP settings. Stop joins worker before cancellation.
Latest physical success remains32: two4K linear NV12 Requests and clean release.
33 unconsumed/uninstalled/unarmed; automatic Golden return + independent watchdog
required. Superseded43/lib03 remained source-only, never installed/consumed.
Golden8ec205f1-a1c1-4493-96ad-3f6d9e6a1395; native55/64IDs128boots, prestream9,
failed-after-start20; combined71IDs142boots. Source28 remains unconsumed/uninstalled.
NEXT install and qualify33 persistent rear capture, then restart/lifecycle,
semantic IPA/statistics/controls/SensorTimestamp and matched Windows optics.
No rear adaptive IPA, SensorTimestamp, full-rate, long-soak or optics claim.
Evidence docs/NATIVE-RGB-REAR-GENERATION-33-PREP-20261008.json.
Earlier entries are historical.

# Rear libcamera public request qualification

Isolated standard libcamera pipeline for two rear 4K NV12 requests using exported/imported DMA-BUF application buffers. Kernel hardware ISP produces all pixels. The handler does not map pixels, implement a software ISP, or provide a camera daemon.

The candidate remains finite and uses the private compiler-bound startup profile. It proves application request transport and lifetime, not continuous capture, independent rear IPA, adaptive IQ, exposure timestamps or Windows quality parity. Maintained front pipeline/IPA sources are unchanged.

Continuous work must replace the fixed 16-entry completion history with a consumed event queue and establish live buffer retirement before releasing any mapping while hardware runs. Existing rear retirement only authorizes full-stop release; never substitute false stop proofs to recycle a live mapping.
