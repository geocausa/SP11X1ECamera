# E003h PIX oracle capsule v1

Local disposable runtime input only. The capsule is not committed.

Header is 1024 bytes, little-endian, magic `E3HPIX01`, version 1. It carries two startup period values, two priming period values, steady variant `0x958`, a u64 request ID, u32 subrequest, and 36 `<type,index,offset,size>` descriptors. Section data is 64-byte aligned.

Section types: 1 = four refined startup normalized main lists; 2 = sixteen startup DMI payloads; 3 = one normalized steady main list; 4 = nine 32-byte named-module value/valid-mask records; 5 = fourteen steady DMI payloads in the Linux 0025 payload-slot order.

The schema deliberately contains no Windows allocator address, source-window offset, or ring stride. Captured period/module/payload values are same-machine oracle test inputs, not a production algorithm or formula.
