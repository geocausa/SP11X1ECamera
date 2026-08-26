# E001 Windows driver provenance for static routing RE

Exact installed Windows binaries used only as local oracle inputs; raw binaries are not committed.

| Binary | SHA-256 | Size | Relevant RE result |
|---|---|---:|---|
| `qccamplatform8380.sys` | `836714ec41f92f45af363d7bf3c9b9cfc2cccdbd19a1c57f355b471068648049` | 144584 | PCFG parser RVA `0x2ef0`; I2C-master splitter RVA `0xa988` |
| `qccammipicsi8380.sys` | `033f5b1431ad4c76a12ac3b7f0a5be42e460a03bcff40d249511b3034786d407` | 104648 | host CSI diagnostics include PHY index/mode, lane count and data rate |
| `surfacecamrearsensor8380.sys` | `b7d7a278c5e7b92ebf35f870a7e06cbad670ffb35bfaf40106e27b09bf33fabb` | 164216 | CSI payload logs lane mask/assign, 3-phase, combo, lane count, settle time and data rate |

The Surface rear sensor driver reports file version `1.0.4258.7908`. Core Qualcomm binaries report embedded file version `1.0.0.20182`; INF package revision is separately recorded in E000/E001 provenance.
