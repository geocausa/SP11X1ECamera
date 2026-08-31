# E003h 0062r1 candidate — CGC-release diagnostic retry

Distinct retry package after the first 0062 boot froze before persistent journald/PiSlave. Camera assets and camera programming are byte-identical to the public 0062 package: the only camera delta versus consumed 0061 remains removal of the private X1E80100 VFE1 BUS `+0xc08=0x1ff` write, with no replacement zero write.

The retry changes only boot diagnostics: `systemd.unit=multi-user.target`, `plymouth.enable=0`, visible tty0 boot status, and no `quiet`/`splash`. PiSlave is installed under `multi-user.target`, so remote recovery remains available if userspace reaches that target. Package must remain unarmed until a separate public authorization checkpoint.
