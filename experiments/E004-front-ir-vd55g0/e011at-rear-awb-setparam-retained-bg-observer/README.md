# E011AT — actual AWB SetParam retained BG observer

Prepared from parent96e7a441 (observer scripts checkpoint0482be9d). One fresh Windows user-mode CDB run will bracket the actual CAWBMain::AWBSetParameter actor record at +FB744, watch the retained quad at +FB798, observe the source-identified tuning helper, and compare the first GetParam2/publication/cold consumer. This is specifically upstream of the closed GetParam2 copy boundary.

No kernel debugger, kernel/BCD change, raw optical storage or Linux camera action. Original code, process data and captures remain private on the same SP11. One camera Start/Stop only; atomic entry marker, manual-only task, explicit detach and normal reboot to protected Golden are required. The identity is consumed on entry and must never be reused. Native rear runtime remains denied.
