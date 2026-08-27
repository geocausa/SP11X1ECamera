# E003b pre-runtime result

Status: **READY FOR ONE-SHOT RUNTIME IDENTITY TEST**.

Hard boundary: electrical identity only. No front CAMSS port, endpoint, remote-endpoint, V4L2 sensor or C-PHY configuration exists in this candidate.

## Accepted artifacts

- accepted R3 source DTB base SHA-256: `8cb5783fed2711758763aa81dc2f28c9f348259830ad6f57ffa18a6c5fd0d553`
- E003b candidate DTB SHA-256: `0fef5f385392fe74823a730a52a1c65848c145e402f01dcafe8eb7ce9301f4fa`
- probe module SHA-256: `fa191954fe8682703bcf7c813de56fa9f29b59476de0b9e9b261fab0d0889cc7`
- probe srcversion: `3881AD933BB056C941626AB`
- exact Golden vermagic: `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`
- module imports: 24/24 exact Golden CRCs, 0 missing/mismatched
- E003b initrd SHA-256 A/B: `d993971920e33a4e73aa2f29e34a222283809354b0f8402336e46a6bc248ca8b`
- initrd semantic delta over accepted R3: exactly 4 entries

## DT semantic gate

- node changes: 11
- property changes: 470
- phandle-renumber-only: 401
- unexpected nodes: 0
- unexpected properties: 0
- `E003B_DT_SCOPE=PASS`

The two source patches replay with `patch --fuzz=0 -p1` against the exact accepted pre-E003b source state.

## Runtime acceptance

Require all of:

1. one-shot boot marker proves E003b, while saved Golden remains `sp11-audio-fullio-v19c`;
2. probe logs `IMX681 chip ID 0x0aff at 0x10`;
3. probe immediately tears down reset/MCLK4/LDO7_B/LDO3_M;
4. CSIPHY2 remains unused; no front media endpoint exists;
5. no serious kernel fault; Wi-Fi, touch and FullIO audio remain healthy;
6. return to Golden and verify Golden hashes/state.
