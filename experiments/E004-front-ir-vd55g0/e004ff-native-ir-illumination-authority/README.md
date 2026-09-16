# E004ff: native IR illumination authority (offline)

E004fe closes generated-pattern processing. Ordinary IR captures remain near
pedestal, so illumination is a concrete candidate cause, not yet a proven cause.

The exact exported Qualcomm flash extension INF specifies the DWORD
IrLedCurrentMilliampere=700. The exact flash binary independently uses 700 mA as
both registry fallback and object default. Its registry-derived value is passed
to the white-LED configuration object. These are configuration facts, not a live
current measurement, proof of final registry binding, or permission to light it.

E004g already proved hardware trigger type 0 for this sensor and the sensor's
GPIO1 strobe selector. The physical PMIC channel, polarity, exposure pulse width,
safety timeout and sustained duty cycle still need same-machine confirmation.
FLSH ACPI identifies QCOM0C27 with no direct register resources; it does not provide
the physical PMIC channel mapping. The existing Denali DT has a disabled PM8550
flash node, so that node alone is not proof it controls the IR emitter.

A native implementation can potentially reuse LED flash class, V4L2 flash controls
and leds-qcom-flash. Inspection of the current local driver and hash-pinned upstream
source found that external strobe only enables the module/channels, while current
and timeout callbacks merely cache requests. The software strobe path performs
budget checks, current programming and timeout programming. V4L2 switching to
FLASH first turns torch off; the torch callback selects torch-current resolution
and disables the timeout. Thus the external path needs the same preparation before
arming. E004fg will address this in an isolated compile-only patch/test.

No PMIC or illumination register was changed. Sensor GPIO outputs remain disabled;
Golden FullIO v19c remains permanent. Linux SecureISP remains inactive.
RESULT.json pins all input hashes and the exact upstream revision inspected.
