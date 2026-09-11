# E003i-EO — bounded R5–R9 live one-shot

Status: **staged offline; not installed, not armed, no runtime yet.**

EO is the fresh disposable live successor to consumed EA. It preserves EA's six-frame / exactly-three-sensor-write current-first safety envelope and changes only the IQ side needed to extend the bounded proof through R9:

- parent CQ gain feed publishes G1..G6 (EN), while sensor release remains G1@G2, G2@G3, G3@G4 only;
- producer consumes all six paired STATS3A/TL_BG generations;
- R5/R6 keep the accepted EA compatibility path;
- R7/R8/R9 use EM, which is template-free for those requests and joins DV Demux, EL AWB scalars, sequential Tintless LSC/GIC and EB's stable post-R6 GTM.

Live acceptance requires five successful submissions R5..R9, six parent↔producer gain-feed matches, unchanged three-write sensor schedule, clean STREAMOFF/kernel health, and a post-run same-scene offline replay of the new run's own G1..G6 evidence reproducing all five saved submitted capsules byte-for-byte. The six-frame loop can prove R9 submission/acceptance only; it does **not** prove a later frame visibly applied R9. Unrestricted continuous AEC remains outside this checkpoint.
