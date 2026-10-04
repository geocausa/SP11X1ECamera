# E011EL: joined parent mode-parser prefix

Status: PASS_JOINED_PARENT_MODE_PARSER_PREFIX.

E011EL resumes the accepted E011EK state at 0xCED150 with parent frames retained and the selected stream non-null. Across four selected-object placements, original source sets the exact 0xCED174 -> 0xCFA968 arguments, enters 0xCFA968, and executes the complete 0xCFA2E0 mode parser.

The parser's first new global dependency is 0x16A382C. It is writable virtual-zero BSS and Ghidra finds two direct reads and no direct writer references. E011EL therefore admits only a bounded source cold-zero model; native runtime selection remains explicitly unqualified. The accepted immutable two-byte mode literal remains SHA-pinned and unexported. The parser returns flags 0x100000000 with validity 1 in all four cases.

At the next frontier, 0xCFA968 has prepared the exact call arguments for 0xCFA9BC -> 0xCFD550: local result pointer, retained 640-byte formatted output, w2=0, w3=128 and w4=384. The call itself is not executed here. Until that boundary all new writes are stack-only; the selected object and formatted output remain unchanged, the selected-object lock remains held and the index-8 global lock remains released.

Totals: 4 cases, 4 exact cold-global reads, 16 exact mode-literal reads, 8 qualified call-argument sets and 60 altered-contract rejections. NEXT E011EM follows the CFD550/CFCC18 wrapper path and stops before deeper 0xCFD410 effects unless independently qualified. IRQ/DMA/IOMMU and distinct front hardware retirement remain parallel dynamic gates. Native rear runtime remains denied.
