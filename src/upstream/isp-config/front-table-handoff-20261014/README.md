# Own front LSC/ABF table handoff

Existing fit-lsc.py and gen-abf-lut.py, measured outputs and calibrated native
unified48/libcamera21/run93 remain authoritative. No refitting, spatial math,
mesh resampling, tuning extraction or new calibration is done here.

The existing native override copied own tables into private capsule offsets.
New typed preparation admits the same existing outputs directly and serializes
four DMI transfers: LSC4308 selectors1/2/3,884bytes each; ABF4908 selector1,
256bytes. Source builders b3cda0 and b404f0 execute with owned ordinary contexts.
Their fixed addresses, sizes, selectors and word-to-byte offsets are observed;
original CDM helpers are argument observers/success only, not serializer proof.
Constructors and the LSC/ABF arithmetic packers are not executed by this fixture.
Prior front generator/backend work supplies prepared-format policy.

Own LSC has13-bit Q10 lanes at0/14, identical green lanes and zero selector3.
Own ABF has9-bit nonzero inverse-noise values and exact decrements, zero last
decrement. These are own generator admission policies, not all hardware modes.
Actual already-generated measured front files are tested locally on SP11.
Their values and hashes remain on SP11 and are not committed or exported.

Request-tagged ownership follows retained E007i: reject stale/incomplete input
before publication. New startup admits nonzero matching parent-owned request ID;
no assertion that rear request>=4 is valid front startup policy.

One allocation contains disjoint declared LSC/ABF extents. Parent must prove
immutable CPU/DMA correspondence, live mappings, bank/configuration setup,
exclusive startup and completion lifetime. This compiler validates arithmetic
and encoding only and emits no module/bank activation, profile reads or runtime.
The optional ABF request flag at17130=1 reaches unmodeled source context and is
not admitted or treated as logging-only. Ordinary flag0 is the qualified fixture.

Core/module controls, complete LSC/ABF configuration and precision remain open.
This48byte table plan is not a complete startup and does not alter the117-address
configuration catalog. Both private runtime consumers remain/upstream_ready=false.

Qualification:38 original-builder cases;2050 commands/3702 atomic negatives
and six compiled unsafe mutations each GCC/Clang ASan/UBSan PASS, including
one actual existing own measured table pair per compiler. Final source native02/
compile02; earlier header alignment checkpoint excluded. Evidence in
`docs/FRONT-TABLE-HANDOFF-20261014.json`.
