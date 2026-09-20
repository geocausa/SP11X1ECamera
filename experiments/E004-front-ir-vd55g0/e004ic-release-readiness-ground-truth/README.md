# E004ic — synchronize current camera-stack release-readiness truth

OFFLINE STATIC PASS, 2026-09-20. The maintained
src/sp11-camera-stack/READINESS.md had a stale front RGB paragraph,
still claiming that no post-G3 naturally changed one-shot could apply.
This contradicted BOTH the existing maintained READINESS.json and the
original consumed E004en live acceptance evidence dated 2026-09-15:
27 front frames, exactly one naturally changed native post-G3 IMX681
write from G4/request7 for effect at G7, no synthetic control delta,
no second later write, no same-boot rerun, and proper Golden return.
E004en's old one-shot is consumed and MUST NOT be repeated.

We corrected the maintained human-readable readiness paragraph, leaving
the accepted full-stack package inputs, original captured logs, protected
worker source and completed camera runtime untouched. We also added a
separately named safety_gates section to maintained READINESS.json,
without overwriting the historically true accepted RGB or protected
trust fields. The status now explicitly distinguishes:

* Guarded, non-default rear/front RGB package: ready under E004eo.
* Changed front post-G3 feedback: already PROVEN by E004en.
* Unilluminated live VD55G0: 16 ambient frames processed in E004fu,
  with low optical signal and NO face-auth quality conclusion.
* Uninstalled HLOS C+public face-model diagnostic: E004ia PASS only
  on a pinned visible-light public example, no user enrollment.
* Native Linux IR illumination: E004ge still has FIVE independent
  physical safety evidence categories missing, including genuine
  host/strobe-fault autonomous off proof; activation stays BLOCKED.
* Protected IR / Windows Hello runtime: unsigned SecurePD worker still
  lacks legitimate production signing/admission; no verification bypass.
  Full 1:1 default promotion remains HELD, independent of the RGB result.

verify_readiness.py pins these exact original E004en/EO/FU/GE/IA evidence
files and current maintained READINESS.md/JSON to SHA256 hashes, checks
the actual accepted statuses, rejects stale scene narrative and unsupported
IR/biometric/trust conclusions. test_readiness.py exercises 11
in-memory contradictory release states that fail closed.
No Windows/KD, reboot, camera, LED, PMIC/SPMI, Golden or PAM interaction
was needed. This is a release documentation and gate-consistency fix,
NOT a new physical IR/optical, signed-worker or camera runtime test.
