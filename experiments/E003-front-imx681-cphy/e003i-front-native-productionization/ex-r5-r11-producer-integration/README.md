# E003i-EX — R5-R11 producer integration

Status: **offline integration only; no EX camera runtime.**

EX is a fresh extension of the closed EN producer. It preserves G1..G6 behavior and extends the existing post-R6 template-free composer to G7/G8 -> R10/R11. The replay source is the successful EV nine-frame Linux capture, so sequential trigger, Tintless/LSC and stateful calibrated AWB state advance through the exact Linux generations that will seed R10/R11.

R10/R11 stay inside existing oracle coverage: EB proves stable post-R6 GTM through R12, ED proves sequential LSC/Tintless through R12, and EL/EG prove calibrated AWB/GainAdj through R11. No new Windows stream is required for this bounded extension, and no whole-capsule Windows R10/R11 equality is claimed.
